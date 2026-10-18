# 算法变体补充：六个明确题设的Python解法

[返回练习目录](README.md) · [完整可运行代码](../../examples/interview_algorithms/solutions.py) · [测试](../../examples/interview_algorithms/test_solutions.py)

这些变体不能直接由Hot100主线替代。每题明确声明输入、输出与必要假设，配合讲解、Python代码和合成测试。

2026-10-10，Python 3.12.14运行8个测试入口全部通过，含固定种子随机对拍、小范围穷举与X04的5,000位字符串边界；没有向在线判题站提交。附带的[历史运行记录](../../examples/interview_algorithms/validation-result.json)对应2026-10-09的6项测试，不包含新增的超大字符串与输入验证入口；当前8项可从根目录用`python -B examples/interview_algorithms/test_solutions.py`复现。链表题重连原节点，调用后原链表结构改变。共享节点类型如下：

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Node:
    value: int
    next: "Node | None" = None
```

## 目录

[X01 原地单词逆序](#x01) · [X02 奇升偶降链表](#x02) · [X03 大数相加](#x03) · [X04 数位构造的题设边界](#x04) · [X05 删除所有重复值](#x05) · [X06 异位词判断](#x06)

Hot100 之外的独立补充：[LC395 重复字符最长子串](#lc395) · [LC115 删除位置方案计数](#lc115)

<a id="x01"></a>
## X01 原地反转句中单词，Python字符串可以直接改吗？

**优先级：P1。**

**知识点详解：** Python的str不可变。因此“原地O(1)额外空间”在本题中指调用者已经提供可变字符列表；把str转换为list本身要额外O(n)空间，不能隐瞒。明确单词之间恰好一个ASCII空格、无首尾空格；空句子允许。若业务要合并多个空白，还要另写压缩步骤。

先反转整个字符序列，单词顺序颠倒，但每个单词字母也反了；再逐个反转单词，恢复单词内部顺序。交换只用左右下标，不使用切片生成新列表。

**具体例子：** “we build agents”先整体反转为“stnega dliub ew”，逐词反转后成为“agents build we”。两个反转的作用分别是换词序和恢复字母序，不能只做其中一步。

```python
def reverse_words_in_place(chars: list[str]) -> None:
    """Mutate an existing character list; words separated by one ASCII space."""
    def reverse(left: int, right: int) -> None:
        while left < right:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1
    reverse(0, len(chars) - 1)
    start = 0
    for end in range(len(chars) + 1):
        if end == len(chars) or chars[end] == " ":
            reverse(start, end - 1)
            start = end + 1
```

**面试答法：** 先说明输入是已有可变字符数组，再整体反转和逐词反转。每个字符被处理常数次，时间O(n)，额外工作空间O(1)；若从Python str开始转换，转换空间另算。

**追问：** 需要压缩多个空格怎么办？在可变数组上用读写双指针压缩，再反转；最后可能调整有效长度。是否保留标点由“单词”的定义决定。

**常见误区：** 用split再join却声称原地；用chars[::-1]产生副本；把Python字符串赋值当作可修改字符。

**验证边界：** 本节为原创明确题设与代码，对应测试已运行

<a id="x02"></a>
## X02 奇数位递增、偶数位递减的链表，如何线性排序？

**优先级：P1。**

**知识点详解：** 位置从1开始计数；奇数位置值非递减，偶数位置值非递增，链表无环。利用已有结构比通用O(n log n)排序更快：先按位置拆成两条链表，反转偶数位置链表，使两条都非递减，再归并。操作的是next指针，不把值复制到数组排序。

分离时必须把奇数链末尾next置空，避免残留跨链连接造成错误或环。反转保存following后才能改current.next，否则会丢失后续链。

**具体例子：** 输入1→8→3→6→5→4，奇数链是1→3→5，偶数链是8→6→4；偶数链反转成4→6→8；归并得到1→3→4→5→6→8。值可以重复；这时使用非严格单调前提。

```python
def sort_odd_up_even_down(head: Node | None) -> Node | None:
    """1-based odd positions nondecreasing, even positions nonincreasing.

Input is acyclic. Relinks existing nodes; consumes the original list topology.
"""
    if head is None or head.next is None:
        return head
    odd = head
    even_head = head.next
    even = even_head
    while even is not None and even.next is not None:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = None
    previous = None
    current = even_head
    while current is not None:
        following = current.next
        current.next = previous
        previous, current = current, following
    left, right = head, previous
    dummy = Node(0)
    tail = dummy
    while left is not None and right is not None:
        if left.value <= right.value:
            tail.next, left = left, left.next
        else:
            tail.next, right = right, right.next
        tail = tail.next
    tail.next = left if left is not None else right
    return dummy.next
