import smtplib

import time

from credentials import LOGIN, PASSWORD

email_sent = False
iterations = 0


def check_waitlist():
    global iterations
    if iterations % 500 == 0:
        print("checking_waitlist")


def send_email(subject="4510 Spot Opened Up", message="Sign up yooo",
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


if __name__ == '__main__':
    while not email_sent:
        check_waitlist()
        time.sleep(120)
