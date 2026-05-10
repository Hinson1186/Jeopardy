import os
import json
import time
import base64
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

class LLMHelper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("AZURE_API_KEY")
        
        self.base_url = "https://cuhk-apip.azure-api.net/openai-eus2/openai/v1"
        self.image_endpoint = self.base_url + "/images/generations/standard"
        
        if self.api_key == None:
            print("API KEY IS MISSING!")
            
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={"api-key": self.api_key},
        )

    def generate_jeopardy_board(self, num_categories=6, clues_per_category=5, round_num=1):        
        # Adjust values based on the round
        if round_num == 1:
            val_str = "200, 400, 600, 800, 1000"
        elif round_num == 2:
            val_str = "400, 800, 1200, 1600, 2000"
        else:
            val_str = "0"
            num_categories = 1
            clues_per_category = 1

        system_prompt = "You are a Jeopardy game show assistant. Generate trivia categories and clues. Always respond ONLY in valid JSON format. Do not include markdown code blocks like ```json."
        
        user_prompt = f"Generate a Jeopardy board with {num_categories} categories. Each category must have {clues_per_category} clues with values {val_str}. For each clue, provide the clue text, 3 multiple-choice options (phrased as questions, e.g., 'What is X?'), and specify the correct answer exactly as it appears in the options. Format the output strictly as this JSON structure: {{\"categories\":[{{\"name\": \"Category Name\", \"questions\":[{{\"value\": 200, \"clue\": \"Clue text here\", \"choices\":[\"Option 1\", \"Option 2\", \"Option 3\"], \"correct\": \"Option 2\"}}]}}]}}"

        print(f"asking gpt-5.1 for Round {round_num} questions... wait a sec")
        
        try:
            res = self.client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            chat_reply = res.choices[0].message.content
            
            # Fix markdown issue
            chat_reply = chat_reply.strip()
            if chat_reply.startswith("```json"):
                chat_reply = chat_reply[7:-3].strip()
            elif chat_reply.startswith("```"):
                chat_reply = chat_reply[3:-3].strip()
            
            return json.loads(chat_reply)

        except Exception as e:
            print("Error getting board:", e)
            return None

    def generate_image_for_clue(self, prompt):
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "medium",
            "output_format": "png"
        }

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        print("asking for image: " + prompt)

        try:
            res = requests.post(self.image_endpoint, headers=headers, json=payload, timeout=120)
            
            if res.status_code == 200:
                img_data = res.json()["data"][0]["b64_json"]
                img_bytes = base64.b64decode(img_data)

                try:
                    os.mkdir("assets")
                except:
                    pass
                try:
                    os.mkdir("assets/images")
                except:
                    pass

                file_name = "assets/images/clue_img_" + str(int(time.time())) + ".png"
                img = Image.open(BytesIO(img_bytes))
                img.save(file_name)
                return file_name
            else:
                print("api error:", res.text)
                return None

        except Exception as e:
            return None