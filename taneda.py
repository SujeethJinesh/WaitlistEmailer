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
hour_in_seconds = 3600
minute_in_seconds = 60
url = "https://tanedaseattle.com/reservation.html"
driver = None

DATE_PICKER = 'TockDatePicker-selectedDate'
MONTH_HEADER = 'InlineWidgetConsumerCalendar-monthHeading'
NEXT_MONTH_CHEVRON = 'InlineWidgetConsumerCalendar-headerNavNext'
BOOK_NOW_BUTTON = 'TockButton-blue'

def click_element_by_class_name(path):
  return driver.find_element(by=By.CLASS_NAME, value=path).click()

def get_element_inner_text(value, tag_name, index=0):
  html = get_list_of_elements_found(value, tag_name)
  return html[index].get_attribute("innerHTML")

def get_list_of_elements_found(value, tag_name):
  return driver.find_element(by=By.CLASS_NAME, value=value).find_elements(by=By.TAG_NAME, value=tag_name)

def run_webdriver():
  global driver
  options = Options()
  # options.headless = True
  service = Service(ChromeDriverManager().install())
  
  driver = webdriver.Chrome(options=options, service=service)
  wait = WebDriverWait(driver, minute_in_seconds)

  driver.get(url)

  # open date picker
  click_element_by_class_name(DATE_PICKER)

  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, NEXT_MONTH_CHEVRON)))

  # look at the month header and move to july if needed
  month_header_text = get_element_inner_text(MONTH_HEADER, 'span')

  if "July" not in month_header_text:
    click_element_by_class_name(NEXT_MONTH_CHEVRON)

  # click on friday (5th element in list)
  get_list_of_elements_found('InlineWidgetConsumerCalendar-week', 'button')[5].click()

  # click on book now button
  click_element_by_class_name(BOOK_NOW_BUTTON)

  # need to identify the iframe
  wait.until(EC.visibility_of_element_located((By.ID, "TockWidget-iframe")))

  # switch to the iframe
  import ipdb; ipdb.set_trace()
  iframe = driver.find_element(by=By.ID, value="TockWidget-iframe")
  driver.switch_to.frame(iframe)

  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ConsumerCalendar')))
  buttons = driver.find_elements(by=By.XPATH, value="//*[@data-testid='consumer-calendar-day']")
  driver.find_elements(by=By.CLASS_NAME, value="ConsumerCalendar-month")
  for button in buttons:
    # if the button is enabled, click into it to see if there's a spot available
    if button.is_enabled():
      button.click()
      driver.close()
      return True

  driver.close()

def check_waitlist(proxy):
    global iterations
    if iterations % 30 == 0:
        print("checking_waitlist, iteration: ", iterations)
    iterations += 1
    try:
        run_webdriver()
    except:
        print("Wasn't able to get response")
    return False


def send_email(subject="4510 Spot Opened Up",
               message="Don't forget to turn off less secure apps: https://myaccount.google.com/lesssecureapps",
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
        if check_waitlist(proxy):
            send_email()
        rand = random.randint(1, 600)
        time.sleep(hour_in_seconds + rand) # check every hour along with a randomizer
