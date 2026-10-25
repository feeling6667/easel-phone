# agy 桥接设置说明

本仓库的 agy 部分包括 agy-bridge/agy-bridge.py 和 agy-bridge/agy-bridge-start.sh。
桥接只监听 127.0.0.1:37289，请勿把 37289 对外发布。

## 新机器复现步骤
1. 安装 agy 1.4.7。
2. 用自己的 Google AI Pro 账号，通过交互式 agy 流程完成登录。
3. agy 登录凭证不在本仓库中，新机器上需要用户自己完成登录。
4. 在仓库目录运行 bash agy-bridge/agy-bridge-start.sh，启动本地桥接。

## Easel 设置
- 使用 direct-api 模式，transport=api，使用 direct-api 槽位。
- 模型 openclaw/default，地址 http://127.0.0.1:37289/v1，Key 留空。
- 模型列表来源 http://127.0.0.1:37289/v1。
- 请勿切回 openclaw/http 网关模式。

## 不入库的文件
- 真实 .env 不入库，示例见 .env.example。
- 请勿提交 .env、htpasswd、agy 凭证文件、密码或令牌。
