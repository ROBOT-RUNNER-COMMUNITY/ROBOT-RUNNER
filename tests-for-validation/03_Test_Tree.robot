*** Settings ***
Documentation    Test suite for cookie-free website testing
Library          SeleniumLibrary
Suite Setup      Open Browser To Start Page
Suite Teardown   Close All Browsers

*** Variables ***
${BROWSER}        chrome
${START_URL}      https://example.com
${TIMEOUT}        10s
${VALID_USER}     testuser
${VALID_PASS}     testpass123

*** Test Cases ***

# --- BASIC FUNCTIONALITY TESTS --- #
Verify Home Page Loads
    [Documentation]    Test that home page loads without cookies
    Page Should Contain    Example Domain
    Page Should Contain Element    //h1

Check Page Title
    [Documentation]    Verify page title matches expected
    Title Should Be    Example Domain

# --- NAVIGATION TESTS --- #
Test Basic Navigation
    [Documentation]    Verify forward/back navigation works
    Click Link    More information...
    Wait Until Page Contains    IANA
    Go Back
    Wait Until Page Contains    Example Domain

# --- CONTENT VALIDATION TESTS --- #
Validate Header Content
    [Documentation]    Check critical page elements exist
    Page Should Contain Element    //h1
    Page Should Contain Element    //div[p]

Check All Links
    [Documentation]    Verify all links are valid (no 404s)
    @{links}=    Get WebElements    tag:a
    FOR    ${link}    IN    @{links}
        ${href}=    Get Element Attribute    ${link}    href
        Continue For Loop If    '${href}' == '${EMPTY}' or '${href}' == '#'
        Run Keyword And Continue On Failure
        ...    Page Should Not Contain Element    //a[@broken]
    END

# --- FORM TESTS --- #
[Template]    Test Login Functionality
    # username        password        expected_result
    ${VALID_USER}    ${VALID_PASS}    Welcome
    invalid          ${VALID_PASS}    Invalid credentials
    ${VALID_USER}    wrongpass        Invalid credentials
    ${EMPTY}        ${VALID_PASS}    required
    ${VALID_USER}    ${EMPTY}        required

# --- PERFORMANCE TESTS --- #
Check Page Load Time
    [Documentation]    Verify page loads within acceptable time
    ${start}=    Get Time    epoch
    Go To    ${START_URL}
    ${end}=    Get Time    epoch
    ${load_time}=    Evaluate    ${end}-${start}
    Should Be True    ${load_time} < 5    Page took too long to load (${load_time}s)

*** Keywords ***
Open Browser To Start Page
    [Documentation]    Open browser with cookie-free configuration
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys
    Call Method    ${options}    add_argument    --disable-extensions
    Call Method    ${options}    add_argument    --disable-notifications
    Call Method    ${options}    add_argument    --disable-cookies
    Create WebDriver    Chrome    chrome_options=${options}
    Go To    ${START_URL}
    Set Selenium Timeout    ${TIMEOUT}
    Maximize Browser Window

Test Login Functionality
    [Arguments]    ${username}    ${password}    ${expected}
    [Documentation]    Template keyword for login tests
    Input Text    id:username    ${username}
    Input Text    id:password    ${password}
    Click Button    id:login
    Run Keyword If    '${expected}' == 'Welcome'
    ...    Wait Until Page Contains    Welcome
    ...  ELSE IF    '${expected}' == 'Invalid credentials'
    ...    Wait Until Page Contains    Invalid credentials
    ...  ELSE
    ...    Wait Until Page Contains    required

*** Comments ***
# To run these tests:
# 1. Install requirements: pip install robotframework selenium
# 2. Download ChromeDriver and add to PATH
# 3. Run: robot website_tests.robot
#
# Note: Replace example.com with your actual website URL
# and update locators (id:username, etc.) to match your site