```

**面试答法：** 拆奇偶、反偶链、归并，两次左右遍历仍是O(n)，只用常数指针和一个哨兵节点。这个优化依赖输入的奇偶单调前提，任意链表不适用。

**追问：** 怎样证明没有丢节点？需要分阶段的不变量，而不只是对几个样例比较节点集合：

1. 拆链：按尾指针划定的已处理奇数前缀、已处理偶数前缀、尚未处理的原后缀，节点身份两两不交，并集始终是全部原节点。这里前缀到尾指针为止，不把尾部尚未断开的next计入前缀。每轮将后缀的下一个奇数节点接到奇链，再把其原后继接到偶链；游标前进前已经保住后续节点的入口。后缀每轮缩短，结束后`odd.next = None`断掉最后的跨链连接，得到两条互不相交的无环链。
2. 反转：previous已反转前缀与current未处理后缀仍构成偶链的身份分割；先保存following，再改current.next，每轮仅将一个节点从后缀转移到前缀。后缀变空时，偶链原节点恰好都出现一次，顺序相反。
3. 归并：以tail为止的已完成输出前缀、left剩余链、right剩余链仍是原节点的身份分割；每轮只取一条剩余链的头节点接到tail并移动该链的头。两条剩余链有序，因此选较小头维持输出非递减；一个头耗尽后接上另一条完整后缀。没有新结果节点被创建，哨兵不在返回链内，终止时每个原节点恰好输出一次，也不会接回已完成前缀形成环。

测试中的身份集合相等、遍历检测环、排序比较是上述性质在有限输入上的佐证，不能替代对所有允许输入的证明。若要求保留原链结构，则需要复制节点或不同接口约定；本解法也不承诺相等值按原位置稳定排序。证明应明确初始化成立、每步保持以及终止时推出目标三个环节。

**常见误区：** 把奇偶按节点值而不是位置拆；未断链；反转顺序错误丢next；违反前提时仍保证有序。

**验证边界：** 本节为原创明确题设与代码，对应测试已运行

<a id="x03"></a>
## X03 不用大整数转换，怎样把两个十进制字符串相加？

**优先级：P0。**

**知识点详解：** 明确输入是非空、ASCII十进制、非负整数，可有前导零。负号、小数和其他Unicode数字不在本题合同内。模拟竖式：从个位向左，把两位数字与carry相加，个位进输出，高位变下一轮carry。最终倒转数字，去除无意义前导零但保留一个0。

代码只将单个字符变成0–9，不把整个输入转成整数。测试参考可用Python大整数比对，因为被限制的是解法实现，不是测试判定器。

**具体例子：** 999+1：第一位9+1=10写0进1；后两位同样写0进1；输入都耗尽后还要输出最后的1，得到1000。循环条件不能只看两个字符串是否还有字符。

```python
def add_decimal_strings(a: str, b: str) -> str:
    """Nonempty ASCII decimal, nonnegative; no whole-input int conversion."""
    if not a or not b or any(c < "0" or c > "9" for c in a + b):
        raise ValueError("expected nonempty ASCII decimal strings")
    i, j, carry = len(a) - 1, len(b) - 1, 0
    reversed_digits = []
    while i >= 0 or j >= 0 or carry:
        x = ord(a[i]) - ord("0") if i >= 0 else 0
        y = ord(b[j]) - ord("0") if j >= 0 else 0
        carry, digit = divmod(x + y + carry, 10)
        reversed_digits.append(chr(ord("0") + digit))
        i -= 1
        j -= 1
    return "".join(reversed(reversed_digits)).lstrip("0") or "0"
