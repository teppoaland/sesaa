import time
import os
import sys
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from datetime import datetime

print("\nTest_features_automation.py - Automation test starting!\n App should open now Notifications view run this test.")
time.sleep(2)

# Default test result is false if tests not passed
test_passed = False

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Read optional start parameter
start_param = sys.argv[1] if len(sys.argv) > 1 else None

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "Android_test_device"  
options.app_package = "fi.sbweather.app"
options.app_activity = "fi.sbweather.app.MainActivity"
options.automation_name = "UiAutomator2"
# Prevent app reset as this test is ran after automation test
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

def save_screenshot(driver, filename_prefix, timestamp, failed=False):
    dirname = "screenshots_failed" if failed else "screenshots"
    os.makedirs(dirname, exist_ok=True)
    filename = f"{filename_prefix}_{timestamp}.png"
    filepath = os.path.join(dirname, filename)
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")
    return filepath

try:
    # App should be on Main view to start and ready to run some tests
    time.sleep(4)  

    #print("Current package:", driver.current_package)
    #print("Current activity:", driver.current_activity)

    # Press Allow button
    print("Press Allow button...")    
    driver.find_element("accessibility id", "Allow").click()
    time.sleep(3)

    # Press Allow notifications button
    print("Press Allow notifications button...")    
    driver.find_element(By.ID, "com.android.permissioncontroller:id/permission_allow_button").click()
    time.sleep(3)

    # Press Get started 1 (Device Protection) button
    save_screenshot(driver, "Get_started", timestamp)
    print("Press Get started 1, Device Protection, button...")    
    #driver.find_element("accessibility id", "Get started").click()
    driver.find_element(By.XPATH, "//android.widget.Button[@content-desc='Get started']").click()
    time.sleep(3)
    
    # Press Get started 2 button
    save_screenshot(driver, "Get_started", timestamp)
    print("Press Get started 2 button...")    
    driver.find_element("accessibility id", "Get started").click()
    #driver.find_element(By.XPATH, "//android.widget.Button[@content-desc='Get started']").click()
    time.sleep(3)
    
    # Press Continue button
    save_screenshot(driver, "Continue_", timestamp)
    print("Press File access Continue button...")    
    driver.find_element("accessibility id", "Continue").click()
    time.sleep(3)

    # Set Allow files access for app switch
    save_screenshot(driver, "File_access_", timestamp)
    print("Checking for File Access switch...")

    try:
        # 5s wait
        switch_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("android:id/switch_widget")')
            )
        )
        print("File Access switch found, toggling...")
        switch_element.click()
        time.sleep(2)
    except TimeoutException:
        print("File Access switch not found, skipping...")
    time.sleep(2)
    
# Find Back / Navigate back to scan view - Commented out as OS will set focus back to previous view when toggle moved!
#    print("Checking for Back button...")
# 
#   back_element = None
#     back_ids = [
#         "com.android.permissioncontroller:id/navigation_bar_item_icon_view",
#         "android:id/home",
#         "com.android.permissioncontroller:id/toolbar"
#     ]
# 
#     for bid in back_ids:
#         try:
#             back_element = driver.find_element(By.ID, bid)
#             print(f"Back button found ({bid}), clicking...")
#             back_element.click()
#             time.sleep(2)
#             break
#         except NoSuchElementException:
#             print("except NoSuchElementException - << Back button not found?")
#             continue
# 
#     if back_element is None:
#         print("Back button not found, need to use hardware back...")
#         driver.back()

    print("Stop the scan. This can take some time thus 15s wait here...")    
    driver.find_element("accessibility id", "Stop scan").click()
    time.sleep(15)
    
    #IF tests are passed so far with no issues then setting test_passed=true and take a screenshot.
    test_passed = True
    save_screenshot(driver, "Scan_cancelled_all_ok", timestamp)

    # Final view verification: check if some expected txt is visible on the screen. The problem is that UI elements vary randomly in Total App
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//*[contains(@text, 'Security reports')]"
            ))
        )
        print("Security reports -text found – activation flow confirmed.")
        test_passed = True
        save_screenshot(driver, "Setup_Protection_view_ok_", timestamp)
    except TimeoutException:
        print("Security reports text NOT found – activation may have failed.")
        test_passed = False
        save_screenshot(driver, "Setup_Protection_view_fail_", timestamp, failed=True)

except Exception as e:
    print(f"Note some test or tests failed: {e}")
    test_passed = False
    # Save screenshot on any exception
    save_screenshot(driver, "Exception_", timestamp, failed=True)

finally:
    # Quit the driver
    driver.quit()

# Exit code for Jenkins (0 = success, 1 = failure)
sys.exit(0 if test_passed else 1)