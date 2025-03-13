import os
from enum import Enum
from OpenAI_Client import OpenAIClient
from PIL import Image
from picamera2 import Picamera2, Preview
from gpiozero import Button
import threading

import subprocess
import time
import pigpio
from gpiozero import DistanceSensor 
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device

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
print("PiGPIOFacotry: " )
print(type(factory))

# Initialize ultrasonic sensors
sensor_list = [ DistanceSensor(echo=ECHO1, trigger=TRIG1, max_distance=500, pin_factory=factory), 
DistanceSensor(echo=ECHO2, trigger=TRIG2, max_distance=500, pin_factory=factory),
DistanceSensor(echo=ECHO3, trigger=TRIG3, max_distance=500, pin_factory=factory),
DistanceSensor(echo=ECHO4, trigger=TRIG4, max_distance=500, pin_factory=factory),
DistanceSensor(echo=ECHO5, trigger=TRIG5, max_distance=500, pin_factory=factory)]



motor_pins = [MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR]

pi = pigpio.pi()
lock = threading.Lock()

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

        self.state_button = Button(state_button)
        self.visual_aid_button = Button(visual_aid_button)
        self.cooldown = False
        self.prev_state = ControlState.Idle

      

        #self.factory = PiGPIOFactory(host = 'localhost')
        print("Distance sensor setup begin")
        #self.setup_distance_sensors()
        print("Distance snesor setup end")
        #self.motor_pins = [MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR]
        #self.pi = pigpio.pi()

        #N = len(self.sensor_list)
        #self.distances = [[0] * 5 for _ in range(N)]
        #self.curr_dist = [0] * N

        #if not self.pi.connected:
        #    print("Error: pigpio daemon is not running.")
        #    exit(1)
        #for pin in motor_pins:
        #    self.pi.set_PWM_frequency(pin, 1000)  # Set PWM frequency
        #    self.pi.set_PWM_dutycycle(pin, 0)  # Start with 0% duty cycle



    def listen_visual_aid_button(self):
        print("Listening for visual aid button")
        if self.visual_aid_button.is_pressed:
            print("-----------------------------Held button---------------------------------------")
            time.sleep(0.1)
            if self.visual_aid_button.is_pressed:
                print("-------------------------------Visual aid button pressed-----------------------------------")
                self.set_state(ControlState.VisualAid)

        return False


    def listen_state_button(self):
        print("Listening for state button")
        if self.state_button.is_pressed:
            time.sleep(0.01)
            if self.state_button.is_pressed:
                return True

        return False

    
    def setup_distance_sensors(self):
        self.sensor_list = []
        for i, (trig, echo) in enumerate([(TRIG1, ECHO1), (TRIG2, ECHO2), (TRIG3, ECHO3), (TRIG4, ECHO4), (TRIG5, ECHO5)]):
            try:
                sensor = DistanceSensor(echo=echo, trigger = trig, max_distance=2.0, threshold_distance=1.0)#, pin_factory=self.factory)
                self.sensor_list.append(sensor)
            except Exception as e:
                print(f"Error initializing sensor {i}: {e}")


    def toggle_state(self):
        print("Toggle button pressed")
        if (not self.cooldown):
            with lock: 
                if self.state == ControlState.Idle:
                    self.set_state(ControlState.ObjectDetection)
                elif self.state == ControlState.ObjectDetection:
                    self.set_state(ControlState.Idle)

    def visual_aid(self):
        print("Visual aid button pressed") 
        with lock:
            if not self.camera.started:
                self.set_state(ControlState.VisualAid)
    
    def set_state(self, state: ControlState):
        os.system("/usr/bin/mpg123 " + self.path + "/audio/" + state.name + ".mp3")
        self.state = state

    def get_state(self):
        return self.state
    
    def process(self):
        self.cooldown = False


            
        if self.state == ControlState.Idle:
            self.prev_state = ControlState.Idle
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
            time.sleep(0.1)

        config = self.camera.create_still_configuration(main = {"size": (1920, 1080)})
        
        print("configuiring camera")
        self.camera.configure(config)

        print("Starting camera")
        self.camera.start()
        self.camera.capture_file("image.jpg")
        self.camera.stop() 
        print("Image captured and camera stopped")

        # image rotation
        print("Image rotation start")
        img = Image.open("./image.jpg")
        rotate_img = img.rotate(180)
        rotate_img.save("./image.jpg")

        print ("Image rotation end")
        
        print("Prompt generation start")
        image_response = self.openai.general_visual_aid("image.jpg")
        print(image_response)
        print("Prompt generation end")
        #if image_response is None:
            # Process locally
            #with open("local_processing.txt", "w") as f_obj:
            #    f_obj.write("Local")
            #while os.exists("/home/edwartiu/SightGuide/image.jpg"):
            #    pass
            #with open("local_processing.txt", "w") as f_obj:
            #    f_obj.write("Remote")
            #os.system("/usr/bin/mpg123 " + self.path + "/audio/speech.mp3")
            #self.set_state(ControlState.Idle)
        #else: 
            #speech_response = self.openai.generate_audio(image_response)
            #if speech_response is None:
            #    pass
        #subprocess.run(["/usr/bin/mpg123 " + self.path + "/audio/speech.mp3"],check=True)
        print("Speech generation start")
        speech_response = self.openai.generate_audio(image_response)
        print("Speech generation end")

        os.system("/usr/bin/mpg123 " + self.path + "/audio/speech.mp3")
        self.set_state(self.prev_state)

    def process_object_detection(self):
        time.sleep(0.2)
        print("Obstacle detection activated")

        visual_aid = False
        state = False
        while(not visual_aid and not state):
            for i in range(N):
                
                if (self.visual_aid_button.is_pressed):
                    visual_aid = True
                    break
                if (self.state_button.is_pressed):
                    state = True
                    break

                # Update distance data
                for j in range(N-1):
                    distances[i][j] = distances[i][j+1]

                distances[i][N-1] = sensor_list[i].distance * 100  # Convert to cm
                #print(f"Sensor {i}: {distances[i][N]:.2f} cm")

                sorted_distances = sorted(distances[i]) # Sort the distance data to retrieve median
                distance = sorted_distances[2]

                # delta = abs(distance - curr_dist[i])
                
                if 0 <= distance <= MAX_DISTANCE:
                    speed = int(0.25 * (255 - (0.65 * distance / MAX_DISTANCE * 255)))
                    pi.set_PWM_dutycycle(motor_pins[i], speed)
                    # vibrate_array[i] = True
                    # vib_counter[i] = 0
                else:
                    pi.set_PWM_dutycycle(motor_pins[i], 0)
                
                curr_dist[i] = distance
                time.sleep(0.01)
        
        for pin in motor_pins:
            pi.set_PWM_dutycycle(pin, 0)  

        if (state):
            self.set_state(ControlState.Idle)
            print("set to idle")
            self.cooldown = True
        elif (visual_aid):
            self.set_state(ControlState.VisualAid)
            self.prev_state = ControlState.ObjectDetection
            print("set to visual aid")
        time.sleep(0.1)


    def run(self):
        while True:
            self.process()
            if self.listen_visual_aid_button():
                self.visual_aid()
                continue
            if self.listen_state_button():
                self.toggle_state()
            time.sleep(0.005)

