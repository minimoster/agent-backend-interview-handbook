# 静态阅读页

这个目录为仓库中的原创讲义提供一个适合长期阅读的轻量入口：专题导航、中文全文搜索、章内目录、主题与算法难度筛选、知识区折叠、明暗主题，以及本机收藏与已读标记。

## 打开阅读

- **在线**：[打开学习讲义](https://minimoster.github.io/agent-backend-interview-handbook/)。在线版由 GitHub Pages 提供静态文件，使用同一套阅读与搜索功能。
- **离线**：下载整个仓库后，直接用现代浏览器打开 `site/index.html`。JavaScript、样式、搜索数据和关联源码都随仓库提供，不需要联网，也不使用 `file://` 下的 `fetch`。
- **本地静态服务器**：在仓库根目录执行 `python -m http.server 8000 --directory site`，再打开 `http://localhost:8000`。Python 只用于预览，不是运行页面的必需依赖。
- **Markdown 备用入口**：[GitHub 仓库](https://github.com/minimoster/agent-backend-interview-handbook)保留原始讲义与源码。阅读页内的“GitHub 原文”与代码旁的 GitHub 链接指向本仓库的 `main` 分支。

不需要账号、后端接口、数据库、CDN 或外部字体。阅读记录只保存在当前浏览器，页面没有分析统计或远端数据接口；只有主动点击外部参考链接时才离开阅读页。下载后的离线版不需要请求在线资源。

## 怎样使用

1. 首页按学习路线或专题进入，先建立一条主线。
2. 顶部搜索同时匹配标题、题号与正文。可以输入 `A01`、`LC287`、`线程池`、`极端哈希碰撞`；多个词用空格分隔，要求全部匹配。按 `/` 或 `Ctrl/Cmd + K` 可聚焦搜索。
3. 主题筛选可定位 Hot100 的 17 类模式；简单、中等、困难采用题单中的官方算法难度。P0 / P1 / P2 表示学习优先级，优先级筛选按整章包含的题目匹配。
   - “算法补充资源”另列15道非Hot100练习，按题号、标题、分类和已核验的官方难度搜索。它们指向一份资源练习单中的独立小节，不代表15份原创代码。
   - Hot100 阅读页提供“代码随想录·对照学习”入口，准确区分本题精确讲解、对应Python、直接视频与相关题迁移视频；外部作者署名和核验日期保留在页面中。
4. 阅读页的目录直接定位小节。可以收起知识区或解答，先尝试独立解释，再展开对照。代码块可横向滚动和复制；复制权限受浏览器限制时，仍可手动选择文本。
5. 调整正文大小、行距与明暗主题。收藏、已读和上次阅读位置只存在当前浏览器的本地存储，不上传、不跨设备同步。清除浏览器数据会清除这些记录；禁用本地存储时，本次打开期间仍可使用。

页面使用响应式 CSS 与原生链接、按钮、输入框和 `details`。手机导航支持 Esc 关闭和键盘焦点约束；正文与代码分别控制换行，长代码不会要求整页横向滚动。

## 更新与可复现构建

**源码只有一份**：`docs/`、仓库索引和关联的 `examples/` / `tests/` 文件是内容来源。`site/assets/data.*.js`、`site/assets/data.js` 与 `site/assets/repo/` 是自动生成的阅读产物，不在它们里面修正文。

需要 Node.js 20 或以上；构建无联网、无安装步骤：

```bash
# 从仓库根目录执行
node site/build.mjs
node site/build.mjs --check
node site/test.mjs
```

- 构建读取稳定的 `content-index.json`、Hot100 `manifest.json` 和当前 Markdown 原文，生成 HTML、章内锚点及搜索段落。阅读数据使用内容摘要命名的本地脚本分片，入口按顺序加载；离线时仍无需fetch。
- 有代码随想录资源映射时，同时读取 `sources/carl-hot100-resources.json`，生成直接/相关资源入口与15个补充题检索条目。原始461条讲义与Hot100索引不变，补充题独立计数。
- `docs/`、`examples/`、`coverage/`、`errata/`、`sources/` 中的 Markdown 都进入同一阅读层；这些文件互相链接时会转为站内路由，不会把 README 单独复制成缺少关联文件的资源。
- `--check` 检查源文和关联源码与已提交的阅读产物是否一致。修改内容后，应重建并一并提交生成文件。
- `test.mjs` 检查索引覆盖、原文一致性、本地锚点与资源、输出安全和实际搜索模型。它是非渲染自动检查，不能代替实际浏览器、手机或辅助技术测试。
- 生成数据有 SHA-256 源摘要，无构建时间戳。同一套输入得到相同输出。
- GitHub 备用地址与分支在 `site/config.json` 中配置；仓库迁移后修改它并重新构建。

Markdown 渲染器为随目录提供的 Marked 17.0.5，MIT 许可保存在 `vendor/marked.LICENSE.md`。构建器仅允许必要的 Markdown 锚点，不把任意原始 HTML 或脚本当作可执行页面内容。

## GitHub Pages 发布

在线入口为 [minimoster.github.io/agent-backend-interview-handbook](https://minimoster.github.io/agent-backend-interview-handbook/)。仓库的 `.github/workflows/pages.yml` 将 `site/` 发布为静态站点，`main` 分支的 `site/` 或该工作流变更会触发部署，也支持手动运行。

更新正文后，先运行构建与检查，再一并提交原文和生成产物；部署工作流使用已提交的静态文件，不会替你重建。保留 `index.html`、`.nojekyll` 和整个 `assets/`。页面使用相对资源路径和 hash 路由，不依赖服务端路由重写，离线入口仍可单独使用。

