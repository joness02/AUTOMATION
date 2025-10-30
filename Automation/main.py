import time
import pyautogui as pg
import keyboard

# ---- basic settings ----
pg.FAILSAFE = True
pg.PAUSE = 0.5
CONFIDENCE = 0.90
TIMEOUT = 30  # 30 second timeout for most operations

# Global flag for emergency exit
exit_flag = False
# Global variables to track progress
start_angle = 0
iterations_to_run = 180
completed_iterations = 0
last_angle_used = 0

def check_emergency_exit():
    """Check if Ctrl+Shift is pressed to exit the program"""
    global exit_flag
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift'):
        exit_flag = True
        return True
    return False

def show_exit_dialog(message):
    """Show dialog box when exiting"""
    pg.alert(message, 'Program Exit')

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
        if attempts % 2 == 0:  # Print every 20 seconds (2 * 10)
            print(f"Still waiting for: {img} (attempt {attempts})")
        
        time.sleep(10)  # Check every 10 seconds
    
    raise TimeoutError(f"Image not found within {timeout} seconds: {img}")

def wait_center_30min(img, confidence=CONFIDENCE, grayscale=True):
    """Wait for image to appear with 30 minute timeout"""
    timeout_30min = 1800  # 30 minutes in seconds
    print(f"Waiting for: {img} (timeout: 30 minutes)")
    attempts = 0
    start_time = time.time()
    
    while time.time() - start_time < timeout_30min:
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
        if attempts % 6 == 0:  # Print every minute (6 * 10 seconds)
            print(f"Still waiting for: {img} (attempt {attempts})")
        
        time.sleep(10)  # Check every 10 seconds
        
    raise TimeoutError(f"Image not found within 30 minutes: {img}")

def click_img_timeout(img, timeout=TIMEOUT, confidence=CONFIDENCE, grayscale=True):
    """Click image with timeout"""
    if check_emergency_exit():
        raise KeyboardInterrupt("Emergency exit triggered")
    pt = wait_center_timeout(img, timeout=timeout, confidence=confidence, grayscale=grayscale)
    pg.moveTo(pt.x, pt.y, duration=0.12)
    pg.click()
    return pt

def move_mouse_up(pixels=50, duration=0.12):
    """Get current mouse coordinates and move cursor up by given pixels"""
    x, y = pg.position()
    pg.moveTo(x, y - pixels, duration=duration)
    return (x, y - pixels)

def type_text(text):
    """Reliable text typing"""
    pg.hotkey('ctrl', 'a')
    pg.press('backspace')
    pg.write(str(text))

