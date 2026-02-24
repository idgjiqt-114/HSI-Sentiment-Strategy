import pandas as pd
import numpy as np


def load_data(filepath):
    df=pd.read_excel(filepath)
    df.columns=['Date', 'Open', 'High', 'Low', 'Close', 'Up', 'Down']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.sort_values('Date').reset_index(drop=True)

    df['intraday_return']=(df['Close'] - df['Open'])/df['Open']   
    df['vote_spread']=df['Up']-df['Down']
    df['bull_day']=(df['intraday_return']>0).astype(int)
    df_votes=df.dropna(subset=['Up', 'Down', 'intraday_return']).copy()

    return df, df_votes


def print_summary(df, df_votes):
    print(f"Total trading days: {len(df)}")
    print(f"Days with vote data: {len(df_votes)}")
    print(f"Data Coverage: {len(df_votes)/len(df) *100: .1f}%")
    print(f"Avg Up Vote: {df_votes['Up'].mean() *100: .1f}%")
    print(f"Avg Down Vote: {df_votes['Down'].mean() *100: .1f}%")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(df_votes[['Up','Down','vote_spread','intraday_return']].describe())
