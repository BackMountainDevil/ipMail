import configparser
import subprocess
import re
import smtplib
import threading
from email.mime.text import MIMEText
from email.utils import formataddr


def get_ip(netcard="wlan0"):
    """use command ifconfig to get internet ipv4 of netcard wlan0

    Args:
        netcard (str, optional): 网卡名称，默认是无线网卡 "wlan0"，网线一般是 "lo".
        如果网卡不存在，将会返回ifconfig的错误信息：
            "error fetching interface information: Device not found"

    Returns:
        string: ipv4 address if netcard exist.
    """
    cmd = ["ifconfig", netcard]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception(f"Command {cmd} failed with error: {err.decode()}")
    now_ip = out.decode()
    match_data = re.search(r"inet \d+\.\d+\.\d+\.\d+", now_ip)
    if match_data:
        now_ip = match_data.group().split(" ")[1]
    else:
        now_ip = ""
    return now_ip


def get_ipv6(netcard="wlan0"):
    """use command ifconfig to get internet ipv6 address of netcard

    Args:
        netcard (str, optional): 网卡名称，默认是无线网卡 "wlan0"，网线一般是 "lo".
        如果网卡不存在，将会返回ifconfig的错误信息：
            "error fetching interface information: Device not found"

    Returns:
        string: ipv6 address if netcard exist.
    """
    cmd = ["ifconfig", netcard]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception(f"Command {cmd} failed with error: {err.decode()}")
    output = out.decode()
    start_str = "inet6"
    start = output.find(start_str)
    end = output.find("prefixlen")
    return output[start + len(start_str) : end].strip()  # 切片去除空格


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


def send_email(
    from_addr=getConfig("SMTP", "SENDER"),
    password=getConfig("SMTP", "PASSWORD"),
    to_addr=getConfig("SMTP", "RECEIVER"),
    subject="ip",
    content="content",
    smtp_server=getConfig("SMTP", "SMTP_SERVER"),
    smtp_port=465,
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


def main():
    # user function get_ip to get ip every hour, if ip change, then send an email
    ip_now = get_ip()  # 获取当前ip
    ipv6_now = get_ipv6()
    global ip, ipv6
    if not ip_now == ip or not ipv6_now == ipv6:
        print("ip update to:", ip_now, ipv6_now)
        send_email(content=ip_now + "\n" + ipv6_now)
        ip = ip_now
        ipv6 = ipv6_now
    else:
        print("ip not change:", ip_now, ipv6_now)
    threading.Timer(3600, main).start()  # 3600s 后调用该函数


# python main func
if __name__ == "__main__":
    ip = get_ip()
    ipv6 = get_ipv6()
    print("ipv4:", ip, "\tipv6:", ipv6)
    send_email(content=ip + "\n" + ipv6)
    main()
