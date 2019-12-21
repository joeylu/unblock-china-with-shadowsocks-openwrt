# unblock-china-with-shadowsocks-openwrt
为了能够让海外华人获得中国本地的影视等资源，而不会因为地区关系被封锁 之前我一直跟的Unblock Youku解决方案，感觉因为国内本地资源的使用需求越来越复杂，Unblock Youku的url.js表已经无法满足使用需求，比方说，新入的百度智能音箱，就会出现很多音乐和广播资源因为海外IP的关系被封锁，而这些Request往往不会出现在Unblock Youku的列表中，与其自己写一个列表，干脆直接做一个更方便的路由系统。 

总体概念，通过刷Openwrt固件，安装Shadowsocks client，连接国内本地的Shadowsocks Server，创建自己的国内服务IP列表，最终获得以下功能。  
1. 家里需要直连国内资源的设备链接到Openwrt路由器，既能不被识别为海外IP 
2. 仅仅在检查IP时使用Shadowsocks代理，播放视频流的时候则不走代理，以节省大量的带宽 
3. 路由自动获取IP列表更新，基本做到随插即用