# ----------------- USER INPUT -----------------
def get_user_input():
    """Get start angle and number of iterations from user"""
    global start_angle, iterations_to_run
    
    # Get start angle
    while True:
        try:
            angle_input = pg.prompt(
                "Enter the starting gantry angle (even number between 0 and 358):", 
                "Start Angle", 
                default="0"
            )
            if angle_input is None:
                raise KeyboardInterrupt("User cancelled input")
            
            start_angle = int(angle_input)
            if start_angle < 0 or start_angle > 358 or start_angle % 2 != 0:
                pg.alert("Please enter an even number between 0 and 358", "Invalid Input")
                continue
            break
        except ValueError:
            pg.alert("Please enter a valid number", "Invalid Input")
        except KeyboardInterrupt:
            raise
    
    # Get number of iterations
    while True:
        try:
            iterations_input = pg.prompt(
                f"Enter the number of iterations to run (1-{180 - start_angle//2}):", 
                "Iterations", 
                default=str(180 - start_angle//2)
            )
            if iterations_input is None:
                raise KeyboardInterrupt("User cancelled input")
            
            iterations_to_run = int(iterations_input)
            max_iterations = 180 - start_angle//2
            if iterations_to_run < 1 or iterations_to_run > max_iterations:
                pg.alert(f"Please enter a number between 1 and {max_iterations}", "Invalid Input")
                continue
            break
        except ValueError:
            pg.alert("Please enter a valid number", "Invalid Input")
        except KeyboardInterrupt:
            raise

# ----------------- FLOW -----------------
pg.prompt("Make sure CERR is open and visible, then click OK.")

print("Press Ctrl+Shift together at any time to emergency exit the program.")

# Get user input for start angle and iterations
get_user_input()

start_index = start_angle // 2
end_index = start_index + iterations_to_run

try:
    # Do the initial setup once (before the loop)
    print("=== Running initial setup ===")
    
    # Import -> DICOM (30 second timeout)
    click_img_timeout('import_dropdown.png')
    move_mouse_up()
    click_img_timeout('dicom_option.png')

    # Review -> Study (30 second timeout)
    click_img_timeout('review_dropdown.png')
    move_mouse_up()
    click_img_timeout('study_option.png')

    print("Waiting for new window to appear...")
    # Wait for the next window to appear - 30 seconds
    wait_center_timeout('new_window_image.png')
    print("New window found!")

    # File -> Data path (30 second timeout)
    click_img_timeout('file_button.png')
    click_img_timeout('open_button.png')
    click_img_timeout('data.png')
    #hit enter
    pg.press('enter')
    
    # Now start the loop from imrt_image.png
    for i in range(start_index, end_index):
        if exit_flag:
            break
            
        gantry_angle = i * 2  # 0, 2, 4, 6... up to 358
        last_angle_used = gantry_angle
        completed_iterations = i - start_index + 1
        
        print(f"\n=== Starting iteration {completed_iterations}/{iterations_to_run} with angle {gantry_angle}° ===")
        
        # Wait for IMRT item to be visible, then click it (30 second timeout)
        click_img_timeout('imrt_image.png')

        # IMRTP creation (30 second timeout) - either/or
        try:
            click_img_timeout('imrtp_creation.png')
        except TimeoutError:
            click_img_timeout('imrtp_creation1.png')

        print("Waiting for second new window to appear...")
        # Wait for another window to appear - 30 seconds
        wait_center_timeout('new_window_image2.png')
        print("Second new window found!")

        # Equispace (30 second timeout)
        click_img_timeout('new_button_for_equispace.png')

        # Beam dialog box -> type gantry angle (30 second timeout)
        click_img_timeout('gantry_angle.png')
        type_text(gantry_angle)

        # structure dropdown button (30 second timeout)
        structure_center = wait_center_timeout('structure_dropdown.png')
        pg.moveTo(structure_center.x + 150, structure_center.y + 10, duration=0.12)
        pg.click()
        click_img_timeout('body_option.png')

        # structure dropdown button (30 second timeout)
        structure_center = wait_center_timeout('structure_dropdown.png')
        pg.moveTo(structure_center.x + 150, structure_center.y + 10, duration=0.12)
        pg.click()
        click_img_timeout('ptv_option.png')

        PTV_center = wait_center_timeout('PTV_image.png')
        pg.moveTo(PTV_center.x + 70, PTV_center.y, duration=0.12)
        pg.click()

        #sampr column (30 second timeout)
        sampr_center = wait_center_timeout('sampr_column.png')
        pg.moveTo(sampr_center.x, sampr_center.y + 15, duration=0.12)
        pg.click()
        type_text('1')

        pg.moveTo(sampr_center.x, sampr_center.y + 40, duration=0.12)
        pg.click()
        type_text('1')

        # Beamlet delta X / Y (30 second timeout)
        bldx_center = wait_center_timeout('beamletdelta_x.png')
        pg.moveTo(bldx_center.x + 100, bldx_center.y, duration=0.12)
        pg.click()
        type_text('0.3')

        pg.moveTo(bldx_center.x + 100, bldx_center.y + 20, duration=0.12)
        pg.click()
        type_text('0.3')

        # Go (30 second timeout)
        click_img_timeout('go_button.png')

        # Wait for completion - 30 minutes (look for BOTH finished.png AND 100%done.png)
        print("Waiting for BOTH completion images... (timeout: 30 minutes)")
        start_time = time.time()
        found_first = False
        found_second = False

        while time.time() - start_time < 1800:  # 30 minutes
            if check_emergency_exit():
                raise KeyboardInterrupt("Emergency exit triggered")
            
            if not found_first:
                try:
                    pt1 = pg.locateCenterOnScreen('finished.png', confidence=CONFIDENCE)
                    if pt1:
                        print("Found: finished.png")
                        found_first = True
                except:
                    pass
            
            if not found_second:
                try:
                    pt2 = pg.locateCenterOnScreen('100%done.png', confidence=CONFIDENCE)
                    if pt2:
                        print("Found: 100%done.png")
                        found_second = True
                except:
                    pass
            
            if found_first and found_second:
                print("Both completion images found!")
                break
                
            time.sleep(10)
        else:
            raise TimeoutError("Both finished.png and 100%done.png not found within 30 minutes")
        time.sleep(5)  # Short wait before proceeding
        # First action with offset -50, 26
        pt1 = wait_center_timeout('x_image.png')
        pg.moveTo(pt1.x + 50, pt1.y - 26, duration=0.12)
        pg.click()

        # Second action with different offset (example: 30, -10)
        pt2 = wait_center_timeout('yes_image.png')
        pg.moveTo(pt2.x - 31, pt2.y + 19, duration=0.12)
        pg.click()
        time.sleep(5)
        
        print(f"Completed iteration {completed_iterations}/{iterations_to_run} with angle {gantry_angle}°")

except KeyboardInterrupt:
    show_exit_dialog(f"Emergency exit triggered by user!\n\nCompleted: {completed_iterations}/{iterations_to_run} iterations\nLast angle used: {last_angle_used}°")
except TimeoutError as e:
    error_msg = f"Program stopped because it couldn't find an image:\n\n{str(e)}\n\nProgress: {completed_iterations}/{iterations_to_run} iterations\nLast angle used: {last_angle_used}°"
    print(error_msg)
    show_exit_dialog(error_msg)
except Exception as e:
    error_msg = f"Program stopped because of an unexpected error:\n\n{str(e)}\n\nProgress: {completed_iterations}/{iterations_to_run} iterations\nLast angle used: {last_angle_used}°"
    print(error_msg)
    show_exit_dialog(error_msg)

if exit_flag:
    show_exit_dialog(f"Program exited via emergency stop (Ctrl+Shift)\n\nProgress: {completed_iterations}/{iterations_to_run} iterations\nLast angle used: {last_angle_used}°")
else:
    show_exit_dialog(f"Completed all {iterations_to_run} iterations!\n\nLast angle used: {last_angle_used}°\nTotal iterations completed: {completed_iterations}")