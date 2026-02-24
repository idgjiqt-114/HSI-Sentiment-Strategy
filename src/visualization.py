import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from pathlib import Path


def fig1_overview(df_votes, output_dir='outputs'):
    #Fig1: HSI Price + Vote
    fig,(ax1,ax2,ax3)=plt.subplots(3,1, figsize=(14,11))
    fig.suptitle('HSI Price and Social Media Sentiment Overview',
                 fontsize=16, fontweight='bold')
    #Price
    ax1.plot(df_votes['Date'], df_votes['Close'], lw=1.5, label='HSI Close')
    ax1.set_ylabel('Price', fontsize=11)
    ax1.set_title('HSI Close Price', fontsize=12)
    ax1.grid(True, alpha=0.5, ls='--', linewidth=0.5)

    #Up/Down Vote
    ax2.stackplot(df_votes['Date'], df_votes['Up'], df_votes['Down'], 
                  alpha=0.7, labels=['Up Vote', 'Down Vote'])
    ax2.axhline(0.5, lw=1.2, color='r', ls='--')
    ax2.set_ylabel('% Vote', fontsize=11)
    ax2.set_title('Daily Social Media Vote Distribution', fontsize=12)
    ax2.set_ylim(0, 1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x:.0%}'))
    ax2.legend(loc='upper right', fontsize=9)

    #Vote Spread
    colors_bar = ['g' if x > 0 else 'r' for x in df_votes['vote_spread']]
    ax3.bar(df_votes['Date'], df_votes['vote_spread'], color=colors_bar, alpha=0.8, width=1.5)
    ax3.axhline(0, color='black', lw=0.8)
    ax3.set_ylabel('Vote Spread\n(Up-Down)', fontsize=11)
    ax3.set_title('Vote Spread', fontsize=12)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x:.0%}'))
    ax3.grid(True, alpha=0.5, ls='--', linewidth=0.5)

    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(df_votes['Date'].min(), df_votes['Date'].max())
    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig1_overview.png', dpi=150, bbox_inches='tight')
    plt.close()


