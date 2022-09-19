import json
import re #正则表达式
import os
import pandas as pd
#基础路径
BasePathData ='C:/Users/86187/Desktop/data/'
BasePathExcel='C:/Users/86187/Desktop/Excel/'
#以字符串形式返回对应的文件内容
def getStr(index):
    str=""
    #文件名
    fileName=os.listdir(BasePathData)[index]
    #文件路径
    filepath=BasePathData+fileName
    #读取文件内容
    with open(filepath,"r",encoding='utf-8') as fp:
        str=fp.read()
    return str

provinceNames=["河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","海南","四川","贵州","云南","陕西","甘肃","青海","内蒙古","广西","西藏","宁夏","新疆","北京","天津","上海","重庆"]
provincesLength=len(provinceNames)
def isProvinceHave(str):
    index=0
    result=""
    while index < provincesLength:
        provinceName=provinceNames[index]
        flag=str.find(provinceName)
        #说明该省符合条件
        if(flag!=-1):
            result=provinceName
            break
        index=index+1
    return result
def init():
    provinceList={}
    for province in provinceNames:
        provinceList.update({province:"0"})
    return provinceList

def divideData(province):
    provinceRule=re.compile(r'(.*?)([0-9]+.*)')            
    provinceName=provinceRule.findall(province)[0][0] #省份名称
    provinceNum=provinceRule.findall(province)[0][1]  #对应数量
    provinceItem={provinceName:provinceNum} 
    return provinceItem


def getProvinceData(str):
    provinceList=init()
    index=0
    while index < provincesLength:
        provinceName=provinceNames[index]
        flag=str.find(provinceName)
        #说明该省有疫情
        if(flag!=-1):
            head=flag
            item=""
            #获取省份总数据
            while 1:
                item=item+str[head]
                head=head+1
                if str[head]=='例' :
                    break 
            provinceItem=divideData(item)   
            provinceList.update(provinceItem)
        index=index+1
    return provinceList

def confirmDataOnly(str,nameText):
    #获取病例数
    onlyRule=re.compile(r'新增确诊病例.*?本土.*?(\d+?)例',re.M)
    provinceNum=onlyRule.findall(str)[0]

    provinceList=init()
    #获取省份名称
    provinceName=isProvinceHave(nameText)
    provinceItem={provinceName:provinceNum} 
    provinceList.update(provinceItem)
    return provinceList

def noSymptomDataOnly(str,nameText):
     #获取病例数
    onlyRule=re.compile(r'新增无症状感染者.*?本土.*?(\d+?)例',re.M)
    provinceNum=onlyRule.findall(str)[0]

    provinceList=init()
    #获取省份名称
    provinceName=isProvinceHave(nameText)
    provinceItem={provinceName:provinceNum} 
    provinceList.update(provinceItem)
    return provinceList

def transformJson(data): 
    data=json.dumps(data,ensure_ascii=False)
    return data


def getData(str,date):
    print(date)
    confirmData={}  #存储确诊数据
    noSymptomData={} #存储无状态感染者数据
    DataSum={}
    #通过正则匹配出对应本土新增确诊病例
    confirmRule=re.compile(r'新增确诊病例.*?本土.*?（(.*?)）',re.M)
    confirmText=confirmRule.findall(str)
    print(confirmText)
    if(confirmText==[]):
        confirmData=init()
    else:
        confirmStr=confirmText[0]
        if bool(re.search(r'\d', confirmStr))==False:
            confirmData=confirmDataOnly(str,confirmStr)
        else:
            confirmData=getProvinceData(confirmStr)

    #通过正则匹配出对应本土新增无症状感染者
    noSymptomRule=re.compile(r'新增无症状感染者.*?本土.*?（(.*?)）',re.M)
    noSymptomText=noSymptomRule.findall(str)
    if noSymptomText==[]:
        noSymptomData=init()
    else:
        noSymptomStr=noSymptomText[0]
        if bool(re.search(r'\d', noSymptomStr))==False:
            noSymptomData=noSymptomDataOnly(str,noSymptomStr)
        else:
            noSymptomData=getProvinceData(noSymptomStr)

    DataSum.update({"确诊病例":confirmData})
    DataSum.update({"无症状感染者":noSymptomData})
    DataSum=transformJson(DataSum)
    df=pd.read_json(DataSum,orient='index',encoding='utf-8')
    df.to_excel(BasePathExcel+date+'.xlsx')
    
    
def dataProcess():
    
    length=len(os.listdir(BasePathData))
    index=length-1
    while index>=0:
        txtName=os.listdir(BasePathData)[index]
        dateRule=re.compile(r'.*?(\d+月\d+日)')
        date=dateRule.findall(txtName)[0]
    
        getData(getStr(index),date)
        index=index-1
dataProcess()
