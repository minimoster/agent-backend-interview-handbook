# Agent应用实验与Python附录：验证范围

[返回覆盖状态](README.md) · [Agent目录](../docs/10-agent/README.md) · [技术参考](../sources/agent-labs-references.md)

日期：2026-10-10。新增7篇Agent专题、Python/FastAPI与AI Coding两篇附录，以及1篇面试准备；KV生命周期与容量算例合并入已有推理章。现有361道讲义题、100道Hot100、15道外部资源题及26张公开场景卡分别计数，不因这批专题而增加。没有创建新的A/FA题号。

## 原创范围与资料缺口

新增正文、教学输入、参考设计和代码为独立组织的原创材料。35条仅有问题、标题或空正文的内容获得明确标注的新写答案、练习规格或准备框架；它们不是原材料中已经存在的答案。第一人称填答结构需要学习者替换为自己的事实。

受限外部回答仍未读取，外部Skill ZIP仍未读取。代码审查流程与六表SQL Skill是原创教学替代，不能算作读取、还原或测试了外部包。未复制私有链接、原图、受限导出或联系信息。Transformer底层原理的系统先修模块仍待补充，本批只给已列的机制与容量边界。

## 94项聚焦测试与11项旧协议检查

本批在CPython3.12.14重跑通过：

- 12项内存订单/审批/未知结果合同测试
- 23项Python语言与NumPy测试
- 13项FastAPI进程内API测试
- 13项AI Coding参考内核测试
- 3项KV预算算术测试
- 20项跨度、排序、MMR、过滤及工具目录合同测试
- 10项标准库/SQLite合成SQL Skill测试

合计94项单元/合同测试。另有一次真实本地stdio会话完成11项命名检查，固定MCP Python SDK1.29.0，实际协商协议2025-11-25。现代2026-07-28规范说明与这个旧SDK实验分开，现代互通或迁移未执行。

固定直接依赖：FastAPI0.141.1、Pydantic2.13.4、Starlette1.6.0、HTTPX0.28.1、Uvicorn0.52.1、NumPy2.3.5、python-multipart0.0.32；旧MCP例子另用MCP1.29.0与AnyIO4.14.2。SQLite运行时为3.53.1。这些是已运行教学环境，不是最新版本或生产推荐组合，requirements不构成完整传递依赖锁文件。Starlette/HTTPX TestClient适配仍出现弃用警告，当前固定组合通过。

## 复现命令

从仓库根目录执行；在隔离环境中按固定依赖准备后再运行：

```sh
cd examples/agent_scenario_contracts
python -B -m unittest -v test_ordering
cd ../..
cd examples
python -B -m unittest -v test_python_language_lab test_fastapi_lab test_coding_kernels test_kv_budget
cd retrieval_contracts
python -B -m unittest -v test_lab test_store_skill
python -B test_mcp_legacy.py
cd ../..
python -B tools/refresh_question_metadata.py --check
python -B tests/test_question_metadata.py
node site/build.mjs
node site/build.mjs --check
node site/test.mjs
```

[场景合同](../examples/agent_scenario_contracts/README.md)与[检索/工具实验](../examples/retrieval_contracts/README.md)说明各自的数据、依赖与限制。[Python/FastAPI](../docs/40-backend/40-python-fastapi-lab.md)记录API清理、输出过滤、幂等与租户测试；[AI Coding](../docs/70-practice/ai-coding-exercises.md)包含11项应用练习和1项通用质量契约，实际实现仅覆盖列出的4类参考内核。

## 尚未执行的阶段

没有真实模型、Embedding/ANN、在线RAG、GPU推理/训练、性能基准、真实支付、招聘决策、医疗系统或11个完整应用验收。没有现代MCP互通、HTTP/OAuth、跨版本迁移、真实数据库权限、生产恢复或安全证明。FastAPI例子不提供真实认证、多进程一致性或耐久队列。

## 整合回归与渲染边界

最终静态构建与26组非渲染检查通过，覆盖规范Markdown、相对链接、实际锚点、源码副本、正文搜索和独立计数。原有Python算法/合同、有限穷举、公开场景测试以及Java排序/单例实验重跑通过。Go语言运行时在本地执行环境中不可用，既有未改动Go实验本次没有重跑；不把历史记录称为本批新结果。

发布前，云浏览器无法连接这个执行环境的本地候选预览，当时实际浏览器、屏幕尺寸与辅助技术渲染检查未完成。静态检查不代替渲染测试；发布后的独立结果另列如下。

本地合同通过只支持所列合成分支；源码准备与远端发布/部署也分开。

## 2026-10-11：发布后的CI与桌面浏览器实测

提交[6dacaf1dd1f6f7bd5b71b8e74c017e9d5a91e833](https://github.com/minimoster/agent-backend-interview-handbook/commit/6dacaf1dd1f6f7bd5b71b8e74c017e9d5a91e833)的[知识检查](https://github.com/minimoster/agent-backend-interview-handbook/actions/runs/38103623825)与[Pages部署](https://github.com/minimoster/agent-backend-interview-handbook/actions/runs/38103623851)均成功。CI在CPython3.12.15中重跑94项新教学测试及11项旧MCP stdio检查，通过；实际仍协商2025-11-25。已有Python、Java与Go fixture检查通过，其中Go执行`go test -race -count=1 -timeout=60s ./...`。这条CI记录与前述本地环境记录分开。

上线后的云桌面Chrome在1183×759 CSS像素、DPR1下，实测10篇新章节均可打开并渲染，已有推理章的7个小节锚点可定位。361/100/15/26计数仍分别显示；校准阈值、MMR、依赖缓存、ROUND_HALF_UP全文搜索与结果锚点正常，主题/优先级/难度筛选、清空和无结果状态正常。重复导航、浏览器前进/后退、明暗主题切换及代码和表格布局通过。配套MCP源码下载的HTTP响应和字节匹配已核实，GitHub源码页面已实际打开。

这只是上述桌面浏览器流程的实测，不是所有设备、真实手机、屏幕阅读器或其他辅助技术验收，也没有扩大现代MCP、真实模型/GPU、生产服务或完整应用的未执行范围。
