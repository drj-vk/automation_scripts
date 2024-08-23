import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

# Define variables for the IDs
email_id = "request_anonymous_requester_email"
problem_type_id = "request_custom_fields_360018017014"
subject_id = "request_subject"
description_id = "request_description"
date_id = "request_custom_fields_360017858514"
booking_number_id = "request_custom_fields_360017856254"
payment_method_id = "request_custom_fields_360017880553"
iban_id = "request_custom_fields_360017857374"
bank_name_id = "request_custom_fields_360017857734"
account_holder_name_id = "request_custom_fields_360018049793"
flight_number_id = "request_custom_fields_360017858494"
phone_number_id = "request_custom_fields_360017857434"

# Configure the webdriver (make sure you have the appropriate driver installed)
driver = webdriver.Edge()

# Open the webpage
driver.get("https://help.flyadeal.com/hc/en-us/requests/new?ticket_form_id=360000957934")

try:
    # Wait for the form to be available and fill in the fields
    wait = WebDriverWait(driver, 10)
    
    # Fill in the email address field
    email_field = wait.until(EC.presence_of_element_located((By.ID, email_id)))
    email_field.send_keys("diederik@vkrieken.com")

    # Select a random option for the type of website/app problem field
    problem_type_value = random.choice(["website_app_checkin", "website_technical"])
    driver.execute_script(f'document.getElementById("{problem_type_id}").value = "{problem_type_value}";')

    # Select the payment method field
    payment_method_value = "card_payment_airport"
    driver.execute_script(f'document.getElementById("{payment_method_id}").value = "{payment_method_value}";')

    # Wait for 2 seconds
    time.sleep(2)

    # Fill in the subject field
    subject_field = driver.find_element(By.ID, subject_id)
    # subject_field.send_keys("Faulty website causes flyadeal to steal money")
    subject_field.send_keys("Checkin website did not work")
    # Fill in the description field
    description_field = driver.find_element(By.ID, description_id)
    escription_content = ("""
                          Despite trying multiple browsers, I couldn't complete my online check-in. At the airport counter, I was informed this issue is quite common and was directed to fill out the form at https://help.flyadeal.com/hc/en-us/articles/360022294154-I-cannot-check-in-online to request a refund.
                          As I said, I had to pay for the counter check-in and have not received my refund.
                          Flyadeal, this situation is unacceptable. Your website's malfunction prevented me from checking in online, yet I've been left to shoulder the cost. Your customer service has been unresponsive and has attempted to shift the blame onto me.
                          Please fix your website and return my money. It's only fair that I am not penalised for an issue caused by your system."""
                        )
    # description_content = (
    # "Despite trying multiple browsers, I couldn't complete my online check-in. "
    # "At the airport counter, I was informed this issue is quite common and was directed to fill out the form at "
    # "https://help.flyadeal.com/hc/en-us/articles/360022294154-I-cannot-check-in-online to request a refund. "
    # "Unfortunately, I had to pay for the counter check-in and have yet to receive my refund.\n\n"
    # "Flyadeal, this situation is unacceptable. Your website's malfunction prevented me from checking in online, "
    # "yet I've been left to shoulder the cost. Your customer service has been unresponsive and has attempted to shift the blame onto me.\n\n"
    # "Please, fix your website and return my money. It's only fair that I am not penalized for an issue caused by your system."
    # )
    # description_content = (
    #     "The website did not work, and I was unable to check - in. "
    #     "At the counter I was told that this is a common issue and that I should fill in the form https://help.flyadeal.com/hc/en-us/articles/360022294154-I-cannot-check-in-online."
    #     "Repair your website and return the money. Don't let me pay for YOUR fault."
    # )
    # description_content = (
    #     "After multiple attempts in different browsers, I could not check-in online. At the counter, "
    #     "I was told that this was a common issue and that I should fill in the form https://help.flyadeal.com/hc/en-us/articles/360022294154-I-cannot-check-in-online "
    #     "to retrieve my money back. I still paid for the counter check-in. I still haven't received my money back. "
    #     "Flyadeal continuously ignored me, trying to blame me for not checking in online—which was not possible due to a faulty website.\n\n"
    #     "@Flyadeal, Repair your website and return the money. Don't let me pay for YOUR fault."
    # )
    description_field.send_keys(description_content)

    # Fill in the date field using JavaScript
    driver.execute_script(f'document.getElementById("{date_id}").value = "2023-05-11";')

    # Fill in the booking number field
    booking_number_field = driver.find_element(By.ID, booking_number_id)
    booking_number_field.send_keys("T36YGL")

    # Fill in the IBAN field
    iban_field = driver.find_element(By.ID, iban_id)
    iban_field.send_keys("NL74INGB0008680188")

    # Fill in the Bank Name field
    bank_name_field = driver.find_element(By.ID, bank_name_id)
    bank_name_field.send_keys("INGB")

    # Fill in the Account Holder Name field
    account_holder_name_field = driver.find_element(By.ID, account_holder_name_id)
    account_holder_name_field.send_keys("DRJ van Krieken")

    # # Fill in the Flight Number field
    # flight_number_field = driver.find_element(By.ID, flight_number_id)
    # flight_number_field.send_keys("FZ123")

    # Fill in the Phone Number field
    phone_number_field = driver.find_element(By.ID, phone_number_id)
    phone_number_field.send_keys("+31643831347")

    # Wait before submitting the form
    wait = WebDriverWait(driver, 60)
    
    # Wait for 2 seconds
    time.sleep(60)

    # Submit the form
    submit_button = driver.find_element(By.NAME, "commit")
    submit_button.click()

    # Wait for confirmation (adjust as necessary)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".confirmation_message")))

    print("Form submitted successfully!")

finally:
    # Close the browser
    driver.quit()
