import socket
import os
import textwrap

urls = [
    "data.video.iqiyi.com", 
    "data.video.qiyi.com",
    "www.iqiyi.com",
    "control-i.iqiyi.com",
    "qiqu.iqiyi.com",
    "search.video.iqiyi.com",
    "pub.m.iqiyi.com",
    "cache.video.iqiyi.com",
    "cache.video.qiyi.com",
    "cache.vip.iqiyi.com",
    "cache.vip.qiyi.com",
    "api.vip.iqiyi.com",
    "qosp.iqiyi.com",
    "iface.iqiyi.com",
    "iface2.iqiyi.com",
    "iplocation.geo.qiyi.com",
    "iplocation.geo.iqiyi.com"
]

#get current records in file
records = set(line.strip() for line in open('hostname.txt'))
newRecords = set()
#init indent for easier copy paste in ssh
wrapper = textwrap.TextWrapper(initial_indent='\t', subsequent_indent='\t')

#get turble from given hostnames
for url in urls:        
    try:
        name, aliases, addresses = socket.gethostbyname_ex(url)
        #check the ip is not existed in file, then add       
        for ip in addresses:
            newRecords.add(ip)
    except:
        print(url + " not get resolved")
#remove duplicates (convert dict to auto remove)
newRecords = list(dict.fromkeys(newRecords))
#write (sort list while looping)
with open('hostname.txt', 'w') as file:
    for record in sorted(newRecords):
        wrapped = wrapper.fill("list wan_fw_ips")
        file.write(wrapped + " '" + record + "'" +'\n')

    
                    
