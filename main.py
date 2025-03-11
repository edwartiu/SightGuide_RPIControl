from ControlLogic import ControlLogic
from server import app
from time import sleep
import threading

STATE_BUTTON = 2
VISUAL_AID_BUTTON = 3
PROJECT_PATH = "/home/edwartiu/SightGuide"
#PROJECT_PATH = "/home/lndnf/Documents/SightGuide_RPIControl"

lock = threading.Lock()

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    try:
        control_logic = ControlLogic(PROJECT_PATH, STATE_BUTTON, VISUAL_AID_BUTTON)
        control_logic.run()
    except Exception as e:
        print(f"Error: {e}")
        pass
    finally:
        exit()
