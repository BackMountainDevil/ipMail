import os
import re
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def get_ip(netcard="wlan0"):
    # use command ifconfig to get internet ipv4 of netcard wlan0
    now_ip = os.popen("ifconfig %s | grep inet" % netcard).read()
    match_data = re.search(r"inet \d+\.\d+\.\d+\.\d+", now_ip)
    if match_data:
        now_ip = match_data.group().split(" ")[1]
    else:
        now_ip = ""
    return now_ip


def send_email(
    from_addr, password, to_addr, subject, content, smtp_server, smtp_port=465
):
    # send email via smtp
    ret = True
    try:
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = formataddr(["Sender", from_addr])
        msg["To"] = formataddr(["Receiver", to_addr])
        msg["Subject"] = subject

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_addr, password)
        server.sendmail(
            from_addr,
            [
                to_addr,
            ],
            msg.as_string(),
        )
        server.quit()
    except Exception:
        ret = False
    return ret


# python main func
if __name__ == "__main__":
    print(get_ip())
    print(get_ip("lo"))
