from openai import OpenAI
from pathlib import Path
from typing import Union
import os
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


    def upload_text_prompt(self, prompt: str) -> Union[str, None]:
        """
        Makes an API call to OpenAI where the given prompt is processed
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a visually impaired user. Can you also limit the text to 20 words please!"},
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print("An error occurred while processing the prompt.")
            return None
    

    def general_visual_aid(self, image_path: str ) -> Union[str, None]:
        """
        Makes an API call to OpenAI where image is processed to determine objects 
        within a camera image
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant for a visually impaired user. Your job is to help a visually impaired user get around and know what's in their surrounding."},
                    {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Can you give a general description of what is in front of me please. It's also important to point out things that can pose danger to me, "
                        "You should also point things out that a blind person might wanna know the direction of, such as doorways and handicap accessible ramps (Only if its in the image). Keep it under 60 words"},
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
        except Exception as e:
            print("An error occurred while processing the image.")
            return None


    # Function to encode the image (Souce: OpenAI Documenation)
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    
    def generate_audio(self, text: str) -> Union[str, None]:
        """
        Generates speech from a given input using OpenAI's audio generation
        """
        speech_file_path = Path(__file__).parent / "audio" / "speech.mp3"
        try:
            response = self.client.audio.speech.create (
                model = "tts-1",
                voice = "nova",
                input = text
            )
            response.stream_to_file(speech_file_path)
            return "Speech generated successfully."
        except Exception as e:
            print("An error occurred while generating audio.")
            return None

            
