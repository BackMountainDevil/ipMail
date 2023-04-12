import os
import re


def get_ip(netcard="wlan0"):
    # use command ifconfig to get internet ipv4 of netcard wlan0
    now_ip = os.popen("ifconfig %s | grep inet" % netcard).read()
    match_data = re.search(r"inet \d+\.\d+\.\d+\.\d+", now_ip)
    if match_data:
        now_ip = match_data.group().split(" ")[1]
    else:
        now_ip = ""
    return now_ip


# python main func
if __name__ == "__main__":
    print(get_ip())
    print(get_ip("lo"))
