from asyncio import tasks
import os
#异步IO
import asyncio
from pyppeteer import launcher
# 在导入 launch 之前 把 --enable-automation 禁用 防止监测webdriver
launcher.DEFAULT_ARGS.remove("--enable-automation")

from pyppeteer import launch
from bs4 import BeautifulSoup

BasePathData ='./data/'
if not os.path.exists(BasePathData):
        os.makedirs(BasePathData) 
#将pyppeteer的操作封装成fetchUrl函数，用于发起网络请求，获取网页源码
async def pyppteer_fetchUrl(url):
    #设置浏览器驱动
    #-headless 无头浏览器模式
    #-dumpio 解决chromium浏览器多开页面卡死问题
    #-autoClose 脚本完成时自动关闭浏览器进程
    browser = await launch({'headless': False,'dumpio':True, 'autoClose':True})
    page = await browser.newPage()
    await page.goto(url)
    await asyncio.wait([page.waitForNavigation()])
    str =await page.content()
    #关闭驱动
    await browser.close()
    return str

def fetchUrl(url):
    return asyncio.get_event_loop().run_until_complete(pyppteer_fetchUrl(url))

#通过 getPageUrl 函数构造每一页的 URL 链接
def getPageUrl(head,tail):
    #如果只爬取一页
    if head==tail:
        if(head!=1):
            url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_'+ str(head) +'.shtml'
        else:
            url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
        yield url 
    #爬取多页
    for page in range(head,tail):
        if page == 1:
            yield 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
        else:
            url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_'+ str(page) +'.shtml'
            yield url

#通过 getTitleUrl 函数，获取某一页的文章列表中的每一篇文章的标题，链接，和发布日期。
def getTitleUrl(html):
    #创建BeautifulSoup对象
    bsobj = BeautifulSoup(html,'html.parser')
    #找到存放二级目录的li
    titleList = bsobj.find('div', attrs={"class":"list"}).ul.find_all("li")
    for item in titleList:
        #补全链接
        link = "http://www.nhc.gov.cn" + item.a["href"]
        #获取标题
        title = item.a["title"]
        #获取发布时间
        date = item.span.text
        #返回数据
        yield title, link,date

#返回文章内容
def getContent(html):
    #创建BeautifulSoup对象      
    bsObj = BeautifulSoup(html,'html.parser')
    #找到存放文章内容的全部P标签
    Plist = bsObj.find('div', attrs={"id":"xw_box"}).find_all("p")
    str = ""
    if Plist:
        for item in Plist:
            str += item.text
        return str

    return "爬取失败！"

#存储文件
def saveFile(path, filename, content):
    #如果没有文件夹先创建
    if not os.path.exists(path):
        os.makedirs(path)  
    # 保存文件
    with open(path + filename + ".txt", 'w', encoding='utf-8') as f:
        f.write(content)

#主函数运行爬取
def webFetch():
    print("请输入起始页码")
    head=int(input())
    print("请输入结束页码")
    tail=int(input())
    for url in getPageUrl(head,tail):
        s =fetchUrl(url)
        for title,link,date in getTitleUrl(s):
            html =fetchUrl(link)
            content = getContent(html)
            print(content)
            saveFile(BasePathData, date+'-'+title, content)
if "__main__" == __name__: 
    webFetch()    
