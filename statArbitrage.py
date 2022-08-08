import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
exchange = ccxt.binanceusdm()

def main(first, second, k, smaDeltaConst, stdDeltaConst):
    df = pd.DataFrame()
    df['first'] = [i[4] for i in exchange.fetch_ohlcv(f'{first}USDT', '1h')] 
    df['second'] = [i[4] for i in exchange.fetch_ohlcv(f'{second}USDT', '1h')] 

    df['pctFirst'] = df['first'].pct_change() 
    df['pctSecond'] = df['second'].pct_change() 

    df['delta'] = df['pctFirst']-df['pctSecond'] 

    df['smaDelta'] = df['delta'].rolling(smaDeltaConst).mean()
    df['stdDelta'] = df['delta'].rolling(stdDeltaConst).std()
    df['highStd'] = df['smaDelta'] + df['stdDelta']*k
    df['lowStd'] = df['smaDelta'] - df['stdDelta']*k
    df['deltaDistance'] = df['delta'] - df['smaDelta']

    df['firstPosition'] = np.where(df['delta']>df['highStd'], -1, np.where(df['delta']<df['lowStd'],  1, np.nan)) 
    df['firstPosition'] = np.where(df['deltaDistance']*df['deltaDistance'].shift(1) < 0, 0, df['firstPosition'])
    df['firstPosition'] = df['firstPosition'].ffill().fillna(0)
    df['secondPosition'] = np.where(df['delta']>df['highStd'], 1, np.where((df['delta']<df['lowStd']),  -1, np.nan)) 
    df['secondPosition'] = np.where(df['deltaDistance']*df['deltaDistance'].shift(1) < 0, 0, df['secondPosition']) 
    df['secondPosition'] = df['secondPosition'].ffill().fillna(0)
    df['strategy'] = ((df['firstPosition'].shift(1)*df['pctFirst'])+(df['secondPosition'].shift(1)*df['pctSecond'])).apply(lambda x : x-0.0008 if(x != 0) else x)
    return df

df = main('DASH', 'DEFI', 2, 5, 11)
fig, axs = plt.subplots(5, sharex=True)
axs[0].plot(df['first'])
axs[1].plot(df['second'])
axs[2].plot(df[['smaDelta', 'highStd', 'lowStd', 'delta']])
axs[3].plot(df[['firstPosition', 'secondPosition']])
axs[3].legend(['firstPosition', 'secondPosition'])
axs[4].plot(df['strategy'].cumsum())
plt.show()
