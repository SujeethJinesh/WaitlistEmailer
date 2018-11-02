import random
import smtplib
import requests
import time
from bs4 import BeautifulSoup
from lxml.html import fromstring

from credentials import LOGIN, PASSWORD

email_sent = False
iterations = 0
headers = {'Accept-Encoding': 'identity'}


def check_waitlist(proxy):
    global iterations
    if iterations % 500 == 0:
        print("checking_waitlist")
    iterations += 1
    try:
        response = requests.get(
            "https://oscar.gatech.edu/pls/bprod/bwckschd.p_disp_detail_sched?term_in=201902&crn_in=21318",
            proxies={"http": proxy, "https": proxy}, headers=headers)
        soup = BeautifulSoup(response.text)
        table = soup.findAll("table", class_="datadisplaytable")[1]
        if table("td")[-1].text != '0':
            return True
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
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return random.choice(list(proxies))


if __name__ == '__main__':
    while not email_sent:
        proxy = get_proxies()
        if check_waitlist(proxy):
            send_email()
        rand = random.randint(1, 5)
        time.sleep(60 + rand)
