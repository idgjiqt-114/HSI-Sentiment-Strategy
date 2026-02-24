import numpy as np
import pandas as pd

commission = 0.0005
initial = 100000


def backtest(df_sub, signal, strat):
    d = df_sub.copy()
    d['Signal']=signal
    d=d[d['Signal']!=0].reset_index(drop=True)
    if len(d) == 0:
        return None
    d['gross_ret']=d['intraday_return']*d['Signal']
    d['net_ret']=d['gross_ret'] - commission
    val = initial
    cur_val = []
    for r in d['net_ret']:
        val *= (1+r)
        cur_val.append(val)
    d['Value']=cur_val
    arr = np.array(cur_val)
    peak = np.maximum.accumulate(arr)
    dd = ((arr - peak)/peak)*100
    n_yrs = max((d['Date'].iloc[-1] - d['Date'].iloc[0]).days/365.25, 0.5)
    total_ret = (((d['Value'].iloc[-1]/initial)-1)*100)
    return {
        'strat':strat,
        'df':d,
        'cur_value': np.concatenate([[initial], arr]),
        'date': np.concatenate([[d['Date'].iloc[0]], d['Date'].values]),
        'n_trades': len(d),
        'win_rate': (d['net_ret']>0).mean() * 100,
        'total_ret': total_ret,
        'cagr': ((cur_val[-1]/initial)**(1/n_yrs)-1)*100,
        'sharpe_ratio': d['net_ret'].mean()/d['net_ret'].std()*np.sqrt(252),
        'max_dd': dd.min(),
        'avg_ret': d['net_ret'].mean()*100,
        'dd':dd,
        'dd_dates': d['Date'],
        'net_ret': d['net_ret'],
        'monthly': d.groupby(d['Date'].dt.to_period('M'))['net_ret'].sum()*100,
    }


def run_base_strategies(df_votes):
    s1 = backtest(df_votes, np.where(df_votes['Up']>df_votes['Down'], 1, -1), 'S1.Follow Majority (Always)')
    s2 = backtest(df_votes, np.where(df_votes['vote_spread']>0.15, 1,
                                     np.where(df_votes['vote_spread']<-0.15, -1, 0)), 'S2.Follow Majority (High Conviction, |Vote Spread|>15%)')
    s3 = backtest(df_votes, np.where(df_votes['Up']>df_votes['Down'], -1, 1), 'S3.Contrarian (Always)')
    s4 = backtest(df_votes, np.where(df_votes['Up']>0.6,-1,
                                      np.where(df_votes['Down']>0.6, 1, 0)), 'S4.Extreme Contrarian (Up/Down>0.6)')
    result = [r for r in [s1, s2, s3, s4] if r]

    for r in result:
        print(f"{r['strat']}")
        print(f"  Trades:{r['n_trades']:4d}  WinRate:{r['win_rate']:.1f}%  Return:{r['total_ret']:+.1f}%  CAGR:{r['cagr']:+.1f}%  Sharpe:{r['sharpe_ratio']:.2f}  MaxDD:{r['max_dd']:.1f}%")

    return result


def buy_and_hold(df):
    bh_ret = df['Close'].pct_change().dropna()
    bh_val = np.cumprod(1+bh_ret.values)*initial
    bh_total = (bh_val[-1]/initial -1)*100
    bh_date = df['Date'].iloc[1:].values
    bh_n_yrs = (df['Date'].iloc[-1]-df['Date'].iloc[0]).days/365.25
    bh_cagr = ((bh_val[-1]/initial)**(1/bh_n_yrs)-1)*100
    bh_sharpe = bh_ret.mean()/bh_ret.std()*np.sqrt(252)
    return {
        'cur_value': bh_val,
        'date': bh_date,
        'total_ret': bh_total,
        'cagr': bh_cagr,
        'sharpe': bh_sharpe,
    }


def apply_filter(base_sig, flt_val, mode):
    sig = base_sig.copy().astype(float)
    flt = np.array(flt_val)
    if mode == 'agree':
        sig[sig*flt <=0] = 0   #trade only when filter sign == signal sign
    else: #nonoppose
        sig[sig * flt < 0] = 0    #trade unless filter opposes signal
    return sig


def run_filtered_strategies(df_votes):
    sig_contra = np.where(df_votes['Up']>df_votes['Down'], -1, 1).astype(float)
    sig_ext_contra = np.where(df_votes['Up']>0.6, -1, 
                              np.where(df_votes['Down']>0.6, 1, 0)).astype(float)

    filtered_strategies = {
        'S3.Contrarian + SMA': apply_filter(sig_contra, df_votes['flt_sma'],'agree'),
        'S3.Contrarian + RSI': apply_filter(sig_contra, df_votes['flt_rsi'],'nonoppose'),
        'S3.Contrarian + MACD': apply_filter(sig_contra, df_votes['flt_macd'],'agree'),
        'S3.Contrarian + All Filters': apply_filter(sig_contra, df_votes['flt_all'],'agree'),
        'S4.Ext.Contra + SMA': apply_filter(sig_ext_contra,df_votes['flt_sma'],'agree'),
        'S4.Ext.Contra + RSI': apply_filter(sig_ext_contra, df_votes['flt_rsi'],'nonoppose'),
        'S4.Ext.Contra + MACD': apply_filter(sig_ext_contra, df_votes['flt_macd'],'agree'),
        'S4.Ext.Contra + All Filters': apply_filter(sig_ext_contra, df_votes['flt_all'],'agree'),
    }

    filtered_results = []
    for name, sig in filtered_strategies.items():
        r = backtest(df_votes, sig, name)
        if r:
            filtered_results.append(r)

    print(f"{'Strategy':<40} {'Trades':>6} {'WinRate':>8} {'CAGR':>7} {'Return':>8} {'Sharpe':>7} {'MaxDD':>7}")
    for r in filtered_results:
        print(f"{r['strat']:<40} {r['n_trades']:>6} {r['win_rate']:>7.1f}% {r['cagr']:>+7.1f}% {r['total_ret']:>+7.1f}% {r['sharpe_ratio']:>7.2f} {r['max_dd']:>6.1f}%")

    return filtered_results
