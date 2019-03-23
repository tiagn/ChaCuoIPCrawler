# 查错 IT 网 IP 工具页面数据的抓取

查错 IT 网 IP 工具页面包含了一些有用的数据，并且作者每天更新，保证了数据的准确和及时更新，非常推荐使用者访问。

关于 IP 的相关数据非常多，如果手动下载确实麻烦，此项目是将下载相关数据自动化。

## 用法

```python
>>> from crawler import Crawler
>>> crawler = Crawler()
>>> crawler.click("http://ipblock.chacuo.net/view/c_BL")
{'clickable': {'ip_range': 'http://ipblock.chacuo.net/down/t_txt=c_BL'}, 'info': {'update_time': '2019-03-23', 'global_count': '3,618,114,107', 'count': '256', 'percent': '0.00%', 'global_list': '238', 'url': 'http://ipblock.chacuo.net/down/t_txt=c_BL'}}
>>> crawler.click("ip_range")   # click 可以直接使用 clickable 里的 key 或 value
{'clickable': {}, 'info': {'ip_range': ['192.131.134.0-192.131.134.255']}}
>>> crawler.click("http://ipblock.chacuo.net/down/t_txt=c_BL")
{'clickable': {}, 'info': {'ip_range': ['192.131.134.0-192.131.134.255']}}
>>> 
```
说明
1. 查错 IT 网 IP 工具相关页面都可以直接用 click 来获取信息
2. 结果里 clickable 代表的是可调用 click 方法的链接信息；
3. 结果里 info 是相关数据


## 获取数据

通过简单的代码组合可以实现批量获取数据

crawler 里已经实现了以下功能，可以直接使用：
1. 获取所有国家的IP段并保存为国家名称为单位的文件
2. 获取国内运营商的IP段并保存为运营商名称为单位的文件
3. 获取国内省份IP段并保存为省份为单位的文件
4. 获取全球网络公司IP段并保存为网络公司为单位的文件
5. 获取全球网络公司 as 并保存为网络公司为单位的文件
6. 获取所有国家的as并保存为国家名称为单位的文件
7. 根据国家获取国家as的IP段并保存为as名称为单位的文件, 如果下载美国这种大量as数据请检查系统是否支持
