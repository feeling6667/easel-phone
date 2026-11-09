# 贡献指南

感谢参与 Easel。项目以 Apache-2.0 开源，欢迎 Issue 和 PR。

## 反馈 Issue

- **环境问题**：附上 OS、Python、Node.js、`openclaw --version` 版本、`easel doctor` 输出和 `easel gateway logs` 相关片段。先查 [已知问题](docs/known-issues.md)。
- **功能建议 / 新技能**：先开 Issue 说明场景与预期产物，确认方向后再动手，避免大改撞车。

## 提交前必跑

```bash
python scripts/validate_skills.py            # SKILL frontmatter、目录结构、发布契约
python scripts/validate_skill_commands.py    # 文档中的 python 命令与脚本真实 argparse 对齐
python scripts/validate_document_paths.py
python scripts/local_patches.py --check      # 本机补丁标记与 docs/local-patches.md 是否一致
python -m pytest tests/                      # 核心单测（不会调用真实模型或平台）
```

路径校验覆盖根文档、`docs/`、`agents/` 和 `skills/` 下的 Markdown，以及画像模板和前端说明，包括深层参考文档和 Agent 提示材料。命令里的 `skills/...` 相对项目根，技能资源名相对技能目录，Markdown 链接与显式 `../` 相对当前文档；占位符和运行时生成的产物不要求预先存在。

仅更新 OpenClaw 已同步的提示文档时可运行 `bash agents/sync.sh --docs-only`：更新内置技能与共享 Markdown、身份文档和运行时路径说明，不清空 `MEMORY.md`、不删除 `USER.md` 或自定义技能、不修改脚本和产物链接。其它原生执行引擎直接读取 `agents/workspace/`，不需要这一步。

## Skill 约定

- 遵循 [SKILL 接口规范](docs/SKILL-SPEC.md)：frontmatter 含 `name / description / layer`，SKILL.md 精简（≤ 600 行），领域知识进 `references/`，可执行脚本进 `scripts/`。上限是 600 而不是更小，是因为「单文件重型技能」（如 `dbs-content-system` 的操作手册）拆出去后，多数客户端不会自动加载 `references/`，等于功能残缺；超过 600 行才强制拆。
- 产物统一写入 `outputs/<项目>/`，路径经 `skills/shared/scripts/output_paths.py` 校验；不要在技能里散落写其他目录。
- 发布类技能保持门禁语义：先预览与发布前检查，真实发布由用户确认后执行。
- 技能内的账号画像只从 `profiles/<画像>/` 读取，不写全局 `MEMORY.md`（见 [提示词分层](docs/prompt-stack.md)）。

## 代码约定

- Python ≥ 3.10；Web 为 FastAPI + React（`web/`），CLI 入口在 `easel/`。
- 超时只改 [`easel/timeouts.py`](easel/timeouts.py) 单一真相源，不要在调用处各写各的。
- OpenClaw 的缺陷优先跟随上游修复；本仓库确实需要保留的差异，按下一节「本机补丁与契约」登记，不留隐形分叉。
- 凭证不进仓库：`.env` 不入库；测试不得调用真实模型、真实平台或外部消息渠道。

## 本机补丁与契约（本仓库特有）

本仓库是上游 Easel 的分叉，**行为以本仓库为准**：代码怎么跑，测试就该怎么说。凡是和上游不一样的地方，一个提交里必须做完三件事，缺一件就当没做完。

**1. 标出来。** 改动处加 `【本机补丁 YYYY-MM-DD】`，一句话写清「上游怎么做的 / 本机为什么不一样」。

**2. 对齐断言。** 改测试、改校验器，而不是删测试。测试里也留一段三段式说明：

```text
上游期望：loopback 一律拒绝
本机行为：默认放行（本机模型网关走 127.0.0.1），EASEL_ALLOW_LOOPBACK_MODEL_ENDPOINT=0 可关回
原因：设置面板要能填本机中转地址，否则用户配不了自建网关
```

**3. 更新账本。** 跑 `python scripts/local_patches.py --write` 重写 `docs/local-patches.md`；CI 的 `--check` 会核对，漏了直接红。

为什么值得这么麻烦：测试本身没有立场，它只是把「当年的假设」写死了。你改了行为却没改断言，红的是它、看不清的是你；而**留着红不管，比删掉测试更糟**——删掉至少是清醒的决定，留着红是长期噪音，最后没人再看任何一条失败。

**跟上游合并时**：先开 `docs/local-patches.md`。冲突只要落在这张表覆盖的位置，就按本机行为解决；不在表里的冲突，才是需要重新读上游意图的地方。

## PR 约定

- 一个 PR 只做一件事；标题用 `feat: / fix: / docs: / chore: / polish:` 前缀。
- 描述里写清动机与验证方式；涉及技能行为改动时附上触发示例。
- 第三方素材或技能引入需在 [ACKNOWLEDGMENTS](docs/ACKNOWLEDGMENTS.md) 登记来源与许可。
