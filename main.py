from ControlLogic import ControlLogic
import pigpio

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"

# Constants
MAX_DISTANCE = 220  
OUTLIER_THRESH = 100
VIBRATE_COOLDOWN = 4

# GPIO Pin Definitions
TRIG1, ECHO1 = 6, 26
TRIG2, ECHO2 = 4, 17  
TRIG3, ECHO3 = 27, 22
TRIG4, ECHO4 = 10, 9
TRIG5, ECHO5 = 0, 5 #CHANGE
MOTORL, MOTORLM, MOTORM, MOTORRM, MOTORR = 14, 15, 23, 24, 25  # PWM motor control pins

if __name__ == "__main__":
    control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
    while True:
        pass