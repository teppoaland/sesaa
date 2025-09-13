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
start_param = sys.argv[1] if len(sys.argv) > 1 else None

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Default test result is false if tests not passed
test_passed = False

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
    dirname = "screenshots_failed" if failed else "screenshots"
    os.makedirs(dirname, exist_ok=True)
    filename = f"{filename_prefix}_{timestamp}.png"
    filepath = os.path.join(dirname, filename)
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")
    return filepath

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
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3"
            ))
        )
        print("KOTI-painike löytyi. App is on Main view state confirmed.")
        test_passed = True
        save_screenshot(driver, "KOTI_painike_main_ok", timestamp)
    except TimeoutException:
        print("KOTI-painiketta ei löytynyt. Something may have failed.")
        test_passed = False
        save_screenshot(driver, "KOTI_painike_main_fail", timestamp, failed=True)
    
    # Tap and input Oulu text to field
    driver.tap([(400, 780)])  
    time.sleep(3) 
    driver.execute_script('mobile: shell', {
        'command': 'input',
        'args': ['text', 'Oulu'],
        'includeStderr': True,
        'timeout': 5000
    })
    save_screenshot(driver, "Oulun_saa_asemat_lista", timestamp)
    
    # Uusi koodi Accessibility ID:n käytöllä:
    
    # Tap and select Oulu Vihreäsaari
    try:
        vihreasaari_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Oulu Vihreäsaari"))
        )
        vihreasaari_element.click()
        print("Oulu Vihreäsaari -elementti löytyi ja klikattiin onnistuneesti.")
        
        # Odota että säädata latautuu
        time.sleep(10)
        
        # Tarkista että "LÄMPÖTILA" on näkyvissä
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "LÄMPÖTILA"))
            )
            print("LÄMPÖTILA-elementti löytyi. Säädata on latautunut.")
            test_passed = True
            save_screenshot(driver, "Saa_oulu_vihreasaari_ok", timestamp)
            
        except TimeoutException:
            print("LÄMPÖTILA-elementtiä ei löytynyt. Säädatan lataus epäonnistui.")
            test_passed = False
            save_screenshot(driver, "Saa_oulu_vihreasaari_fail", timestamp, failed=True)
            
    except TimeoutException:
        print("Oulu Vihreäsaari -elementtiä ei löytynyt aikarajan sisällä.")
        test_passed = False
        save_screenshot(driver, "Oulu_vihreasaari_not_found", timestamp, failed=True)
    
    # Tap and select Oulu lentoasema
    try:
        oulu_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Oulu lentoasema"))
        )
        oulu_element.click()
        print("Oulu lentoasema -elementti löytyi ja klikattiin onnistuneesti.")
        
        # Odota että säädata latautuu
        time.sleep(10)
        
        # Tarkista että "LÄMPÖTILA" on näkyvissä 
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "LÄMPÖTILA"))
            )
            print("LÄMPÖTILA-elementti löytyi. Säädata on latautunut.")
            test_passed = True
            save_screenshot(driver, "Saa_oulu_lentoasema_ok", timestamp)
            
        except TimeoutException:
            print("LÄMPÖTILA-elementtiä ei löytynyt. Säädatan lataus epäonnistui.")
            test_passed = False
            save_screenshot(driver, "Saa_oulu_lentoasema_fail", timestamp, failed=True)
            
    except TimeoutException:
        print("Oulu lentoasema -elementtiä ei löytynyt aikarajan sisällä.")
        test_passed = False
        save_screenshot(driver, "Oulu_lentoasema_not_found", timestamp, failed=True)
    
    # Return to Main view - Bad implementation as if prevous click was not working there is needed only one back button to return to Main view!
    driver.back()
    time.sleep(3)
    driver.back()
    print("Used Android back button x2 to return to the Main view.")

    # Open and check these four views by opening these views using driver.tap these coordinates: (300, 1150), (790, 1150), (300, 1480), (790, 1480)
    # Take screenshot of each view using save_screenshot function
    # Use driver.back() function to return to Main view from each view.
    # Use time.sleep(3) between actions
    # Check each view, take screenshot about the view if it is visible or not after opening, 
    # using the following accessibility ids "Lämpimimmät", "Kylmimmät", "Sateisimmat", "Tuulisimmat"

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
        time.sleep(5) # Wait for the view to open. Conten may may miss the view but not that important as we cannot analyze the content.
        
        # Tarkista onko näkymä oikeasti avautunut
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    AppiumBy.ACCESSIBILITY_ID, view_accessibility_ids[idx]
                ))
            )
            print(f"{view_accessibility_ids[idx]} -elementti löytyi. Näkymä avautui onnistuneesti.")
            screenshot_name = f"{view_names[idx]}_ok"
            test_passed = True
            save_screenshot(driver, screenshot_name, timestamp)
        except TimeoutException:
            print(f"{view_accessibility_ids[idx]} -elementtiä ei löytynyt. Näkymän avautuminen epäonnistui.")
            screenshot_name = f"{view_names[idx]}_fail"
            test_passed = False
            save_screenshot(driver, screenshot_name, timestamp, failed=True)
    
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
        
        # Check if widget view (ImageView) is visible - BAD check here as in widget view there is no accessibility id!
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.ImageView"))
            )
            print("Widget-kuva (ImageView) löytyi ENNÄTYKSET-näkymästä.")
            save_screenshot(driver, "Ennatykset_widget_ok", timestamp)
        except TimeoutException:
            print("Widget-kuvaa (ImageView) ei löytynyt ENNÄTYKSET-näkymästä.")
            save_screenshot(driver, "Ennatykset_widget_fail", timestamp, failed=True)
        
        time.sleep(3)     
    except TimeoutException:
        print("ENNÄTYKSET-välilehteä ei löytynyt.")
        save_screenshot(driver, "Ennatykset_tab_not_found", timestamp, failed=True)

    # Final view verification: check if KOTI tab button is still visible using accessibility id
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3"
            ))
        )
        print("KOTI-painike löytyi edelleen. All inportant views confirmed.")
        test_passed = True
        save_screenshot(driver, "KOTI_painike_ok", timestamp)
    except TimeoutException:
        print("KOTI-painiketta ei löytynyt. Something may have failed.")
        test_passed = False
        save_screenshot(driver, "KOTI_painike_fail", timestamp, failed=True)

except Exception as e:
    print(f"Note some test or tests failed: {e}")
    test_passed = False
    # Save screenshot on any exception
    save_screenshot(driver, "Exception_", timestamp, failed=True)

finally:
    # Quit the driver
    driver.quit()

# Exit code for test automation results (0 = success, 1 = failure)
sys.exit(0 if test_passed else 1)