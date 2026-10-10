# 394. 字符串解码

[官方题目](https://leetcode.cn/problems/decode-string/) · MEDIUM · 官方分类：栈

## 题意与接口

解码嵌套重复表达式，k[片段]表示把片段重复k次。`decodeString(s)`返回解码字符串；输入保证编码合法，数字只作重复次数。

## 从朴素方法到优化

直接递归按括号解析很自然，但深嵌套受Python递归深度限制。显式栈保存进入一层括号前的文本片段和次数，可以迭代解析。

## 核心思路

数字可能多位，要逐位累加；遇[时保存(当前片段列表,次数)并进入空子层；遇]时把子层join后重复、附回父层；普通字母追加到当前片段列表。

## 手推一个小例子

"2[a3[b]]"：2[保存外层和次数2；读a后3[保存[a]和3；读b遇]得到bbb并回到[a,bbb]；再遇]得到abbbabbb。

## 为什么正确

栈帧完整保存暂停的外层状态。每个]对应最近未关闭的[，此时子层文本已完整解码，重复指定次数并拼回父层恰符合语法定义。由内向外处理最终得到完整解码结果。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0394_decode_string.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def decodeString(self, s: str) -> str:
        stack = []
        parts = []
        repeat = 0
        for ch in s:
            if ch.isdigit():
                repeat = repeat * 10 + int(ch)
            # 遇到左括号，暂停并保存外层上下文。
            elif ch == '[':
                stack.append((parts, repeat))
                parts, repeat = [], 0
            elif ch == ']':
                block = ''.join(parts)
                parent, count = stack.pop()
                parent.append(block * count)
                parts = parent
            else:
                parts.append(ch)
        return ''.join(parts)
```

## 复杂度

设输入长n，最终输出长L，最大嵌套深度d。构造字符串的精确成本与各层展开中间文本总长C有关，时间O(n+C)，保守上界O(n+dL)，不能一概声称O(n)。峰值空间O(n+L+d)，包含片段、栈与结果。

## 边界与易错点

- 重复次数可能是12等多位数，不能只读一个数字。
- 进入新层要重置repeat与parts，离开层后恢复对应父层。
- 输出可能远大于输入；题设限制解码长度，但一般服务需要防止解压炸弹。

## 本地测试与复习

测试嵌套、多位次数、字母前后缀；随机生成浅层合法编码，与递归语法解析器对拍；额外测深嵌套避免RecursionError。

复习：为何字符串反复+=可能增加复制成本？为什么最终长度L不足以描述所有嵌套中间复制？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/decode-string/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0300-0399/0394.Decode%20String/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：用嵌套编码与多位重复数检查上下文栈，说明什么时候保存和恢复当前字符串。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
