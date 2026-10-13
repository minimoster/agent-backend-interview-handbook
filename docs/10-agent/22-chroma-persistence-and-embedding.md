# Chroma持久化与嵌入集成

[返回 Agent 目录](README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

本章学习向量存储的持久化与嵌入接口。API 依据2026-10-09读取的官方文档整理；练习前固定 SDK 版本，并在该版本执行验证清单。文中方案尚未实现或测试。

<a id="fa63"></a>

### FA63 Chroma怎样持久化 文本是谁转成Embedding的？

**优先级：P1。**

**知识点详解**

当前Python参考区分EphemeralClient的内存存储、PersistentClient的本地磁盘存储和连接服务器的HttpClient。PersistentClient适合本地开发与测试；当前官方Client参考建议生产优先采用server-backed实例。实际部署还要核对并发客户端、备份恢复、升级和访问控制，目录落盘本身不等于生产可用。持久客户端要明确数据目录，重启时使用相同目录、租户、数据库与collection；容器环境还要确认目录是否位于持久卷。服务端部署的持久性由服务配置负责，不由客户端本地路径决定。

**具体例子**

教学流程先创建本地持久client和明确版本的collection，写入稳定ID、文档和元数据，关闭进程后重新打开并按ID查询，确认记录确实存在。文本可通过配置的embedding function转向量，也可由应用先编码再传embeddings；用query_texts时依赖嵌入配置，直接query_embeddings时应用负责向量兼容。

**常见误区与适用边界**

不同SDK和版本对默认嵌入、配置保存与自动恢复支持可能不同，不能只看示例省略了参数就假设永远一致。查询与文档要处于兼容的嵌入空间并使用相同维数，分别遵守模型对查询和文档的前缀、预处理及距离约定；维数相同不保证空间兼容。换成不兼容的embedding通常需要重建索引。向量库本地落盘不代表embedding调用一定本地，配置远程服务仍会传出文本。

**30 秒答题主线**

我先确定client类型与数据实际存放位置，再固定collection和embedding契约。持久化用跨进程回读验证，文本向量化由所选嵌入组件完成；存储、编码和权限是三件事。

**追问与验证**

追问：重新创建collection查不到旧数据怎么办？验证：核对路径、挂载、tenant/database、集合名和版本；测试重启、备份恢复和模型替换。本文没有运行Chroma，以上是待执行验证方案。

**来源**：[FA-S070](https://docs.trychroma.com/reference/python/client)、[FA-S071](https://docs.trychroma.com/docs/embeddings/embedding-functions)。
