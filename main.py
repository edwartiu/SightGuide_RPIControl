from ControlLogic import ControlLogic
from server import app
from time import sleep

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"
#PROJECT_PATH = "/home/lndnf/Documents/SightGuide_RPIControl"

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    try:
        control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
        while True:
            control_logic.process()
            sleep(0.1)
    except KeyboardInterrupt as e:
        print(f"Error: {e}")
        pass
    finally:
        exit()
