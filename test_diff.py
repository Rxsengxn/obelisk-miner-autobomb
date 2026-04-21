import cv2
import numpy as np
import pyautogui
import time

# REGION = (1780, 255, 10, 400) # Vasak serv
REGION = (2004, 477, 190, 150)
CHECK_INTERVAL = 0.5  # seconds
DEBUG = True

def images_are_same_cv2(img1, img2, threshold=80):
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

if __name__ == "__main__":

    previous_img = pyautogui.screenshot(region=REGION)
    last_check_time = time.time()  # Initialize check timer

    while True:

        if time.time() - last_check_time >= CHECK_INTERVAL:

            now_img = pyautogui.screenshot(region=REGION)
            is_same, diff_percent = images_are_same_cv2(previous_img, now_img)
            if not is_same:
                print(f"Images are different {f'(Difference: {diff_percent:.2f}%)' if DEBUG else ''}")
            else:
                if DEBUG:
                    print(f"Images are the same  {f'(Difference: {diff_percent:.2f}%)' if DEBUG else ''}")
                pass
            previous_img = now_img
            last_check_time = time.time()  # reset check timer

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            cv2.destroyAllWindows()
            exit()