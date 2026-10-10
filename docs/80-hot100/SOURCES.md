# 题单、来源与权利边界

## 官方范围

- [力扣中国：热题100](https://leetcode.cn/studyplan/top-100-liked/)，本模块的分类与顺序基准。
- [LeetCode.com：Top 100 Liked](https://leetcode.com/studyplan/top-100-liked/)，交叉核对题号与slug集合。
- 核对日期：2026-10-09。两站得到相同的100个不同题号、100个不同slug；中国站17类，国际站15类，因此分类只采用中国站。
- 难度：简单20、中等68、困难12。具体清单、相对文件路径与官方题目链接见[manifest.json](manifest.json)。

## 本模块原创范围

每题的短题意概述、朴素到优化的思考、手推例子、正确性说明、代码注释、Python主解与测试为本学习模块独立编写。没有搬运第三方完整题解、官方完整题面、官方插图或成组官方样例。题目名称与链接用于识别练习目标；官方题面的权利仍属于其权利人。

算法思想与常见数据结构不是某个题解仓库的专属表达。实现采用通行算法，自建本地测试核对行为，不依据另一项目的“已AC”标记宣称本实现提交通过。

## 延伸阅读（只引用链接）

- [doocs/leetcode](https://github.com/doocs/leetcode) 固定版本 `c412a46586590f020b0d861c163758cb60987270`。研究时逐题核实100题存在Python代码块，但未把其代码复制进本模块。
- [doocs固定版本LICENSE](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/LICENSE)声明CC BY-SA 4.0；其README另有商业转载联系作者的表述。读者若自行改编，应先核清授权边界、署名与同方式共享义务，不要把这些材料改贴本仓库许可证。
- [walkccc/LeetCode](https://github.com/walkccc/LeetCode) 固定版本 `9b85aa15e086d0b5dc1ead7184bca547942e6ff6`，作为另一套风格简洁的对照。该版本核验到99/100题Python文件；994未核验到Python，不宣称完整Python覆盖。
- [walkccc固定版本LICENSE](https://github.com/walkccc/LeetCode/blob/9b85aa15e086d0b5dc1ead7184bca547942e6ff6/LICENSE)为MIT。若读者另行复制其代码，需保留相应版权与许可声明。

第三方项目对自身作品的许可，不自动代表有权重新许可LeetCode完整题面。本页仅说明材料来源和本模块使用方式，不构成法律意见。

## 验证边界

本模块区分三件事：官方题单范围核实、源码可导入且本地测试通过、在线判题是否提交。前两项可通过仓库资料与命令复现；第三项未执行，也没有声称执行。题目页的内容获取状态与约束核对范围见[测试说明](TESTING.md)。
