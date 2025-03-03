from openai import OpenAI
import os
from pathlib import Path
import base64

"""
OpenAI Client object that will facilitate communication between 
user and OpenAI API. Built on top of OpenAI develop quickstarts (https://platform.openai.com/docs/overview)
for Sight Guide specific use.
"""

class OpenAIClient:
    def __init__(self):
        """
        Initializes an instance of OpenAIClient
        """
        self.set_api_key()
        self.client = OpenAI()


    def set_api_key(self):
        """
        Retrieves OpenAI key stored in file 'openai_apikey.txt' and sets an environment variable for the API key
        """
        with open("./openai_apikey.txt", "r") as f_obj:
            api_key = f_obj.read().strip()

        os.environ["OPENAI_API_KEY"] = api_key


    def upload_text_prompt(self, prompt: str) -> str:
        """
        Makes an API call to OpenAI where the given prompt is processed
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    

    def general_visual_aid(self, image_path: str ) -> str:
        """
        Makes an API call to OpenAI where image is processed to determine objects 
        within a camera image
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant for a visually impaired user."},
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you give a general description of what is in front of me please."},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url":  f"data:image/jpeg;base64,{self.encode_image(image_path)}"
                    },
                    },
                ],
                }
            ],
            max_tokens=300,
        )

        return response.choices[0].message.content


    # Function to encode the image (Souce: OpenAI Documenation)
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    
    def generate_audio(self, text: str) -> None:
        """
        Generates speech from a given input using OpenAI's audio generation
        """
        speech_file_path = Path(__file__).parent / "audio" / "speech.mp3"
        response = self.client.audio.speech.create (
            model = "tts-1",
            voice = "nova",
            input = text
        )
        response.stream_to_file(speech_file_path)
            
