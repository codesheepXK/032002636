from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Bar, Page, Map, Pie
from pyecharts.faker import Faker
import pandas as pd


#放入处理好的数据
date="9月16日"
province_data=[['甘肃', 1350], ['四川', 5154], ['新疆', 1166], ['海南', 8946], ['台湾', 5930927], ['北京', 4153], ['山东', 3070], ['黑龙江', 3241], ['河南', 3317], ['广东', 9762], ['青海', 233], ['安徽', 1506], ['福建', 4239], ['内蒙古', 2740], ['辽宁', 1882], ['江苏', 2374], ['江西', 1495], ['天津', 2287], ['湖北', 68427], ['西藏', 1249], ['贵州', 247], ['重庆', 1024], ['湖南', 1450], ['香港', 405061], ['山西', 469], ['陕西', 3720], ['浙江', 3394], ['河北', 2027], ['广西', 2325], ['上海', 63989], ['云南', 2338], ['吉林', 40329], ['澳门', 793], ['宁夏', 122]]
provinceNames=["河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","海南","四川","贵州","云南","陕西","甘肃","青海","内蒙古","广西","西藏","宁夏","新疆","北京","天津","上海","重庆"]
allData=pd.read_excel('C:/Users/86187/Desktop/Excel/'+date+'.xlsx', index_col=None)
confirmData=[]
noSymptomData=[]
infectConfirmProvince=[]
infectConfirmData=[]
infectNoSymptomProvince=[]
infectNoSymptomData=[]
def getProvinceData():
    length=len(provinceNames)
    index=0
    while index < length:
        confirmData.append(allData.values[0][index+1])
        noSymptomData.append(allData.values[1][index+1])
        if(confirmData[index]!=0):
            infectConfirmProvince.append(provinceNames[index])
            infectConfirmData.append(confirmData[index])
        if(noSymptomData[index]!=0):
            infectNoSymptomProvince.append(provinceNames[index])
            infectNoSymptomData.append(noSymptomData[index])
        index=index+1
def makeZip(x_data, y_data):
    data_pair = [list(z) for z in zip(x_data, y_data)]
    return data_pair
getProvinceData()
confirmDataPair=makeZip(infectConfirmProvince,infectConfirmData)
confirmDataPair.sort(key=lambda x: x[1])
noSymptomDataPair=makeZip(infectNoSymptomProvince,infectNoSymptomData)
noSymptomDataPair.sort(key=lambda x: x[1])

def makePie(dataPair,name) -> Pie:
    c = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK)) 
        .add(
            name,
            data_pair= dataPair,
            radius=["50%", "70%"],
            center=["50%", "50%"],
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=name),
            legend_opts=opts.LegendOpts(pos_left="right", orient="vertical")
        )
        .set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"
            ),
            label_opts=opts.LabelOpts(formatter="{b}: {c}")
        )

    )
    return c
# 条形图
def makeBar() -> Bar:
    c = (
        
        Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add_xaxis(provinceNames)
        .add_yaxis("确诊病例", confirmData)
        .add_yaxis("无症状感染者", noSymptomData)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=date+"本土各省新增确诊病例"),
            datazoom_opts=[opts.DataZoomOpts()],
        )
    )
    return c
#中国地图
def makeMap() -> Map:  
    c = (
        Map(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add("该省确诊人数",province_data, "china",is_map_symbol_show=False)
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="新型冠状病毒全国疫情地图",
            ),
            
            visualmap_opts=opts.VisualMapOpts(
                is_show=True,  
                min_=0,  # 刻度最小值
                max_=10000
            )
        )
    )
    return c

def page_simple_layout():
    page = Page(layout=Page.DraggablePageLayout)  
    # 将上面定义好的图添加到 page
    page.add(
        makeMap(),
        makeBar(),
        makePie(confirmDataPair,"新增确诊病例占比")
    )
    #第二次使用这个更新排版布局
    page.save_resize_html(
        "page_simple_layout.html", 
	    cfg_file="chart_config.json",
 	    dest="my_test.html"
    )

    #第一次使用这个先设置可移动布局获取配置后使用上面函数
    # page.render("page_simple_layout.html")
if __name__ == "__main__":
    page_simple_layout()
