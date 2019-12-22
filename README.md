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
另一个教程：https://www.reddit.com/r/China/comments/8hp0kr/shadowsocks_server_on_raspberry_pi/ （比较详细，不过使用的是script启动）

步骤：
```
    sudo apt-get update
    sudo apt-get install python3-pip
    sudo pip install shadowsocks    
    nano /etc/shadowsocks.json
```
写一个配置的json文档
```
    {
       "server":"服务器公共IP",
       "server_port":8888,
       "local_port":3333,
       "password":"密码",
       "timeout":600,
       "method":"aes-256-cfb"
    }
```
local_port随便填
password这段如果没有多人登陆需求，就保留目前设置，如果有，可以用port和密码来配对
```
    "port_password": {
        "8888": "password1",
        "8000": "password2",
        "8383": "password3",
        "8384": "password4"
    }
```
method这一段如果没有太大的加密需求，可以考虑采用其他方案，嫌麻烦就保留目前设置
https://github.com/shadowsocks/luci-app-shadowsocks/wiki/Bandwidth-of-encrypt-method  （加密速度对比）
启动
```
    sudo ssserver -c /etc/shadowsocks.json -d start
```
停止
```
    sudo ssserver -c /etc/shadowsocks.json -d stop
```
服务器重启后自动启动
```
    nano /etc/rc.local
```
添加以下命令
```
    /usr/bin/python /usr/local/bin/ssserver -c /etc/shadowsocks.json -d start
```
    
### 服务器设置转发（小坑）
以8888为服务器端口为例：
首先服务器如果有内建防火墙，开启相关端口，比如在ubuntu里
```
    sudo ufw allow 8888
```
其次如果你使用的是某云的ECS，腾讯也好华为也好阿里也好，基本上大同小异，在安全组里添加8888端口转发
再次如果你是打算搞个树莓派在家里做测试，就在你的路由器上开启8888端口转发，树莓派的eth0需要设置一个static IP，这里我遇到一个小坑，家里的是光纤宽带，本身并不具有公共IP（估计整个大楼都共享一个公共IP），因此即使路由器转发了，但没半毛钱用，最后还是放弃。所以如果在家里架设，务必看一下主路由的DHCP获取的IP是private IP还是public，如果是10.0.xx或192.168.xx啥的，放弃吧。你没有可能让ISP在大楼的主路由上单独给你设置一个端口转发的。
 
    
完成后可以去Shaodowsocks官网下载一个客户端，我测试时使用的时安卓版本
https://shadowsocks.org/en/download/clients.html
输入IP地址，端口，密码和加密方式，链接，通了的话就代表服务器正常运行了。

## 刷Openwrt固件

* putty 或类似ssh软件
* winscp 传输档案用
* U盘
* 大头针或牙签
* Cat5 网线
* Win32DiskImager （树莓派用）

因为尝试了小米路由mini和树莓派2B，虽然基本上没太大区别，网上都搜得到，我还是分两个设备各自简要介绍下流程

### 小米路由mini （算是原生支持openwrt，推荐，便宜而且方便，但不适合进一步折腾）
首先刷小米开发板固件（有坑）
很多教程里都直接让你去官网下载开发板固件，其实有误，原因是这些教程都过期了，新的官方开发板固件里的ssh秘钥算法不匹配官网自己的ssh.bin，因此需要下载一个旧的开发板固件版本，我用的是0.436，据说0.8以内都可以，这里放一篇教程
https://www.shuyz.com/posts/unhappy-experience-with-miwifi-mini-ssh-access/
下载完开发板固件，电脑连上小米路由，在固件更新页面里上传开发板固件，直接在路由器界面里更新，很方便。
更新，重启完，如果你没有小米账号，先去官网注册一个，并且下载miwifi的app，把你新刷的路由器加进你的账号里