```

**面试答法：** 从右向左逐位处理，用divmod得到进位和当前位，再倒转结果。时间O(max(m,n))，结果与临时列表占O(max(m,n))空间，不能把结果空间忽略后说整个实现O(1)。

**追问：** 扩展有符号整数，要先处理符号，再比较绝对值，选择加法或大数减法；不能直接在这段非负代码里跳过负号。

**常见误区：** 漏最终进位；用int(a)+int(b)绕过要求；把isdigit认为只接受ASCII；0000结果变成空串。

**验证边界：** 本节为原创明确题设与代码，对应测试已运行

<a id="x04"></a>
## X04 怎样构造小于N的最大整数，原题少条件时怎么办？

**优先级：P1。**

**知识点详解：** 若题目只有简短标题，没有给出允许数字集合等关键约束，就不能确定唯一的标准答案。下面提供一个明确的原创变体：给定正整数N和允许数字集合D，每个数字可以重复，结果必须是无前导零的正整数，严格小于N；无解返回None。如果限制每位只能用一次，算法必须更换。

面向超大输入的`largest_below_decimal(n, digits)`用非空ASCII十进制字符串表示N和结果，不把整个数转成int。N允许前导零并先规范化；0或1这个扩展输入返回None。非法字符串或非0–9整数的集合成员抛ValueError，bool不视为合法数位。结果保持规范十进制形式，严格小于N。

`largest_below(n, digits)`保留整数便利接口，但整数须能在当前解释器配置下完成十进制str/int转换；超出转换限制抛ValueError，并提示使用字符串接口。CPython 3.11+及包含相关安全修补的较早版本对这类转换设有可配置长度限制，常见默认值为4,300位；它不是所有Python版本/实现的统一上限。本实现和测试均不修改或关闭该安全限制。机制见Python十进制整数转换限制。

同位数时希望尽量长地与N保持相同前缀。在每个前缀仍可行的位置，记录“把当前位改为小于N该位的最大允许数字”的机会；一旦严格变小，后缀全填最大允许数字即可。越靠后的可行下降点保留越长相等前缀，结果越大。若同位数无解，则退到少一位并填最大数字。

**具体例子：** N=678，D={1,4,7}，第一位6不可用，选小于6的最大允许数4，后面填7，得到477。N=1234，D={1,2,3,4}，尽量保留123，末位降成3，得到1233。N=100，D={0,1}同位数无法严格下降，退成11。

```python
def largest_below_decimal(n: str, digits: set[int]) -> str | None:
    """Largest positive decimal < n, with reusable digits and no leading zero.

    n is nonempty ASCII decimal; leading zeros are accepted and normalized.
    No whole-input integer conversion or interpreter-limit changes occur.
    """
    if not isinstance(n, str) or not n or any(c < "0" or c > "9" for c in n):
        raise ValueError("n must be a nonempty ASCII decimal string")
    if any(type(d) is not int or d < 0 or d > 9 for d in digits):
        raise ValueError("digits must be integers in 0..9")
    bound = n.lstrip("0") or "0"
    if bound in ("0", "1") or not digits or not (digits - {0}):
        return None
    allowed = sorted(digits)
    last_drop = None
    for i, char in enumerate(bound):
        limit = ord(char) - ord("0")
        smaller = [d for d in allowed if d < limit and (i != 0 or d != 0)]
        if smaller:
            last_drop = (i, smaller[-1])
        if limit not in digits:
            break
    if last_drop is not None:
        i, digit = last_drop
        return bound[:i] + str(digit) + str(allowed[-1]) * (len(bound) - i - 1)
    shorter = len(bound) - 1
    if shorter == 0:
        return None
    largest_nonzero = max(digits - {0})
    return str(largest_nonzero) + str(allowed[-1]) * (shorter - 1)


