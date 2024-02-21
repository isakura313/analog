import pandas as pd
from polygon import RESTClient
from datetime import datetime, timedelta, timezone
import technic as ta  # Предполагаем, что библиотека technic содержит нужную функцию расчета RSI


def tema(tr, w, wilders):
    return tr

def wwma(values, n):
    """
     J. Welles Wilder's EMA
    """
    return values.ewm(alpha=1/n, adjust=False).mean()


def tatr(high, low, close, n=14):
    data = pd.DataFrame()
    high = high
    low = low
    close = close
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = wwma(tr, n)
    return atr

# Функция для извлечения данных и сохранения в Excel

def fetch_intraday_data_atr(api_key, ticker, days):
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    print(f"Начинаем загрузку внутридневных данных для тикера {ticker}...")

    client = RESTClient(api_key)
    aggs = client.list_aggs(ticker=ticker, multiplier=1, timespan="day", from_=start_date.strftime("%Y-%m-%d"), to=end_date.strftime("%Y-%m-%d"))

    df = pd.DataFrame([{
        'timestamp': agg.timestamp,
        'open': agg.open,
        'high': agg.high,
        'low': agg.low,
        'close': agg.close,
        'volume': agg.volume,
        'transactions': agg.transactions  # Предполагаем, что есть атрибут transactions
    } for agg in aggs])

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('America/New_York')

    df.set_index('timestamp', inplace=True)
    #df = df.between_time('09:30', '15:59')
    df.reset_index(inplace=True)
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)

    df['DAYS'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    # Расчет ATR с помощью библиотеки technic
    # Убедитесь, что функция tatr принимает аргументы: закрытие, максимум, минимум и окно
    df['ATR'] = tatr(df['close'], df['high'], df['low'])  # Используем функцию tatr с периодом в 14 дней
    return df
    #df.to_excel(file_name + '.xlsx', index=False)
    #print(f"Внутридневные данные с ATR успешно сохранены в файл {file_name}.xlsx")

def fetch_intraday_data_rsi(api_key, ticker, days):
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    print(f"Начинаем загрузку внутридневных данных для тикера {ticker}...")

    client = RESTClient(api_key)
    aggs = client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_=start_date.strftime("%Y-%m-%d"), to=end_date.strftime("%Y-%m-%d"))

    df = pd.DataFrame([{
        'timestamp': agg.timestamp,
        'open': agg.open,
        'high': agg.high,
        'low': agg.low,
        'close': agg.close,
        'volume': agg.volume,
        'transactions': agg.transactions  # Предполагаем, что есть атрибут transactions
    } for agg in aggs])

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('America/New_York')

    df.set_index('timestamp', inplace=True)
    df = df.between_time('09:30', '15:59')
    df.reset_index(inplace=True)
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)

    # Расчет RSI с помощью библиотеки technic
    df['RSI'] = ta.trsi(df['close'], 14)  # Используем функцию trsi из библиотеки technic
    df['DAYS'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    #df.to_excel(file_name + '.xlsx', index=False)
    #print(f"Внутридневные данные с RSI успешно сохранены в файл {file_name}.xlsx")
    return df


# Ваши параметры
api_key = "ADD_API_KEY"  # Замените на ваш действительный API ключ
ticker = "BA"
days = 50


ATR_ar = []

RSI = fetch_intraday_data_rsi(api_key, ticker, days)
ATR = fetch_intraday_data_atr(api_key, ticker, days)

print(RSI)
print(ATR)
count = 0


final = pd.merge(RSI, ATR, on="DAYS")

file_name = input('Введите имя файла:\n')
RSI.to_excel(file_name + '.xlsx', index=False)