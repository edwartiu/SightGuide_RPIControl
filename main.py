from ControlLogic import ControlLogic
from server import app

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
    while True:
        control_logic.process()