def largest_below(n: int, digits: set[int]) -> int | None:
    """Integer convenience wrapper; decimal conversion limits remain active.

    Non-int bounds raise ValueError; n <= 1 has no positive solution.
    Oversized decimal conversions raise ValueError; use the string API instead.
    """
    if type(n) is not int:
        raise ValueError("n must be an integer")
    if any(type(d) is not int or d < 0 or d > 9 for d in digits):
        raise ValueError("digits must be integers in 0..9")
    if n <= 1:
        return None
    try:
        result = largest_below_decimal(str(n), digits)
        return int(result) if result is not None else None
    except ValueError as error:
        raise ValueError(
            "decimal conversion limit exceeded; use largest_below_decimal "
            "with a decimal string"
        ) from error
```

**面试答法：** 先补全合同再解。沿合法相等前缀寻找最靠后的可行下降点，下降后后缀贪心取最大；没有同长解再缩短。字符串接口扫描输入和构造输出需O(d)时间、O(d)空间，d按含前导零的输入长度计，最多10个允许数位使每位的选择成本有常数上界。整数便利接口还要另计大整数十进制转换成本与其失败条件，不能据此宣称不限位数。

**追问：** 是否允许0作为结果？本题不允许，若允许要补特殊返回。数字可重复、必须全用、固定长度等条件任一改变，都不能继续套用本算法。怎样核对5,001位边界？对`"1" + "0"*5000`与D={0,1}，首位不能向下取非零数，同位数无解，答案是`"1"*5000`；直接比较长度与同长字典序即可核验，无需int转换。测试同时核对整数入口的超限异常以及调用前后安全限制相同。

**常见误区：** 题面缺条件却猜成唯一题；把小于写成小于等于；产生前导零；只贪心匹配当前位却不记录退回点。

**验证边界：** 本节为原创明确题设与代码，对应测试已运行

<a id="x05"></a>
## X05 删除排序链表里所有重复值，和保留一个重复值有什么区别？

**优先级：P0。**

**知识点详解：** 本题要求某个值出现两次及以上，就删除该值的全部节点，不是把多次缩成一次。输入已非递减排序且无环，所以相同值一定连续。用哨兵节点避免头部恰好重复的特殊分支；kept指向已确认可保留的最后节点，current扫描未处理段。

如果current和下一节点同值，记住这个值，跳过整段，令kept.next指向第一不同值；否则当前值唯一，推进kept。删除重复段时kept不能跟着跳，否则会保留不该保留的节点。

**具体例子：** 1→1→2→3→3的结果只有2；1→2→2→3的结果为1→3；全部相同时返回空链。输出复用原节点，时间O(n)、额外工作空间O(1)。

```python
def remove_all_duplicate_values(head: Node | None) -> Node | None:
    """Sorted acyclic list; remove every node whose value occurs more than once."""
    dummy = Node(0, head)
    kept = dummy
    current = head
    while current is not None:
        if current.next is not None and current.value == current.next.value:
            repeated = current.value
            while current is not None and current.value == repeated:
                current = current.next
            kept.next = current
        else:
            kept = current
            current = current.next
    return dummy.next
