# 295. 数据流的中位数

难度：HARD · 分类：堆

## 题意与接口

数据流持续加入整数，随时查询当前中位数。类`MedianFinder`提供`addNum(num)`和`findMedian()`；题设查询前至少加入一个数。

## 从朴素方法到优化

每次加入后重新排序代价高；有序数组插入仍O(n)。只需要最大左半和最小右半，两个堆足以维护分界。

## 核心思路

lower用负数模拟大根堆，upper用小根堆。先把新值压入lower，再把lower最大值送到upper，最后若upper人数更多就移回其最小值。保证lower比upper多0或1个且左值≤右值。

## 手推一个小例子

加入6：lower={6},upper={}，中位数6。加入2：lower={2},upper={6}，中位数4。加入9：lower={2,6},upper={9}，中位数6。

## 为什么正确

把lower最大值送到upper修复两堆顺序；若upper过大，再把upper最小值移回lower不会打破顺序。平衡后奇数时lower多一个，根就是中位数；偶数时两根是中央两项。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0295_find_median_from_data_stream.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lower = []  # 存负数，根的相反数为左半最大值
        self.upper = []

    def addNum(self, num: int) -> None:
        # 先修复两堆数值顺序，再修复人数差。
        heapq.heappush(self.lower, -num)
        heapq.heappush(self.upper, -heapq.heappop(self.lower))
        if len(self.upper) > len(self.lower):
            heapq.heappush(self.lower, -heapq.heappop(self.upper))

    def findMedian(self) -> float:
        if not self.lower:
            raise ValueError("no values added")
        if len(self.lower) > len(self.upper):
            return float(-self.lower[0])
        return (-self.lower[0] + self.upper[0]) / 2
```

## 复杂度

已有n项时，addNum均摊O(log(n+1))，findMedian为O(1)，存储O(n)。这里按CPython常见动态列表模型计算：heapq先向底层列表追加再调整堆，堆操作中的尾部pop也可能缩容；单次扩缩容可能搬移O(n)项，不承诺每次插入严格对数时间。没有假定堆内所有元素有序。这里的容器复杂度按CPython动态列表与heapq的组合计算。

## 边界与易错点

- 左堆存负数，跨堆移动必须变号。
- 两堆大小只能相等或左多1个，奇偶中位数规则与此约定绑定。
- 重复值、负数都按普通数值处理，不能用集合保存。

## 本地测试与复习

测试奇偶、负数、重复；随机每次add后与statistics.median比较，并检查两堆大小与边界顺序。

复习：若还要求删除任意旧元素，为什么标准堆不能直接维持同样简单接口？

答案核对：标准堆只能高效取根，不支持由任意值直接定位并删除对应项；列表搜索会花O(n)。可用带索引的堆，或延迟删除计数并在根失效时清理，同时维护有效大小；重复值、堆归属和重平衡都要另设不变量。

<a id="官方追问一所有值都在0100"></a>

### 追问一：所有值都在[0,100]

维护101个频次和总数n即可。按一基排名取`r1=(n+1)//2`与`r2=(n+2)//2`；奇数时二者相同，偶数时取这两项的平均。累加频次到首次不少于r的位置，该位置就是第r小的值。插入O(1)，精确查询O(101)，固定101个频次槽。这里“固定空间”按主题有界整数/机器字模型计算；无限长流的计数器位数另算。

例子：频次只有0出现2次、100出现2次，n=4，排名2和3分别为0、100，中位数50。实现`BoundedMedianFinder`对带外输入报ValueError，不截断数值。

<a id="官方追问二99的值在0100"></a>

### 追问二：99%的值在[0,100]

先说明99%保证对哪些查询成立。设b为小于0的数量，a为大于100的数量，m为带内数量。若**每次查询的数据集**均满足`100*m >= 99*n`，则b、a都不超过0.01n，小于中央排名距两端的距离；两个中央排名必在带内。因此只保存101个频次、b和a，无需保存每个离群值。带内查找的排名为`r1-b`与`r2-b`，不能忽略低端离群值造成的偏移。

例如`[-1] + [0]*49 + [100]*50`共有100项，99%在带内；中央全局排名50、51，减去b=1后变成带内排名49、50，分别得到0与100，中位数50。即使99%条件不成立，只要两个中央排名都在带内，计数仍可给出精确结果；如`[-5,0,100,200]`也是50。实现`BandCountMedianFinder`检查所需排名，带外中央项会报ValueError，绝不夹到0或100，也不输出近似值。

若99%只描述**完成后的整个流**，却允许查询任意初始前缀，就不能丢掉离群值。例子`[-999,999] + [50]*198`在完成时满足99%，但第一项中位数为−999，前两项中位数为0；计数而不保留数值的结构无法回答这两个查询。只存低端数量也无法区分前缀`[-999]`与`[-1]`，虽然后面都可补带内数使最终达到99%。

`ExactPrefixMedianFinder`保留低端与高端的有序离群值列表，并按全局排名分别从低端、频次表或高端精确选择。设当前离群值有k个：带内插入O(1)，这个便于核对的列表版本带外插入O(k+1)，查询O(101)，空间O(101+k)。若改用支持排名选择的平衡树，可优化离群插入/查询；不能把本列表版本误称为对数插入。99%只在结束时成立时，中间k可能等于整个前缀长度。

这三种[可运行实现](../../../examples/hot100/followup_algorithms.py)均沿用主题整数范围−100000至100000，查询前须非空；主类`MedianFinder`及其双堆代码不变。[独立测试](../../../examples/hot100/test_followup_algorithms.py)覆盖带内有限穷举、19,607个混合带内/离群流的每个前缀、中央排名偏移、最终99%但早期带外的情形。根目录运行`python -B -m unittest examples.hot100.test_followup_algorithms -v`。保证作用范围与排名论证在上述解析中明确。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：在每次插入后检查堆的大小差和跨堆顺序，手推奇数与偶数数量时的中位数。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
