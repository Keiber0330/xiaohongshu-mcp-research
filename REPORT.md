# 小红书 (Xiaohongshu / RED) 数据访问 MCP 工具调研报告

调研日期：2026-10-01 · 执行环境：Claude Code 云端容器 (Linux x64)

> **先说结论里最重要的一点**：本环境的网络策略**屏蔽了所有小红书域名**
> (`www.xiaohongshu.com`、`edith.xiaohongshu.com`、`*.xhscdn.com`、`www.rednote.com`)，
> 以及 xpzouying 项目的浏览器分发 CDN `cdn.one-world.ai`（代理返回 403）。
> 因此**本报告中没有任何一项"真实获取小红书数据"的测试是 PASS**。
> 下文凡是写"源码确认"的，都是读源码得出的，不是实测；凡是写"实测"的，都有对应的输出文件在 `results/`。

---

## 0. 哪些步骤做了、哪些做不了

| 步骤 | 状态 | 说明 |
|---|---|---|
| 1 搜索 GitHub | ✅ 完成（有限制） | GitHub 搜索 API 在本会话被禁用，改用 Web 搜索 + 逐个 `git clone` + 读 git 历史获取真实活跃度 |
| 2 候选比较 | ✅ 完成 | 克隆了 16 个仓库，深读了 7 个的源码 |
| 3 选型 | ✅ 完成 | 见 C 节 |
| 4 下载安装 | ✅ 完成 | 两个推荐项目都已编译/安装，源码已做安全审查 |
| 5 功能实测 | ❌ **无法执行** | 小红书域名被网络策略屏蔽；而且需要你的账号扫码登录 |
| 6 JSON/CSV 导出 | ✅ 脚本完成并测试 | 用**合成样例数据**测试（明确标注，非真实数据） |
| 7 MCP 测试 | ✅ 协议层实测通过 | 握手、`tools/list`、`tools/call` 均已实测；数据返回因网络阻断为失败 |
| 8 风险评估 | ✅ 完成 | 见 J 节 |

---

## A. 找到的候选 GitHub 项目

活跃度来自 `git log`（实测，截至 2026-10-01）；Star 数来自 GitHub 页面。