```

**面试答法：** 用哨兵加两个指针，遇重复就跨过整个同值区间，再把上一个保留节点连接到区间后。遇唯一值才推进保留指针。

**追问：** 如果输入无序，相同值不连续，需排序或计数等不同策略。怎样验证删除的是全部重复？用频次恰好1的值作为测试期望，并测试重复出现在头尾及全链。

**常见误区：** 把题目误写成每个值留一个；只删除第二个节点；头部重复时丢失返回头；kept推进太快。

**验证边界：** 本节为原创明确题设与代码，对应测试已运行

<a id="x06"></a>
## X06 判断两个字符串是不是字母异位词，字符范围为什么重要？

**优先级：P0。**

**知识点详解：** 异位词要求每种字符出现次数相同，仅比较字符集合不够。先比长度，再对第一个字符串计数，对第二个逐个扣减，发现不存在或次数不足就失败。这里明确按Unicode码点、区分大小写、保留空格和标点，不做规范化。

若题目保证只有小写a–z，可用26格计数数组。任意Unicode字符则用字典，占O(k)空间，k为不同码点种类。业务若认为某些不同码点序列是同一个显示字符，要先定义规范化与大小写规则，而非偷偷改变算法语义。

**具体例子：** aab和aba为真，aab和abb为假，集合都是{a,b}却无法判断数量。预组合的é与e加组合重音在本题中不同；“看起来一样”与码点相等不是一件事。

```python
def are_anagrams(a: str, b: str) -> bool:
    """Exact case-sensitive Unicode code-point counts; no normalization."""
    if len(a) != len(b):
        return False
    counts = {}
    for char in a:
        counts[char] = counts.get(char, 0) + 1
    for char in b:
        count = counts.get(char, 0)
        if count == 0:
            return False
        if count == 1:
            del counts[char]
        else:
            counts[char] = count - 1
    return not counts
