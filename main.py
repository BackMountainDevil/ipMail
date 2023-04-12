import os
import re
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import configparser


def get_ip(netcard="wlan0"):
    """use command ifconfig to get internet ipv4 of netcard wlan0

    Args:
        netcard (str, optional): 网卡名称，默认是无线网卡 "wlan0"，网线一般是 "lo". 
        如果网卡不存在，将会返回ifconfig的错误信息：
            "error fetching interface information: Device not found"

    Returns:
        string: ipv4 address if netcard exist.
    """
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
    """send email via smtp

    Args:
        from_addr (str): 发送方邮箱地址
        password (str): 发送方账户授权码，非邮箱密码
        to_addr (str): 收件人邮箱地址
        subject (str): 邮件主题
        content (str): 邮件内容
        smtp_server (str): 发送方smtp服务器
        smtp_port (int, optional): smtp服务端口，默认为 465

    Returns:
        Bool: send succ? True:False
    """
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


def getConfig(section, option, configFile="config.ini"):
    # use configparser read config from config.ini
    cfg = configparser.RawConfigParser()  # 创建配置文件对象
    cfg.optionxform = lambda option: option  # 重载键值存储时不重置为小写
    cfg.read(configFile, encoding="utf-8")  # 读取配置文件，没有就创建
    if not cfg.has_section(section):
        cfg.add_section(section)
        with open(configFile, "w") as configfile:
            cfg.write(configfile)
    if cfg.has_option(section, option):
        return cfg.get(section, option)
    return None


# python main func
if __name__ == "__main__":
    print(get_ip())
    print(get_ip("lo"))
    send_email(
        getConfig("SMTP", "SENDER"),
        getConfig("SMTP", "PASSWORD"),
        getConfig("SMTP", "RECEIVER"),
        "ipv4",
        get_ip("lo"),
        getConfig("SMTP", "SMTP_SERVER"),
    )
