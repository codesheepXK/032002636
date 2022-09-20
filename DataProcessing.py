import json
import re #正则表达式
import os
import pandas as pd
import cProfile
#基础路径
BasePathData ='./data/'
BasePathExcel='./excel/'
if not os.path.exists(BasePathData):
        os.makedirs(BasePathData) 
if not os.path.exists(BasePathExcel):
        os.makedirs(BasePathExcel)   
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
#省份名称列表
provinceNames=["河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","海南","四川","贵州","云南","陕西","甘肃","青海","内蒙古","广西","西藏","宁夏","新疆","北京","天津","上海","重庆"]
provincesLength=len(provinceNames)
HotData=[]
#判断传入的字符串是否含有一个省份名称，如果有就返回该省份名称
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

#省份数据初始化
def init():
    provinceList={}
    for province in provinceNames:
        provinceList.update({province:"0"})
    return provinceList

#将例如：北京12例的字符串分开为{"北京"："12"}返回
def divideData(province):
    provinceRule=re.compile(r'(.*?)([0-9]+.*)')            
    provinceName=provinceRule.findall(province)[0][0] #省份名称
    provinceNum=provinceRule.findall(province)[0][1]  #对应数量
    provinceItem={provinceName:provinceNum} 
    return provinceItem

#循环获取各省份疫情数据
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

#用于特例比如：本土疫情1例（在广东）只有一个省份发生疫情的确诊病例数据提取
def confirmDataOnly(str,nameText):
    #获取病例数
    onlyRule=re.compile(r'新增确诊病例.*?本土.*?(\d+?)例',re.M) #正则
    provinceNum=onlyRule.findall(str)[0]

    #数据初始化
    provinceList=init()
    #获取有疫情的省份名称
    provinceName=isProvinceHave(nameText)
    provinceItem={provinceName:provinceNum} 
    provinceList.update(provinceItem)
    return provinceList

#用于特例比如：本土疫情1例（在广东）只有一个省份发生疫情的无症状感染者数据提取
def noSymptomDataOnly(str,nameText):
     #获取病例数
    onlyRule=re.compile(r'新增无症状感染者.*?本土.*?(\d+?)例',re.M) #正则
    provinceNum=onlyRule.findall(str)[0]

    provinceList=init()
    #获取省份名称
    provinceName=isProvinceHave(nameText)
    provinceItem={provinceName:provinceNum} 
    provinceList.update(provinceItem)
    return provinceList

#将传入数据转换为JSON格式
def transformJson(data): 
    data=json.dumps(data,ensure_ascii=False)
    return data

#获取传入文章数据中各省份的疫情数据函数
def getData(str,txtName):
    confirmData={}  #存储确诊数据
    noSymptomData={} #存储无状态感染者数据
    DataSum={}
    #通过正则匹配出对应本土新增确诊病例
    confirmRule=re.compile(r'新增确诊病例.*?本土.*?（(.*?)）',re.M)
    confirmText=confirmRule.findall(str)
    #如果没有发送疫情那么返回值confirmText为[]
    if(confirmText==[]):
        confirmData=init()
    #说明有返回值存在疫情数据
    else:
        confirmStr=confirmText[0]
        #判断是否比如：本土疫情1例（在广东）只有一个省份发生疫情的特例
        if bool(re.search(r'\d', confirmStr))==False:
            confirmData=confirmDataOnly(str,confirmStr)
        else:
            confirmData=getProvinceData(confirmStr)

    #通过正则匹配出对应本土新增无症状感染者，格式同上
    noSymptomRule=re.compile(r'新增无症状感染者.*?本土.*?（(.*?)）',re.M)
    #如果没有发送疫情那么返回值noSymptomText为[]
    noSymptomText=noSymptomRule.findall(str)
    #说明有返回值存在疫情数据
    if noSymptomText==[]:
        noSymptomData=init()
    else:
        noSymptomStr=noSymptomText[0]
        #判断特例
        if bool(re.search(r'\d', noSymptomStr))==False:
            noSymptomData=noSymptomDataOnly(str,noSymptomStr)
        else:
            noSymptomData=getProvinceData(noSymptomStr)

    #汇总数据
    DataSum.update({"确诊病例":confirmData})
    DataSum.update({"无症状感染者":noSymptomData})
    #将汇总数据转换为JSON格式
    DataSum=transformJson(DataSum)
    #利用pandas模块将每日汇总数据转变为EXCEL
    df=pd.read_json(DataSum,orient='index',encoding='utf-8')
    df.to_excel(BasePathExcel+txtName+'.xlsx')
    
#循环读取所爬取的文章内容进行数据处理
def dataProcess():
    length=len(os.listdir(BasePathData))
    index=length-1
    while index>=0:
        #获取时间date
        txtName=os.listdir(BasePathData)[index]
        txtName=txtName.split('.')[0]

        #获取该日数据
        getData(getStr(index),txtName)
        index=index-1
#正常调用
dataProcess()
        
#用于生成性能分析信息
# cProfile.run('dataProcess()','restats')

