import os
from enum import Enum
from OpenAI_Client import OpenAIClient
from picamera2 import Picamera2, Preview
from gpiozero import Button

import time
import pigpio
from gpiozero import DistanceSensor 
from gpiozero.pins.pigpio import PiGPIOFactory

# Constants
MAX_DISTANCE = 220  
OUTLIER_THRESH = 100
VIBRATE_COOLDOWN = 4

# GPIO Pin Definitions
TRIG1, ECHO1 = 5, 6
TRIG2, ECHO2 = 4, 17  
TRIG3, ECHO3 = 27, 22
TRIG4, ECHO4 = 10, 9
TRIG5, ECHO5 = 13, 26 
MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR = 14, 15, 23, 24, 25  # PWM motor control pins


factory = PiGPIOFactory()

# Initialize ultrasonic sensors
sensor_list = [
    DistanceSensor(echo=ECHO1, trigger=TRIG1, max_distance=MAX_DISTANCE/100, pin_factory=factory),
    DistanceSensor(echo=ECHO2, trigger=TRIG2, max_distance=MAX_DISTANCE/100, pin_factory=factory),
    DistanceSensor(echo=ECHO3, trigger=TRIG3, max_distance=MAX_DISTANCE/100, pin_factory=factory),
    DistanceSensor(echo=ECHO4, trigger=TRIG4, max_distance=MAX_DISTANCE/100, pin_factory=factory),
    DistanceSensor(echo=ECHO5, trigger=TRIG5, max_distance=MAX_DISTANCE/100, pin_factory=factory)
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
    VisualAid = 2


class ControlLogic:
    def __init__(self, project_path: str, state_button: int, visual_aid_button: int) -> None:
        self.state = ControlState.Idle
        self.path = project_path
        self.openai = OpenAIClient()

        self.camera = Picamera2()
        self.camera.start_preview(Preview.NULL)

        self.state_button = Button(state_button, bounce_time = 0.5)
        self.visual_aid_button = Button(visual_aid_button, bounce_time = 0.5)

        self.setup_button()
        if not pi.connected:
            print("Error: pigpio daemon is not running.")
            exit(1)
        for pin in motor_pins:
            pi.set_PWM_frequency(pin, 1000)  # Set PWM frequency
            pi.set_PWM_dutycycle(pin, 0)  # Start with 0% duty cycle

    def setup_button(self):
        self.state_button.when_pressed = self.toggle_state
        self.visual_aid_button.when_pressed = self.visual_aid


    def toggle_state(self):
        print("Toggle button pressed")
        if self.state == ControlState.Idle:
            self.set_state(ControlState.ObjectDetection)
        elif self.state == ControlState.ObjectDetection:
            self.set_state(ControlState.Idle)

    def visual_aid(self):
        print("Visual aid button pressed") 
        if not self.camera.started:
            self.set_state(ControlState.VisualAid)
    
    def set_state(self, state: ControlState):
        os.system("/usr/bin/mpg123 " + self.path + "/audio/" + state.name + ".mp3")
        self.state = state
        self.process()

    def get_state(self):
        return self.state
    
    def process(self):
        if self.state == ControlState.Idle:
            print("Idle")

        elif self.state == ControlState.VisualAid:
            print("Visual Aid")
            self.process_general_visual_aid()
        
        elif self.state == ControlState.ObjectDetection:
            print("Object Detection")
            self.process_object_detection()

    def process_general_visual_aid(self):
        if self.camera.started:
            print("stopping camera before reconfiguring")
            self.camera.stop()

        self.camera.allocator.cleanup()

        config = self.camera.create_still_configuration(main = {"size": (1920, 1080)})
        
        print("configuiring camera")
        self.camera.configure(config)

        print("Starting camera")
        self.camera.start()
        self.camera.capture_file("image.jpg")
        self.camera.stop() 
        print("Image captured and camera stopped")
        self.camera.allocator.cleanup()
        
        image_response = self.openai.general_visual_aid("image.jpg")
        if image_response is None:
            # Process locally
            with open("local_processing.txt", "w") as f_obj:
                f_obj.write("Local")
            while os.exists("/home/edwartiu/SightGuide/image.jpg"):
                pass
            with open("local_processing.txt", "w") as f_obj:
                f_obj.write("Remote")
            os.system("/usr/bin/mpg123 " + self.path + "/audio/speech.mp3")
            self.set_state(ControlState.Idle)
        else: 
            speech_response = self.openai.generate_audio(image_response)
            #if speech_response is None:
            #    pass
            
        os.system("/usr/bin/mpg123 " + self.path + "/audio/speech.mp3")
        self.set_state(ControlState.Idle)

    def process_object_detection(self):
        #if not pi.connected:
        #    print("Error: pigpio daemon is not running.")
        #    exit(1)
        
        for i in range(N):
            # Update distance data
            for j in range(N-1):
                distances[i][j] = distances[i][j+1]

            distances[i][N] = sensor_list[i].distance * 100  # Convert to cm
            print(f"Sensor {i}: {distances[i][N]:.2f} cm")

            sorted_distances = sorted(distances[i]) # Sort the distance data to retrieve median
            distance = sorted_distances[2]

            delta = abs(distance - curr_dist[i])
            
            if 0 <= distance <= MAX_DISTANCE:
                speed = int(0.25 * (255 - (0.65 * distance / MAX_DISTANCE * 255)))
                pi.set_PWM_dutycycle(motor_pins[i], speed)
                # vibrate_array[i] = True
                # vib_counter[i] = 0
            else:
                pi.set_PWM_dutycycle(motor_pins[i], 0)
            
            curr_dist[i] = distance
        time.sleep(0.05)
        

