#!C:\Users\kertk\Downloads\autobomb\Scripts\python.exe python3
# This code is a simple script that detects changes in a specific region of the screen and performs mouse clicks when a change is detected. It uses the pyautogui library to take screenshots and perform mouse actions, and the PIL library to compare images.

import pyautogui
import time
from PIL import ImageChops
import keyboard
import cv2
import numpy as np
from enum import Enum

DRONE_CLEANUP_DELAY = 1  # seconds to wait for drones to clean up
DRONE_SWITCH_BUTTON = (2186, 939)  # Coordinates for the drone pause switch


# (x, y, width, height)
# REGION = (1829, 860, 100, 150)  # Bombbag
# REGION = (1780, 455, 10, 200) # Vasak serv
# REGION = (1780, 255, 10, 400) # Vasak serv
REGION = (2004, 477, 190, 150) # keskelt sektsioon


CHECK_INTERVAL = 0.2  # seconds
TIMEOUT = 2.5 + DRONE_CLEANUP_DELAY  # seconds without change

DEBUG = False
OVERRIDE = False
EASMODE = True

class DebugState(Enum):
    OFF = 0
    MINIMAL = 1
    VERBOSE = 2

DEBUG_STATE = DebugState.OFF


# State in enum for better readability
class ScriptState(Enum):
    DEFAULT = 0b0001
    EASMODE = 0b0010
    OVERRIDE = 0b0100
    PAUSED = 0b1000
    QUIT = 0b0000

# Define a global state variable to track the current state of the script (e.g., "DEFAULT", "PAUSED", "OVERRIDE", etc.)
STATE = ScriptState.DEFAULT

# Define a function to update the state and print it in the console with colors
def update_state(new_state, DEBUG=False):
    global STATE
    STATE = new_state
    if DEBUG:
        print(f"{MAGENTA}State updated to: {CYAN}{STATE}")


# Colors for console output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[00m"

# Define print to always end in a reset color code to prevent color bleed in the console
def print(*args, **kwargs):
    end = kwargs.get('end', '\n')
    kwargs['end'] = f"{RESET}{end}"
    __builtins__.print(*args, **kwargs)

# Define a macro to print full messages in colors
def print_color(message, color):
    colors = {
        "red": RED,
        "green": GREEN,
        "yellow": YELLOW,
        "blue": BLUE,
        "magenta": MAGENTA,
        "cyan": CYAN,
        "white": WHITE,
        "reset": RESET
    }
    print(f"{colors.get(color, colors['reset'])}{message}")

# Macro for printing boolean values in green for True and red for False
def print_bool(value, after=RESET):
    return f"{GREEN}True{after}" if value else f"{RED}False{after}"

def images_are_same(img1, img2):
    return ImageChops.difference(img1, img2).getbbox() is not None

def images_are_same_cv2(img1, img2, threshold=2):
    # Convert PIL images to OpenCV format
    img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
    img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)

    # print(f"img1_cv shape: {img1_cv.shape}")

    if DEBUG:
        # Add padding to the images to left and right
        img1_cv_padded = np.pad(img1_cv, ((0, 0), (200, 200), (0, 0)), 'constant', constant_values=(0))
        img2_cv_padded = np.pad(img2_cv, ((0, 0), (200, 200), (0, 0)), 'constant', constant_values=(0))

        cv2.imshow("Image 1", img1_cv_padded)  # Show the first image for debugging
        cv2.imshow("Image 2", img2_cv_padded)  # Show the second image for debugging


    # Compute the absolute difference between the two images
    diff = cv2.absdiff(img1_cv, img2_cv)
    diff_padded = np.pad(diff, ((0, 0), (200, 200), (0, 0)), 'constant', constant_values=(0))

    if DEBUG:
        cv2.imshow("Difference", diff_padded)  # Show the difference image for debugging

    # Get percentage of different pixels
    non_zero_count = np.count_nonzero(diff)
    total_pixels = diff.size
    percent_diff = (non_zero_count / total_pixels) * 100

    # Check if there are any non-zero pixels in the difference image
    return percent_diff < threshold, percent_diff



def click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.mouseDown()
    pyautogui.mouseUp()


