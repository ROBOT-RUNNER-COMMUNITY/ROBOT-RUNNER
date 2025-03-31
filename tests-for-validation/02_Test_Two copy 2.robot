*** Settings ***
Library  SeleniumLibrary

*** Variables ***
${BROWSER}    Chrome
${URL}        https://www.xe.com/
${AMOUNT_FIELD}    name=Amount
${FROM_CURRENCY}    name=From
${TO_CURRENCY}    name=To
${CONVERT_BUTTON}    xpath=//button[text()='Convert']
${RESULT_SECTION}    xpath=//p[contains(@class, 'result__BigRate')]  

*** Test Cases ***
Test Conversion Monnaie XE
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    ${AMOUNT_FIELD}    timeout=5s
    Input Text    ${AMOUNT_FIELD}    100
    Select From List By Label    ${FROM_CURRENCY}    EUR
    Select From List By Label    ${TO_CURRENCY}    USD
    Click Element    ${CONVERT_BUTTON}
    Wait Until Element Is Visible    ${RESULT_SECTION}    timeout=5s
    Element Should Be Visible    ${RESULT_SECTION}
    [Teardown]    Close Browser
