*** Settings ***
Library    AppiumLibrary
Library    Collections
Library    OperatingSystem
Library    String
Library    BuiltIn

Suite Setup      Open Weather App
Suite Teardown   Close Application

*** Variables ***
${APPIUM_SERVER}    http://127.0.0.1:4723

*** Keywords ***
Open Weather App
    ${options}=    Create Dictionary
    ...    platformName=Android
    ...    deviceName=Android_test_device
    ...    appPackage=fi.sbweather.app
    ...    appActivity=fi.sbweather.app.MainActivity
    ...    automationName=UiAutomator2
    ...    noReset=${TRUE}
    ...    fullReset=${FALSE}
    
    Open Application    ${APPIUM_SERVER}    ${options}
    Set Appium Timeout    30 seconds

Tap Coordinates
    [Arguments]    ${x}    ${y}
    Tap With Positions    100    ${x}    ${y}

Input Text Via ADB
    [Arguments]    ${text}
    Execute Mobile Command    shell    command=input    args=text ${text}

Save Screenshot
    [Arguments]    ${filename}
    Capture Page Screenshot    ${filename}.png

Check Element Exists
    [Arguments]    ${locator}    ${timeout}=10
    Wait Until Page Contains Element    ${locator}    ${timeout}
    Page Should Contain Element    ${locator}

*** Test Cases ***
Test Home Tab Visibility
    [Documentation]    Testaa että HOME-välilehti on näkyvissä
    Check Element Exists    accessibility_id=KOTI
    Save Screenshot    home_tab_visible

Test Oulu Search
    [Documentation]    Testaa Oulun hakutoiminnallisuus
    Tap Coordinates    400    780
    Sleep    3s
    Input Text Via ADB    Oulu
    Sleep    5s
    # Odotetaan ensimmäistä hakutulos-elementtiä (korvaa oikealla locatorilla)
    Check Element Exists    xpath=//android.widget.TextView[contains(@text,'Oulu')]
    Save Screenshot    oulu_search

Test Weather Data Loading
    [Documentation]    Testaa että säätiedot latautuvat
    # Käytä tässä tarkkaa locatoria Appium Inspectorista, esim:
    Check Element Exists    xpath=//android.widget.TextView[contains(@content-desc,'LÄMPÖTILA')]    15
    Save Screenshot    weather_data_loaded