```

**面试答法：** 比较字符频次而不是集合。两次线性扫描，期望时间O(m+n)，哈希字典占O(k)；字符集固定26字母时可把额外数组视为常数空间。

**追问：** 返回所有异位词分组时，频次向量或排序后字符串可以作键，见Hot100分组题；寻找窗口内所有异位词时，要维护滑动窗口频次，不必每次重数。

**常见误区：** 只比较set；默认所有题都可用26字母数组；忽略重复次数；混淆异位词判断、分组与滑动窗口三种输出。

**验证边界：** 本节为原创明确题设与代码，对应测试已运行

## 如何运行验证

```sh
python3 examples/interview_algorithms/test_solutions.py
```

测试包含空输入/单元素、重复值、前导零、最终进位、非法数字、字符集、链表节点身份与无环检查。数位构造对数字集合{0,1,2,3,4}的所有子集以及1到299的N做穷举参考比较；这验证该明确变体，不填补源文未给的约束。随机种子固定，可复现。没有在线判题通过声明。

<a id="lc395"></a>

## 独立补充 LC395：每个字符至少出现 k 次的最长子串

本节练习 LC395，与 LC3“无重复字符的最长子串”条件不同，作为 Hot100 之外的补充阅读。以下代码已用本地合成用例验证，尚未提交在线判题系统。

### 从条件推导分治

字符串 `aaabb`，k=3。整个区间中 b 仅出现2次，任何包含 b 的子串都无法达标，所以 b 是合法分割点，答案留在其两侧，左侧 `aaa` 长度3。一般地，在当前区间统计频次，找出少于 k 的字符，把所有这样的字符当作分隔符；分别处理剩余区间。若没有不合格字符，整个区间合法。正确性来自：合法答案不能跨过任何不合格字符，否则它在子串内的次数至多等于当前区间次数，仍小于 k。

实现采用显式区间栈，避免长字符串递归超限，也不逐层复制切片。处理长度小于 k 或不可能超过当前最优值的区间可以剪枝。k<=1时整串都合法，空串结果为0。

### 为什么普通滑动窗口不够

LC3的“出现重复就缩左边”具有可维护的约束；本题中字符出现次数不足时，右边继续增加可能让它合法，立即收缩反而丢失答案。可枚举目标字符种类数 t：窗口只要种类数超过 t 就收缩；同时维护 `distinct` 和出现次数已达到 k 的种类数 `satisfied`。当二者都等于 t，窗口合法。

加入字符时从0到1增加distinct，从k-1到k增加satisfied；移除字符时从k到k-1减少satisfied，从1到0减少distinct。维护阈值跨越，而非每轮重新扫描整个窗口。`ababbc`，k=2时枚举t=2，`ababb`里a出现2次、b出现3次，得到长度5；c加入后触发收缩。

### 实现、复杂度与验证

- [两种完整原创Python实现](../../examples/algorithms/lc395_longest_repeating_substring.py)
- [暴力对照与穷举测试](../../tests/test_agi_algorithms.py)
- 根目录运行 `python -m unittest discover -s tests -p 'test_agi_algorithms.py'`

设U为输入不同字符的数量。枚举窗口用O(U×n)时间、O(U)额外空间；只有限定26个小写字母时，U为常数，才能简写O(n)。分治每层至少排除一种字符，各层区间互不重叠，时间上界同样为O(U×n)，一般字符集合最坏可到O(n²)；显式区间栈和频次结构最坏O(n+U)空间。示例支持Python字符串字符，但不把Unicode码点等同于用户眼中的组合字形。

测试穷举长度0–7的abc字符串，对k=0–9共32,800组输入，将两种实现与独立暴力枚举比较，另测中文、emoji和较长分段边界。这个验证范围只证明这些输入的一致性，不代替上述不变量证明。

题意核对：LeetCode 395。

<a id="lc115"></a>

## 独立补充 LC115：删除位置方案计数

### 题目与合同

给定字符串 s 和 t，从 s 中保留一组严格递增的原始下标，使保留的字符依次拼成 t，返回符合要求的下标集合数量。每个集合与其补集，即删除位置集合，一一对应。相同的最终字符串可以由不同位置形成，分别计数；不区分删除动作的执行先后，也不求最少删除次数。

本节将“删除字符得到目标串的方案数”明确为上述合同。按 Python 字符串的元素比较字符，不做大小写折叠或 Unicode 归一化；不把码点当作用户眼中的组合字形。官方 LC115 约束为非空英文字符串，本实现额外定义空串边界：空目标有一种空选择，空源不能生成非空目标。

例如 s="aaba"、t="aa"，以零基下标计，合法选择是 (0,1)、(0,3)、(1,3)，所以答案是 3。不是最终不同文本数 1，也不是最少删除次数 2，更不是三组选择分别乘上删除排列。

### 可口述答案

“我按源串位置决定选或不选。dp[i][j] 表示只看 s 的前 i 个字符、生成 t 的前 j 个字符的方案数。不用当前字符时继承上一行同列；当前字符与目标末尾相同时，还能给上一行前一列的每个方案追加当前位置。这两类按是否包含当前位置分组，互斥且覆盖全部方案，所以可以相加。空目标始终有一种方案。压成一维后要从右往左更新，确保读取的是上一轮的状态，不会把一个源字符用两次。”

### 状态、递推与证明

定义 D[i][j]：从 s[:i] 选位置，拼成 t[:j] 的方案数。

- D[i][0]=1：只能什么都不选，不随可删字符数增加。
- D[0][j]=0，其中 j>0：没有字符，不能形成非空目标。
- 不保留位置 i-1：有 D[i-1][j] 种。
- 保留位置 i-1：只有 s[i-1]==t[j-1] 才可行；删去这个最后位置后，恰好对应 D[i-1][j-1] 的一个方案。
- 因而相等时 D[i][j]=D[i-1][j]+D[i-1][j-1]，否则 D[i][j]=D[i-1][j]。

每个方案要么含 i-1，要么不含，两类不能重合。含当前位置的方案剥掉最后位置后，与上一行前一列的方案一一对应；反向追加也不会破坏下标递增。初始状态正确，逐行归纳便得到 D[|s|][|t|]。

s="aaba"、t="aa" 时，一维表只列 j=0,1,2：
- 初始：[1,0,0]
- 读第一个 a：[1,1,0]
- 读第二个 a：[1,2,1]
- 读 b：[1,2,1]
- 读最后的 a：[1,3,3]

### 完整 Python 答案

```python
def count_subsequence_choices(s: str, t: str) -> int:
    """Count increasing original-index selections in s spelling exactly t."""
    if not t:
        return 1
    n, m = len(s), len(t)
    if m > n:
        return 0
    dp = [0] * (m + 1)
    dp[0] = 1
    for i, ch in enumerate(s, start=1):
        for j in range(min(i, m), 0, -1):
            if ch == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[m]
