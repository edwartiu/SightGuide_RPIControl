import os
#from main import PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON, MAX_DISTANCE, TRIG1, ECHO1, TRIG2, ECHO2, TRIG3, ECHO3, TRIG4, ECHO4, TRIG5, ECHO5, MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR
from enum import Enum
from OpenAI_Client import OpenAIClient
#from picamera2 import Picamera2
from gpiozero import Button

import time
import pigpio
from gpiozero import DistanceSensor
from signal import pause



STATE_BUTTON = 20
VISUAL_AID_BUTTON = 21
PROJECT_PATH = "/home/lndnf/Documents/SightGuide_RPIControl"

# Constants
MAX_DISTANCE = 220  
OUTLIER_THRESH = 100
VIBRATE_COOLDOWN = 4

# GPIO Pin Definitions
TRIG1, ECHO1 = 5, 6
TRIG2, ECHO2 = 4, 17  
TRIG3, ECHO3 = 27, 22
TRIG4, ECHO4 = 10, 9
TRIG5, ECHO5 = 13, 26 #CHANGE
MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR = 14, 15, 23, 24, 25  # PWM motor control pins


# Initialize ultrasonic sensors
sensor_list = [
    DistanceSensor(echo=ECHO1, trigger=TRIG1, max_distance=MAX_DISTANCE/100),
    DistanceSensor(echo=ECHO2, trigger=TRIG2, max_distance=MAX_DISTANCE/100),
    DistanceSensor(echo=ECHO3, trigger=TRIG3, max_distance=MAX_DISTANCE/100),
    DistanceSensor(echo=ECHO4, trigger=TRIG4, max_distance=MAX_DISTANCE/100),
    DistanceSensor(echo=ECHO5, trigger=TRIG5, max_distance=MAX_DISTANCE/100),
]

motor_pins = [MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR]

pi = pigpio.pi()

# Distance data storage
N = len(sensor_list)
distances = [[0] * 5 for _ in range(N)]
curr_dist = [0] * N

class ControlState(Enum):
    Idle = 0
    ObjectDetection = 1
    VisiualAid = 2


class ControlLogic:
    def __init__(self, project_path: str, state_button: int, visual_aid_button: int) -> None:
        self.state = ControlState.Idle
        self.path = PROJECT_PATH
        self.openai = OpenAIClient
        #self.camera = PiCamera2()
        self.state_button = Button(STATE_BUTTON)
        self.visual_aid_button = Button(VISUAL_AID_BUTTON)
        if not pi.connected:
            print("Error: pigpio daemon is not running.")
            exit(1)
        for pin in motor_pins:
            pi.set_PWM_frequency(pin, 1000)  # Set PWM frequency
            pi.set_PWM_dutycycle(pin, 0)  # Start with 0% duty cycle
        print("end of init")
        self.setup_button()

    def setup_button(self):
        print ("setup button step")
        # self.state_button.when_pressed = self.toggle_state
        # self.visual_aid_button.when_pressed = lambda: self.set_state(ControlState.VisiualAid)
        # while (True): 
        #     time.sleep(0.5)

    def toggle_state(self):
        print("toggle state")
        if self.state == ControlState.Idle:
            self.set_state(ControlState.ObjectDetection)
        elif self.state == ControlState.ObjectDetection:
            self.set_state(ControlState.Idle)
    
    def set_state(self, state: ControlState):
        #os.system("usr/bin/mpg123 " + self.path + "/audio/" + state.name + ".mp3")
        print("set state")
        self.state = state
        self.process()

    def get_state(self):
        return self.state
    
    def process(self):
        if self.state == ControlState.Idle:
            print("Idle")
            self.setup_button()

        elif self.state == ControlState.VisiualAid:
            print("Visual Aid")
            self.process_general_visual_aid()
        
        elif self.state == ControlState.ObjectDetection:
            print("Object Detection")
            self.process_object_detection()

    def process_general_visual_aid(self):
        # self.camera.start_and_capture_file("image.jpg")
        # response = self.openai.general_visual_aid("image.jpg")
        # print(response)
        # os.system("usr/bin/mpg123 " + self.path + "audio/speech.mp3")
        print("Test visual aid")
        self.set_state(ControlState.Idle)

    def process_object_detection(self):
        # if not pi.connected:
        #     print("Error: pigpio daemon is not running.")
        #     exit(1)
        
        # some_condition = True #CHANGE
        # while some_condition:
        #     for i in range(N):
        #         # Update distance data
        #         for j in range(N-1):
        #             distances[i][j] = distances[i][j+1]

        #         distances[i][N] = sensor_list[i].distance * 100  # Convert to cm
        #         print(f"Sensor {i}: {distances[i][N]:.2f} cm")

        #         sorted_distances = sorted(distances[i]) # Sort the distance data to retrieve median
        #         distance = sorted_distances[2]

        #         delta = abs(distance - curr_dist[i])
                
        #         if 0 <= distance <= MAX_DISTANCE:
        #             speed = int(0.25 * (255 - (0.65 * distance / MAX_DISTANCE * 255)))
        #             pi.set_PWM_dutycycle(motor_pins[i], speed)
        #             # vibrate_array[i] = True
        #             # vib_counter[i] = 0
        #         else:
        #             pi.set_PWM_dutycycle(motor_pins[i], 0)
                
        #         curr_dist[i] = distance
        #     time.sleep(0.05)
        #while (True):
        print("hello, test object detect")
        # distance = sensor_list[i].distance * 100  # Convert to cm
        # print(f"Sensor {1}: {distance:.2f} cm")
        time.sleep(0.5)
        self.set_state(ControlState.Idle)

        pass


if __name__ == "__main__":
    control = ControlLogic()

    while True:
        pass
