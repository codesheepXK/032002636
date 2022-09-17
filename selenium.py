
from time import sleep
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from lxml import etree #Xpath
from fake_useragent import UserAgent
import json
import random
import re
import io
import sys
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
pageNum=4
service=Service("D:\python\MicrosoftWebDriver.exe")
#配置selenium
def setOptions():
    ua=UserAgent()
    uA=ua.random
    edge_options = webdriver.EdgeOptions() 
    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    edge_options.add_argument('--disable-blink-features=AutomationControlled')
    edge_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    edge_options.add_argument('--headless')
    edge_options.add_argument('lang=zh_CN.UTF-8')
    edge_options.add_argument('User-Agent='+uA)
    return edge_options
options=setOptions()

def init():
    provinceList={}
    provinces=["河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","海南","四川","贵州","云南","陕西","甘肃","青海","内蒙古","广西","西藏","宁夏","新疆","北京","天津","上海","重庆"]
    for province in provinces:
        provinceList.update({province:""})
    return provinceList

def getProvinceAllData(date_list,href_list):   
    ConfirmData={}
    NoSymptomData={}
    index=0
    length=len(href_list)
    while index < length:
        #获取页面数据
        browser = webdriver.Edge(service=service,options=options) 
        browser.get(url=href_list[index])
        browser.implicitly_wait(8)
        page_source=browser.page_source
        if page_source=='<html><head></head><body></body></html>':
            print('获取失败page_source')
            sleep(5)
            browser.close()
            continue
            
        #通过xpath获取页面主要内容
        tree=etree.HTML(page_source)
        text=tree.xpath('//div[@class="con"]/p//text()')
        #将获取的文章内容化成字符串
        texts="".join(text)
        if(texts==''):
            print('获取失败text')
            browser.close()
            continue
        #通过正则匹配出本土各省新增确诊病例
        confirmRule=re.compile(r'新增确诊病例.*?本土.*?（(.*?)）',re.M)
        dealingData1=confirmRule.findall(texts)
        if len(dealingData1[0])<4:
            print(date_list[index])
            index=index+1
            continue
        ConfirmDateItem=getProvinceData(dealingData1[0],date_list[index])
        ConfirmData.update(ConfirmDateItem)

        #通过正则匹配出本土各省新增无症状感染者
        noSymptomRule=re.compile(r'新增无症状感染者.*?本土.*?（(.*?)）',re.M)
        dealingData2=noSymptomRule.findall(texts)
        NoSymptomDataItem=getProvinceData(dealingData2[0],date_list[index])
        NoSymptomData.update(NoSymptomDataItem)
        #关闭browser
        browser.quit()
        index=index+1
    #将数据存储为JSON格式数据
    with open('./各省每日新增确诊病例JSON/各省每日确诊病例4.json','w',encoding="utf-8") as fp:
        json.dump(ConfirmData,fp,ensure_ascii=False) 
    with open('./各省每日新增无症状感染者JSON/各省每日新增无症状感染者4.json','w',encoding="utf-8") as fp:
        json.dump(NoSymptomData,fp,ensure_ascii=False)  
     

def getProvinceData(dealingData,date):
    #通过逗号划分各省病例
    provinces=dealingData.split('，')
    provinceList=init()
    for province in provinces:
        provinceRule=re.compile(r'(.*?)([0-9]+.*)')            
        provinceName=provinceRule.findall(province)[0][0] #省份名称
        provinceNum=provinceRule.findall(province)[0][1]  #对应数量
        provinceItem={provinceName:provinceNum}   
        provinceList.update(provinceItem) 
    provinceDataItem={date:provinceList}
    return provinceDataItem   



def main():

    df=pd.read_json(path_or_buf='./各省每日新增无症状感染者JSON/各省每日新增确诊病例1.json',orient='index',encoding='utf-8')
    df.to_excel(path='./各省每日新增确诊病例EXCEL/各省每日新增确诊病例1.xlsx')

    browser = webdriver.Edge(service=service,options=options) 
    if pageNum==1:
        page=""
    else: 
        page='_'+str(pageNum)   
    url='http://www.nhc.gov.cn/xcs/yqtb/list_gzbd'+page+'.shtml'
    browser.get(url=url)
    browser.implicitly_wait(8)
    page_source=browser.page_source
    
    tree=etree.HTML(page_source)
    li_list=tree.xpath("//ul/li")

    date_list=[]
    href_list=[]
    for li in li_list:
        date=li.xpath('./span[@class="ml"]/text()')[0]
        date=date+'-0时'
        href="http://www.nhc.gov.cn"+li.xpath("./a/@href")[0]
        date_list.append(date)
        href_list.append(href)

    if len(href_list)!=0:
        print('获取href成功\n')
        getProvinceAllData(date_list,href_list)

    browser.quit() 

if __name__ == '__main__':
    main()
   
