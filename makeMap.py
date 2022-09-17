from pyecharts import options as opts
from pyecharts.charts import Map
from  datetime import date
from pyecharts.globals import ThemeType
 
update_date=date.today()
#放入处理好的数据
province_data=[['甘肃', 1350], ['四川', 5154], ['新疆', 1166], ['海南', 8946], ['台湾', 5930927], ['中国', 6584806], ['北京', 4153], ['山东', 3070], ['黑龙江', 3241], ['河南', 3317], ['广东', 9762], ['青海', 233], ['安徽', 1506], ['福建', 4239], ['内蒙古', 2740], ['辽宁', 1882], ['江苏', 2374], ['江西', 1495], ['天津', 2287], ['湖北', 68427], ['西藏', 1249], ['贵州', 247], ['重庆', 1024], ['湖南', 1450], ['香港', 405061], ['山西', 469], ['陕西', 3720], ['浙江', 3394], ['河北', 2027], ['广西', 2325], ['上海', 63989], ['云南', 2338], ['吉林', 40329], ['澳门', 793], ['宁夏', 122]]
c = (
    Map(init_opts=opts.InitOpts(theme=ThemeType.DARK))
    .add("该省确诊人数",province_data, "china",is_map_symbol_show=False)
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="新型冠状病毒全国疫情地图",
            subtitle="更新日期:{}".format(update_date),
        ),
        
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,  
            min_=0,  # 刻度最小值
            max_=10000
        )
     )
    .render("./新型冠状病毒全国疫情地图.html")
)