# 版本核验与面试使用规则

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

1. Go 1.22：循环内声明的迭代变量语义发生变化；回答要结合 go.mod 与构建条件。[官方说明](https://go.dev/doc/go1.22)
2. Go 1.24：内置 map 改为 Swiss Table 实现；旧 bucket 细节要限定版本。[官方说明](https://go.dev/doc/go1.24)
3. Go 1.25：引入容器感知 GOMAXPROCS 默认行为；显式配置及兼容设置仍需核对。[官方博客](https://go.dev/blog/container-aware-gomaxprocs)
4. Go 1.26：Green Tea GC 默认启用；GC 基础仍以可达性、标记清扫、并发协调理解。[官方说明](https://go.dev/doc/go1.26)
5. Go 1.27：goroutineleak profile 正式可用。其正式发布状态已由 2026-08-19 的发布公告与 Release History 交叉确认，非仅凭存在 release-notes 页面推断。[发布公告](https://go.dev/blog/go1.27)、[发布历史](https://go.dev/doc/devel/release)

这些更新用于避免答错，不要求新手把所有新 API 都放进项目。面试先说明项目实际 Go 版本，再说稳定语义、实现原理及测量证据。未核项目代码前，可说“如果让我实现，我会……”；不能说“我的项目已用……”或编造 QPS、延迟、测试覆盖率。
