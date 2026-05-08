import requests
import json

class LLMHelper:
    def __init__(self, key_filename="YOUR_API_KEY_FILE.txt"):
        self.api_key = self._read_api_key(key_filename)
        
        # NOTE
        self.endpoint = "https://cuhk-apip.azure-api.net/openai"

    def _read_api_key(self, filename):
        """Read API key from file."""
        try:
            with open(filename, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"Error: Could not find the file '{filename}'.")
            return None

    def generate_jeopardy_board(self, num_categories=3, clues_per_category=3):
        """Call API to generate a list of categories and questions."""
        if not self.api_key:
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

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }

        print("Sending request to Azure ChatGPT... (This might take a few seconds)")
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            chat_reply = response_data['choices'][0]['message']['content']
            
            board_data = json.loads(chat_reply)
            return board_data

        except Exception as e:
            print(f"Failed to generate questions: {e}")
            return None

# --- Testing Block ---
if __name__ == "__main__":
    llm = LLMHelper(key_filename="api_key.txt") 
    
    test_board = llm.generate_jeopardy_board(num_categories=2, clues_per_category=2)
    
    if test_board:
        print("\nSuccess! Here is the parsed data:\n")
        print(json.dumps(test_board, indent=4))
    else:
        print("\nFailed to get the board. Check your API key and endpoint URL.")