下一步我们要开通路由器的SSH功能
去 http://www1.miwifi.com/miwifi_open.html 点击 “开启SSH工具”，这里有第二个坑，目前点击该链接，如果你在海外，你会得到一个出错页面。还记得之前设置好的Shadowsocks Server吗？先下载个客户端，全局代理，模拟当前设备在国内，然后再点那个链接，才会跳转出来。
该页面会列出属于你的当前路由器列表，如果你不把新刷的路由器加进你的账户，你看不到该路由器在列表中，也就无法得到SSH秘钥的密码。
该密码是每台路由器都不同的，不同路由器之间无法公用。
另一个教程： https://www.jianshu.com/p/984d3c914e35
写下密码，下载 miwifi_ssh.bin

下一步我们需要把 miwifi_ssh.bin 写进U盘里，又有一个坑。
如果你是Win 10，你会发现Format U盘时没有Fat32选项，只有exFat和NTFS，如果你用这两个format，刷ssh的时候你会看到路由器LED灯变红。
所以你需要找一台Win7的电脑，或者下一个Fat32的format软件，不麻烦。
Format U盘后，复制 miwifi_ssh.bin 到U盘，插进小米路由，把电源先拔了，拿针顶住Reset按钮，插回电源，看到黄灯闪烁，放开reset按钮，过一分钟ssh就刷好了，然后用putty或你喜欢的ssh客户端连接，ssh的用户名是root，密码是123456

然后去openwrt官网下载最新版的固件
https://downloads.openwrt.org/releases/18.06.5/targets/ramips/mt7620/openwrt-18.06.5-ramips-mt7620-miwifi-mini-squashfs-sysupgrade.bin
目前亲测18.06.5可用，以后新版本不兼容的话，刷这个版本配合shadowsocks-libev肯定不会有问题
你也可以根据自己想要的版本下载，只要能找到mt7620的子文件夹和miwifi-mini那个bin文件即可

另外，有不少教程建议小米路由刷openwrt前先刷breed，这样即使变砖也能救回，建议这么做，不过我嫌麻烦没做 /dodge

最后把下载的openwrt 固件通过winscp上传到路由器上，假设上传路径和档案名为 /tmp/openwrt.bin
输入
```
    mtd -r write /tmp/openwrt.bin firmware
```
如果出现Could not open mtd device: firmware，就改成
```
    mtd -r write /tmp/openwrt.bin OS1
```
相关教程： https://swsmile.info/2019/01/30/%E3%80%90Embeded-System%E3%80%91%E5%B0%8F%E7%B1%B3%E8%B7%AF%E7%94%B1%E5%99%A8mini%E5%88%B7OpenWRT/

