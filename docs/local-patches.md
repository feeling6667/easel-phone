# 本机补丁清单

> 本文件由 `python scripts/local_patches.py --write` 生成，**不要手改**。
> CI 会跑 `--check`，标记与本文档不一致就红。

本仓库的行为**以本仓库为准**：凡是和上游 Easel 不一样的地方，都在源码里用
`【本机补丁 YYYY-MM-DD】` 标出来，并对齐了对应的测试断言。
规则与模板见 [CONTRIBUTING.md](../CONTRIBUTING.md) 的「本机补丁与契约」一节。

共 **32** 处，分布在 **8** 个文件：

| 文件 | 行 | 标记 | 说明 |
| --- | ---: | --- | --- |
| `scripts/check_raw_stream.py` | 9 | 4/4 | 负责把这两个参数带上， |
| `scripts/gateway.ps1` | 83 | 1/3 | 运行时定位改为绝对路径（不再依赖 PATH） |
| `scripts/gateway.ps1` | 91 | 2/3 | Node spawnSync EBUSY 的绕行补丁 |
| `scripts/gateway.ps1` | 106 | 3/3 | 收敛大小写重名的环境变量键 |
| `scripts/gateway.ps1` | 129 | — | 官方正则要求 openclaw 出现在 --profile 之前；本机改成 |
| `scripts/gateway.ps1` | 153 | — | 官方这里用 `openclaw`（PATH .cmd shim）+ powershell -Command， |
| `scripts/gateway.ps1` | 175 | 4/4 | 开启 gateway 的原始流（token / 思考流）日志 |
| `scripts/gateway.ps1` | 197 | — | 冷启动要读并迁移状态库，实测可能超过 20 秒，给足 90 秒 |
| `scripts/gateway.ps1` | 212 | — | 带上 PID，便于确认 restart 是否真的换过进程 |
| `tests/test_web_security.py` | 222 | 2026-10-12 | 回环是**故意放行**的：让设置面板能填 |
| `web/app.py` | 113 | 2026-10-12 | 官方这里只读 os.environ，而 app.py 自己解析 .env 却不回填 |
| `web/app.py` | 139 | 2026-10-12 | 对话页「选模型」下拉的落点 |
| `web/app.py` | 241 | 4/4 | 设为 |
| `web/app.py` | 574 | 2026-10-12 | 对话页模型下拉写的三个键（不加进来 _write_env 会拒写） |
| `web/app.py` | 980 | 2026-10-12 | 放行**本机回环地址**（127.0.0.0/8、::1）。 |
| `web/app.py` | 1003 | — | 放行 127.0.0.0/8 与 ::1 |
| `web/app.py` | 1163 | — | 本轮模型：调用方显式传 > .env 里记着的 > 不传（落回 openclaw.json 默认） |
| `web/app.py` | 1966 | 2026-10-12 | 对话页模型下拉的两个接口 |
| `web/app.py` | 2792 | 2026-10-12 | 本轮显式指定的模型（来自对话页下拉）。空 = 用 .env 记着的那个。 |
| `web/app.py` | 3735 | 2026-10-13 | HTTP 路径必须用请求头把「本轮模型」告诉网关。 |
| `web/app.py` | 3825 | — | 本轮模型：请求体显式带 > .env 里记着的 > 不传（落回 openclaw.json 默认） |
| `web/app.py` | 4089 | 2026-10-22 思考进度 · 二次修正 | 网关 HTTP 模式不给浏览器回流式正文， |
| `web/app.py` | 4117 | 2026-10-22 思考进度 · 终修 | 正文不能重复发，但这段 delta |
| `web/app.py` | 4129 | 2026-10-22 思考进度 · CLI 补口 | CLI 传输下 text_delta 逐字进 |
| `web/app.py` | 4232 | 2026-10-22 | 流式期间的实时增量（_handle 对 commentary_update |
| `web/frontend/src/App.tsx` | 62 | — | 。空串 = 用 openclaw.json 的默认模型。 |
| `web/frontend/src/App.tsx` | 210 | — | 同步一次「记着的模型」，让下拉按钮上直接显示当前模型名。 |
| `web/frontend/src/App.tsx` | 223 | — | 当前模型的 ref：startStream 的依赖数组里不想进 model， |
| `web/frontend/src/App.tsx` | 420 | — | 空串则后端用 .env 记着的那个 |
| `web/frontend/src/components/ChatPage.tsx` | 24 | — | 值由 App 持有，选中即写后端 .env，重启不丢 ---- |
| `web/frontend/src/lib/api.ts` | 1001 | — |  |
| `web/frontend/src/styles/index.css` | 1495 | 2026-10-12 |  |
