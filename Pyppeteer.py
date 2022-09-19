from asyncio import tasks
import os
#异步IO
import asyncio
from pyppeteer import launcher
# 在导入 launch 之前 把 --enable-automation 禁用 防止监测webdriver
launcher.DEFAULT_ARGS.remove("--enable-automation")

from pyppeteer import launch
from bs4 import BeautifulSoup


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
    for page in range(head,tail):
        if page == 1:
            yield 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
        else:
            url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_'+ str(page) +'.shtml'
            yield url

#通过 getTitleUrl 函数，获取某一页的文章列表中的每一篇文章的标题，链接，和发布日期。
def getTitleUrl(html):
    bsobj = BeautifulSoup(html,'html.parser')
    titleList = bsobj.find('div', attrs={"class":"list"}).ul.find_all("li")
    for item in titleList:
        link = "http://www.nhc.gov.cn" + item.a["href"]
        title = item.a["title"]
        date = item.span.text
        yield title, link, date

#返回文章内容
def getContent(html):      
    bsobj = BeautifulSoup(html,'html.parser')
    cnt = bsobj.find('div', attrs={"id":"xw_box"}).find_all("p")
    s = ""
    if cnt:
        for item in cnt:
            s += item.text
        return s

    return "爬取失败！"

#存储文件
def saveFile(path, filename, content):
    if not os.path.exists(path):
        os.makedirs(path)  
    # 保存文件
    with open(path + filename + ".txt", 'w', encoding='utf-8') as f:
        f.write(content)

if "__main__" == __name__: 
    print("请输入起始页码")
    head=int(input())
    print("请输入结束页码")
    tail=int(input())
    for url in getPageUrl(head,tail):
        s =fetchUrl(url)
        for title,link,date in getTitleUrl(s):
            print(title,link)
            
            mon = int(date.split("-")[1])
            day = int(date.split("-")[2])
            if mon <= 1 and day <= 1: 
                break
            html =fetchUrl(link)
            content = getContent(html)
            print(content)
            saveFile("C:/Users/86187/Desktop/data/", title, content)
