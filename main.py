from ControlLogic import ControlLogic
from server import app

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
    while True:
        control_logic.process()