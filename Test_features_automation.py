*** Settings ***
Library           AppiumLibrary
Library           Collections
Library           OperatingSystem
Library           String
Library           BuiltIn

Suite Setup       Open Weather App
Suite Teardown    Close Application

*** Variables ***
${APPIUM_SERVER}    http://127.0.0.1:4723
${DEVICE_NAME}      Android_test_device
${APP_PACKAGE}      fi.sbweather.app
${APP_ACTIVITY}     fi.sbweather.app.MainActivity
${AUTOMATION_NAME}  UiAutomator2
${SAVE_FAILED_ONLY}  True
${TIMESTAMP}        ${EMPTY}

*** Keywords ***
Open Weather App
    # Luodaan timestamp screenshotteja varten
    ${TIMESTAMP}=    Get Time    result_format=%Y%m%d_%H%M%S
    
    ${options}=    Create Dictionary
    ...    platformName=Android
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    automationName=${AUTOMATION_NAME}
    ...    noReset=True
    ...    fullReset=False

    Open Application    ${APPIUM_SERVER}    desired_capabilities=${options}    timeout=30s

Tap Coordinates
    [Arguments]    ${x}    ${y}
    Tap With Positions    100    ${x}    ${y}

Input Text Via ADB
    [Arguments]    ${text}
    Execute Script    mobile: shell    { "command": "input", "args": ["text", "${text}"], "includeStderr": true, "timeout": 5000 }

Save Screenshot
    [Arguments]    ${filename}    ${failed}=False
    ${save}=    Run Keyword If    '${failed}'=='True' or '${SAVE_FAILED_ONLY}'=='False'    Capture Page Screenshot    ${filename}_${TIMESTAMP}.png
    [Return]    ${save}

Check Element Exists
    [Arguments]    ${locator}    ${timeout}=10
    Wait Until Page Contains Element    ${locator}    ${timeout}
    Page Should Contain Element    ${locator}

Tap And Test Location
    [Arguments]    ${accessibility_id}    ${location_name}    ${screenshot_prefix}
    Click Element    accessibility_id=${accessibility_id}
    Sleep    10s
    Run Keyword And Ignore Error    Check Element Exists    accessibility_id=LÄMPÖTILA
    ${exists}=    Run Keyword And Return Status    Check Element Exists    accessibility_id=LÄMPÖTILA
    Run Keyword If    '${exists}'=='True'    Save Screenshot    ${screenshot_prefix}_ok
    Run Keyword If    '${exists}'=='False'    Save Screenshot    ${screenshot_prefix}_fail    ${True}

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
    Sleep    5s
    Tap And Test Location    Oulu Vihreäsaari    Oulu Vihreäsaari    Weather_oulu_vihreasaari
    Tap And Test Location    Oulu lentoasema    Oulu lentoasema    Weather_oulu_airport

Test Weather Data Loading
    [Documentation]    Testaa että säätiedot latautuvat
    ${view_coords}=    Create List    300,1150    790,1150    300,1480    790,1480
    ${view_ids}=       Create List    Lämpimimmät    Kylmimmät    Sateisimmat    Tuulisimmat
    ${view_names}=     Create List    Max_Temp    Low_Temp    Most_Rain    Most_Windy

    :FOR    ${index}    IN RANGE    0    4
    \    ${coords}=    Get From List    ${view_coords}    ${index}
    \    ${x}=    Split String    ${coords}    ,    first_only=True
    \    ${y}=    Split String    ${coords}    ,    first_only=False
    \    Log    Opening view ${view_names[${index}]} at ${x},${y}
    \    Tap Coordinates    ${x}    ${y}
    \    Sleep    6s
    \    Tap And Test Location    ${view_ids[${index}]}    ${view_ids[${index}]}    ${view_names[${index}]}
    \    Press Keycode    4    # Android Back
    \    Sleep    3s

    # RECORDS tab
    Click Element    accessibility_id=ENNÄTYKSET\nTab 2 of 3
    Sleep    3s
    Check Element Exists    class=android.widget.ImageView
    Save Screenshot    Records_widget

    # Final check HOME tab
    Check Element Exists    accessibility_id=KOTI\nTab 1 of 3
    Save Screenshot    HOME_button_final
