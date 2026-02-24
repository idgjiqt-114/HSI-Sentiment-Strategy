import numpy as np


def add_indicators(df_votes):
    #SMA20
    df_votes['SMA20']=df_votes['Close'].rolling(20).mean()

    #RSI
    def calc_rsi(series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))
    df_votes['RSI14'] = calc_rsi(df_votes['Close'])

    # MACD (12/26/9)
    ema12 = df_votes['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df_votes['Close'].ewm(span=26, adjust=False).mean()
    df_votes['MACD'] = ema12 - ema26
    df_votes['MACD_signal'] = df_votes['MACD'].ewm(span=9, adjust=False).mean()
    df_votes['MACD_hist'] = df_votes['MACD'] - df_votes['MACD_signal']

    return df_votes


def add_filter_signals(df_votes):
    #SMA: +1 if Close>SMA20 (bullish trend), -1 if Close<SMA20 (bearish trend)
    df_votes['flt_sma'] = np.where(df_votes['Close']>df_votes['SMA20'], 1, -1)

    #RSI: +1 oversold (<40), -1 overbought(>60), 0 neutral
    df_votes['flt_rsi'] = np.where(df_votes['RSI14']<40, 1,
                               np.where(df_votes['RSI14']>60, -1, 0))

    #MACD: +1 if MACD>signal (bullish monmentum), -1 if MACD<signal (bearish momentum)
    df_votes['flt_macd'] = np.where(df_votes['MACD']>df_votes['MACD_signal'], 1, -1)

    #Combined 3
    score = df_votes['flt_sma'] + df_votes['flt_rsi'] + df_votes['flt_macd']
    df_votes['flt_all'] = np.sign(score)
    df_votes['combined_score'] = score

    return df_votes
