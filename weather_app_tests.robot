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
    ...    noReset=${True}
    ...    fullReset=${False}
    
    Open Application    ${APPIUM_SERVER}    ${options}
    Set Appium Timeout    30 seconds

Tap Coordinates
    [Arguments]    ${x}    ${y}
    Tap With Positions    100    ${x}    ${y}

Input Text Via ADB
    [Arguments]    ${text}
    Execute Script    mobile: shell    { "command": "input", "args": ["text", "${text}"], "includeStderr": true, "timeout": 5000 }

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
    Check Element Exists    accessibility_id=KOTI\nTab 1 of 3
    Save Screenshot    home_tab_visible

Test Oulu Search
    [Documentation]    Testaa Oulun hakutoiminnallisuus
    Tap Coordinates    400    780
    Sleep    3s
    Input Text Via ADB    Oulu
    Save Screenshot    oulu_search
    Sleep    5s    # Odota hakutuloksia

Test Weather Data Loading
    [Documentation]    Testaa että säätiedot latautuvat
    Check Element Exists    accessibility_id=LÄMPÖTILA    15
    Save Screenshot    weather_data_loaded
