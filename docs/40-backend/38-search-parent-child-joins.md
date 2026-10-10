# Elasticsearch父子关系与RAG父子分块

[返回后端目录](README.md) · [RAG索引与证据](../10-agent/17-rag-indexes-and-evidence.md)

本章为原创补充，不增加面试题计数。核查日期：2026-10-10。API概念按读取日的Elasticsearch官方参考说明；示例未连接真实集群运行。

<a id="es-parent-join"></a>

## 一个名称，两种数据关系

Elasticsearch的 `join` 字段关联同一索引中的父、子文档，例如商品与商品报价。子报价变化时可单独更新其文档；`has_child` 查有特定报价的商品，`has_parent` 查父商品满足条件的报价。这是搜索引擎的数据建模与查询机制。

RAG父子分块则把较小的子块用来定位证据，再按父块ID取回较完整的上下文。它可以由关系数据库、KV或应用层完成，不要求Elasticsearch `join`；“父块不生成向量”也只是某个方案的选择。不要看到“父子索引”就把这两种机制合成一条结论。

### 路由约束与查询成本

商品 p7 与它的报价必须落在同一分片。索引、更新、删除和按ID读取子文档时，要传一致的routing值，让父子关系始终共置。关系只允许一个父节点；不要把多级join当作一般关系数据库使用。

例如声明 `product -> offer`，写入报价o9时，join对象说明它是offer、父ID为p7，同时按p7路由。查询“有库存且价格低于200的报价对应哪些商品”需要has_child；只查报价自身的价格与库存，则不必付父子查询代价。商品名称若经常用于子报价检索，也可评估在报价中冗余名称，代价是更新传播。

Join查询会消耗额外内存与计算，并可能构建global ordinals。高基数、频繁刷新、多层关系都可能放大成本。不能脱离数据规模和更新频率声称它普遍比SQL JOIN快或总比nested更好。

### 三种建模的实验设计

- 反规范化：搜索简单；冗余字段改变时要批量更新，并验证更新窗口
- nested：适合需要保留数组对象内字段对应关系的场景；更新嵌套内容可能重索引整个文档
- parent-child：子对象显著多于父对象且独立更新有价值时才考虑；承担共分片routing和join查询成本

固定数据量、更新速率、刷新间隔与查询分布，比较P95/P99、堆内存、索引量和更新成本，加入“同名商品不同ID”“错routing”“父删除后子仍存”“高频报价更新”反例。测试还要验证租户过滤分别覆盖父、子对象；有父ID并不表示当前用户获准读取父文档。

[Elasticsearch官方join字段说明](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/parent-join) · [官方nested说明](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/nested)

### 来源边界