```

处理第 i 个源字符之前，dp[j] 是 D[i-1][j]。倒序时，dp[j-1] 还没被本轮覆盖，所以转移恰好读取上一行。j>i 的目标前缀不可能形成，可跳过。dp[0] 保持 1。

反例说明为什么不能正序：s="aa"、t="aa"。第一轮若先更新 dp[1]=1，再用这个新值更新 dp[2]=1，就把第一个 a 用了两次。即使加上 j<=i 的上界，第二轮正序仍把 dp[1] 先改为 2，再加进 dp[2]，错误得到 2 而非 1。因此“循环只到当前长度”不能替代倒序。

### 复杂度与整数边界

令 n=|s|、m=|t|。在每次整数加法视为 O(1) 的通常算法分析中，至多做 O(nm) 次状态处理，保存 O(m) 个整数。空目标、m>n 的提前返回耗时 O(1)，不分配 DP 表；一般实现没有构建二维表或所有下标方案。

严格说，Python 整数可以变大：计数不超过 2^n，最多需要 O(n) 位。按位成本计算，单次加法最坏 O(n)，所以保守上界为 O(n²m) 位操作、O(nm) 位的 DP 存储。通常面试中报 O(nm) 时间、O(m) 空间时，应说明指的是状态/算术操作口径，而不是对任意大整数都常数时间。

不擅自取模，Python 返回精确整数。Java/C++ 应按约束选择并验证足够宽的整数或使用大整数。仅“最终答案能放进 32 位”不保证每个中间状态都能放下。例如 s 是 100 个 a，t 是 50 个 a 后接 b，最终答案为 0，但中间生成 50 个 a 的计数已为 C(100,50)，远超 64 位。不能用最终结果为零为中间溢出开脱。

### 边界与追问

- ("", "") → 1；("abc", "") → 1。
- ("", "a") → 0；("a", "aa") → 0。
- ("abc", "d") → 0；("abc", "abc") → 1。
- ("aaaa", "aa") → 6，对应 C(4,2)。
- ("aaba", "aa") → 3。

问：为什么不能用 LCS 长度？
答：LCS 求最长长度，不能区分形成同一目标的多个位置方案。即使长度等于 |t|，也只说明至少存在一个方案，不能得知有几个。

问：最少删除数不是 n-m 吗？
答：只允许从 s 删除且能得到 t 时，删除个数确实固定为 n-m；但计数题问的是哪些位置可以删，两者的状态目标不同。不存在时计数为 0，不能返回一个伪造的删除方案。

问：本题“不同”到底不同在哪里？
答：原始位置集合不同。重复字符的不同出现位置可以产生同一个 t。若题目要数“删除的执行顺序”，合同和组合因子都会改变，应先澄清，不能套用本答案。

问：怎样验证不是自己和自己对拍？
答：对小规模 s 枚举所有下标子集，按原始顺序拼接并与 t 比较，直接统计匹配的子集。它不使用 DP 递推。穷举短二元字符串，再测试组合数和大整数边界，能覆盖初始化、重复字符与更新方向等错误。

### 实现与验证

[完整可运行实现](../../examples/algorithms/lc115_distinct_subsequences.py) · [独立暴力对拍测试](../../tests/test_agi_algorithms.py)

在仓库根目录运行：

```sh
python3 -B tests/test_agi_algorithms.py
```

测试将长度 0–6 的二元源串与长度 0–5 的二元目标串两两组合，共 8,001 对，逐一与原始下标子集枚举比较；另检查空串、Unicode、重复字符组合数与最终为零但中间计数很大的情形。正文代码与可运行实现也做一致性检查。这些是本地合成验证，不是在线判题提交记录或真实业务压测。

继续对照：[LC1143 的最长长度目标](../80-hot100/problems/1143-longest-common-subsequence.md#核心思路) · [LC72 的最小编辑代价](../80-hot100/problems/0072-edit-distance.md#核心思路)。状态都可按两个字符串的前缀定义，但转移的聚合目标分别是方案数、最大长度与最小代价，不能互换。

