import json
from pathlib import Path

from src.data_loader import load_data, print_summary
from src.data_analysis import compute_accuracy, compute_return_by_bin, print_extreme_stats
from src.technical_indicator import add_indicators, add_filter_signals
from src.strategies_and_backtest import run_base_strategies, buy_and_hold, run_filtered_strategies
from src.visualization import (fig1_overview, fig2_accuracy, fig3_equity_curves,
                                fig4_performance_bars, fig5_technical,
                                fig6_filtered_equity, fig7_full_comparison)

Path('outputs').mkdir(exist_ok=True)

# 1. Load data
df, df_votes = load_data('data/HSI.xlsx')
print_summary(df, df_votes)

# 2. Analysis
df_votes, accuracy, sameday_acc = compute_accuracy(df_votes)
df_votes, ret_by_bin = compute_return_by_bin(df_votes)
print_extreme_stats(df_votes)

# 3. Base strategies
result = run_base_strategies(df_votes)
bh = buy_and_hold(df)

# 4. Technical indicators
df_votes = add_indicators(df_votes)
df_votes = add_filter_signals(df_votes)

# 5. Filtered strategies
filtered_results = run_filtered_strategies(df_votes)

# 6. Figures
fig1_overview(df_votes)
fig2_accuracy(df_votes, accuracy, ret_by_bin)
fig3_equity_curves(result, bh)
fig4_performance_bars(result, bh)
fig5_technical(df_votes)
fig6_filtered_equity(result, filtered_results, df_votes)
fig7_full_comparison(result, filtered_results, bh)

print('Done. Figures saved to outputs/')

# 7. Summary JSON
summary = {
    'n_days':len(df),
    'n_voted':len(df_votes),
    'coverage':round((len(df_votes) / len(df) * 100), 1),
    'accuracy':sameday_acc,
    'up_mean':round(df_votes['Up'].mean()*100, 1),
    'down_mean':round(df_votes['Down'].mean()*100, 1),
    'bull_days':int(df_votes['bull_day'].sum()),
    'bear_days':int((df_votes['bull_day']==0).sum()),
    'bh_total':round(bh['total_ret'], 1),
    'bh_cagr':round(bh['cagr'], 1),
    'bh_sharpe':round(bh['sharpe'], 2),
    'results': [{
        'strat':r['strat'],
        'trades':r['n_trades'],
        'win_rate':round(r['win_rate'], 1),
        'total_ret': round(r['total_ret'], 1),
        'cagr':round(r['cagr'], 1),
        'sharpe':round(r['sharpe_ratio'], 2),
        'max_dd':round(r['max_dd'], 1),
        'avg_ret':round(r['avg_ret'], 4),
    } for r in result + filtered_results],
}
with open('outputs/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('Done. Figures and summary.json saved to outputs/')
