import time
import os
import sys
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from appium.webdriver.common.appiumby import AppiumBy

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Read optional start parameter - Optional, not used in this test
start_param = sys.argv[1] if len(sys.argv) > 1 else None

# Global setting: Save only failed screenshots (True) or all screenshots (False)
if start_param == "all":
    SAVE_ONLY_FAILED_SCREENSHOTS = False
else:
    SAVE_ONLY_FAILED_SCREENSHOTS = True  

# Default test result is false if tests not passed
test_passed = True  # Initialize as True, set to False if any test fails

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "Android_test_device"  
options.app_package = "fi.sbweather.app"
options.app_activity = "fi.sbweather.app.MainActivity"
options.automation_name = "UiAutomator2"
# Prevent app reset as this test is ran after installation test - optional in this case
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

def save_screenshot(driver, filename_prefix, timestamp, failed=False):
    """Save screenshot based on settings."""
    if failed or not SAVE_ONLY_FAILED_SCREENSHOTS:
        dirname = "screenshots_failed" if failed else "screenshots"
        os.makedirs(dirname, exist_ok=True)
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = os.path.join(dirname, filename)
        driver.save_screenshot(filepath)
        print(f"Screenshot saved: {filepath}")
        return filepath
    return None

def check_element(driver, by, value, timeout=10):
    """Check if element exists and return True/False."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return True
    except TimeoutException:
        return False

def test_element(driver, by, value, element_name, screenshot_prefix, timeout=10):
    """Test element existence, save screenshot and update test_passed variable."""
    global test_passed
    if check_element(driver, by, value, timeout):
        print(f"{element_name} found.")
        save_screenshot(driver, f"{screenshot_prefix}_ok", timestamp, failed=False)
        return True
    else:
        print(f"{element_name} not found.")
        save_screenshot(driver, f"{screenshot_prefix}_fail", timestamp, failed=True)
        test_passed = False
        return False

def tap_and_test_location(driver, accessibility_id, location_name, screenshot_prefix):
    """Tap location and test if temperature is visible. Save screenshot for success/failure."""
    global test_passed
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        element.click()
        print(f"{location_name} - element found and clicked successfully.")
        
        # Wait for weather data to load
        time.sleep(10)
        
        # Check if "LÄMPÖTILA" is visible (NOTE: This is the actual element ID in the app)
        if check_element(driver, AppiumBy.ACCESSIBILITY_ID, "LÄMPÖTILA", 10):
            print("Temperature element found. Weather data loaded successfully.")
            save_screenshot(driver, f"{screenshot_prefix}_ok", timestamp, failed=False)
            return True
        else:
            print("Temperature element not found. Weather data loading failed.")
            save_screenshot(driver, f"{screenshot_prefix}_fail", timestamp, failed=True)
            test_passed = False
            return False
            
    except TimeoutException:
        print(f"{location_name} - element not found within timeout period.")
        save_screenshot(driver, f"{location_name}_not_found", timestamp, failed=True)
        test_passed = False
        return False

print("\nTest_features_automation.py - Automation test starting...")
time.sleep(2)

try:
    # Close app first to ensure initial view
    driver.terminate_app("fi.sbweather.app")
    print("App closed. Reopening...")
    time.sleep(2)
    
    # Reopen the app
    driver.activate_app("fi.sbweather.app")
    print("Opening app Main view...")   
    time.sleep(5)
    
    # Main view verification: check if HOME tab button is visible using accessibility id (JIRA-123)
    test_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 
                "HOME button", "HOME_button_main")
    
    # Tap and input Oulu text to field
    driver.tap([(400, 780)])  
    time.sleep(3) 
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', 'Oulu'],
        'includeStderr': True,
        'timeout': 5000
    })
    save_screenshot(driver, "Oulu_weather_stations_list", timestamp, failed=False)
    
    # Test Oulu Vihreäsaari
    tap_and_test_location(driver, "Oulu Vihreäsaari", "Oulu Vihreäsaari", "Weather_oulu_vihreasaari")
    
    # Test Oulu lentoasema
    tap_and_test_location(driver, "Oulu lentoasema", "Oulu lentoasema", "Weather_oulu_airport")
    
    # Return to Main view
    driver.back()
    time.sleep(3)
    driver.back()
    print("Used Android back button x2 to return to the Main view.")

    # Check each view "Lämpimimmät", "Kylmimmät", "Sateisimmat", "Tuulisimmat"
    view_coords = [
        (300, 1150),
        (790, 1150),
        (300, 1480),
        (790, 1480)
    ]
    view_accessibility_ids = [
        "Lämpimimmät",
        "Kylmimmät",
        "Sateisimmat",
        "Tuulisimmat"
    ]
    view_names = [
        "Max_Temp",
        "Low_Temp",
        "Most_Rain",
        "Most_Windy"
    ]

    for idx, coords in enumerate(view_coords):
        print(f"Opening {view_names[idx]} View...")
        driver.tap([coords])
        time.sleep(6)
        
        # Check if the view actually opened
        test_element(driver, AppiumBy.ACCESSIBILITY_ID, view_accessibility_ids[idx],
                    f"{view_accessibility_ids[idx]} element", view_names[idx])
        
        # Return to Main view    
        driver.back()
        print(f"Returned to Main view from {view_names[idx]}.")
        time.sleep(3)

    # Open RECORDS tab and check for widget view
    try:
        # Click RECORDS tab
        records_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "ENNÄTYKSET\nTab 2 of 3"))
        )
        records_tab.click()
        print("RECORDS tab opened.")
        time.sleep(3)
        
        # Check if widget view (ImageView) is visible
        test_element(driver, AppiumBy.CLASS_NAME, "android.widget.ImageView",
                    "Widget image (ImageView)", "Records_widget")
        
        time.sleep(3)     
    except TimeoutException:
        print("RECORDS tab not found.")
        save_screenshot(driver, "Records_tab_not_found", timestamp, failed=True)
        test_passed = False

    # Final view verification: check if HOME tab button is still visible
    test_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3",
                "HOME button", "HOME_button_final")
    
    # Closing the app - optional
    print("Test completed. Closing the app...")
    time.sleep(3)
    driver.terminate_app("fi.sbweather.app")

except Exception as e:
    print(f"Note: Some test or tests failed: {e}")
    test_passed = False
    save_screenshot(driver, "Exception_", timestamp, failed=True)

finally:
    # Quit the driver
    driver.quit()

# Print test results 
if test_passed:
    print("All tests passed successfully!")
else:
    print("Some test failed. Check screenshots_failed directory.")

# Exit code for test automation results (0 = success, 1 = failure)
sys.exit(0 if test_passed else 1)