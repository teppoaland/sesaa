import time
import os
import sys
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

print("\nTotal_Activation_automation.py - Automation test starting...\n")

# Default test result is false if tests not passed
test_passed = False

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Read optional start parameter
start_param = sys.argv[1] if len(sys.argv) > 1 else None

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "RF8N32S7ZWB"  # Varmista, että tämä vastaa yhteydessä olevaa laitetta
options.app_package = "com.fsecure.ms.safe"
options.app_activity = "com.fsecure.ui.main.MainNavigationActivity"
options.automation_name = "UiAutomator2"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

# Clear app settings if script started with parameter "clean"
if start_param == "clean":
    driver.execute_script('mobile: shell', {
        'command': 'pm',
        'args': ['clear', 'com.fsecure.ms.safe'],
        'includeStderr': True,
        'timeout': 5000
    })
    print("App settings cleared!")
    driver.activate_app("com.fsecure.ms.safe")
    time.sleep(4)

def save_screenshot(driver, filename_prefix, timestamp, failed=False):
    dirname = "screenshots_failed" if failed else "screenshots"
    os.makedirs(dirname, exist_ok=True)
    filename = f"{filename_prefix}_{timestamp}.png"
    filepath = os.path.join(dirname, filename)
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")
    return filepath

try:
    time.sleep(10)  # Wait for app to start

    #print("Current package:", driver.current_package)
    #print("Current activity:", driver.current_activity)

    # Accept EULA if visible
    try:
        toggle = driver.find_element("xpath", '//o.bua/android.view.View/android.view.View/android.view.View[3]/android.view.View[1]')
        toggle.click()
        accept_btn = driver.find_element("accessibility id", "Accept and continue")
        accept_btn.click()
        time.sleep(7)
    except NoSuchElementException:
        print("'Accept and continue' not found – EULA likely already accepted")

    # Open "Create account" view
    driver.find_element("accessibility id", "Create account").click()
    time.sleep(7)

    print("Filling the create account form:")

    # Prepare data ahead
    email = f"john.smith{timestamp}@mail.com"
    passwd = f"x.X{timestamp}"

    # Tap and input First name using adb shell input text
    driver.tap([(128, 736)])
    time.sleep(1)
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', 'John'],
        'includeStderr': True,
        'timeout': 5000
    })
    time.sleep(1)

    # Tap and input Last name 
    driver.tap([(128, 835)])
    time.sleep(1)
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', 'Smith'],
        'includeStderr': True,
        'timeout': 5000
    })
    time.sleep(1)

    # Tap and input Email 
    driver.tap([(128, 935)])
    time.sleep(1)
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', email],
        'includeStderr': True,
        'timeout': 5000
    })
    time.sleep(1)

    # Tap and input Password 
    driver.tap([(128, 1035)])
    time.sleep(1)
    print("Created password:", passwd)
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', passwd],
        'includeStderr': True,
        'timeout': 5000
    })
    time.sleep(1)
    
    # Tap to show password 
    driver.tap([(111, 1150)])
    time.sleep(2)

    save_screenshot(driver, "create_account", timestamp)

    # Tap "Accept and create account" button
    time.sleep(1)
    driver.hide_keyboard()
    driver.tap([(504, 1450)])
    print("Tapped Create account -button. 10s wait as this may be bit slow depending on server side response and connection speed.")
    time.sleep(10)
    
    # Tap Continue button (after activation)
    driver.tap([(500, 900)])
    print("Tapped Continue -button. Long 12s wait as this is usually slow server connection.")
    time.sleep(12)
    save_screenshot(driver, "App activated", timestamp)

    # Final view verification: check if "Notifications" is visible on the screen
    # Korjattu: Käytetään XPath:ia ANDROID_UIAUTOMATORin sijaan
    try:
        # Etsitään elementtiä XPath:llä joka sisältää tekstin "Notifications"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//*[contains(@text, 'Notifications')]"
            ))
        )
        print("Notifications text found – activation flow confirmed.")
        test_passed = True
        save_screenshot(driver, "Notifications_view_ok_", timestamp)
    except TimeoutException:
        print("Notifications text NOT found – activation may have failed.")
        test_passed = False
        save_screenshot(driver, "Notifications_view_fail_", timestamp, failed=True)

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