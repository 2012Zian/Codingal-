import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from binance.client import Client
from ta.trend import SMAIndicator
import time

# ==== Binance Test API Keys ====
API_KEY = 'hghsZ0I7sQeQzQp7bzH1JX3aMDDA1FZrHqpOk1Bq1Se3RSr38FtW381Z6b1NdgIf'
API_SECRET = 'G7EKnjuLQ4imN1xGCMBirtKFakQ39zwF87DjI12Pg48Mg6Uj5ayW6ZEBW9i5hIws'
USE_TESTNET = True  # Use Binance testnet

client = Client(API_KEY, API_SECRET, testnet=USE_TESTNET)

# ==== Bot Parameters ====
SYMBOL = 'BTCUSDT'
INTERVAL = '1m'
TRADE_SIZE = 100  # Simulated USD value
SHORT_WINDOW = 5
LONG_WINDOW = 20

# ==== Paper Trading State ====
balance = 1000
position = 0
entry_price = 0
trade_history = []

# ==== Plot Setup ====
plt.style.use('seaborn-darkgrid')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=50)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['SMA_short'] = SMAIndicator(df['close'], SHORT_WINDOW).sma_indicator()
    df['SMA_long'] = SMAIndicator(df['close'], LONG_WINDOW).sma_indicator()
    return df

def simulate_trade(price, signal):
    global balance, position, entry_price, trade_history

    if signal == 'buy' and balance >= TRADE_SIZE:
        position = TRADE_SIZE / price
        entry_price = price
        balance -= TRADE_SIZE
        trade_history.append({'type': 'BUY', 'price': price, 'time': pd.Timestamp.now()})

    elif signal == 'sell' and position > 0:
        exit_value = position * price
        profit = exit_value - TRADE_SIZE
        balance += exit_value
        trade_history.append({'type': 'SELL', 'price': price, 'time': pd.Timestamp.now(), 'pnl': profit})
        position = 0

def update(frame):
    df = get_data()

    ax1.clear()
    ax2.clear()

    # Plot chart
    ax1.plot(df.index, df['close'], label='Price', color='blue')
    ax1.plot(df.index, df['SMA_short'], label=f'SMA {SHORT_WINDOW}', color='green')
    ax1.plot(df.index, df['SMA_long'], label=f'SMA {LONG_WINDOW}', color='red')
    ax1.set_title(f"{SYMBOL} Live Chart")
    ax1.legend()

    # Generate signal
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if prev['SMA_short'] < prev['SMA_long'] and last['SMA_short'] > last['SMA_long']:
        simulate_trade(last['close'], 'buy')
    elif prev['SMA_short'] > prev['SMA_long'] and last['SMA_short'] < last['SMA_long']:
        simulate_trade(last['close'], 'sell')

    # Stats
    total_trades = len([t for t in trade_history if t['type'] == 'SELL'])
    total_profit = sum(t.get('pnl', 0) for t in trade_history if t['type'] == 'SELL')
    win_trades = [t for t in trade_history if t.get('pnl', 0) > 0]
    win_rate = len(win_trades) / total_trades * 100 if total_trades > 0 else 0

    stats = {
        'Balance': f"${balance:.2f}",
        'Position': f"{position:.4f} BTC" if position else "None",
        'Trades': total_trades,
        'Profit': f"${total_profit:.2f}",
        'Win Rate': f"{win_rate:.2f}%"
    }

    ax2.axis('off')
    text = '\n'.join([f"{k}: {v}" for k, v in stats.items()])
    ax2.text(0.01, 0.95, text, fontsize=12, verticalalignment='top')

    print(f"Balance: {balance:.2f}, Position: {position:.4f} BTC, Trades: {total_trades}, Profit: {total_profit:.2f}, Win Rate: {win_rate:.2f}%")

# Run live
ani = FuncAnimation(fig, update, interval=60000)  # updates every 60 sec
plt.tight_layout()
plt.show()