import requests
import time
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 配置区 ====================

# Google 表格链接（需替换为你的实际表格ID）
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit?usp=sharing"

# 要写入的格子
TARGET_CELL = "C4"

# ETH API Key（线上运行时从环境变量读取）
ETH_API_KEY = os.environ.get("ETH_API_KEY", "YOUR_ETH_API_KEY")

# ==================== 核心逻辑 ====================

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

def get_eth_balance(address):
    """查 ETH 链余额 (带重试)"""
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
    """查 BSC 链余额 (RPC)"""
    data = "0x70a08231000000000000000000000000" + address[2:]
    payload = {"jsonrpc":"2.0", "method":"eth_call", "params":[{"to": CONTRACT, "data": data}, "latest"], "id":1}
    try:
        res = requests.post(BSC_RPC_URL, json=payload, timeout=10).json()
        if "result" in res:
            return int(res["result"], 16) / 1e18
    except:
        pass
    return 0

def get_google_creds():
    """获取 Google 凭证 (支持本地文件或环境变量)"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # 优先从环境变量读取 (GitHub Actions 用)
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    # 本地文件（需将你的Google Service Account JSON文件放在此目录）
    keyfile = os.path.join(SCRIPT_DIR, 'google-credentials.json')
    if os.path.exists(keyfile):
        return ServiceAccountCredentials.from_json_keyfile_name(keyfile, scope)

    return None

def update_sheet(final_apy):
    """写入 Google Sheet"""
    print("正在写入 Google Sheets...")

    try:
        creds = get_google_creds()
        if not creds:
            print("未找到 Google 凭证，跳过写表。")
            return False

        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL).sheet1

        # 格式化: "15.35% (动态估算)"
        cell_text = f"{final_apy:.2f}% (动态估算)"

        sheet.update_acell(TARGET_CELL, cell_text)
        print(f"成功! 单元格 {TARGET_CELL} 已更新为: {cell_text}")
        return True

    except Exception as e:
        print(f"写入失败: {e}")
        return False

def main():
    print("正在扫描全网资产 (ETH + BSC 双链)...")
    total = 0

    for addr in WALLETS:
        eth_bal = get_eth_balance(addr)
        bsc_bal = get_bsc_balance(addr)
        total += eth_bal + bsc_bal
        time.sleep(0.2)

    if total > 0:
        base_apy = (10_000_000 * 52) / total * 100

        print(f"全网总持仓: {total:,.0f}")
        print(f"现货 APY: {base_apy:.2f}%")
        print(f"合约 APY: {base_apy * 1.2:.2f}%")

        # 写入基础年化 (不乘1.2)
        update_sheet(base_apy)
    else:
        print("数据获取为 0，跳过写入")

if __name__ == "__main__":
    main()
