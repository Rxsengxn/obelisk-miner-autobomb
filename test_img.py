import pyautogui


# capture a small region (x, y, width, height)
img = pyautogui.screenshot(region=(1780, 455, 10, 200))

# Show the image
img.show()