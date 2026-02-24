# HSI Sentiment Strategy

Using social media pre-market votes to trade the Hang Seng Index as a contrarian indicator, combined with technical indicator (SMA, RSI, MACD).

The crowd is directionally correct only 47.8% of the time. Fading extreme crowd conviction
combined with a SMA filter delivers +31.6% total return vs Buy and Hold +6.5%, with a
Sharpe of 5.64 and max drawdown of only -3.4%.

## Results

| Strategy | Total Return | Sharpe | Max Drawdown |
|---|---|---|---|
| Buy and Hold | +6.5% | 0.21 | -35.9% |
| S3 Contrarian | +9.9% | 0.31 | -22.0% |
| S4 Extreme Contrarian | +8.1% | 0.61 | -16.6% |
| S3 Contrarian + SMA | +109.4% | 3.76 | -10.5% |
| S4 Extreme Contrarian + SMA | +31.6% | 5.64 | -3.4% |

## Project structure

```
├── HSI_Analysis_and_Strategy_Report.pdf
├── main.py                 entry point, run this
├── data/
│   └── HSI.xlsx
├── notebooks/
│   └── HSI_Analysis_and_Strategy.ipynb
├── outputs/                figures and summary.json saved here
└── src/
    ├── data_loader.py                   load and preprocess data
    ├── data_analysis.py                 crowd accuracy analysis
    ├── technical_indicator.py           SMA, RSI, MACD indicators
    ├── strategies_and_backtest.py       backtest engine and all strategies
    └── visualization.py                 all figures
```

## Data

Period: 2022-02-23 to 2025-03-12, 747 trading days, 552 days with vote data (73.9% coverage).
HSI.xlsx has 7 columns: Date, Open, High, Low, Close, Up vote fraction, Down vote fraction.

## Backtest rules

- Signal from pre-market votes before open on day T
- Entry at open, exit at close, no overnight positions
- Commission 0.05% per trade
- Initial capital HK$100,000, no leverage
