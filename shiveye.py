from ctypes import sizeof
from itertools import filterfalse
from unittest.util import _MAX_LENGTH
import pyautogui
import time
import os
import threading
import numpy
import opennsfw2
from PIL import Image
from keras import Model
import tkinter as tk
import ctypes

#for now, the logic is to take screenshots and analyse them every 4-5 seconds for NSFW content

# and i didn't find a way to install it in such a way that it can't be deleted/uninstalled so the solution I found was to hide this file somewhere
# so that no one can find it and delete it

# for doing this it searches for a directory having the longest path lenght among 1000 directories and then moves itself in that directory.


if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

PREDICTOR = None
THREAD_LOCK = threading.Lock()
MAX_PROBABILITY = 0.35

class installation():

    def longest_path(directory, num_directories):
        max_path = ""
        max_length = 0

        analyzed_directories = 0

        for root, _, files in os.walk(directory):
            if analyzed_directories >= num_directories:
                break
        
            for file in files:
                analyzed_directories += 1
                file_path = os.path.join(root, file)
                print("Analyzing path:", file_path) 
                if len(file_path) > max_length:
                    max_length = len(file_path)
                    max_path = file_path

        return max_path

    user_directory = os.path.expanduser("~")
    num_directories_to_analyze = 1000

    longest_path_in_user_dir = longest_path(user_directory, num_directories_to_analyze)

    if longest_path_in_user_dir:
        print("Longest path after analyzing 1000 directories:", longest_path_in_user_dir)
    else:
        print("No files found in the user directory.")



class NSFW():

    def get_predictor() -> Model:
        global PREDICTOR

        with THREAD_LOCK:
            if PREDICTOR is None:
                PREDICTOR = opennsfw2.make_open_nsfw_model()
        return PREDICTOR

    def clear_predictor() -> None:
        global PREDICTOR

        PREDICTOR = None

    def predict_frame(target_frame: numpy.ndarray) -> bool:
        image = Image.fromarray(target_frame)
        image = opennsfw2.preprocess_image(image, opennsfw2.Preprocessing.YAHOO)
        views = numpy.expand_dims(image, axis=0)
        _, probability = NSFW.get_predictor().predict(views)[0]
        return probability > MAX_PROBABILITY

    def capture_and_predict_screenshot():
        screenshot_path = "screenshots/img.png"
        while True:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            is_nsfw = NSFW.predict_frame(numpy.array(screenshot))

            print("NSFW" if is_nsfw else "Safe")
            if is_nsfw:
                NSFW.protect()
            else:
                pass
            time.sleep(5)

    def disable_close():
        pass

# while trying to close the current window the program is terminating itself T_T 

    def close_current_window():
        try:
            user32 = ctypes.windll.user32
            user32.PostMessageW(user32.GetForegroundWindow(), 0x10, 0, 0)  
            return True
        except Exception as e:
            print(e)
            return False

    def protect():
        NSFW.close_current_window()
        root = tk.Tk()
        if NSFW.close_current_window() == True:
            button = tk.Button(root, text="close", command=root.destroy())
            button.pack()
        else:
            pass
        root.title("porn blocker")
        root.wm_attributes("-topmost", 1)
        root.protocol("WM_DELETE_WINDOW", NSFW.disable_close)
        root.overrideredirect(True)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        label = tk.Label(root, text="this is last warning")
        label.pack(fill="both", expand=True)
        root.mainloop()

screenshot_thread = threading.Thread(target=NSFW.capture_and_predict_screenshot)
screenshot_thread.start()



