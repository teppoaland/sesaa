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

# Read optional start parameter - Optional, not used in this test
# start_param = sys.argv[1] if len(sys.argv) > 1 else None

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Global setting: Save only failed screenshots (True) or all screenshots (False)
SAVE_ONLY_FAILED_SCREENSHOTS = True  # Muuta Falseksi jos tarvii tallentaa kaikki kuvat

# Default test result is false if tests not passed
test_passed = True  # Alustetaan True, muutetaan False jos testi epäonnistuu

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "Android_test_device"  
options.app_package = "fi.sbweather.app"
options.app_activity = "fi.sbweather.app.MainActivity"
options.automation_name = "UiAutomator2"
# Prevent app reset as this test is ran after installation test - On this case this is optional
options.no_reset = True
options.full_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

def save_screenshot(driver, filename_prefix, timestamp, failed=False):
    """Tallentaa kuvakaappauksen asetuksen mukaan."""
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
    """Tarkistaa onko elementti olemassa ja palauttaa True/False"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return True
    except TimeoutException:
        return False

def test_element(driver, by, value, element_name, screenshot_prefix, timeout=10):
    """Testaa elementin olemassaoloa, tallentaa kuvan ja päivittää test_passed-muuttujan."""
    global test_passed
    if check_element(driver, by, value, timeout):
        print(f"{element_name} löytyi.")
        save_screenshot(driver, f"{screenshot_prefix}_ok", timestamp, failed=False)
        return True
    else:
        print(f"{element_name} ei löytynyt.")
        save_screenshot(driver, f"{screenshot_prefix}_fail", timestamp, failed=True)
        test_passed = False
        return False

def tap_and_test_location(driver, accessibility_id, location_name, screenshot_prefix):
    """Napauttaa sijaintia ja testaa onko lämpötila näkyvissä. Tallentaa kuvan onnistumisesta/epäonnistumisesta."""
    global test_passed
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        element.click()
        print(f"{location_name} -elementti löytyi ja klikattiin onnistuneesti.")
        
        # Odota että säädata latautuu
        time.sleep(10)
        
        # Tarkista että "LÄMPÖTILA" on näkyvissä
        if check_element(driver, AppiumBy.ACCESSIBILITY_ID, "LÄMPÖTILA", 10):
            print("LÄMPÖTILA-elementti löytyi. Säädata on latautunut.")
            save_screenshot(driver, f"{screenshot_prefix}_ok", timestamp, failed=False)
            return True
        else:
            print("LÄMPÖTILA-elementtiä ei löytynyt. Säädatan lataus epäonnistui.")
            save_screenshot(driver, f"{screenshot_prefix}_fail", timestamp, failed=True)
            test_passed = False
            return False
            
    except TimeoutException:
        print(f"{location_name} -elementtiä ei löytynyt aikarajan sisällä.")
        save_screenshot(driver, f"{location_name}_not_found", timestamp, failed=True)
        test_passed = False
        return False

print("\nTest_features_automation.py - Automation test starting...")
time.sleep(2)

try:
    # Sulje sovellus ensin varmistaaksesi alkunäkymä
    driver.terminate_app("fi.sbweather.app")
    print("Sovellus suljettu. Avataan uudelleen...")
    time.sleep(2)
    
    # Avaa sovellus uudelleen
    driver.activate_app("fi.sbweather.app")
    print("Open app Main view...")   
    time.sleep(5)
    
    # Main view verification: check if KOTI tab button is visible using accessibility id
    test_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 
                "KOTI-painike", "KOTI_painike_main")
    
    # Tap and input Oulu text to field - Could have a list of locations and test several locations but this is enough for now
    driver.tap([(400, 780)])  
    time.sleep(3) 
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', 'Oulu'],
        'includeStderr': True,
        'timeout': 5000
    })
    save_screenshot(driver, "Oulun_saa_asemat_lista", timestamp, failed=False)
    
    # Testaa Oulu Vihreäsaari
    tap_and_test_location(driver, "Oulu Vihreäsaari", "Oulu Vihreäsaari", "Saa_oulu_vihreasaari")
    
    # Testaa Oulu lentoasema
    tap_and_test_location(driver, "Oulu lentoasema", "Oulu lentoasema", "Saa_oulu_lentoasema")
    
    # Return to Main view - Dum way to go back like this but ok now
    driver.back()
    time.sleep(3)
    driver.back()
    print("Used Android back button x2 to return to the Main view.")

    # Next Check each view "Lämpimimmät", "Kylmimmät", "Sateisimmat", "Tuulisimmat"
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
        
        # Tarkista onko näkymä oikeasti avautunut
        test_element(driver, AppiumBy.ACCESSIBILITY_ID, view_accessibility_ids[idx],
                    f"{view_accessibility_ids[idx]} -elementti", view_names[idx])
        
        # Return to Main view    
        driver.back()
        print(f"Returned to Main view from {view_names[idx]}.")
        time.sleep(3)

    # Open ENNÄTYKSET tab and check for widget view
    try:
        # Click ENNÄTYKSET tab
        ennatykset_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "ENNÄTYKSET\nTab 2 of 3"))
        )
        ennatykset_tab.click()
        print("ENNÄTYKSET-välilehti avattu.")
        time.sleep(3)
        
        # Check if widget view (ImageView) is visible
        test_element(driver, AppiumBy.CLASS_NAME, "android.widget.ImageView",
                    "Widget-kuva (ImageView)", "Ennatykset_widget")
        
        time.sleep(3)     
    except TimeoutException:
        print("ENNÄTYKSET-välilehteä ei löytynyt.")
        save_screenshot(driver, "Ennatykset_tab_not_found", timestamp, failed=True)
        test_passed = False

    # Final view verification: check if KOTI tab button is still visible then can assume that the app survived all tests
    test_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3",
                "KOTI-painike", "KOTI_painike_final")
    
    # Sulje sovellus - optionl
    # driver.terminate_app("fi.sbweather.app")
    # print("Sovellus suljettu.")

except Exception as e:
    print(f"Note some test or tests failed: {e}")
    test_passed = False
    save_screenshot(driver, "Exception_", timestamp, failed=True)

finally:
    # Quit the driver
    driver.quit()

# Tulosta testin tulos
if test_passed:
    print("🎉 Kaikki testit läpäisty onnistuneesti!")
else:
    print("💥 Jokin testi epäonnistui. Tarkista screenshots_failed-kansio.")

# Exit code for test automation results (0 = success, 1 = failure)
sys.exit(0 if test_passed else 1)