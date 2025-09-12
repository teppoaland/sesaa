import time
import os
import sys
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from datetime import datetime

print("\nTotal_Installation_From_GP_automation.py - Automation test starting!\n")

PACKAGE_NAME = "com.fsecure.ms.safe"
PLAY_STORE_PACKAGE = "com.android.vending"
PLAY_STORE_ACTIVITY = "com.google.android.finsky.activities.MainActivity"

# Function to check if package is installed on device
def is_package_installed(package_name):
    result = subprocess.run(
        ["adb", "shell", "pm", "list", "packages", package_name],
        capture_output=True,
        text=True
    )
    return package_name in result.stdout

# Function to save screenshots
def save_screenshot(driver, filename_prefix, timestamp, failed=False):
    dirname = "screenshots_failed" if failed else "screenshots"
    os.makedirs(dirname, exist_ok=True)
    filename = f"{filename_prefix}_{timestamp}.png"
    filepath = os.path.join(dirname, filename)
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")
    return filepath

# Create timestamp for screenshots
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Default test result
test_passed = False

try:
    if is_package_installed(PACKAGE_NAME):
        print(f"{PACKAGE_NAME} is already installed. No installation needed.")
        test_passed = True
    else:
        print(f"{PACKAGE_NAME} not installed. Launching Play Store for installation...")

        # Start separate driver for Play Store
        play_options = UiAutomator2Options()
        play_options.platform_name = "Android"
        play_options.device_name = "Android_test_device"
        play_options.app_package = PLAY_STORE_PACKAGE
        play_options.app_activity = PLAY_STORE_ACTIVITY
        play_options.automation_name = "UiAutomator2"
        play_options.no_reset = True

        play_driver = webdriver.Remote("http://127.0.0.1:4723", options=play_options)
        time.sleep(5)

        # Try to find and click the search box
        try:
            search_box = WebDriverWait(play_driver, 15).until(
                EC.presence_of_element_located((AppiumBy.ID, "com.android.vending:id/search_box_idle_text"))
            )
            search_box.click()
            time.sleep(2)
            
            # Enter search query
            search_input = WebDriverWait(play_driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, "com.android.vending:id/search_box_text_input"))
            )
            search_input.send_keys("F-Secure Total Security")
            time.sleep(1)

            # Press Enter
            play_driver.press_keycode(66)
            time.sleep(5)
        except TimeoutException:
            print("Search box not found, using direct Play Store intent...")
            play_driver.execute_script('mobile: shell', {
                'command': 'am',
                'args': ['start', '-a', 'android.intent.action.VIEW', '-d', f'market://details?id={PACKAGE_NAME}'],
                'includeStderr': True,
                'timeout': 5000
            })
            time.sleep(5)

        # Try to click Install button
        try:
            install_button = WebDriverWait(play_driver, 15).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//*[contains(@text, 'Install') or contains(@text, 'INSTALL')]")
                )
            )
            install_button.click()
            print("Install clicked. Waiting for installation to complete...")

            # Wait for installation to complete
            for i in range(30):  # up to ~90s
                if is_package_installed(PACKAGE_NAME):
                    print(f"{PACKAGE_NAME} successfully installed!")
                    test_passed = True
                    break
                time.sleep(3)
            else:
                print(f"Failed to install {PACKAGE_NAME}.")
                test_passed = False

        except TimeoutException:
            print("Install button not found. Installation may have failed.")
            if is_package_installed(PACKAGE_NAME):
                print(f"{PACKAGE_NAME} was installed successfully anyway!")
                test_passed = True
            else:
                print(f"{PACKAGE_NAME} installation failed.")
                test_passed = False

        play_driver.quit()

except Exception as e:
    print(f"Unexpected exception: {e}")
    test_passed = False
    if 'play_driver' in locals():
        save_screenshot(play_driver, "Unexpected_Error", timestamp, failed=True)

finally:
    print("Installation test finished. Exiting...")
    sys.exit(0 if test_passed else 1)
