import os
from enum import Enum
from OpenAI_Client import OpenAI
from picamera2 import Picamera2
from gpiozero import Button


class ControlState(Enum):
    Idle = 0
    ObjectDetection = 1
    VisiualAid = 2


class ControlLogic:
    def __init__(self, project_path: str, state_button: int, visual_aid_button: int) -> None:
        self.state = ControlState.Idle
        self.path = project_path
        self.openai = OpenAI()
        self.camera = PiCamera2()
        self.state_button = Button(state_button)
        self.visual_aid_button = Button(visual_aid_button)

        self.setup_button()

    def setup_button(self):
        self.state_button.when_pressed = self.toggle_state()
        self.visual_aid_button.when_pressed = self.set_state(ControlState.VisiualAid)


    def toggle_state(self):
        if self.state == ControlState.Idle:
            self.set_state(ControlState.ObjectDetection)
        elif self.state == ControlState.ObjectDetection:
            self.set_state(ControlState.Idle)
    
    def set_state(self, state: ControlState):
        os.system("usr/bin/mpg123 " + self.path + "/audio/" + state.name + ".mp3")
        self.state = state
        self.process()

    def get_state(self):
        return self.state
    
    def process(self):
        if self.state == ControlState.Idle:
            print("Idle")

        elif self.state == ControlState.VisiualAid:
            print("Visual Aid")
            self.process_general_visual_aid()
        
        elif self.state == ControlState.ObjectDetection:
            print("Object Detection")
            self.process_object_detection()

    def process_general_visual_aid(self):
        self.camera.start_and_capture_file("image.jpg")
        image_response = self.openai.general_visual_aid("image.jpg")
        if image_response is None:
            # Process locally
            with open("local_processing.txt", "w") as f_obj:
                f_obj.write("Local")
            while os.exists("/home/edwartiu/SightGuide/image.jpg"):
                pass
            with open("local_processing.txt", "w") as f_obj:
                f_obj.write("Remote")
            os.system("usr/bin/mpg123 " + self.path + "audio/speech.mp3")
            self.set_state(ControlState.Idle)
        else: 
            speech_response = self.openai.generate_audio(image_response)
            #if speech_response is None:
            #    pass
            
        os.system("usr/bin/mpg123 " + self.path + "audio/speech.mp3")
        self.set_state(ControlState.Idle)

    def process_object_detection(self):
        pass

