import pandas as pd
import numpy as np


def compute_accuracy(df_votes):
    df_votes['major_up']=(df_votes['Up']>0.5).astype(int)
    df_votes['right_predict']=(df_votes['major_up']==df_votes['bull_day']).astype(int)

    sameday_acc=df_votes['right_predict'].mean()
    print(f'Same day Accuracy: {sameday_acc:.1%}')

    df_votes['vspread_abs']=df_votes['vote_spread'].abs()
    bins = [0, 0.1, 0.2, 0.3, 0.4, 1.0]
    labels = ['<10%','10-20%','20-30%','30-40%','>40%']
    df_votes['vspread_bin']=pd.cut(df_votes['vspread_abs'], bins=bins, labels=labels)

    accuracy = df_votes.groupby('vspread_bin', observed=True).agg(
        Sameday_Acc=('right_predict','mean'),
        Count=('right_predict','count')).reset_index()
    accuracy['Sameday_Acc %'] = accuracy['Sameday_Acc'].apply(lambda x: f'{x:.1%}')

    return df_votes, accuracy, sameday_acc


def compute_return_by_bin(df_votes):
    df_votes['up_bin'] = pd.cut(df_votes['Up'],
        bins=[0, 0.35, 0.45, 0.55, 0.65, 1],
        labels=['Very Bear\n(<35%)','Bearish\n(35-45%)','Neutral\n(45-55%)','Bullish\n(55-65%)','Very Bull\n(>65%)'])
    ret_by_bin = df_votes.groupby('up_bin', observed=True)['intraday_return'].mean() * 100
    return df_votes, ret_by_bin


def print_extreme_stats(df_votes):
    print(f'n_days: {(df_votes["Up"]>0.6).sum()}')
    print(f'Market Move Down days: {(df_votes[df_votes["Up"]>0.6]["intraday_return"]<0).sum()}')
    print(f'Market Move Down days%:{(df_votes[df_votes["Up"]>0.6]["intraday_return"]<0).sum()/ (df_votes["Up"]>0.6).sum() *100: .1f}%')
    print(f'Average Return: {(df_votes[df_votes["Up"]>0.6]["intraday_return"]).mean() * 100: .3f}%')

    print(f'n_days: {(df_votes["Down"]>0.6).sum()}')
    print(f'Market Move Up days: {(df_votes[df_votes["Down"]>0.6]["intraday_return"]>0).sum()}')
    print(f'Market Move Up days%:{(df_votes[df_votes["Down"]>0.6]["intraday_return"]>0).sum()/ (df_votes["Down"]>0.6).sum() *100: .1f}%')
    print(f'Average Return: {(df_votes[df_votes["Down"]>0.6]["intraday_return"]).mean() * 100: .3f}%')
