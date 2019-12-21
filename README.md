# unblock-china-with-shadowsocks-openwrt
之前我一直跟的Unblock Youku解决方案，并不适合长期在线的设备比如小米盒子，百度智能音箱等。
感觉国内本地资源的使用需求越来越复杂，这些设备的Request往往不会出现在Unblock Youku的列表中，与其自己写一个列表，干脆直接做一个更方便的路由系统。
注：如果仅仅为了能让自己的PC或手机获得国内资源，Unblock Youku的解决方案是更优解。

总体概念，通过刷Openwrt固件，安装Shadowsocks client，连接国内本地的Shadowsocks Server，创建自己的国内服务IP列表，最终获得以下功能。  
1. 家里需要直连国内资源的设备链接到Openwrt路由器，既能不被识别为海外IP 
1. 仅仅在检查IP时使用Shadowsocks代理，播放视频流的时候则不走代理，以节省大量的带宽 
1. 路由自动获取IP列表更新，基本做到随插即用

## 前期准备

* 一个能刷Openwrt固件的系统 （我目前尝试了小米路由Mini和树莓派2B）
* 一个U盘 （主要用于搜集监听数据和其他Log，路由器本身的内存太少）
* 一个主路由 （Openwrt路由最终会全部使用国内DNS，为了能让家里那些使用国内资源的设备长期在线，不建议使用同一个路由）
* 一台国内的Shadowsocks Server （我目前尝试了xx云的ECS和家里树莓派4）

## 设置Shadowsocks Server

总体来说这一步是最简单的，无脑操作，先把成就感拉出红线 ^^

相关的教程：https://gist.github.com/nathanielove/40c1dcac777e64ceeb63d8296d263d6d （虽然是Ubuntu的，但其实在树莓派上也大同小异）

步骤：
```
    sudo apt-get update
    sudo apt-get install python3-pip
    sudo pip install shadowsocks    
    nano /etc/shadowsocks.json
```
写一个配置的json文档
    {
       "server":"服务器公共IP",
       "server_port":8888,
       "local_port":3333,
       "password":"密码",
       "timeout":600,
       "method":"aes-256-cfb"
    }
local_port随便填
password这段如果没有多人登陆需求，就保留目前设置，如果有，可以用port和密码来配对
    "port_password": {
        "8888": "password1",
        "8000": "password2",
        "8383": "password3",
        "8384": "password4"
    },
method这一段如果没有太大的加密需求，可以考虑采用其他方案，嫌麻烦就保留目前设置
https://github.com/shadowsocks/luci-app-shadowsocks/wiki/Bandwidth-of-encrypt-method  （加密速度对比）
启动
    sudo ssserver -c /etc/shadowsocks.json -d start
停止
    sudo ssserver -c /etc/shadowsocks.json -d stop
服务器重启后自动启动
    nano /etc/rc.local
添加以下命令
    /usr/bin/python /usr/local/bin/ssserver -c /etc/shadowsocks.json -d start
    
### 服务器设置转发（小坑）
以8888为服务器端口为例：
首先服务器如果有内建防火墙，开启相关端口，比如在ubuntu里
    sudo ufw allow 8888
其次如果你使用的是某云的ECS，腾讯也好华为也好阿里也好，基本上大同小异，在安全组里添加8888端口转发
再次如果你是打算搞个树莓派在家里做测试，就在你的路由器上开启8888端口转发，树莓派的eth0需要设置一个static IP，这里我遇到一个小坑，家里的是光纤宽带，本身并不具有公共IP（估计整个大楼都共享一个公共IP），因此即使路由器转发了，但没半毛钱用，最后还是放弃。所以如果在家里架设，务必看一下主路由的DHCP获取的IP是private IP还是public，如果是10.0.xx或192.168.xx啥的，放弃吧。你没有可能让ISP在大楼的主路由上单独给你设置一个端口转发的。
 
    
完成后可以去Shaodowsocks官网下载一个客户端，我测试时使用的时安卓版本
https://shadowsocks.org/en/download/clients.html
输入IP地址，端口，密码和加密方式，链接，通了的话就代表服务器正常运行了。

