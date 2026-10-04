# 小红书 MCP 20 项本机实测

本次实测时间：2026-10-03 22:05:42 PDT。

- 登录状态检查：工具返回超时错误，耗时 32.8 秒；本次未确认登录状态。
- 搜索“咖啡”：调用成功，耗时 35.4 秒，返回 0 条笔记。
- 笔记详情、评论和作者主页等后续 18 项未执行。

本次记录不能证明后续能力可用或不可用，也不能说明小红书上没有咖啡内容。此前可视模式返回 20 条的记录仍有效，当前结果说明请求表现存在波动。

测试来源：Keiber0330/xiaohongshu-mcp-research，分支 claude/xiaohongshu-mcp-research-wpsoxf，基础提交 a46e06a。

关键词：咖啡。结果统计：PARTIAL: 1, FAIL: 1, NOT TESTED: 18。

NOT TESTED 表示前置步骤未完成，该能力没有被实际调用。

| # | 能力 | 结果 | 证据 |
|---|---|---|---|
| 1 | 搜索关键词 | PARTIAL | call succeeded but 0 notes for keyword=咖啡 (0 raw items before note filter) |
| 2 | 获取搜索结果 | FAIL | 0 notes (0 raw items) |
| 3 | 获取笔记 ID | NOT TESTED | not reached |
| 4 | 获取笔记标题 | NOT TESTED | not reached |
| 5 | 获取正文 | NOT TESTED | not reached |
| 6 | 获取发布时间 | NOT TESTED | not reached |
| 7 | 获取作者昵称 | NOT TESTED | not reached |
| 8 | 获取作者 ID | NOT TESTED | not reached |
| 9 | 获取点赞数 | NOT TESTED | not reached |
| 10 | 获取收藏数 | NOT TESTED | not reached |
| 11 | 获取评论数 | NOT TESTED | not reached |
| 12 | 获取分享数 | NOT TESTED | not reached |
| 13 | 获取图片 URL | NOT TESTED | not reached |
| 14 | 获取视频 URL | NOT TESTED | not reached |
| 15 | 获取评论内容 | NOT TESTED | not reached |
| 16 | 获取评论用户 | NOT TESTED | not reached |
| 17 | 获取作者主页 | NOT TESTED | not reached |
| 18 | 获取作者历史笔记 | NOT TESTED | not reached |
| 19 | 分页 | NOT TESTED | not reached |
| 20 | 批量请求 | NOT TESTED | not reached |

原始响应仅保存在本机研究目录；本报告不含认证 token 或 cookie。
