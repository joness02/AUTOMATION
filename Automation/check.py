import pyautogui as pg
import time
import keyboard

# ---- basic settings ----
TIMEOUT = 30
CONFIDENCE = 0.90
exit_flag = False

def check_emergency_exit():
    global exit_flag
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift'):
        exit_flag = True
        return True
    return False

def wait_center_timeout(img, timeout=TIMEOUT, confidence=CONFIDENCE, grayscale=True):
    """Wait for image to appear with timeout"""
    print(f"Waiting for: {img} (timeout: {timeout}s)")
    attempts = 0
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_emergency_exit():
            raise KeyboardInterrupt("Emergency exit triggered")
        
        try:
            pt = pg.locateCenterOnScreen(img, confidence=confidence, grayscale=grayscale)
            if pt:
                print(f"Found: {img}")
                return pt
        except Exception as e:
            print(f"Error searching for {img}: {e}")
            
        attempts += 1
        if attempts % 2 == 0:
            print(f"Still waiting for: {img} (attempt {attempts})")
        
        time.sleep(10)
    
    raise TimeoutError(f"Image not found within {timeout} seconds: {img}")

# Show dialog box at start
pg.alert('Click OK to start finding image center', 'Image Center Finder')

# First action with offset -50, 26
pt1 = wait_center_timeout('x_image.png')
pg.moveTo(pt1.x + 50, pt1.y - 26, duration=0.12)
pg.click()

# Second action with different offset (example: 30, -10)
pt2 = wait_center_timeout('yes_image.png')
pg.moveTo(pt2.x - 31, pt2.y + 19, duration=0.12)
pg.click()