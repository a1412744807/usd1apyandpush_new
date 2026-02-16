# 资产监控与推送系统

这是一个在中国开源项目基础上创建的脱敏版本，用于监控加密资产持仓和年化收益率（APY）的自动化系统。所有敏感信息已隐去，需要通过环境变量或GitHub Secrets进行配置。

## 功能特性

- **双链资产监控**：同时支持 ETH 和 BSC 链的余额查询
- **自动化推送**：通过 Telegram 和企业微信推送资产变动通知
- **Google Sheets 集成**：自动更新 APY 数据到 Google Sheets
- **历史数据追踪**：记录7天的历史持仓数据，计算日环比变动
- **GitHub Actions 工作流**：完整配置实现定时自动执行

## 项目结构

```
usd1_public/
├── usd1_push.py              # 资产推送脚本
├── update_apy.py             # APY更新脚本
├── requirements.txt          # Python依赖
├── .gitignore               # Git忽略配置
├── .github/
│   └── workflows/
│       ├── push.yml         # 推送工作流
│       └── update_apy.yml   # APY工作流
└── README.md                # 本文档
```

## 快速开始

### 1. 本地运行配置

需要设置以下环境变量：

```bash
# ETH API Key (从 etherscan.io 获取)
export ETH_API_KEY="your_etherscan_api_key"

# Telegram 推送配置
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export TELEGRAM_CHAT_IDS="chat_id1,chat_id2"

# 企业微信推送配置
export QYWX_WEBHOOK="your_qywx_webhook_url"

# Google Sheets 凭证（仅update_apy.py需要）
export GOOGLE_CREDENTIALS='{"type":"service_account","project_id":"...","key_id":"...",...}'
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 本地测试

```bash
# 测试资产推送
python usd1_push.py

# 测试APY更新
python update_apy.py
```

## GitHub Actions 配置

### 设置 Secrets

在 GitHub 仓库中，进入 Settings → Secrets and variables → Actions，添加以下密钥：

| 密钥名称 | 说明 | 获取方式 |
|---------|------|--------|
| `ETH_API_KEY` | Etherscan API Key | https://etherscan.io/apis |
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人 Token | 从 @BotFather 创建 |
| `TELEGRAM_CHAT_IDS` | Telegram 聊天ID（逗号分隔） | 从 @userinfobot 获取 |
| `QYWX_WEBHOOK` | 企业微信 Webhook 地址 | 企业微信应用管理后台 |
| `GOOGLE_CREDENTIALS` | Google Service Account JSON | Google Cloud Console |

### Telegram Bot 创建步骤

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示输入机器人名称和用户名
4. 获取 Bot Token

### 获取 Telegram Chat ID

1. 将机器人添加到你的聊天群组
2. 在 Telegram 中搜索 `@userinfobot`
3. 查看返回的 Chat ID

### Google Sheets 配置

1. 在 [Google Cloud Console](https://console.cloud.google.com) 创建项目
2. 启用 Sheets API 和 Drive API
3. 创建 Service Account 并下载 JSON 密钥
4. 将 JSON 内容（整体）作为 `GOOGLE_CREDENTIALS` Secret 的值
5. 在脚本中修改 `SHEET_URL` 为你的 Google Sheets 链接
6. 在 Google Sheet 中，与 Service Account 邮箱共享编辑权限

## 配置文件说明

### usd1_push.py

- `ETH_API_KEY`：Etherscan API Key，用于查询ETH链余额
- `WALLETS`：监控的钱包地址列表
- `TELEGRAM_BOT_TOKEN`：Telegram 机器人令牌
- `TELEGRAM_CHAT_IDS`：推送的聊天ID列表
- `QYWX_WEBHOOK`：企业微信 Webhook 地址

### update_apy.py

- `SHEET_URL`：Google Sheets 工作表 URL
- `TARGET_CELL`：目标单元格（如C4）
- `ETH_API_KEY`：Etherscan API Key
- `WALLETS`：监控的钱包地址列表

## 工作流说明

### push.yml - 资产推送工作流

**触发时间**：
- 北京时间 08:00（UTC+8)
- 北京时间 16:00（UTC+8)
- 北京时间 00:00（UTC+8)
- 支持手动触发 (`workflow_dispatch`)

**功能**：
1. 查询所有钱包在 ETH 和 BSC 链上的余额
2. 计算年化收益率（APY）
3. 通过 Telegram 和企业微信推送通知
4. 将历史数据保存到 `history.json`

### update_apy.yml - APY更新工作流

**触发时间**：
- 每30分钟运行一次
- 支持手动触发

**功能**：
1. 查询双链余额
2. 计算当前 APY
3. 更新 Google Sheets 中指定单元格

## 常见问题

### Q: 如何修改钱包监控列表？
A: 编辑 `usd1_push.py` 和 `update_apy.py` 中的 `WALLETS` 列表，添加或移除钱包地址。

### Q: 如何修改推送时间？
A: 编辑 `.github/workflows/push.yml` 中的 `cron` 表达式。

### Q: 如何禁用某个推送渠道？
A: 在对应的 GitHub Secret 中删除该配置，或在脚本中注释相关推送函数。

### Q: Google Sheets 更新失败怎么办？
A: 
1. 检查 Service Account 是否有编辑权限
2. 确认 `SHEET_URL` 和 `TARGET_CELL` 配置正确
3. 在 GitHub Actions 日志中查看具体错误信息

## 隐私和安全建议

⚠️ **重要提示**：
- 不要在代码中硬编码任何 API Keys 或敏感信息
- 使用 GitHub Secrets 存储所有敏感数据
- 定期轮换 API Keys 和令牌
- 不要将包含真实凭证的配置文件上传到代码仓库
- `.gitignore` 已配置忽略敏感文件，但请再次确认

## 许可证

本项目基于原始项目创建的脱敏版本

## 支持

如有问题，请：
1. 检查 GitHub Actions 执行日志
2. 验证所有 Secrets 配置是否正确
3. 确认 API 配额未超出限制
