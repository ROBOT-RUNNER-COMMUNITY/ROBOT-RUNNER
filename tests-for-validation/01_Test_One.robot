*** Settings ***
Library  SeleniumLibrary

*** Variables ***
${BROWSER}    Chrome
${URL}        https://www.wikipedia.org/
${SEARCH_FIELD}    name=search
${SEARCH_BUTTON}    xpath=//button[@type='submit']
${RESULT_TITLE}    id=firstHeading

*** Test Cases ***
Test Recherche Wikipedia
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    ${SEARCH_FIELD}    timeout=5s
    Input Text    ${SEARCH_FIELD}    Robot Framework
    Click Element    ${SEARCH_BUTTON}
    Wait Until Element Is Visible    ${RESULT_TITLE}    timeout=5s
    Element Should Contain    ${RESULT_TITLE}    Robot Framework
    [Teardown]    Close Browser