def fig2_accuracy(df_votes, accuracy, ret_by_bin, output_dir='outputs'):
    #Fig2: Accuracy and Distribution Analysis
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1], hspace=0.3, wspace=0.25)
    ax1 = plt.subplot(gs[0, :]) 
    ax2 = plt.subplot(gs[1, 0])  
    ax3 = plt.subplot(gs[1, 1])  
    fig.suptitle('Prediction Vote Signal Accuracy and Statistical Analysis',
                 fontsize=15, fontweight='bold')

    #Vote Spread Distribution
    ax1.hist(df_votes['vote_spread'], bins=30, alpha=0.8, edgecolor='white')
    ax1.axvline(0, lw=1, color='black', ls='--')
    bull_pct = (df_votes['vote_spread'] > 0).mean()
    bear_pct = (df_votes['vote_spread'] < 0).mean()
    ax1.set_title(f'Vote Spread Distribution\n(Bullish: {bull_pct:.1%} | Bearish: {bear_pct:.1%})', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Vote Spread (Up% − Down%)')
    ax1.set_ylabel('Frequency')

    #Sameday Accuracy by vote spread bin
    bars=ax2.bar(accuracy['vspread_bin'].astype(str),
                accuracy['Sameday_Acc'],
                color=['red' if x<0.5 else 'green' for x in accuracy['Sameday_Acc']])
    ax2.axhline(0.5, lw=1, ls='--', label='50% baseline')
    for bar,c,v in zip(bars, accuracy['Count'], accuracy['Sameday_Acc %']):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
                f'{v}\nn={c}', ha='center', va='bottom', fontsize=9)
    ax2.set_title('Sameday Directional Accuracy\nby Vote Spread Bins', fontsize=11, fontweight='bold')
    ax2.set_xlabel('|Vote Spread| Bin')
    ax2.set_ylabel('Accuracy')
    ax2.set_ylim(0, 0.75)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x:.0%}'))
    ax2.legend(fontsize=9)

    #Avg intraday return by Up vote bin
    cols = ['red' if v < 0 else 'green' for v in ret_by_bin.values]
    bars = ax3.bar(ret_by_bin.index, ret_by_bin.values, color=cols, alpha=0.85, edgecolor='white', width=0.6)
    ax3.axhline(0, color='black', lw=0.8)
    for b, v in zip(bars, ret_by_bin.values):
        ax3.text(b.get_x()+b.get_width()/2, v+(0.001 if v>=0 else -0.004),
                f'{v:.3f}%', ha='center', va='bottom' if v>=0 else 'top', fontsize=9)
    ax3.set_title('Average Intraday Return by Up Vote Bin', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Up Vote Bin')
    ax3.set_ylabel('Avg Return %')

    for x in [ax1, ax2, ax3]:
        x.grid(True, alpha=0.5, ls='--', linewidth=0.5)
    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig2_accuracy.png', dpi=150, bbox_inches='tight')
    plt.close()


def fig3_equity_curves(result, bh, output_dir='outputs'):
    #Fig3: Equity Curves
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(bh['date'], bh['cur_value'], color='gray', lw=2.2, linestyle='--', label='Buy & Hold', zorder=2)
    for i, r in enumerate(result):
        ax.plot(pd.to_datetime(r['date']), r['cur_value'], lw=1.8, label=r['strat'], zorder=3)
    ax.set_title('Strategy Equity Curves  (Initial Capital HK$100,000)', fontsize=15, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Portfolio Value (HK$)')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'HK${x/1000:.0f}K'))
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(True, alpha=0.5, ls='--', linewidth=0.5)
    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig3_equity_curves.png', dpi=150, bbox_inches='tight')
    plt.close()


def fig4_performance_bars(result, bh, output_dir='outputs'):
    #Fig4: Strategies Performance Comparison
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('Strategies Performance Comparison', fontsize=15, fontweight='bold')
    short_names = ['S1\nMajority','S2\nHigh Conv','S3\nContrar','S4\nExt.\nContra']

    #Total return
    ax = axes[0]
    rets = [r['total_ret'] for r in result]
    bars = ax.bar(short_names, rets,
                  color=['green' if v>=0 else 'red' for v in rets],
                  alpha=0.85, edgecolor='white', width=0.55)
    ax.axhline(bh['total_ret'], color='black', ls='--', lw=1.8, label=f'B&H {bh["total_ret"]:.1f}%')
    for b, v in zip(bars, rets):
        ax.text(b.get_x()+b.get_width()/2, v+(0.5 if v>=0 else -2), f'{v:.1f}%',
                ha='center', fontsize=9)
    ax.set_title('Total Return (%)',fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)

    #Sharp Ratio
    ax = axes[1]
    sharpe = [r['sharpe_ratio'] for r in result]
    bars = ax.bar(short_names, sharpe,
                  color=['green' if v>=0 else 'red' for v in rets],
                  alpha=0.85, edgecolor='white', width=0.55)
    ax.axhline(bh['sharpe'], color='black', ls='--', lw=1.8, label=f'B&H {bh["sharpe"]:.2f}')
    for b, v in zip(bars, sharpe):
        ax.text(b.get_x()+b.get_width()/2, v+(0.005 if v>=0 else -0.07), f'{v:.2f}',
                ha='center', fontsize=9)
    ax.set_title('Sharpe Ratio',fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)

    #Max Drawdown
    ax = axes[2]
    max_dd = [r['max_dd'] for r in result]
    bars = ax.bar(short_names, max_dd,
                  color='red',
                  alpha=0.85, edgecolor='white', width=0.55)
    for b, v in zip(bars, max_dd):
        ax.text(b.get_x()+b.get_width()/2, v-2, f'{v:.1f}%', ha='center', fontsize=9)
    ax.set_title('Maximum Drawdown(%)',fontsize=11, fontweight='bold')

    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig4_performance_bars.png', dpi=150, bbox_inches='tight')
    plt.close()


def fig5_technical(df_votes, output_dir='outputs'):
    #Fig5: Technical Indicators Overview
    fig, axes = plt.subplots(4, 1, figsize=(14, 14), sharex=True)
    fig.suptitle('Technical Indicators Overview', fontsize=15, fontweight='bold')

    #SMA
    ax = axes[0]
    ax.plot(df_votes['Date'], df_votes['Close'], lw=1.2, label='Close', color='blue')
    ax.plot(df_votes['Date'], df_votes['SMA20'], lw=1.5, label='SMA20', color='orange')
    ax.fill_between(df_votes['Date'], df_votes['Close'], df_votes['SMA20'],
                    where=(df_votes['Close'] >= df_votes['SMA20']), alpha=0.15, color='green')
    ax.fill_between(df_votes['Date'], df_votes['Close'], df_votes['SMA20'],
                    where=(df_votes['Close'] < df_votes['SMA20']), alpha=0.15, color='red')
    ax.set_ylabel('Price', fontsize=10)
    ax.set_title('Price + SMA20', fontsize=11)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.4, ls='--', lw=0.5)

    #RSI
    ax = axes[1]
    ax.plot(df_votes['Date'], df_votes['RSI14'], lw=1.2, color='orange', label='RSI14')
    ax.axhline(60, color='red', ls='--', lw=1, label='Overbought 60')
    ax.axhline(40, color='green', ls='--', lw=1, label='Oversold 40')
    ax.fill_between(df_votes['Date'], df_votes['RSI14'], 60,
                    where=(df_votes['RSI14'] >= 60), alpha=0.2, color='red')
    ax.fill_between(df_votes['Date'], df_votes['RSI14'], 40,
                    where=(df_votes['RSI14'] <= 40), alpha=0.2, color='green')
    ax.set_ylim(0, 100)
    ax.set_ylabel('RSI', fontsize=10)
    ax.set_title('RSI14 (<40 bullish, >60 bearish)', fontsize=11)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.4, ls='--', lw=0.5)

    # MACD
    ax = axes[2]
    ax.plot(df_votes['Date'], df_votes['MACD'], lw=1.2, label='MACD', color='blue')
    ax.plot(df_votes['Date'], df_votes['MACD_signal'], lw=1.2, label='Signal', color='orange', ls='--')
    hist_colors = ['green' if v >= 0 else 'red' for v in df_votes['MACD_hist']]
    ax.bar(df_votes['Date'], df_votes['MACD_hist'], color=hist_colors, alpha=0.6, width=1.5, label='MACD - Signal')
    ax.axhline(0, color='black', lw=0.8)
    ax.set_ylabel('MACD', fontsize=10)
    ax.set_title('MACD (12,26,9)', fontsize=11)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.4, ls='--', lw=0.5)

    # Combined score
    ax = axes[3]
    score = df_votes['combined_score']
    bar_cols = ['green' if v > 0 else ('red' if v < 0 else 'gray') for v in score]
    ax.bar(df_votes['Date'], score, color=bar_cols, alpha=0.75, width=1.5)
    ax.axhline(0, color='black', lw=0.8)
    ax.set_yticks([-3,-2,-1,0,1,2,3])
    ax.set_ylabel('Score', fontsize=10)
    ax.set_title('Combined Filter Score (SMA + RSI + MACD, range -3 to +3)', fontsize=11)
    ax.grid(True, alpha=0.4, ls='--', lw=0.5)

    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig5_technical.png', dpi=150, bbox_inches='tight')
    plt.close()


