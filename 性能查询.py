import pstats
from pstats import SortKey

# 加载保存到restats文件中的性能数据
p = pstats.Stats('restats')

# 打印所有统计信息
p.sort_stats(SortKey.CUMULATIVE).print_stats(10)