| 项目 | Star | 最后提交 | 近 3 个月提交 | 技术栈 | 原生 MCP | 许可证 |
|---|---|---|---|---|---|---|
| [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) | 16.1k | 2026-09-23 | 67 | Go + go-rod + 定制 Chromium | ✅ 18 个工具 | Apache-2.0 |
| [JoeanAmier/XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) | 12.9k | 2026-09-16 | 79 | Python + curl_cffi + fastmcp | ✅ 2 个工具 | GPL-3.0 |
| [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) | 66.1k | 2026-09-19 | 29 | Python + Playwright | ❌ | 非商业学习许可 |
| [cv-cat/Spider_XHS](https://github.com/cv-cat/Spider_XHS) | 8.0k | 2026-09-27 | 16 | Python + Node.js 签名 | ❌ | MIT |
| [jobsonlook/xhs-mcp](https://github.com/jobsonlook/xhs-mcp) | 517 | 2026-08-24 | 1 | Python + Playwright + 混淆 JS | ✅ 6 个工具 | pyproject 写 MIT，仓库无 LICENSE 文件 |
| [iFurySt/RedNote-MCP](https://github.com/iFurySt/RedNote-MCP) | 1.1k | 2025-05-11 | 0（停更） | TypeScript + Playwright | ✅ 4 个工具 | MIT |
| [ReaJason/xhs](https://github.com/ReaJason/xhs) | 2.2k | 2025-07-01 | 0（停更） | Python | ❌ | MIT |
| [ShunL12324/xhs-mcp](https://github.com/ShunL12324/xhs-mcp) | 47 | 2026-02-23 | 0 | TS + patchright（反检测版 Playwright） | ✅ | MIT |
| [sykuang/rednote-mcp](https://github.com/sykuang/rednote-mcp) | 4 | 2026-07-28 | 12 | TS + Playwright | ✅ | MIT |
| [DevinChen2014/xiaohongshu-xhs-rednote-mcp](https://github.com/DevinChen2014/xiaohongshu-xhs-rednote-mcp) | 2 | 2026-09-29 | 28 | 只是配置文件 | 远程 MCP | MIT |

其余查看过但排除的：`vmxmy/xiaohongshu-mcp`（xpzouying 的 fork，2026-03 起停更）、`TimeCyber/mcp-xiaohongshu`（2025-06 后无提交）、
`chenningling/RedBook-Search-Comment-MCP`（2025-04 后无提交，以自动评论为主）、`ShellyDeng08/rednote-analyzer-mcp`（2026-03 后无提交）、
`shanyang-me/xhs-mcp`（只有 3 次提交，依赖 `playwright-stealth`）。

**特别提醒**：`DevinChen2014/...` 不是开源实现。它只是指向付费第三方服务 `https://mcp.socialdatax.com/xhs/mcp` 的配置，
需要 API Key，数据经过第三方服务器，不符合"开源、本地可审查"的要求。

---

## B. 横向比较（源码确认，不是 README）

### B.1 数据访问方式分类

| 类型 | 项目 | 源码证据 |
|---|---|---|
| **官方 API** | **没有任何项目使用** | 所有项目都访问网页端 |
| 浏览器自动化 + 读页面内嵌状态 | xpzouying | `xiaohongshu/*.go` 用 go-rod 打开页面，读取 `window.__INITIAL_STATE__` |
| HTML 页面解析（无浏览器） | XHS-Downloader（MCP 路径） | `source/expansion/converter.py` 从 HTML 的 `<script>` 中解析 `window.__INITIAL_STATE__` |
| 浏览器自动化 + DOM 选择器 | iFurySt/RedNote-MCP | `src/tools/noteDetail.ts` 用 `.note-container`、`#detail-title` 等 CSS 选择器 |
| 逆向接口（在浏览器内签名） | jobsonlook/xhs-mcp v2、MediaCrawler | 直接请求 `edith.xiaohongshu.com/api/sns/web/...`，签名在页面里生成 |
| 逆向接口（本地复现签名算法） | Spider_XHS、MediaCrawler (`xhs_sign.py`)、jobsonlook v1（595 KB 混淆 JS）、XHS-Downloader 的 `user_posted.py`（依赖 `xhshow`，MCP 未使用） | 复现了 `x-s` / `x-s-common` 签名 |

### B.2 功能矩阵（源码确认）

| 能力 | xpzouying | XHS-Downloader | MediaCrawler | Spider_XHS | jobsonlook |
|---|---|---|---|---|---|
| 原生 MCP | ✅ HTTP | ✅ HTTP（stdio 有 bug，见 E） | ❌ | ❌ | ✅ stdio |
| 关键词搜索 | ✅ 支持筛选 | ❌ | ✅ | ✅ | ✅ |
| 笔记详情 | ✅ | ✅（按链接） | ✅ | ✅ | ✅ |
| 作者主页/公开信息 | ✅ | ⚠️ 只有笔记里的昵称和 ID | ✅ | ✅ | ❌ |
| 作者历史笔记 | ⚠️ 只有第一页 | ❌ | ✅ 全量 | ✅ 全量 | ❌ |
| 评论 | ✅ 含子评论，可滚动加载 | ❌ | ✅ 含子评论 | ✅ | ⚠️ 只有第一页 |
| 图片 URL | ✅ | ✅ | ✅ | ✅ | ✅ |
| 视频 URL | ✅（带签名、会过期） | ✅ | ✅ | ✅ | ? |
| 搜索分页 | ❌ 没有 page/cursor 参数 | — | ✅ | ✅ | ❌ 固定 page=1 |
| 批量 | ❌ 每次调用都启动一个新浏览器 | ⚠️ CLI 支持多链接，MCP 一次一条 | ✅ | ✅ | ❌ |
| 需要登录 | ✅ 搜索/详情/主页都需要 | ⚠️ 可选 cookie | ✅ | ✅ cookie | ✅ cookie |
| 需要 cookie | 登录后自动存入本地 `cookies.json` | 可选 | ✅ | ✅ 手动粘贴 | ✅ 环境变量 `XHS_COOKIE` |
| 扫码登录 | ✅ | ❌ | ✅（也支持手机号/cookie） | ❌ | ❌ |
| 浏览器依赖 | go-rod + **专用指纹 Chromium** | 无 | Playwright/CDP | 无（Node 跑签名） | Playwright |
| 反检测手段 | **指纹伪装浏览器、拟人化鼠标/输入** | curl_cffi 模拟浏览器 TLS 指纹 | `stealth.min.js`、IP 代理池 | 签名伪造 | 隐藏 `navigator.webdriver` |
| 易失效程度 | 中高（依赖 DOM 点击和页面状态） | 中（依赖 SSR 状态） | 高（签名算法），但维护积极 | 高（签名算法） | 高 |
| Windows / macOS | Win x64、mac arm64（不支持 Intel Mac） | ✅ | ✅ | ✅ | ✅ |
| 导出 JSON/CSV | 只有 JSON（经 MCP/HTTP 返回） | JSON + 下载文件 | CSV/JSON/JSONL/SQLite/Excel/DB | Excel | JSON |
| 接入 Claude 难度 | 低 | 低 | 中（需要封装） | 中（需要封装） | 低 |

---

## C. 最推荐测试的项目

### 首选：xpzouying/xiaohongshu-mcp（功能最完整，但有重要保留意见）

选它的原因：
1. 唯一一个原生 MCP、同时支持**搜索 + 详情 + 评论 + 作者主页**的活跃项目（近 3 个月 67 次提交，31 名贡献者）。
2. 返回结构化 JSON，字段最丰富：互动数、图片、视频流、字幕、评论树、IP 属地。
3. 安装简单：有预编译二进制或 Docker；MCP 是标准 Streamable HTTP。
4. 没有逆向签名：数据读自页面内嵌的 `__INITIAL_STATE__`，不需要伪造请求签名。

**必须告诉你的保留意见**（源码确认）：
- **它在设计上就是为了规避机器人检测。** 自 v2.0（2026-07）起，强制使用一个"指纹 Chromium"
  （`--fingerprint=<seed>`、`--fingerprint-platform`，Linux 上会伪装成 Windows），
  并带有 `humanize/` 拟人化鼠标轨迹和输入节奏。你要求"不要绕过反机器人系统"，这一点与该要求**存在冲突**，需要你自己判断能否接受。
- **未知二进制**：这个浏览器从 `https://cdn.one-world.ai/browsers/<版本>/` 下载。工作流注释写明
  "公开 repo 不引用上游"，即公开仓库不披露上游来源。SHA256 校验文件来自**同一个 CDN**，所以校验只能防传输损坏，防不了供应链被替换。
- **本地 HTTP 服务默认无鉴权、CORS 为 `*`、监听所有网卡**（`:18060`）。任何你浏览的网页都可能通过浏览器向
  `localhost:18060` 发请求，包括"发布""评论"接口。**务必设置 `AUTH_TOKEN`**。

### 次选（低风险补充）：JoeanAmier/XHS-Downloader 的 MCP 模式

选它的原因：手里已经有笔记链接时，这是**风险最低**的方案。普通 HTTP 请求公开笔记页面，不跑浏览器、不伪造签名，cookie 可选，返回结构化数据。
不足：MCP 只有 2 个工具，**不能搜索、不能拿评论、不能拿作者主页**。

两者可以组合使用：用 xpzouying 搜索拿到 `note_id + xsec_token`，再用 XHS-Downloader 逐条取详情。

### 不推荐
- **MediaCrawler**：数据能力最强，但没有 MCP；许可证是**非商业学习许可**，且明确禁止"大规模爬取"；内置 IP 代理池、stealth 脚本、短信验证码接收（`recv_sms.py`），反检测色彩最重。
- **jobsonlook/xhs-mcp**：签名逻辑在 595 KB 的**混淆 JS** 里，无法审计；近期基本不维护。
- **iFurySt/RedNote-MCP**：停更 17 个月，CSS 选择器多半已失效；`package.json` 里还有一个**没被使用**的第三方包 `mcp-sdk@0.1.0`（无安装脚本，风险低，但没必要存在）。

---

## D. 实际安装过程（实测）

### xpzouying/xiaohongshu-mcp
```
git clone https://github.com/xpzouying/xiaohongshu-mcp   # HEAD = 2026-09-23 (v2.5.5)
go build -o xhs-mcp .            # ✅ 成功 (Go 1.24.7)
go vet ./... && go test ./...    # ✅ 9 个包全部通过
./xhs-mcp -port :18060           # ❌ 退出：下载内置浏览器失败 cdn.one-world.ai → 403 Forbidden
```
没有浏览器它拒绝启动（`browser.go` 中是有意为之）。为了在不运行这个二进制、也不访问小红书的情况下验证 MCP 层，
我写了 `tests/xpzouying/zz_mcp_discovery_test.go`：在进程内挂载项目**真实的** gin 路由和 MCP handler，再用官方 Go MCP SDK 客户端连接。

### JoeanAmier/XHS-Downloader
```
git clone https://github.com/JoeanAmier/XHS-Downloader   # HEAD = 2026-09-16 (v2.8)
uv sync                          # ❌ uv.lock 把源固定在 mirrors.ustc.edu.cn（中国科大镜像），本环境无法访问
uv venv .venv-pypi -p 3.12 && uv pip install --index-url https://pypi.org/simple -r requirements.txt   # ✅
python main.py mcp               # ✅ 启动，监听 http://0.0.0.0:5556/mcp
```

### 安全审查结果（两个推荐项目）

| 检查项 | xpzouying | XHS-Downloader |
|---|---|---|
| 上传 cookie/token 到第三方 | 未发现。cookie 只存本地 `cookies.json` | 未发现 |
| 硬编码远程地址 | `cdn.one-world.ai`（浏览器下载）；其余均为 `*.xiaohongshu.com` | 只有 `*.xiaohongshu.com`、`*.xhscdn.com`、GitHub 链接 |
| 未知二进制 | ⚠️ **有**：定制 Chromium，上游来源未披露 | 无 |
| 危险 shell 命令 | macOS 上会执行 `hdiutil`、`cp`、`xattr -dr com.apple.quarantine`（去掉 Gatekeeper 隔离标记） | 无 |
| 网络暴露 | ⚠️ 监听所有网卡、默认无鉴权、CORS `*` | ⚠️ 监听 `0.0.0.0:5556`、无鉴权 |
| 其他 | 无遥测 | fastmcp 启动时会检查自身更新（PyPI） |

---

## E. 遇到的问题

1. **小红书全部域名被本环境网络策略屏蔽（403）**，真实数据测试无法进行。
2. **GitHub 搜索 API 被会话策略禁用**，改用 Web 搜索 + git clone。
3. **xpzouying 没有内置浏览器就拒绝启动**，而浏览器 CDN 也被屏蔽。
4. **XHS-Downloader 的 `uv.lock` 固定使用中国镜像**，改为从 PyPI 安装。
5. **XHS-Downloader 上游的 stdio 模式有 bug**：`run_mcp_server()` 总是传 `host/port`，fastmcp 的 stdio 运行器会抛 `TypeError`（实测）。
   我在 `tools/xhs_downloader_stdio.py` 里做了约 15 行的补丁，没有修改上游代码，补丁后 stdio 实测可用。
6. **XHS-Downloader 抓取失败时 `is_error=false`**：返回 `{"message":"获取小红书作品数据失败","data":{}}`（实测）。
   Claude 不会把它当作错误，需要检查 `data` 是否为空。
7. **分享数字段名不一致**：xpzouying 和多数项目读 `interactInfo.sharedCount`，XHS-Downloader 读 `interactInfo.shareCount`。
   至少有一方会拿到空值，需要实测确认。我的导出脚本两个字段名都接受。
8. **fastmcp 4.x 默认走新的协议协商方式**，没有 `InitializeResult`；测试脚本改用 `mode="legacy"`，与 Claude 客户端的握手方式一致。

---

## F. 实际测试结果

### F.1 小红书数据能力：20 项

"实测"列是本环境的结果；"源码判断"列是读源码得出的，**不能当作测试结论**。

| # | 能力 | 实测（本环境） | xpzouying 源码判断 | XHS-Downloader 源码判断 |
|---|---|---|---|---|
| 1 | 搜索关键词 | **PASS**（用户本地第 2 次实测；云端为 BLOCKED） | 支持 | NOT SUPPORTED |
| 2 | 获取搜索结果 | **PASS**（用户本地实测："咖啡"返回 20 条） | 支持（只有第一页） | NOT SUPPORTED |
| 3 | 获取笔记 ID | BLOCKED | 支持 | 支持 |
| 4 | 获取笔记标题 | BLOCKED | 支持 | 支持 |
| 5 | 获取正文 | BLOCKED | 只能通过详情接口 | 支持 |
| 6 | 获取发布时间 | BLOCKED | 只能通过详情接口 | 支持 |
| 7 | 获取作者昵称 | BLOCKED | 支持 | 支持 |
| 8 | 获取作者 ID | BLOCKED | 支持 | 支持 |
| 9 | 获取点赞数 | BLOCKED | 支持 | 支持 |
| 10 | 获取收藏数 | BLOCKED | 支持（详情） | 支持 |
| 11 | 获取评论数 | BLOCKED | 支持（详情） | 支持 |
| 12 | 获取分享数 | BLOCKED | 支持（详情） | ⚠️ 字段名可能不对 |
| 13 | 获取图片 URL | BLOCKED | 支持 | 支持 |
| 14 | 获取视频 URL | BLOCKED | 支持（带签名、会过期） | 支持 |
| 15 | 获取评论内容 | BLOCKED | 支持（默认前 10 条，可滚动加载更多） | NOT SUPPORTED |
| 16 | 获取评论用户 | BLOCKED | 支持 | NOT SUPPORTED |
| 17 | 获取作者主页 | BLOCKED | 支持 | NOT SUPPORTED |
| 18 | 获取作者历史笔记 | BLOCKED | PARTIAL（只有第一页） | NOT SUPPORTED |
| 19 | 分页 | BLOCKED | NOT SUPPORTED（搜索没有分页参数，实测 schema 确认） | NOT SUPPORTED |
| 20 | 批量请求 | BLOCKED | NOT SUPPORTED（只能逐条调用） | 每次一条 |

第 19 项是唯一一项"实测"得出的结论：`tools/list` 返回的 `search_feeds` 只有 `keyword` 和 `filters` 两个参数。

**你可以在自己电脑上补完这张表**：`tests/run_live_check.py` 会依次调用只读工具，带间隔、少量请求，
自动生成 PASS/FAIL/PARTIAL/NOT SUPPORTED 矩阵和原始响应。我已经在本环境用 mock 服务器（返回合成数据）验证过脚本本身可用。

### F.1b 用户本地实测（2026-10-03，用户本人账号，本机 127.0.0.1）

原始记录：`results/live_local_2026-10-03.md`。这是本项目**第一份连到真实小红书的结果**。

| 检查 | 结果 | 说明 |
|---|---|---|
| 健康检查 `/health` | ✅ PASS | HTTP 200 |
| 只监听本机 | ✅ PASS | 用户把监听地址改成了 127.0.0.1，没有用默认的所有网卡 |
| 不带 token 的请求被拒 | ✅ PASS | HTTP 401（`AUTH_TOKEN` 生效） |
| 带 token 的 MCP 初始化 | ✅ PASS | |
| `tools/list` | ✅ PASS | 18 个工具，与本环境实测一致 |
| `check_login_status` | ✅ PASS | 扫码登录成功，状态为已登录 |
| `search_feeds`（关键词"咖啡"），第 1 次 21:06 | ⚠️ PARTIAL | 调用成功、没有报错，但**返回 0 条笔记** |
| `search_feeds`（关键词"咖啡"），第 2 次 21:21 | ✅ **PASS** | **返回 20 条笔记**（`results/live_local_2026-10-03_run2.md`） |
| `run_live_check.py` 第 3 次 22:05 | ❌ | `check_login_status` **超时（32.8 秒）**；`search_feeds` 用时 35.4 秒、**0 条**；其余 18 项未执行（`results/live_local_2026-10-03_run3_matrix.md`） |
| 其余 13 项（详情、评论、作者等） | 未测 | 当时用户本地还没有 `tests/run_live_check.py` |

**三次运行的规律**：唯一成功的第 2 次是用**可视模式**（`-headless=false`）跑的；第 1、3 次推测是默认无头模式，都是 0 条。
第 3 次连 `check_login_status` 都超时了。查源码，它只给小红书首页 30 秒加载时间（`xiaohongshu/login.go` 第 22–23 行），
说明那次**连页面都没有加载完成**，不是登录态失效。样本只有 3 次，还不能确定原因：可能是无头模式被平台区别对待，
也可能是网络或平台当时响应慢。**本研究不会尝试让无头浏览器"更像真人"来规避检测**，下一步只在可视模式下复测。
`run_live_check.py` 已加入"搜索 0 条时等 60 秒再重试一次"（`--search-retries`、`--retry-wait`）。

**第 2 次搜索成功**，说明 0 条并非搜索功能完全失效。没有观察浏览器窗口，所以无法确定具体原因，
可能是结果加载完成前就读取了页面，也可能是短时的平台限制。实际研究中**要允许重试，并把"0 条"当作需要复查的结果，不能当作"没有内容"**。
20 条与源码判断一致：只返回第一页，无法翻页。

**第 1 次为什么是 0 条（源码分析）**：`xiaohongshu/search.go` 打开搜索页后读取 `window.__INITIAL_STATE__.search.feeds`，
再用 `onlyNotes()` 过滤掉非笔记条目。返回 0 条且不报错，只可能是这两种情况之一：
(a) 页面里的结果列表本身是空的，例如出现了验证页、结果还没加载完就读取了，或者账号搜索受限；
(b) 列表里只有直播卡片或热词等非笔记条目，全被过滤掉了。
"咖啡"这种热门词正常情况下必然有结果，所以这**不是**"真的没有内容"。
上游仓库在 2026-10-04 查看时，没有与"搜索返回 0 条"直接对应的 issue，只有超时类问题（#813、#836）。

为了在搜索不可用时仍能测其余项目，`tests/run_live_check.py` 新增了 `--note-url` 参数：
用户从浏览器地址栏复制带 `xsec_token` 的笔记链接，脚本据此测试详情、评论、作者主页等项目。
用这种方式拿到的结果会标注"来自链接、不是来自搜索"。

### F.2 MCP 协议层（实测通过）

| 测试 | xpzouying | XHS-Downloader |
|---|---|---|
| MCP server 能否启动 | ⚠️ 二进制启动不了（没有浏览器）；真实路由在进程内挂载后 ✅ | ✅ HTTP 和 stdio（stdio 需补丁）都 ✅ |
| `initialize` 握手 | ✅ server `xiaohongshu-mcp 2.0.0`，协议 `2025-06-18` | ✅ server `XHS-Downloader 2.8.stable` |
| `tools/list` | ✅ 18 个工具（`results/xpzouying_tools_list.json`） | ✅ 2 个工具（`results/xhs_downloader_mcp_probe.json`） |
| `tools/call` | ✅ 调用链路通，结果是预期中的错误（无浏览器） | ✅ 调用链路通，结果是"获取失败"（网络 403） |

---

## G. 可以获取的数据字段（源码中的结构体）

**xpzouying `search_feeds`**（每个结果卡片）：`id`、`xsecToken`、`modelType`、`noteCard.type`、`noteCard.displayTitle`、
`noteCard.user{userId,nickname,avatar}`、`noteCard.interactInfo{likedCount,collectedCount,commentCount,sharedCount}`、
`noteCard.cover{urlDefault,…}`、`noteCard.video.capa.duration`。**没有正文、没有发布时间**。

**xpzouying `get_feed_detail`**：`note{noteId,xsecToken,title,desc,type,time,ipLocation,user,interactInfo,imageList[{urlDefault,urlPre,width,height,livePhoto}],video{media.stream{h264/h265/av1:[{masterUrl,backupUrls,width,height,…}]},subtitles}}`、
`comments{list[{id,content,likeCount,createTime,ipLocation,userInfo,subCommentCount,subComments[…]}],cursor,hasMore}`。

**xpzouying `user_profile`**：`userBasicInfo{nickname,desc,gender,ipLocation,redId,images}`、`interactions[{type,name,count}]`（关注/粉丝/获赞与收藏）、`feeds[…]`（第一页）。

**XHS-Downloader `get_detail_data`**：`作品ID、作品链接、作品标题、作品描述、作品类型、作品标签、发布时间、最后更新时间、时间戳、
作者昵称、作者ID、作者链接、点赞数量、收藏数量、评论数量、分享数量、下载地址[]、动图地址[]`。

---

## H. MCP tools 列表（实测 `tools/list` 结果）

### xpzouying/xiaohongshu-mcp（18 个）

| 工具 | 只读 | 参数 |
|---|---|---|
| `check_login_status` | ✅ | — |
| `get_login_qrcode` | ✅ | — |
| `delete_cookies` | ❌ | — |
| `list_feeds` | ✅ | — |
| `search_feeds` | ✅ | `keyword`，`filters{sort_by,note_type,publish_time,search_scope,location}` |
| `get_feed_detail` | ✅ | `feed_id`、`xsec_token`、`load_all_comments`、`limit`、`click_more_replies`、`reply_limit`、`scroll_speed` |
| `user_profile` | ✅ | `user_id`、`xsec_token`、`tab`(note/fav/liked) |
| `get_my_profile` | ✅ | `tab` |
| `get_unread_count` | ✅ | — |
| `list_notifications` | ✅（但会清除未读标记） | `tab`、`limit` |
| `publish_content` / `publish_with_video` | ❌ | 标题、正文、图片/视频、标签、定时、可见范围、商品 |
| `post_comment_to_feed` / `reply_comment_in_feed` | ❌ | `feed_id`、`xsec_token`、`content`… |
| `like_feed` / `favorite_feed` | ❌ | `feed_id`、`xsec_token`、`unlike`/`unfavorite` |
| `reply_notification` / `like_notification` | ❌ | `comment_id`… |

> 建议：只做研究时，在 Claude 的权限设置里**只允许只读工具**，禁止 publish/comment/like 类工具被自动调用。

### XHS-Downloader（2 个）
| 工具 | 参数 |
|---|---|
| `get_detail_data` | `url`（`/explore/…`、`/discovery/item/…`、`xhslink.com/…`） |
| `download_detail` | `url`、`index`（图片序号）、`return_data` |

### MCP 配置示例
见 `configs/claude_code.md` 和 `configs/claude_desktop_config.example.json`。最简形式：
```bash
claude mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp --header "Authorization: Bearer <你的AUTH_TOKEN>"
claude mcp add xhs-downloader --env XHS_DOWNLOADER_DIR=/abs/XHS-Downloader -- /abs/XHS-Downloader/.venv/bin/python /abs/xiaohongshu-mcp-research/tools/xhs_downloader_stdio.py
```

---

## I. CSV / JSON 导出

两个项目都**没有**按你要求字段导出 CSV 的功能（xpzouying 只返回 JSON；XHS-Downloader 主要是下载文件）。
我写了 `tools/xhs_export.py`（只用 Python 标准库）：
- 输入：两个项目各工具返回的 JSON，或 `run_live_check.py` 保存的原始响应；
- 同一个 `note_id` 的多条记录会合并（详情字段覆盖搜索卡片的空字段）；
- 输出 `notes.json`、`notes.csv`、`comments.csv`；CSV 用 UTF-8 BOM 编码，Excel 打开中文不会乱码。

`notes.csv` 列：`note_id,title,description,author_name,author_id,publish_time,likes,favorites,comments,shares,image_urls,video_url,note_url,keyword,crawl_time`
外加 `note_type,ip_location,tags,xsec_token,source`。`comments.csv` 保留父子评论关系（`parent_comment_id`）。

测试：`tests/test_xhs_export.py` 共 5 个用例，**全部通过**。测试用的是 `tests/fixtures/` 里的**合成数据**
（照源码结构体手写，所有值都标了 `FIXTURE`）。导出样例在 `results/fixture_export/`。
用实测失败的真实 MCP 响应（`data:{}`）跑导出，结果正确为 0 行（`results/real_call_export/`）。

---

## J. 风险与限制

| 问题 | 回答 |
|---|---|
| 是否依赖非官方 API | **是，全部都是。** 没找到任何使用官方开放接口读取内容的开源项目。最好的情况也只是读网页内嵌状态（xpzouying、XHS-Downloader）；其余是逆向签名接口 |
| 是否容易被接口更新破坏 | **是。** xpzouying 依赖 DOM 结构和点击流程，近 3 个月有大量 `fix(search)`、`fix(feed)` 提交，说明网站经常变动；签名类项目每次算法更新都会失效 |
| 是否可能触发 rate limit | **是。** MediaCrawler 的 issue 里有 461 状态码（风控）报告；xpzouying 每次调用都启动一个完整浏览器，本身就慢 |
| 是否需要登录账号 | xpzouying：搜索、详情、主页都需要。XHS-Downloader：单条公开笔记 cookie 可选（README 所述，**未实测**） |
| 账号限制风险 | **有。** xpzouying README 自述：同一账号不能在多个网页端同时登录（会互踢），新账号可能被要求实名认证。建议用专门的研究账号，不要用主账号 |
| 是否适合长期使用 | 不太适合。需要持续跟进上游修复，登录态会过期，需要重新扫码 |
| 是否适合批量研究 | **不适合大批量。** 没有分页、没有批量接口；MediaCrawler 的许可证明确禁止大规模爬取。适合几十到几百条量级的定性研究 |
| ToS / 合规风险 | **明显存在。** 自动化访问、绕过签名或指纹检测，通常违反平台用户协议；采集到的数据包含个人信息（昵称、IP 属地、评论），在中国适用《个人信息保护法》，用于研究需要做匿名化、最小化处理。各项目 README 也都声明"仅供学习"。**我不是律师**，正式研究项目建议咨询所在机构的伦理/法务部门 |
| 与你设定边界的冲突 | xpzouying（指纹伪装 + 拟人化操作）、MediaCrawler（stealth + 代理池）、ShunL12324（patchright）、jobsonlook（隐藏 webdriver + 签名）都包含**规避检测**的设计。XHS-Downloader 的 MCP 路径最轻：只有 curl_cffi 的浏览器 TLS 指纹模拟 |

---

## K. 是否值得继续使用

- **小规模、定性研究**（几十到几百条笔记，人工监督，用专门账号）：**值得一试。**
  在自己的电脑（Windows x64 或 Apple Silicon Mac）上跑 xpzouying，一定设置 `AUTH_TOKEN`，只开放只读工具，
  然后运行 `tests/run_live_check.py` 拿到真实的 20 项结果，再决定。
- **已有笔记链接，只要详情和互动数**：用 XHS-Downloader 的 MCP 模式，风险最低。
- **大规模、长期、可复现的研究**：**不值得。** 没有任何方案能保证稳定，合规风险也最高。
  更合适的路径是向平台申请官方数据合作，或使用有合法授权的数据服务商。本次调研**没有**核实小红书目前是否提供面向研究者的官方数据接口，这一点需要你另外确认。

---

## 最终回答

**"目前是否存在一个可以让 Claude 通过 MCP 稳定读取小红书数据的可用方案？"**

**基于本次实际检查和测试：没有。**

> 2026-10-03 更新：用户在本机用自己的账号跑通了连接、鉴权、登录和 MCP 工具发现。
> 搜索第 1 次返回 0 条，约 15 分钟后第 2 次返回 20 条（见 F.1b）。
> 所以"Claude 能连上并搜到笔记"已经实测成立；但同一关键词两次结果不一致，
> 而且详情、评论、作者等其余 18 项尚未实测，"能稳定读到数据"仍然**没有**被证实。

- 我**实测确认**了：xpzouying/xiaohongshu-mcp（18 个工具）和 XHS-Downloader（2 个工具）的 MCP 协议层可以被 Claude 类客户端发现和调用。
- 我**没能实测**任何一项真实的小红书数据读取：本环境屏蔽了小红书域名，而且登录需要你本人扫码。
- 从源码看，功能最全的方案（xpzouying）依赖浏览器自动化、未公开来源的指纹伪装浏览器和登录态，本质上就**不是"稳定"方案**；
  风险最低的方案（XHS-Downloader）又不能搜索、不能拿评论。
- 没有任何开源项目使用官方 API。

**下一步你需要提供/做的事**（任选其一）：
1. **在你自己的电脑上运行**（推荐）：按 `configs/claude_code.md` 装好 xpzouying，用研究账号扫码登录，然后运行
   `uv run tests/run_live_check.py --keyword <关键词>`，把生成的 `results/live/matrix.md` 发给我，我来解读并更新这份报告。
2. **放开本云环境的网络限制**：在环境设置里把 `xiaohongshu.com`、`xhscdn.com`（如果用 xpzouying，还要加 `cdn.one-world.ai`）加入允许域名。
   但要注意：云端数据中心的 IP 更容易被风控，而且扫码登录时需要我把二维码发给你用手机扫。所以我仍然建议方案 1。

我不需要、也不会索取你的密码。如果用 cookie 方式，请你自己把 cookie 配置到本地环境变量或文件里，不要发到对话中。
