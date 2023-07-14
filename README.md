# ipMail

Dynamic DNS

定时检测本机ip,使用smtp发送到指定邮箱

首先修改 config.ini 中的配置，需要注意的是不需要加上双引号，否则程序识别出错，下面是 zhangsan 发给 wangwu 的案例

```ini
[SMTP]
SENDER = zhangsan@qq.com
PASSWORD = zhangsan_password
RECEIVER = wangwu@qq.com
SMTP_SERVER = smtp.qq.com
```

让这个脚本作为系统任务执行，首先根据自身情况修改 ipMail.service 中的 ExecStart 中的代码路径，然后再继续

```bash
sudo cp ipMail.service /usr/lib/systemd/system  # 复制任务
sudo systemctl daemon-reload
sudo systemctl enable ipMail.service --now # 启动任务，并设置为开启自启
sudo journalctl -u ipMail   # 查看日志
```

# 相关阅读

[Linux下当公网IP发生变化时，邮件发送变化的IP，python代码 工学院_9527 2021-09-30](https://blog.csdn.net/qq_41958350/article/details/120568166):socket获取本地ip,smtp发邮件，threading.Timer定时任务

> #获取网卡ip地址函数
> def get_ip_address(ifname):
>         s =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
>         return socket.inet_ntoa(fcntl.ioctl(
>         s.fileno(),
>         0x8915,  # SIOCGIFADDR
>         struct.pack('256s', ifname[:15])
>         )[20:24])

[监测ip变化并发送邮件通知 孔丘闻言 2021-05-11 ](https://blog.csdn.net/xiaodsadwwq/article/details/116654485)：从 ifconfig 的输出截取ip，正则提取ip。死循环sleep定时跑

> now_ip=$(ifconfig utun2 | tr -s ' ' | cut -d' ' -f2 | tail -n1)
>
> ifcon_data = os.popen('ifconfig | grep inet').read()
> match_data = re.search(r'17\.\d+\.\d+\.\d+', ifcon_data)

[Linux环境下纯Python无第三方库读写Netlink 沙老师 2018-03-30](https://blog.csdn.net/shajunxing/article/details/79755996)

[DDNS的实现 erbort  2013-12-20](https://blog.csdn.net/cp25807720/article/details/17452439):轮询ip或者异步钩子

[使用python实现阿里云动态域名解析DDNS 2019-05-15](https://developer.aliyun.com/article/702552):通过网络API获取ip
> with urllib.request.urlopen('http://www.3322.org/dyndns/getip') as response:
>         html = response.read()
>         ip = str(html, encoding='utf-8').replace("\n", "")

[Systemd 定时器教程 阮一峰 2018年3月30日](https://www.ruanyifeng.com/blog/2018/03/systemd-timer.html)
