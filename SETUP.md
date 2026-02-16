# 脱敏项目初始化说明

本文件夹 `usd1_public` 是基于原始项目创建的完全脱敏版本，可以安全地上传到公开的 GitHub 仓库。

## 已脱敏的内容

✅ 所有 API Keys 已替换为占位符：
- `YOUR_ETH_API_KEY`
- `YOUR_TELEGRAM_BOT_TOKEN`
- `YOUR_CHAT_ID1,YOUR_CHAT_ID2`
- `YOUR_QYWX_WEBHOOK_URL`
- `YOUR_SHEET_ID`

✅ 敏感文件已添加到 `.gitignore`：
- `google-credentials.json`
- `*.key`, `*.pem`
- `.env` 文件

✅ GitHub Actions 工作流已配置为使用 Secrets 而非硬编码值

## 上传到 GitHub 准备

### 第一步：初始化 Git 仓库

```bash
cd usd1_public
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
git add .
git commit -m "Initial commit: Complete project setup"
```

### 第二步：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库（可选择 Public），名称如 `my-asset-monitor`
3. **不要** 勾选"Initialize this repository with a README"（你已有README）

### 第三步：上传到 GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/my-asset-monitor.git
git branch -M main
git push -u origin main
```

### 第四步：配置 Secrets

1. 进入 GitHub 仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 逐个添加以下 Secrets：

```
ETH_API_KEY = [你的 Etherscan API Key]
TELEGRAM_BOT_TOKEN = [你的 Telegram Bot Token]
TELEGRAM_CHAT_IDS = [你的 Chat ID，多个用逗号分隔]
QYWX_WEBHOOK = [你的企业微信 Webhook URL]
GOOGLE_CREDENTIALS = [你的 Google Service Account JSON]
```

### 第五步：验证工作流

1. 进入仓库的 Actions 标签
2. 选择 "Asset Push" 或 "Update APY" 工作流
3. 点击 "Run workflow" → "Run workflow" 手动测试

## 本地测试步骤

在上传前，建议先在本地测试：

```bash
# 1. 设置环境变量（Linux/Mac）
export ETH_API_KEY="your_key_here"
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_IDS="your_chat_id"

# Windows PowerShell
$env:ETH_API_KEY="your_key_here"
$env:TELEGRAM_BOT_TOKEN="your_token"
$env:TELEGRAM_CHAT_IDS="your_chat_id"

# 2. 运行测试
python3 usd1_push.py

# 3. 查看输出
# 应该看到：正在获取资产持仓数据...
# 以及推送的消息内容
```

## 文件清单

```
usd1_public/
├── usd1_push.py                # ✅ 已脱敏
├── update_apy.py               # ✅ 已脱敏
├── requirements.txt            # ✅ 依赖清单
├── config.example.json         # ✅ 配置示例
├── README.md                   # ✅ 详细文档
├── setup.sh                    # ✅ 初始化脚本
├── history.json                # ✅ 空历史文件
├── SETUP.md                    # ✅ 本文件
├── .gitignore                  # ✅ Git 忽略配置
└── .github/
    └── workflows/
        ├── push.yml            # ✅ 已脱敏
        └── update_apy.yml      # ✅ 已脱敏
```

## 重要提醒

⚠️ **安全检查清单**：

- [ ] 确认代码中没有硬编码的 API Keys（使用 `git grep` 检查）
- [ ] 确认 `.gitignore` 已配置敏感文件
- [ ] 确认所有 Secrets 已在 GitHub 中添加
- [ ] 不要在 README 或注释中提及真实的敏感信息
- [ ] 在本地测试成功后再推送到 GitHub
- [ ] 定期轮换 API Keys 和 Secrets

## 修改要点

在使用此脱敏项目前，你需要修改以下部分：

### 在代码中修改：

1. **usd1_push.py** 第 14-21 行：
   ```python
   WALLETS = [
       "0x实际钱包地址1",
       "0x实际钱包地址2",
       ...
   ]
   ```

2. **update_apy.py** 第 14 行：
   ```python
   SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/edit"
   ```

3. **update_apy.py** 第 29-36 行：
   ```python
   WALLETS = [
       "0x实际钱包地址1",
       "0x实际钱包地址2",
       ...
   ]
   ```

### 在 GitHub Secrets 中设置：

参考 README.md 中的"GitHub Actions 配置"部分

## 后续维护

- **监控 Workflow 执行**：每次执行后检查 Actions 日志
- **定期检查 API 配额**：避免超出 Etherscan 免费配额
- **更新依赖**：定期运行 `pip list --outdated` 检查更新
- **备份重要数据**：包括 history.json 和 Google Sheet 数据

## 常见问题排查

### Workflow 失败

1. 检查 GitHub Actions 日志获取具体错误
2. 验证 Secrets 配置是否正确（不暴露实际值）
3. 检查 API 调用是否超出配额限制
4. 确认网络连接和防火墙设置

### API 返回 401/403 错误

- 检查 API Key 是否过期
- 检查 Secret 值是否被正确传递（使用 `${{ secrets.SECRET_NAME }}`）
- 尝试重新生成 API Key

### 推送失败

- 验证 Telegram Bot Token 和 Chat ID
- 测试 Webhook URL 是否可访问
- 检查机器人是否有发送消息权限

---

准备好了？开始上传你的脱敏项目到 GitHub 吧！🚀
