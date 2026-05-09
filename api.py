import os
import json
from dotenv import load_dotenv
from openai import OpenAI

class LLMHelper:
    def __init__(self):
        """Get API key from the .env"""
        load_dotenv()
        self.api_key = os.getenv("AZURE_API_KEY")
        
        self.base_url = "https://cuhk-apip.azure-api.net/openai-eus2/openai/v1"
        
        if self.api_key:
            self.client = OpenAI(
                base_url = self.base_url,
                api_key = self.api_key,
                default_headers = {"api-key": self.api_key},
            )
        else:
            print("Error: AZURE_API_KEY not found in .env file.")
            self.client = None

    def generate_jeopardy_board(self, num_categories=3, clues_per_category=3):
        """Call API to generate a list of categories and questions."""
        if not self.client:
            return None

        system_prompt = (
            "You are a Jeopardy game show assistant. "
            "Generate trivia categories and clues. "
            "Always respond ONLY in valid JSON format. Do not include markdown code blocks like ```json."
        )

        user_prompt = (
            f"Generate a Jeopardy board with {num_categories} categories. "
            f"Each category must have {clues_per_category} clues with values $200, $400, $600. "
            "For each clue, provide the clue text, 3 multiple-choice options (phrased as questions, e.g., 'What is X?'), "
            "and specify the correct answer exactly as it appears in the options. "
            "Format the output strictly as this JSON structure:\n"
            "{\n"
            "  \"categories\": [\n"
            "    {\n"
            "      \"name\": \"Category Name\",\n"
            "      \"questions\": [\n"
            "        {\n"
            "          \"value\": 200,\n"
            "          \"clue\": \"Clue text here\",\n"
            "          \"choices\": [\"Option 1\", \"Option 2\", \"Option 3\"],\n"
            "          \"correct\": \"Option 2\"\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        print("Sending request to Azure ChatGPT... (This might take a few seconds)")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            chat_reply = response.choices[0].message.content
            
            chat_reply = chat_reply.strip()
            if chat_reply.startswith("```json"):
                chat_reply = chat_reply[7:-3].strip()
            elif chat_reply.startswith("```"):
                chat_reply = chat_reply[3:-3].strip()
            
            board_data = json.loads(chat_reply)
            return board_data

        except Exception as e:
            print(f"Failed to generate questions: {e}")
            return None

# --- Testing Block ---
if __name__ == "__main__":
    llm = LLMHelper() 
    
    test_board = llm.generate_jeopardy_board(num_categories=2, clues_per_category=2)
    
    if test_board:
        print("\nSuccess! Here is the parsed data:\n")
        print(json.dumps(test_board, indent=4))
    else:
        print("\nFailed to get the board.")