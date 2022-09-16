import random #随机数
import requests #请求
import re #正则
import json #JSON
from lxml import etree #Xpath
from time import sleep #sleep函数
from fake_useragent import UserAgent #随机UA伪装
import pandas as pd #JSON转换Excel函数库

#UA伪装函数
#返回值：headers
def getHeaders():
    ua = UserAgent()
    headers = {
         'User-Agent': ua.random
    }
    return headers

def getProvinceData(date_list,href_list):   
    provinceData={}
    index=0
    length=len(href_list)
    while index < length:
        #获取页面数据
        headers=getHeaders()
        response=requests.get(url=href_list[index],headers=headers)
        if response.status_code != 200:
            sleep(random.uniform(1.1,5.4))
            continue
        print('获取数据成功')

        #防止中文乱码
        response.encoding = response.apparent_encoding
        page_text=response.text
        
        #通过xpath获取页面主要内容
        tree=etree.HTML(page_text)
        text=tree.xpath('//div[@class="con"]/p//text()')
        #将获取的文章内容化成字符串
        texts="".join(text)

        #通过正则匹配出各省本土病例
        localRule=re.compile(r'本土.*?（(.*?)）',re.M)
        localData=localRule.findall(texts)
        provinceDataItem=getLocalInfected(localData[0],date_list[index])
        provinceData.update(provinceDataItem)
        index=index+1
    #将数据存储为JSON格式数据
    with open('./province.json','w',encoding="utf-8") as fp:
        json.dump(provinceData,fp,ensure_ascii=False)    

def getLocalInfected(localData,date):
    #通过逗号划分各省病例
    provinces=localData.split('，')
    provinceList={}
    for province in provinces:
        provinceRule=re.compile(r'(.*?)([0-9]+.*)')            
        provinceName=provinceRule.findall(province)[0][0] #省份名称
        provinceNum=provinceRule.findall(province)[0][1]  #对应数量
        provinceItem={provinceName:provinceNum}   
        provinceList.update(provinceItem) 
    provinceDataItem={date:provinceList}
    return provinceDataItem   
    
def main():
    #step1：指定所爬取的总列表的url
    url="http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml"

    #step2：获取响应数据
    headers=getHeaders()
    response=requests.get(url=url,headers=headers)
    #防止中文乱码
    response.encoding='utf-8'
    mainPage_text=response.text

    #step3：数据处理
    #step3.1 通过xpath获取对应链接所在li
    tree=etree.HTML(mainPage_text)
    li_list=tree.xpath("//ul/li")
    
    #step3.2获取每日对应的通报的href
    date_list=[]
    href_list=[]
    for li in li_list:
        date=li.xpath('./span[@class="ml"]/text()')
        href="http://www.nhc.gov.cn"+li.xpath("./a/@href")[0]
        date_list.append(date[0])
        href_list.append(href)
    
    #将JSON格式文件转换为Excel
    df=pd.read_json('province.json',orient='index',encoding='utf-8') 
    df.to_excel('本土每日新增1.xlsx')

    # if len(href_list)!=0:
    #     print('获取href成功\n')
    #     getProvinceData(date_list,href_list)
   
        

if __name__ ==  "__main__" :
    main()
        

