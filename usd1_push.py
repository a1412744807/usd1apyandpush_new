import requests
import time
import os
import json
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================

ETH_API_KEY = os.environ.get("ETH_API_KEY", "YOUR_ETH_API_KEY")
BSC_RPC_URL = "https://bsc-dataseed.binance.org/"
CONTRACT = "0x8d0D000Ee44948FC98c9B98A4FA4921476f08B0d"

# 钱包列表（示例钱包地址，需替换为实际地址）
WALLETS = [
    "0xF977814e90dA44bFA03b6295A0616a897441aceC",
    "0x5a52E96BAcdaBb82fd05763E25335261B270Efcb",
    "0xE69a89bF579a9C53cbB3FCe34e4e835546Eb58bB",
    "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503",
    "0x28C6c06298d514Db089934071355E5743bf21d60",
    "0x8894E0a0c962CB723c1976a4421c95949bE2D4E3",
    "0xDFd5293D8e347dFe59E907d6a7199945155871f0",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549",
]

# 推送配置（从环境变量读取，不在代码中存储敏感信息）
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = os.environ.get("TELEGRAM_CHAT_IDS", "YOUR_CHAT_ID1,YOUR_CHAT_ID2").split(",")
QYWX_WEBHOOK = os.environ.get("QYWX_WEBHOOK", "YOUR_QYWX_WEBHOOK_URL")

# 历史数据文件
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(SCRIPT_DIR, "history.json")

# ==================== 余额查询 ====================

def get_eth_balance(address):
    url = "https://api.etherscan.io/v2/api"
    params = {"chainid": "1", "module": "account", "action": "tokenbalance",
              "contractaddress": CONTRACT, "address": address, "tag": "latest", "apikey": ETH_API_KEY}
    for _ in range(3):
        try:
            res = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).json()
            if res['status'] == '1':
                return float(res['result']) / 1e18
        except:
            time.sleep(1)
    return 0

def get_bsc_balance(address):
    data = "0x70a08231000000000000000000000000" + address[2:]
    payload = {"jsonrpc":"2.0", "method":"eth_call", "params":[{"to": CONTRACT, "data": data}, "latest"], "id":1}
    try:
        res = requests.post(BSC_RPC_URL, json=payload, timeout=10).json()
        if "result" in res:
            return int(res["result"], 16) / 1e18
    except:
        pass
    return 0

def get_total_balance():
    total = 0
    for addr in WALLETS:
        total += get_eth_balance(addr) + get_bsc_balance(addr)
        time.sleep(0.2)
    return total

# ==================== 历史数据 ====================

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f)

def get_yesterday_balance():
    history = load_history()
    yesterday = (datetime.now(timezone(timedelta(hours=8))) - timedelta(days=1)).strftime('%Y-%m-%d')
    return history.get(yesterday, {}).get('balance')

def save_today_balance(balance):
    history = load_history()
    today = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
    history[today] = {'balance': balance, 'timestamp': datetime.now().isoformat()}
    # 只保留最近7天
    keys = sorted(history.keys())[-7:]
    history = {k: history[k] for k in keys}
    save_history(history)

# ==================== 推送 ====================

def push_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS[0]:
        print("Telegram 未配置")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in TELEGRAM_CHAT_IDS:
        if not chat_id.strip():
            continue
        payload = {
            "chat_id": chat_id.strip(),
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            result = resp.json()
            if result.get('ok'):
                print(f"Telegram 推送成功: {chat_id}")
            else:
                print(f"Telegram 推送失败: {result.get('description')}")
        except Exception as e:
            print(f"Telegram 推送异常: {e}")

def push_qywx(message):
    if not QYWX_WEBHOOK:
        print("企业微信 未配置")
        return

    payload = {
        "msgtype": "markdown",
        "markdown": {"content": message}
    }
    try:
        resp = requests.post(QYWX_WEBHOOK, json=payload, timeout=10)
        result = resp.json()
        if result.get('errcode') == 0:
            print("企业微信 推送成功")
        else:
            print(f"企业微信 推送失败: {result.get('errmsg')}")
    except Exception as e:
        print(f"企业微信 推送异常: {e}")

# ==================== 主逻辑 ====================

def format_number(num):
    """格式化数字，亿为单位"""
    if num >= 100000000:
        return f"{num/100000000:.2f}亿"
    elif num >= 10000:
        return f"{num/10000:.2f}万"
    else:
        return f"{num:,.0f}"

def main():
    print("正在获取币安WLFI持仓数据...")

    # 获取当前余额
    total = get_total_balance()
    if total <= 0:
        print("获取余额失败")
        return

    # 计算 APY（仅参照现货/资金账户年化APY）
    base_apy = (10_000_000 * 52) / total * 100

    # 获取昨日数据计算变动
    yesterday_balance = get_yesterday_balance()
    if yesterday_balance:
        change = total - yesterday_balance
        if change >= 0:
            change_text = f"增加 {format_number(change)}"
        else:
            change_text = f"减少 {format_number(abs(change))}"
    else:
        change_text = "暂无数据"

    # 保存今日数据
    save_today_balance(total)

    # 获取北京时间
    beijing_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')

    # 构建消息
    message = f"""**币安WLFI和USD1活动年化利率更新**

当前币安全网WLFI总持仓数量约为 **{format_number(total)}**，较昨日同期变动{change_text}。

年化APY最高预估约{base_apy:.2f}%

更新时间: {beijing_time} (北京时间)"""

    print(message)
    print("\n" + "="*50)

    # 推送
    push_telegram(message)
    push_qywx(message)

if __name__ == "__main__":
    main()
