# unblock-china-with-shadowsocks-openwrt
之前我一直跟的Unblock Youku解决方案，并不适合长期在线的设备比如小米盒子，百度智能音箱等。
感觉国内本地资源的使用需求越来越复杂，这些设备的Request往往不会出现在Unblock Youku的列表中，与其自己写一个列表，干脆直接做一个更方便的路由系统。
注：如果仅仅为了能让自己的PC或手机获得国内资源，Unblock Youku的解决方案是更优解。

总体概念，通过刷Openwrt固件，安装Shadowsocks client，连接国内本地的Shadowsocks Server，创建自己的国内服务IP列表，最终获得以下功能。  
1. 家里需要直连国内资源的设备链接到Openwrt路由器，既能不被识别为海外IP 
1. 仅仅在检查IP时使用Shadowsocks代理，播放视频流的时候则不走代理，以节省大量的带宽 
1. 路由自动获取IP列表更新，基本做到随插即用

# 前期准备

* 一个能刷Openwrt固件的系统 （我目前尝试了小米路由Mini和树莓派2B）
* 一个U盘 （主要用于搜集监听数据和其他Log，路由器本身的内存太少）
* 一个主路由 （Openwrt路由最终会全部使用国内DNS，为了能让家里那些使用国内资源的设备长期在线，不建议使用同一个路由）
* 一台国内的Shadowsocks Server （我目前尝试了xx云的ECS和家里树莓派4）

