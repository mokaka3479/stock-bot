import yfinance as yf
import pandas as pd
import ta
import requests

# ====== 設定 ======
tickers = ["7203.T", "6758.T", "8035.T", "8058.T"]

def check_stock(ticker):
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)

    if df.empty or len(df) < 200:
        return None

    close = df["Close"].squeeze()
    volume = df["Volume"].squeeze()

    rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
    ma200 = close.rolling(200).mean()
    ma50 = close.rolling(50).mean()
    vol_ma20 = volume.rolling(20).mean()

    latest_close = float(close.iloc[-1])
    latest_rsi = float(rsi.iloc[-1])
    latest_ma200 = float(ma200.iloc[-1])
    latest_ma50 = float(ma50.iloc[-1])
    latest_volume = float(volume.iloc[-1])
    latest_vol_ma20 = float(vol_ma20.iloc[-1])

    high_52 = float(close.max())
    drawdown = (latest_close - high_52) / high_52 * 100

    # ===== 🟢 安定型 =====
    if (
        latest_close > latest_ma200 and
        latest_close > latest_ma50 and
        40 <= latest_rsi <= 55 and
        drawdown <= -8 and
        latest_volume >= latest_vol_ma20
    ):
        return f"""🟢安定型
{ticker}
下落率: {drawdown:.2f}%
RSI: {latest_rsi:.2f}
出来高倍率: {latest_volume/latest_vol_ma20:.2f}倍"""

    # ===== 🔴 ギャンブル型（裏技入り） =====
    elif (
        latest_rsi <= 30 and
        drawdown <= -20 and
        latest_volume >= latest_vol_ma20 * 1.5
    ):
        return f"""🔴ギャンブル型
{ticker}
下落率: {drawdown:.2f}%
RSI: {latest_rsi:.2f}
出来高倍率: {latest_volume/latest_vol_ma20:.2f}倍"""

    return None


def send_discord(message):
    webhook_url = "https://discord.com/api/webhooks/1472955959021146135/yTPrEX63aOE6uOj6g_0OoRdVxYi61PL3-w71Fza7pK86bmEWpKbp_XwFNHBsLhL9YNLx"
    data = {"content": message}
    requests.post(webhook_url, json=data)


# ===== 実行部分 =====
results = []

for ticker in tickers:
    result = check_stock(ticker)
    if result:
        results.append(result)

if results:
    send_discord("\n\n".join(results))
    print("通知送信しました")
else:
    print("該当銘柄なし")