def main():
    global DEBUG, OVERRIDE, EASMODE, DRONE_CLEANUP_DELAY, TIMEOUT, DRONE_SWITCH_BUTTON, CHECK_INTERVAL

    # Take initial screenshot
    previous_img = pyautogui.screenshot(region=REGION)
    last_fire_time = time.time()
    last_check_time = time.time()
    i = 0
    is_same_counter = 0



    try:
        while True:        
            if time.time() - last_check_time >= CHECK_INTERVAL:

                current_img = pyautogui.screenshot(region=REGION)
                # i += 1

                # if i >= 20:
                #     OVERRIDE = True  # Set override if no change detected for 20 checks (10 seconds)

                #print(f"{images_are_same_cv2(previous_img, current_img)=}")

                is_same, diff_percent = images_are_same_cv2(previous_img, current_img)
                if DEBUG: 
                    print(f"{is_same=}, {diff_percent=:.2f}%")

                if is_same:
                    is_same_counter += 1
                    if DEBUG:
                        print(f"{YELLOW}Same image detected ({is_same_counter} checks).")
                else:
                    if is_same_counter > 0:
                        if DEBUG:
                            print(f"{CYAN}Change detected! reset same image counter.")
                    is_same_counter = 0

                # if not images_are_same(previous_img, current_img):
                # if not is_same or OVERRIDE:
                if is_same_counter >= 4 or OVERRIDE: # If images are the same for 7 checks (3.5 seconds) or override is active, consider it a change to prevent getting stuck on minor changes
                    # Change detected
                    if time.time() - last_fire_time >= TIMEOUT:
                        i += 1
                        time_now = time.localtime()
                        print_color(f"Clicking! {i}, time: {time.strftime('%H:%M:%S', time_now)}", "cyan")

                        click(2345, 1076) # Transmuter Bomb
                        # pyautogui.moveTo(2345, 1076) # Transmuter Bomb
                        # pyautogui.mouseDown()
                        # pyautogui.mouseUp()

                        click(2324, 1226) # Fire
                        # pyautogui.moveTo(2324, 1226) # Fire
                        # pyautogui.mouseDown()
                        # pyautogui.mouseUp()

                        click(2044, 1077) # Bomb of Plenty
                        # pyautogui.moveTo(2044, 1077) # Bomb of Plenty
                        # pyautogui.mouseDown()
                        # pyautogui.mouseUp()

                        click(2324, 1226) # Fire
                        # pyautogui.moveTo(2324, 1226) # Fire
                        # pyautogui.mouseDown()
                        # pyautogui.mouseUp()


                        if not EASMODE:

                            # Make drones clean up
                            click(*DRONE_SWITCH_BUTTON) # Drones pause switch (twice)
                            click(*DRONE_SWITCH_BUTTON)
                            # pyautogui.moveTo(DRONE_SWITCH_BUTTON) # Drones pause switch
                            # pyautogui.mouseDown()
                            # pyautogui.mouseUp()
                            # pyautogui.mouseDown()
                            # pyautogui.mouseUp()

                            time.sleep(DRONE_CLEANUP_DELAY)  # Short delay to ensure actions are registered

                            # Non-blocking wait for drones to clean up
                            start_wait_time = time.time()
                            while time.time() - start_wait_time < DRONE_CLEANUP_DELAY:
                                # Here you could add additional checks to see if drones have finished cleaning up
                                            # Check for q keypress to exit
                                if keyboard.is_pressed('q'):
                                    print("\033[91mExiting... (while waiting for drones to clean up)")
                                    raise KeyboardInterrupt
                                #time.sleep(0.1)  # Sleep briefly to avoid busy-waiting

                            # Turn drones back on
                            click(*DRONE_SWITCH_BUTTON) # Drones pause switch (twice)
                            click(*DRONE_SWITCH_BUTTON)
                            # pyautogui.moveTo(DRONE_SWITCH_BUTTON) # Drones pause switch
                            # pyautogui.mouseDown()
                            # pyautogui.mouseUp()
                            # pyautogui.mouseDown()
                            # pyautogui.mouseUp()

                        if OVERRIDE:
                            OVERRIDE = False  # Reset override after firing


                        last_fire_time = time.time()  # reset firing timer
                        #i = 0  # reset change counter after firing
                        # previous_img = current_img  # Update previous image after firing
                        is_same_counter = 0  # reset same image counter after firing
                else:
                    # Change detected
                    # print("Change detected")
                    pass

                previous_img = current_img
                last_check_time = time.time()  # reset check timer

            # Check for q keypress to exit
            if keyboard.is_pressed('q'):
                print(f"\033[91mQuitting...{RESET} ", end="")
                raise KeyboardInterrupt  # Use KeyboardInterrupt to trigger cleanup and exit

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(f"\033[91mQuitting...{RESET} ", end="")
                raise KeyboardInterrupt  # Use KeyboardInterrupt to trigger cleanup and exit

            if keyboard.is_pressed('p') and time.time() - last_fire_time > TIMEOUT:
                print(f"{MAGENTA}Pausing...")
                time.sleep(0.5)  # Sleep briefly to avoid busy-waiting
                # while True:
                    # if keyboard.is_pressed('p'):
                keyboard.wait('p')  # Wait for 'p' key press to resume
                print(f"{GREEN}Resuming...")
                last_fire_time = time.time()  # reset firing timer to prevent immediate firing after pause

            if keyboard.is_pressed('d') and time.time() - last_fire_time > TIMEOUT:
                # Yellow text in console is a debug message, white text is a regular message
                # print(f"Switch Debugging to {not DEBUG}...")
                print(f"{YELLOW}Debugging is now {print_bool(not DEBUG, YELLOW)}...")
                time.sleep(0.5)  # Sleep briefly to avoid busy-waiting
                # while True:
                    # if keyboard.is_pressed('d'):
                DEBUG = not DEBUG
                print(f"{YELLOW}Debugging is now {print_bool(DEBUG, YELLOW)}...")
                cv2.destroyAllWindows()  # Close any open debug windows
                last_fire_time = time.time()  # reset firing timer to prevent immediate firing after debug

            if (keyboard.is_pressed('f') and time.time() - last_fire_time > TIMEOUT) and not OVERRIDE:
                print(f"{MAGENTA}Override! Firing...{RESET} ", end="")
                OVERRIDE = True
                # time.sleep(0.5)  # Sleep briefly to avoid busy-waiting
                last_fire_time = time.time() - TIMEOUT  # Set last fire time to allow immediate firing in the next loop iteration

            if keyboard.is_pressed('e') and time.time() - last_fire_time > TIMEOUT:
                print(f"{MAGENTA}Easymode switch to {print_bool(not EASMODE, MAGENTA)}")
                EASMODE = not EASMODE
                time.sleep(0.5)  # Sleep briefly to avoid busy-waiting
                last_fire_time = time.time()  # reset firing timer to prevent immediate firing after easymode switch                
            
            if keyboard.is_pressed('i') and time.time() - last_fire_time > TIMEOUT:
                print(f"{MAGENTA}Current states: DEBUG={DEBUG}, OVERRIDE={OVERRIDE}, EASMODE={EASMODE}")
                print(f"{YELLOW}Easymode: When enabled, the script will skip the drone cleanup process, allowing for faster firing but potentially leaving drones in the way.")
                print(f"{YELLOW}Override: When enabled, the script will fire on the next detected change regardless of the timeout, then reset the override.")
                print(f"{YELLOW}Debug mode: When enabled, the script will display the current and previous images being compared, as well as the difference image and percentage of difference.")
                time.sleep(0.5)  # Sleep briefly to avoid busy-waiting
                last_fire_time = time.time()  # reset firing timer to prevent immediate firing after info switch              


    except KeyboardInterrupt:
        print(f"{RED}Exiting...")
        pyautogui.mouseUp()  # Ensure mouse is released on exit
        cv2.destroyAllWindows()
        # print("Exiting...")
        exit()


if __name__ == "__main__":
    print(f"{GREEN}Starting...")
    print(f"{YELLOW}Press '{CYAN}q{YELLOW}' to exit, '{CYAN}p{YELLOW}' to pause/resume, '{CYAN}d{YELLOW}' to toggle debug mode, '{CYAN}f{YELLOW}' to force fire, '{CYAN}e{YELLOW}' to toggle easymode, '{CYAN}i{YELLOW}' to display info.")

    #print("{YELLOW}Note: The script will automatically enable override if no change is detected for 20 checks (10 seconds) to prevent getting stuck.")
    print(f"{YELLOW}Starting states: {CYAN}DEBUG{YELLOW}={RED}False{YELLOW}, {CYAN}OVERRIDE{YELLOW}={RED}False{YELLOW}, {CYAN}EASMODE{YELLOW}={GREEN}True")
    main()