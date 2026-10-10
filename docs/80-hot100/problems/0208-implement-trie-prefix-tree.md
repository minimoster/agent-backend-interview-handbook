# 208. 实现 Trie (前缀树)

[官方题目](https://leetcode.cn/problems/implement-trie-prefix-tree/) · MEDIUM · 官方分类：图论

## 题意与接口

实现前缀树 `Trie()`、`insert(word)`、`search(word)`、`startsWith(prefix)`。search 要完整词存在，startsWith 只要此前缀存在。题目字符为小写英文字母。

约束核对（2026-10-09）：word/prefix 长度 1..2000，只含小写英文字母；最多 30000 次方法调用。 [官方来源](https://leetcode.com/problems/implement-trie-prefix-tree/)

## 从朴素方法到优化

把所有单词存列表，每次前缀查询逐词比较，需要与词数相关的时间。Trie 共享公共前缀，让查询成本只与待查字符串长度有关。

## 核心思路

每个节点保存字符→子节点字典和完整单词结束标记。insert 沿字符走、缺失就建；search 检查路径和结束标记；startsWith 只检查路径。

## 手推一个小例子

插入 `cat`、`car`：共同使用 c→a，然后分出 t、r，两个末端标记为词。search(`ca`) 为 False，startsWith(`ca`) 为 True；插入 `ca` 后同一中间节点被标记，search 才为 True。

## 为什么正确

根到节点的路径唯一表示一个前缀，插入恰创建所需路径并标记完整词终点。因此存在路径等价于存在某个已插入词以它为前缀，终点标记进一步区分完整词。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0208_implement_trie_prefix_tree.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class _TrieNode:
    def __init__(self):
        self.children = {}
        self.terminal = False

class Trie:
    def __init__(self):
        self.root = _TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = _TrieNode()
            node = node.children[char]
        # 路径存在仅代表前缀，完整单词另用终点标记。
        node.terminal = True

    def _walk(self, text):
        node = self.root
        for char in text:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.terminal

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None
```

## 复杂度

单次插入或查询期望 O(L)，L 为字符串长度。总空间 O(S)，S 为所有已插入字符总数的上界；共享前缀可减少节点数量。

## 边界与易错点

路径存在不等于完整单词存在。重复插入不应创建重复路径。题目要求非空字符串，代码亦自然支持空字符串，但不是必须测试域。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：若只需完全相等查询，哈希集合和 Trie 各有什么优劣？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/implement-trie-prefix-tree/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0208.Implement%20Trie%20(Prefix%20Tree)/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：用一个单词同时作为另一单词的前缀，检查终止标记与 startsWith 的判断差异。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
