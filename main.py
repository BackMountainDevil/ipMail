import configparser
import platform
import re
import smtplib
import socket
import subprocess
import threading
from email.mime.text import MIMEText
from email.utils import formataddr


def get_ipv4_by_socket():
    """
    通过socket获取IPv4地址
    """
    try:
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        ipv4_addresses = set(ip for ip in ip_addresses)
        return ipv4_addresses
    except Exception as e:
        print(f"获取IPv4地址时出错: {e}")
        return None


def get_ip_by_ifconfig(netcard="wlan0", v4=True, v6=True):
    """use command ifconfig to get internet ip of netcard wlan0

    Args:
        netcard (str, optional): 网卡名称，默认是无线网卡 "wlan0"，网线一般是 "lo".
        如果网卡不存在，将会返回ifconfig的错误信息：
            "error fetching interface information: Device not found"

    Returns:
        set: ip address set if netcard exist.
    """
    cmd = ["ifconfig", netcard]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception(f"Command {cmd} failed with error: {err.decode()}")
    output = out.decode()

    ip = set()
    if v4:
        match_data = re.search(r"inet \d+\.\d+\.\d+\.\d+", output)
        if match_data:
            now_ip = match_data.group().split(" ")[1]
            ip.add(now_ip)
    # 一个网卡可能具有多个 ipv6 地址
    if v6:
        start_str = "inet6"
        stop_str = "prefixlen"
        start = 0
        while True:
            start = output.find(start_str, start)
            end = output.find(stop_str, start)
            if start != -1 and end != -1 and start < end:
                ip.add(output[start + len(start_str) : end].strip())  # 切片去除空格
                start += end - start
            else:
                break
    return ip


def get_ip_by_ipconfig(v4=True, v6=True):
    """
    通过ipconfig获取IP地址
    Args:
        v4 (bool, optional): 是否获取IPv4地址，默认True
        v6 (bool, optional): 是否获取IPv6地址，默认True
    Returns:
        set: ip address set
    """
    try:
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        output = result.stdout
        ip_addresses = set()
        lines = output.splitlines()
        for _, line in enumerate(lines):
            if v4 and "IPv4 Address" in line:
                ip_address = line.split(":")[1].strip()
                ip_addresses.add(ip_address)
            elif v6 and "IPv6 Address" in line:  # ipv6地址内含有冒号，需要特殊处理
                idx = line.find(":") + 1
                ip_address = line[idx:].strip()
                ip_addresses.add(ip_address)
        return ip_addresses
    except Exception as e:
        print(f"获取IP地址时出错: {e}")
        return None


def filter_ip(ips: set):
    """
    自定义过滤规则，过滤掉不需要的IP地址
    """
    ret = set()
    for ip in ips:
        if (
            ip.startswith("192.168.")
            or ip.startswith("127.0.")
            or ip.startswith("fe80:")
        ):
            continue
        else:
            ret.add(ip)
    return ret


def get_ips(filter=None):
    """
    根据不同操作系统，获取ip地址
    Args:
        filter (function, optional): 自定义过滤规则，过滤掉不需要的IP地址
    Returns:
        set: ip address set
    """
    ipv4 = get_ipv4_by_socket()
    os_type = platform.system()
    if os_type == "Windows":
        ip = get_ip_by_ipconfig()
    elif os_type == "Linux":
        ip = get_ip_by_ifconfig()
    else:
        assert False, f"不支持的操作系统类型: {os_type}"
    ip = ip.union(ipv4)
    if filter:
        ip = filter(ip)
    return ip


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
    # 定时任务，判断ip是否有更新，有更新则发送邮件
    ip_now = get_ips(filter_ip)  # 获取当前ip
    global IPS
    if not ip_now == IPS:
        print(
            "ip update to:",
            ip_now,
        )
        send_email(content=ip_now)
        IPS = ip_now
    else:
        print("ip not change:", ip_now)
    threading.Timer(3600, main).start()  # 3600s 后调用该函数


# python main func
if __name__ == "__main__":
    IPS = get_ips(filter_ip)
    print("ips:", IPS)
    send_email(content=IPS)
    main()