最后一步(很坑）
刷完后你会发现路由器的LED灯疯了一般狂闪，还是鲜红鲜红的，输入预设的192.168.1.1也无法接入，感觉像变砖。
其实不然，原因是当前版本的固件，预设不打开wifi和dhcp，另外mini的初始灯状态估计就是疯狂红

解决方法是通过网线，直连你的电脑，把电脑网卡设置为 192.168.0.x, 网关为192.168.0.1
然后浏览器里输入192.168.0.1 若能打开openwrt的管理界面，刷固件搞定！

### 树莓派 （原生不支持openwrt，4和zero目前官网并不支持，不过安装方便，就是不知道我用的2B性能会不会有瓶颈）
去官网下载固件 https://openwrt.org/toh/raspberry_pi_foundation/raspberry_pi
找installation那个表，对应自己树莓派的版本，下载后在你的PC端，用Win32DiskImager把img写到sd卡上，再把sd卡插入树莓派，把树莓派用网线连接到主路由，插入usb电源

和小米路由最后一步差不多，当前固件预设状态不打开wifi和dhcp，且ip地址是固定写死的192.168.1.1
因此如果当前你家网络（主路由）net不是192.168.1.0/24的话，暂时先改一下，我把主路由临时改成了192.168.1.2

接上电源后，等一分钟，在浏览器上输入192.168.1.1，若能打开openwrt的管理界面，刷固件搞定！

## 配置openwrt，安装shadowsocks客户端

进入管理界面后先改密码
然后菜单里点network > interface

小米路由mini的话能看到WAN和LAN的选项，点edit完成WAN和LAN的设置，LAN这一块打开DHCP

树莓派的话，你只能看到一个LAN选项，首先点edit，把一套你家网络环境的static IP，包括dns，此时也可以把主路由的IP也还原到你原来的环境了（我做这个步骤的时候，是用我PC直连树莓派设置后再移植到路由器那端的，所以直接wifi设置会不会出现问题不一定，不过就算变砖，重刷一遍diskImage就行了，也就一分钟的事）

接下来安装一些基础环境
```
    opkg update
    opkg install wget ca-certificates ca-bundle
    opkg install iptables-mod-tproxy
    opkg install block-mount e2fsprogs kmod-fs-ext4 kmod-usb-ohci kmod-usb-storage kmod-usb2 kmod-usb3 
    opkg install usbutils
    opkg install nano #习惯用vi的话可以不装nano
```
树莓派的话也要安装一些wifi相关的组件
```
    opkg install wpad-mini
    opkg install kmod-crypto-hash
    opkg install kmod-lib-crc16
```
另外，我的树莓派2B上有一张usb的wifi卡，但上面没有任何标识，我也不清楚需要安装什么样的驱动，解决方法是把该usb卡插在pc端（我是win10），打开device manager，在network adapter里找到该网卡，右键，在detail里选hardware id，里面会出现一组数据，我的是 USB\VID_148F&PID_5370&REV_0101 I
然后去google下这组数据，回馈给我的是Ralink Rt2870，对应openwrt 以下的驱动
```
    opkg install kmod-rt2800-lib kmod-rt2800-usb kmod-rt2x00-lib kmod-rt2x00-usb
```

### 重启
树莓派的话，输入
```
    lsusb
```
看看wifi usb卡是不是已经识别了
```
    ip link list
```
找到该wifi卡的名字，通常是wlan0
最后启动该卡
```
    ifconfig wlan0 up #wlan0 也可能是其他名字，根据ip link list更改
```
### 保险起见，再重启下

到此为止，如果使用小米路由mini的话，官方定制的openwrt路由包预设就已经把网络配置好，充其量在WAN端调整下pppoe还是dhcp，LAN端调整SSID或加密方式，连上小米路由mini应该已经能上网
如果使用树莓派的话，还需要进一步的设置network，我的做法如下
1. Network > Interfaces 点击 Add new interface
1. 命名 Wireless-AP 选择刚安装好的wlan0作为网卡
1. Protocol 选择 Static 
1. submit
1. Edit 新添加的interface，General setup里输入一个全新subnet的IP，我的是 192.168.3.1， subnet是255.255.255.0 其他保持原状不用填
1. 底部确保 DHCP 是enabled，里面的设置很简单没什么需要注意
1. Advance setting里没东西要改
1. Physical setting里，确保bridge interfaces没有选取（没有√），下一行interface选wlan0
1. Firewall setting里套用系统预设的LAN（绿色）
点击Apply and Save
点 Network > Wireless,此时的Radio0应该是disable的状态，点edit配置ssid等，没什么特别需要注意的，mode确保是Access Point，network选取刚才建立的wireless-ap 那个interface,其他根据需求配置，配好后Apply and Save，并点击enable激活。

### 在PC端连上新建的AP，输入192.168.3.1（或你自己另设的Wireless-AP那个interface的IP）

连上后，回到Interfaces主界面，此时应该有两个LAN，把之前那个etho0的LAN删除，这回我们要把树莓派的RJ45接口改成WAN口
1. Network > Interfaces 点击 Add new interface
1. 命名 WAN 并选择eth0作为网卡
1. Protocol 选择static （也可以选dhcp，不过这样一来你的WAN口IP不好控制）
1. submit
1. Edit 新添加的interface WAN, General setup里，如果是dhcp就啥也不用改，如果是static，则输入主路由IP段的信息，gateway 和 dns填写主路由的IP地址
1. 底部DHCP部分，勾选 ignore interface，WAN端不需要dhcp服务
1. Advance setting里没东西要改
1. Physical setting里，确保bridge interfaces没有选取，下一行interface选etho0
1. Firewall setting里套用系统预设的WAN（红色）
点击Apply and Save
完成后重启路由

到此为止，所有为Shadowsocks做的准备工作都已经完成，我们来回顾下整个方案的结构

### 主路由 --->（通过网线）---->小米路由mini/树莓派 ----> 单独的一个Wifi SSID（假设叫做China_Gateway）
之后的目标，是家里其他不需要长期连着假装在国内的设备，连主路由的wifi SSID，家里所有需要长期假装在国内的设备，比如各种国产TV盒子，各种小爱小度精灵啥的智能设备，连新路由China_Gateway
我们接下去的工作也就是把China_Gateway这个路由，配置成一个用来骗过国内服务器检查是否在海外的透明代理

## 配置Shadowsocks之前，我先说下我之前尝试其他解决方案遇到的各种情况
* DNS污染，以爱奇艺为例，海外DNS解析爱奇艺的很多hostname，会被redirect到海外的服务器，此时即使你通过代理把IP地址装成国内的，也于事无补
* 用来检测是否海外链接的hostname不稳定，常常会变，有时候变IP，有时候直接换了个hostname
* 即使国内你有个大带宽的服务器，也无法做到全局代理或者全局转发VPN，原因是国内对国外的gateway常常堵塞

因此我的整体架构思路如下
* DNS全局转发代理，以防万一就不再做国内国外筛选，后遗症是连上该路由的设备，即使在国外，也连不上google了，不过开头已经提到，单连PC或手机的话，直接使用unblock youku或自己架设一个unblock youku的服务更有效
* 通过tcpdump + wireshark，建立一套简易分析工具，每当有新的智能设备或服务需要假装在国内，就run一遍并把检查地域的host给找出来，加入代理列表
* 开源这个列表，通过脚本的方式让路由器自动更新代理规则，最终达到使用openwrt img配置路由+自动更新，极简化这个代理路由的配置流程

### 预备工作
配一个U盘方便扩展和Logging，插入小米路由mini或树莓派的USB接口上
```
    ls -al /dev/sd*
```
找到U盘的路径，比如说是 /dev/sda1
```
    mkfs.ext4 /dev/sda1
    block detect | uci import fstab
    uci set fstab.@mount[0].enabled='1' && uci set fstab.@global[0].check_fs='1' && uci commit
    /sbin/block mount && service fstab enable
```
完成后登陆openwrt管理界面，在 system > mount points 里， mount point表里应该可以找到 \mnt\sda1

接下来安装Shadowsocks客户端的环境
首先请确保之前配置openwrt时的基础环境组件都已经安装好

先获取自己设备的架构码
```
    opkg print-architecture | awk '{print $2}'
```
小米路由mini应该是mipsel_24kc
树莓派2B应该是arm_cortex-a7_neon-vfpv4

添加opkg key
```
    wget http://openwrt-dist.sourceforge.net/openwrt-dist.pub
    opkg-key add openwrt-dist.pub
```

添加自定义源
```
    nano /etc/opkg/customfeeds.conf
```
在文件底部添加两行source链接,mipsel_24kc红色字段更改为之前获取的设备架构码
```
    src/gz openwrt_dist http://openwrt-dist.sourceforge.net/packages/base/<span style="color:red">s**mipsel_24kc** text</span>
    src/gz openwrt_dist_luci http://openwrt-dist.sourceforge.net/packages/luci
```
安装shadowsock client
```
    opkg update
    opkg install shadowsocks-libev
    opkg install luci-app-shadowsocks
```
完成安装后，重新登录openwrt管理界面，在菜单那会多出一个Service，点击里面的Shadowsock

首先点中间的Server Manage
* 点Add新增一个服务器数据
* Alias随便填
* 其他必填的有server address, server port, connection timeout, password 和 encrypted method，根据你最早配置好的国内SS服务器，自行填入
* 完成后点 Save and Apply
另外：如果要开启 TCP Fast Open 选项，需要修改 sysctl.conf 添加一行net.ipv4.tcp_fastopen = 3，然后使之生效。命令如下
```
    echo "net.ipv4.tcp_fastopen = 3" >> /etc/sysctl.conf
    sysctl -p
```
另外2：最好是设置一个域名，建立一个A record对应当前国内Shadowsocks服务器的IP，这样以后换服务器，只要改下A record即可
不过目前openwrt里的luci版本客户端不支持hostname 作为server name，解决方法是写个脚本，来源如下
https://github.com/shadowsocks/luci-app-shadowsocks/wiki/Auto-Update-Servers-IP

然后回到General setting
* Global Setting 不用改
* Transparent Proxy中，Main server选你刚才添加的Server Alias，UDP relay 选同样的那个Alias，Local port随便填一个没用过的，MTU不改变
* UDP Reply需要你的服务器的防火墙或ECS的安全组打开Shadowsocks端口的UDP，光打开TCP是不够的
* Socket5 保持disable 状态
* Port Forward中，Server选刚添加的Alias，port 5300不变，Destination是指转发后使用的国内DNS，因为做全局DNS代理，这里必须填一个国内的DNS，我填的是阿里的223.5.5.5:53，你也可以选一个你偏爱的，比如114.114.114.114:53
* 以上地址中的53是DNS端口，必须填
* 完成后点 Save and Apply

最后那个Access Control目前没东西需要填，不过你可以点进去看看，大致概念是若强制代理有IP记录，则无论如何都会强制代理，Bypass里若有记录，同时该记录并没有出现在强制代理的记录里，则会在代理时忽略，根据整体方案的策略，预设应该是不代理任何地址，直到有强制代理的地址出现。相关这方面的设置我们会使用两个txt文件，之后会有详述。
更详细的配置介绍，可以参考官方链接 https://github.com/shadowsocks/luci-app-shadowsocks/wiki/Use-UCI-system

完成Shadowsocks的设置，去菜单的 Network > DHCP and DNS
* 在General Setting里找 DNS forwardings，预设为空格，我们输入Shadowsocks的端口 127.0.0.1#5300
* 点 Save and Apply
* 再去 Resolv and Host files，找ignore resolv file 并打钩 （以后如果不想要DNS转发的话，就去掉勾，重新填入 /tmp/resolv.conf.auto）
* 点 Save and Apply

SSH 进路由的命令界面
在 /etc/ 里新建两个txt文件，我的叫 bp_list.txt 和 fw_list.txt，分别用于存储 忽略代理列表的IP和强制代理列表的IP
用nano 或 vi打开 bp_list.txt
目前，我们的目标是不代理任何IP地址，但转发127.0.0.1的DNS请求，所以添加忽略记录CIDR的大致逻辑就是全部IP端，但除去127.0.0.0/24段
如果你有一些IP端是永久性需要代理的，因为之后强制代理的txt文件会自动擦除和更新，所以添加在忽略代理列表里更直观些，比方说111.111.111.0/24段需要永远代理，那么我们就生成一个1.0.0.0>111.111.110.255  110.111.112.0>255.255.255.255的CIDR记录，这样111.111.111.0/24就不会被忽略了
https://www.ipaddressguide.com/cidr 这个工具可以进一步帮助你计算IP段

下一步
```
    nano /etc/config/shadowsocks
```
在config access_control下添加一行
```
    option wan_bp_list '/etc/bp_list.txt'
```
保存后，回到浏览器openwrt管理界面，点service > shadowsocks，点access control，你会看到 bypass list栏出现了刚才添加的忽略列表文件
到此为止，该设置的全部设置完成，目前shadowsocks的状态是

### 已经连接到了国内服务器，并开始转发代理所有DNS，但不代理任何IP地址

我们来做个测试确保shadowsocks工作

* 在 Service > Shadowsocks，点access control
* 在 Forwarded IP栏，填入 59.111.181.52
* 点 Save and Apply
* 打开浏览器访问 http://ipservice.163.com/isFromMainland

如果结果是true，删除59.111.181.52后返回false,那么恭喜，服务器设置完成，完美工作

接下来我们就要开始最头痛的日志分析了

## 设备日志分析 (tcpdump + wireshark)

准备工作，安装tcpdump 和 wireshark，并确保winscp工作，U盘工作
