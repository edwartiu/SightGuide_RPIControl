from ControlLogic import ControlLogic
from server import app
from time import sleep

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"


if __name__ == "__main__":
    control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
    #app.run(host='0.0.0.0', port=5000)

    while True:
        control_logic.process()
        sleep(0.1)
