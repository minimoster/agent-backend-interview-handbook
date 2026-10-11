# Agent应用实验与Python附录：技术参考

[返回来源目录](catalog.md) · [验证范围](../coverage/AGENT_LABS_VALIDATION.md)

以下是一手文档、论文、官方代码或工具作者的方法说明，均来自对应原创章节的公开参考链接。版本与适用条件在正文中说明；整理日期为2026-10-10。这个目录不代表额外运行实验，也不把动态文档称为永久固定规范。

## 采样、KV缓存与推理服务边界

[对应章节](../docs/10-agent/24-inference-and-serving-boundaries.md)

- [PagedAttention论文](https://arxiv.org/abs/2309.06180)
- [vLLM缓存说明](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/)
- [vLLM 0.10.2 自动前缀缓存](https://docs.vllm.ai/en/v0.10.2/features/automatic_prefix_caching.html)
- [Transformers官方解码策略](https://huggingface.co/docs/transformers/main/en/generation_strategies)
- [Transformers 4.57.1 缓存机制](https://huggingface.co/docs/transformers/v4.57.1/cache_explanation)
- [Transformers 4.57.1 缓存策略](https://huggingface.co/docs/transformers/v4.57.1/kv_cache)

## Agent评测、提示回归与模型路由

[对应章节](../docs/10-agent/25-agent-evaluation-and-routing.md)

- [MMLU](https://arxiv.org/abs/2009.03300)
- [BIG-bench](https://arxiv.org/abs/2206.04615)
- [BBH](https://arxiv.org/abs/2210.09261)
- [MT-Bench与Chatbot Arena论文](https://arxiv.org/abs/2306.05685)
- [WebArena](https://arxiv.org/abs/2307.13854)
- [SWE-bench](https://arxiv.org/abs/2310.06770)
- [GPQA](https://arxiv.org/abs/2311.12022)
- [GAIA](https://arxiv.org/abs/2311.12983)
- [MMMU](https://arxiv.org/abs/2311.16502)
- [AgentBoard](https://arxiv.org/abs/2401.13178)
- [VisualWebArena](https://arxiv.org/abs/2401.13649)
- [Arena论文](https://arxiv.org/abs/2403.04132)
- [WorkArena](https://arxiv.org/abs/2403.07718)
- [OSWorld](https://arxiv.org/abs/2404.07972)
- [MMLU-Pro](https://arxiv.org/abs/2406.01574)
- [τ-bench](https://arxiv.org/abs/2406.12045)
- [LiveBench](https://arxiv.org/abs/2406.19314)
- [MMMU-Pro](https://arxiv.org/abs/2409.02813)
- [官方文档](https://crfm-helm.readthedocs.io/en/latest/)
- [Stanford介绍](https://crfm.stanford.edu/2025/03/20/helm-capabilities.html)
- [OpenTelemetry敏感数据说明](https://opentelemetry.io/docs/security/handling-sensitive-data/)
- [Anthropic评测方法](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Agent生产设计：从模块图到可验证合同

[对应章节](../docs/10-agent/26-agent-production-design-lab.md)

- [Reflexion](https://arxiv.org/abs/2303.11366)
- [Tree of Thoughts](https://arxiv.org/abs/2305.10601)
- [ReWOO](https://arxiv.org/abs/2305.18323)
- [授权检查](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP提示注入](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)

## Agent场景题：目标、状态、证据与执行边界

[对应章节](../docs/10-agent/27-practical-agent-scenarios.md)

- [CLIP论文](https://arxiv.org/abs/2103.00020)
- [WHO健康AI治理指导](https://www.who.int/publications/i/item/9789240029200)

## 开放性问题：用条件、证据与实验作判断

[对应章节](../docs/10-agent/28-frontier-and-engineering-decisions.md)

- [Artificial Analysis方法](https://artificialanalysis.ai/methodology)
- [SWE-bench论文](https://arxiv.org/abs/2310.06770)
- [Arena研究](https://arxiv.org/abs/2403.04132)
- [Claude Code官方记忆说明](https://code.claude.com/docs/en/memory)
- [NIST SP 800-226](https://csrc.nist.gov/pubs/sp/800/226/final)
- [OpenClaw官方Skills说明](https://docs.openclaw.ai/tools/skills)
- [Open LLM Leaderboard项目](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)

## Agent框架选型与组件集成

[对应章节](../docs/10-agent/29-framework-selection-and-integration.md)

- [AutoGPT官方入口](https://agpt.co/docs/platform)
- [LlamaIndex](https://developers.llamaindex.ai/python/framework/)
- [CrewAI](https://docs.crewai.com/v1.15.26/en/concepts/crews)
- [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT)
- [BabyAGI当前仓库](https://github.com/yoheinakajima/babyagi)
- [smolagents](https://huggingface.co/docs/smolagents/index)
- [AutoGen](https://microsoft.github.io/autogen/stable/index.html)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [PraisonAI](https://praison.ai/docs)

## RAG数据工程与分块验证实验

[对应章节](../docs/10-agent/30-rag-data-and-chunking-lab.md)

- [Adapters](https://arxiv.org/abs/1902.00751)
- [Prefix-Tuning](https://arxiv.org/abs/2101.00190)
- [Prompt Tuning](https://arxiv.org/abs/2104.08691)
- [LoRA原论文](https://arxiv.org/abs/2106.09685)
- [Chroma](https://docs.trychroma.com/reference/python/client)
- [pgvector](https://github.com/pgvector/pgvector)
- [Milvus](https://milvus.io/docs/filtered-search.md)
- [Stanford信息检索教材](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)
- [MMR原论文](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)
- [Elasticsearch](https://www.elastic.co/docs/solutions/search/vector/knn)

## 工具 MCP与Skill的实用合同

[对应章节](../docs/10-agent/31-tool-mcp-and-skill-contracts.md)

- [Agent Skills格式](https://agentskills.io/specification)
- [v1.29.0官方源代码](https://github.com/modelcontextprotocol/python-sdk/blob/v1.29.0/src/mcp/server/fastmcp/server.py)
- [支持版本文件](https://github.com/modelcontextprotocol/python-sdk/blob/v1.29.0/src/mcp/shared/version.py)
- [2025-11-25生命周期](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)
- [2026-07-28规范](https://modelcontextprotocol.io/specification/2026-07-28)
- [现代基础字段表](https://modelcontextprotocol.io/specification/2026-07-28/basic/index)
- [现代传输规范](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)

## Python 与 FastAPI 工程附录

[对应章节](../docs/40-backend/40-python-fastapi-lab.md)

- [Babel 2.17 概览](https://babel.pocoo.org/en/latest/intro.html)
- [OWASP 密码存储](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 6585 的 429 语义](https://datatracker.ietf.org/doc/html/rfc6585#section-4)
- [RFC 9110 方法语义](https://datatracker.ietf.org/doc/html/rfc9110#section-9)
- [Django 5.2 概览](https://docs.djangoproject.com/en/5.2/intro/overview/)
- [模型契约](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic 严格模式](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [abc](https://docs.python.org/3.12/library/abc.html)
- [Python 3.12 copy](https://docs.python.org/3.12/library/copy.html)
- [Python 3.12 dis](https://docs.python.org/3.12/library/dis.html)
- [Python 3.12 functools.wraps](https://docs.python.org/3.12/library/functools.html#functools.wraps)
- [Python 3.12 标准库目录](https://docs.python.org/3.12/library/index.html)
- [Python 3.12 内置类型](https://docs.python.org/3.12/library/stdtypes.html)
- [Python 3.12 比较](https://docs.python.org/3.12/library/stdtypes.html#comparisons)
- [Python 3.12 range](https://docs.python.org/3.12/library/stdtypes.html#ranges)
- [Python 3.12 字符串方法](https://docs.python.org/3.12/library/stdtypes.html#string-methods)
- [Python 3.12 对象模型](https://docs.python.org/3.12/reference/datamodel.html)
- [Python 3.12 对象构造](https://docs.python.org/3.12/reference/datamodel.html#object.__new__)
- [Python 3.12 执行模型](https://docs.python.org/3.12/reference/executionmodel.html)
- [Python 3.12 名称绑定](https://docs.python.org/3.12/reference/executionmodel.html#naming-and-binding)
- [Python 3.12 字符串字面量](https://docs.python.org/3.12/reference/lexical_analysis.html#string-and-bytes-literals)
- [Python 3.12 return 和 yield](https://docs.python.org/3.12/reference/simple_stmts.html#the-return-statement)
- [Python 3.12 类和实例](https://docs.python.org/3.12/tutorial/classes.html#class-and-instance-variables)
- [Python 3.12 继承与多继承](https://docs.python.org/3.12/tutorial/classes.html#inheritance)
- [Python 3.12 控制流](https://docs.python.org/3.12/tutorial/controlflow.html)
- [Python 3.12 函数定义](https://docs.python.org/3.12/tutorial/controlflow.html#defining-functions)
- [Python 3.12 lambda](https://docs.python.org/3.12/tutorial/controlflow.html#lambda-expressions)
- [SQLAlchemy 2.0 asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI workers](https://fastapi.tiangolo.com/deployment/server-workers/)
- [FastAPI 安全教程](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [FastAPI 密码哈希](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#password-hashing)
- [Flask 3.1 设计](https://flask.palletsprojects.com/en/stable/design/)
- [FastAPI 0.141.1 设置](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/advanced/settings.md)
- [FastAPI 0.141.1 模板](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/advanced/templates.md)
- [FastAPI 0.141.1 WebSocket](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/advanced/websockets.md)
- [FastAPI 0.141.1 异步与调用机制](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/async.md)
- [0.141.1 容器部署](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/deployment/docker.md)
- [FastAPI 0.141.1 GraphQL](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/how-to/graphql.md)
- [FastAPI 0.141.1 后台任务](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/tutorial/background-tasks.md)
- [FastAPI 0.141.1 CORS](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/tutorial/cors.md)
- [FastAPI 0.141.1 yield 依赖](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/tutorial/dependencies/dependencies-with-yield.md)
- [FastAPI 0.141.1 子依赖缓存](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/tutorial/dependencies/sub-dependencies.md)
- [FastAPI 0.141.1 上传](https://github.com/fastapi/fastapi/blob/0.141.1/docs/en/docs/tutorial/request-files.md)
- [NumPy 2.3 索引](https://numpy.org/doc/2.3/user/basics.indexing.html)

## AI Coding 练习附录

[对应章节](../docs/70-practice/ai-coding-exercises.md)

- [datetime](https://docs.python.org/3.12/library/datetime.html)
- [Python 3.12 Decimal](https://docs.python.org/3.12/library/decimal.html)
- [Python 3.12 JSON](https://docs.python.org/3.12/library/json.html)
- [Python 3.12 shlex](https://docs.python.org/3.12/library/shlex.html)
- [arXiv 官方 API 手册](https://info.arxiv.org/help/api/user-manual.html)

## Original retrieval and tool contract experiments

[对应章节](../examples/retrieval_contracts/README.md)

- [Agent Skills format](https://agentskills.io/specification)
- [AnyIO 4.14.2 source](https://github.com/agronholm/anyio/tree/4.14.2)
- [MCP SDK v1.29.0 FastMCP source](https://github.com/modelcontextprotocol/python-sdk/blob/v1.29.0/src/mcp/server/fastmcp/server.py)
- [MCP SDK v1.29.0 protocol versions](https://github.com/modelcontextprotocol/python-sdk/blob/v1.29.0/src/mcp/shared/version.py)
- [Pydantic v2.13.4 source](https://github.com/pydantic/pydantic/tree/v2.13.4)
- [CPython v3.12.14 sqlite3 source](https://github.com/python/cpython/tree/v3.12.14/Lib/sqlite3)
- [SQLite window functions](https://www.sqlite.org/windowfunctions.html)

## Fixture schema and query meanings

[对应章节](../examples/retrieval_contracts/skills/store-report/references/schema.md)

- [Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html)
- [SQLite query planning](https://www.sqlite.org/queryplanner.html)
- [SQLite window functions](https://www.sqlite.org/windowfunctions.html)
