import random
import smtplib
import requests
import time
from lxml.html import fromstring
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from credentials import LOGIN, PASSWORD

email_sent = False
iterations = 0
headers = {'Accept-Encoding': 'identity'}
proxies = {'62.122.97.66:59143', '1.10.189.45:33696', '195.239.176.98:45601', '197.188.222.163:61636'}
ten_minutes_in_seconds = 600
timeout = 15
url = "https://tanedaseattle.com/reservation.html"
driver = None
wait = None

DATE_PICKER = 'TockDatePicker-selectedDate'
MONTH_HEADER = 'InlineWidgetConsumerCalendar-monthHeading'
NEXT_MONTH_CHEVRON = 'InlineWidgetConsumerCalendar-headerNavNext'
BOOK_NOW_BUTTON = 'TockButton-blue'
MODAL_BODY_MESSAGE = 'SearchModal-body'
RESERVATION_DETAILS = 'Consumer-resultsExperienceDetails'

def click_element_by_class_name(path):
  return driver.find_element(by=By.CLASS_NAME, value=path).click()

def get_element_inner_text(value, tag_name, index=0):
  html = get_list_of_elements_found(value, tag_name)
  return html[index].get_attribute("innerHTML")

def get_list_of_elements_found(value, tag_name):
  return driver.find_element(by=By.CLASS_NAME, value=value).find_elements(by=By.TAG_NAME, value=tag_name)

def set_webdriver():
  global driver, wait
  options = Options()
  options.headless = True
  service = Service(ChromeDriverManager().install())
  
  driver = webdriver.Chrome(options=options, service=service)
  wait = WebDriverWait(driver, timeout)

def select_july_and_open_modal():
  global driver, wait

  # open date picker
  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, DATE_PICKER)))
  click_element_by_class_name(DATE_PICKER)

  # wait until the initial modal opens
  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, NEXT_MONTH_CHEVRON)))

  # look at the month header and move to july if needed
  month_header_text = get_element_inner_text(MONTH_HEADER, 'span')

  # click on book now button
  click_element_by_class_name(BOOK_NOW_BUTTON)

  # need to identify the iframe
  wait.until(EC.visibility_of_element_located((By.ID, "TockWidget-iframe")))

def switch_to_iframe():
  global driver
  iframe = driver.find_element(by=By.ID, value="TockWidget-iframe")
  driver.switch_to.frame(iframe)
  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ConsumerCalendar')))

def verify_reservation_is_open():
    global driver, wait
    ineligibilities = [
        'has not opened reservations',
        'has sold out all reservations',
        'is not offering reservations'
    ]

    for ineligibility in ineligibilities:
        if ineligibility in driver.find_element(by=By.CLASS_NAME, value=MODAL_BODY_MESSAGE).get_attribute("innerHTML"):
            return False
    
    try:
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, RESERVATION_DETAILS)))
    except Exception:
        pass

    if driver.find_element(by=By.XPATH, value="//div[contains(@class, 'Consumer-resultsListItem') and contains(@class, 'is-available')]"):
        return True
    return True

def book_if_has_calendar_availability():
  global driver, wait
  buttons = driver.find_elements(by=By.XPATH, value="//*[@data-testid='consumer-calendar-day']")
  driver.find_elements(by=By.CLASS_NAME, value="ConsumerCalendar-month")

  for button in buttons:
    # if the button is enabled, click into it to see if there's a spot available
    if button.is_enabled():
        button.click()
        if verify_reservation_is_open():
            send_email()
            driver.close()
            return True
  driver.close()
  return False

def run_webdriver():
  # global scope variables
  global driver, wait

  # initialize the web driver
  set_webdriver()

  # get initial page
  driver.get(url)

  select_july_and_open_modal()

  # switch to the iframe
  switch_to_iframe()

  # parse through calendar for available dates
  book_if_has_calendar_availability()

def check_waitlist(proxy):
  global iterations
  print("checking_waitlist, iteration: ", iterations)
  iterations += 1
  try:
    run_webdriver()
  except Exception as err:
    print(err)

def send_email(subject="Taneda Spot Opened Up",
               message="Don't forget to turn off less secure app passwords: https://myaccount.google.com/apppasswords. Reserve here: https://tanedaseattle.com/reservation.html",
               smtpserver='smtp.gmail.com:587'):
  global email_sent
  header = 'From: %s\n' % LOGIN
  header += 'To: %s\n' % ','.join([LOGIN])
  header += 'Subject: %s\n\n' % subject
  message = header + message

  server = smtplib.SMTP(smtpserver)
  server.starttls()
  server.login(LOGIN, PASSWORD)
  problems = server.sendmail(LOGIN, [LOGIN], message)
  if problems:
    print(problems)
  server.quit()
  email_sent = True


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies_set = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies_set.add(proxy)
    return proxies_set


if __name__ == '__main__':
  while not email_sent:
      proxy = random.choice(list(proxies))
      try:
        check_waitlist(proxy)
      except Exception:
        continue
      print("completed iteration: ", iterations)
      rand = random.randint(1, 30)
      time.sleep(ten_minutes_in_seconds + rand) # check every 10 mins along with a randomizer
