from ControlLogic import ControlLogic

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"

if __name__ == "__main__":
    control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
    while True:
        pass