import schedule
import time
import smtplib

email_sent = False
iterations = 0


def check_waitlist():
    global iterations
    if iterations % 500 == 0:
        print("checking_waitlist")


def send_email(from_addr="sujeethjinesh@gmail.com", to_addr_list="sujeethjinesh@gmail.com",
               subject="4510 Spot Opened Up", message="Sign up yooo",
               login, password,
               smtpserver='smtp.gmail.com:587'):
    global email_sent
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

    email_sent = True


if __name__ == '__main__':
    while not email_sent:
        check_waitlist()
        time.sleep(120)