def fig6_filtered_equity(result, filtered_results, df_votes, output_dir='outputs'):
    #Fig6: Equity Curves with Technical Filter
    full_idx = pd.date_range(df_votes['Date'].min(), df_votes['Date'].max(), freq='B')
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle('Equity Curves with Technical Filters', fontsize=15, fontweight='bold')
    for i, r in enumerate(result[2:]):
        eq = pd.Series(r['cur_value'][1:], index=pd.to_datetime(r['date'][1:]))
        eq = eq.reindex(full_idx).ffill()
        ax.plot(full_idx, eq, lw=2.2, ls='--', label=f'{r["strat"]} BASE', zorder=2)
    for i, r in enumerate(filtered_results):
        eq = pd.Series(r['cur_value'][1:], index=pd.to_datetime(r['date'][1:]))
        eq = eq.reindex(full_idx).ffill()
        ax.plot(full_idx, eq, lw=1.8, label=r['strat'], zorder=1)
    ax.set_xlabel('Date')
    ax.set_ylabel('Portfolio Value (HK$)')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'HK${x/1000:.0f}K'))
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.5, ls='--', linewidth=0.5)
    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig6_filtered_equity.png', dpi=150, bbox_inches='tight')
    plt.close()


def fig7_full_comparison(result, filtered_results, bh, output_dir='outputs'):
    #Fig7: Performance Comparison (with Technical Filter)
    all_results = result[2:] + filtered_results
    names = [r['strat'].replace('S1.','').replace('S2.','').replace('S3.','').
        replace('S4.','').replace('(Up/Down>0.6)','') for r in all_results]
    edge = ['orange' if i < 2 else 'white' for i in range(len(all_results))]
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle('Performance Comparison: Base vs Technical Filtered Strategies',
                 fontsize=15, fontweight='bold')
    #Total return
    ax = axes[0]
    rets = [r['total_ret'] for r in all_results]
    bars = ax.bar(names, rets,
                  color=['green' if v>=0 else 'red' for v in rets],
                  alpha=0.85, edgecolor=edge, linewidth=1.8, width=0.65)
    ax.axhline(bh['total_ret'], color='black', ls='--', lw=1.8, label=f'B&H {bh["total_ret"]:.1f}%')
    for b, v in zip(bars, rets):
        ax.text(b.get_x()+b.get_width()/2, v+(0.5 if v>=0 else -4), f'{v:.1f}%',
                ha='center', fontsize=9)
    ax.set_title('Total Return (%)',fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)

    #Sharp Ratio
    ax = axes[1]
    sharpe = [r['sharpe_ratio'] for r in all_results]
    bars = ax.bar(names, sharpe,
                  color=['green' if v>=0 else 'red' for v in rets],
                  alpha=0.85, edgecolor=edge, linewidth=1.8, width=0.65)
    ax.axhline(bh['sharpe'], color='black', ls='--', lw=1.8, label=f'B&H {bh["sharpe"]:.2f}')
    for b, v in zip(bars, sharpe):
        ax.text(b.get_x()+b.get_width()/2, v+(0.005 if v>=0 else -0.2), f'{v:.2f}',
                ha='center', fontsize=9)
    ax.set_title('Sharpe Ratio',fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)

    #Max Drawdown
    ax = axes[2]
    max_dd = [r['max_dd'] for r in all_results]
    bars = ax.bar(names, max_dd,
                  color='red',
                  alpha=0.85, edgecolor=edge, linewidth=1.8, width=0.65)
    for b, v in zip(bars, max_dd):
        ax.text(b.get_x()+b.get_width()/2, v-1.5, f'{v:.1f}%', ha='center', fontsize=9)
    ax.set_title('Maximum Drawdown(%)',fontsize=11, fontweight='bold')

    for ax in axes:
        ax.set_xticks(range(len(names))) 
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
    plt.tight_layout()
    fig.savefig(f'{output_dir}/fig7_full_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
