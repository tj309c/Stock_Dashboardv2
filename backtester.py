import pandas as pd
import numpy as np
from datetime import datetime
from valuation_models import calculate_dcf, DCFInputs


def run_dcf_backtest(price_data, income_data, balance_sheet_data, cash_flow_data, assumptions):
    """
    Runs a DCF backtest to compare historical fair values with actual prices.

    Args:
        price_data: DataFrame with historical price data
        income_data: DataFrame with income statement data
        balance_sheet_data: DataFrame with balance sheet data
        cash_flow_data: DataFrame with cash flow data
        assumptions: Dict with DCF assumptions (growth rates, wacc, etc.)

    Returns:
        backtest_df: DataFrame with historical fair values vs actual prices
        mape: Mean Absolute Percentage Error
    """
    try:
        backtest_results = []

        # Get quarterly dates from financial data
        if cash_flow_data.empty:
            return pd.DataFrame(), 0.0

        dates = cash_flow_data.columns[:8]  # Last 8 quarters

        for date in dates:
            try:
                # Extract financial data for this period
                ocf = cash_flow_data.loc['Operating Cash Flow', date] if 'Operating Cash Flow' in cash_flow_data.index else 0
                capex = cash_flow_data.loc['Capital Expenditure', date] if 'Capital Expenditure' in cash_flow_data.index else 0
                cash = balance_sheet_data.loc['Cash And Cash Equivalents', date] if 'Cash And Cash Equivalents' in balance_sheet_data.index and date in balance_sheet_data.columns else 0

                # Get total debt
                if 'Total Debt' in balance_sheet_data.index and date in balance_sheet_data.columns:
                    debt = balance_sheet_data.loc['Total Debt', date]
                else:
                    long_term = balance_sheet_data.loc['Long Term Debt', date] if 'Long Term Debt' in balance_sheet_data.index and date in balance_sheet_data.columns else 0
                    short_term = balance_sheet_data.loc['Short Term Debt', date] if 'Short Term Debt' in balance_sheet_data.index and date in balance_sheet_data.columns else 0
                    debt = long_term + short_term

                # Get revenue for DCF inputs
                revenue = income_data.loc['Total Revenue', date] if 'Total Revenue' in income_data.index and date in income_data.columns else 0

                if revenue <= 0:
                    continue

                # Create DCF inputs
                dcf_inputs = DCFInputs(
                    revenue_growth_rates=assumptions.get('growth_rates', [0.10, 0.10, 0.08, 0.08, 0.06]),
                    ebit_margin=assumptions.get('ebit_margin', 0.20),
                    tax_rate=assumptions.get('tax_rate', 0.21),
                    depreciation_as_pct_revenue=assumptions.get('depreciation_pct', 0.03),
                    capex_as_pct_revenue=assumptions.get('capex_pct', 0.05),
                    nwc_as_pct_revenue=assumptions.get('nwc_pct', 0.10),
                    terminal_growth_rate=assumptions.get('terminal_growth', 0.025),
                    wacc=assumptions.get('wacc', 0.10),
                    cash=float(cash),
                    total_debt=float(debt),
                    shares_outstanding=assumptions.get('shares_outstanding', 1_000_000_000),
                    current_revenue=float(revenue)
                )

                # Calculate DCF value
                fair_value, _ = calculate_dcf(dcf_inputs)

                # Get actual price on this date
                date_ts = pd.to_datetime(date)
                price_on_date = None

                if date_ts in price_data.index:
                    price_on_date = price_data.loc[date_ts, 'Close']
                else:
                    # Find closest date
                    closest_dates = price_data.index[price_data.index >= date_ts]
                    if len(closest_dates) > 0:
                        price_on_date = price_data.loc[closest_dates[0], 'Close']

                if price_on_date and fair_value > 0:
                    backtest_results.append({
                        'Date': date_ts,
                        'Fair Value': fair_value,
                        'Actual Price': price_on_date,
                        'Difference %': ((fair_value - price_on_date) / price_on_date) * 100
                    })

            except Exception as e:
                continue

        if not backtest_results:
            return pd.DataFrame(), 0.0

        backtest_df = pd.DataFrame(backtest_results)

        # Calculate MAPE
        mape = (backtest_df['Difference %'].abs()).mean()

        return backtest_df, mape

    except Exception as e:
        return pd.DataFrame(), 0.0


def run_relative_backtest(price_data, quarterly_income_data, sector_pe):
    """
    Runs a relative valuation backtest using P/E ratios.

    Args:
        price_data: DataFrame with historical price data
        quarterly_income_data: DataFrame with quarterly income data
        sector_pe: Median sector P/E ratio

    Returns:
        backtest_df: DataFrame with historical fair values vs actual prices
        mape: Mean Absolute Percentage Error
    """
    try:
        backtest_results = []

        if quarterly_income_data.empty:
            return pd.DataFrame(), 0.0

        # Find EPS column
        eps_column = None
        for col in ['Basic EPS', 'Diluted EPS', 'Normalized Basic EPS']:
            if col in quarterly_income_data.index:
                eps_column = col
                break

        if not eps_column:
            return pd.DataFrame(), 0.0

        eps_data = quarterly_income_data.loc[eps_column]

        # Calculate TTM EPS for each quarter
        ttm_eps = eps_data.iloc[::-1].rolling(window=4, min_periods=4).sum().iloc[::-1]

        for date, eps_ttm in ttm_eps.items():
            if pd.isna(eps_ttm) or eps_ttm <= 0:
                continue

            try:
                # Calculate fair value using sector P/E
                fair_value = eps_ttm * sector_pe

                # Get actual price on this date
                date_ts = pd.to_datetime(date)
                price_on_date = None

                if date_ts in price_data.index:
                    price_on_date = price_data.loc[date_ts, 'Close']
                else:
                    # Find closest date
                    closest_dates = price_data.index[price_data.index >= date_ts]
                    if len(closest_dates) > 0:
                        price_on_date = price_data.loc[closest_dates[0], 'Close']

                if price_on_date and fair_value > 0:
                    backtest_results.append({
                        'Date': date_ts,
                        'TTM EPS': eps_ttm,
                        'Sector P/E': sector_pe,
                        'Fair Value': fair_value,
                        'Actual Price': price_on_date,
                        'Difference %': ((fair_value - price_on_date) / price_on_date) * 100
                    })

            except Exception as e:
                continue

        if not backtest_results:
            return pd.DataFrame(), 0.0

        backtest_df = pd.DataFrame(backtest_results)

        # Calculate MAPE
        mape = (backtest_df['Difference %'].abs()).mean()

        return backtest_df, mape

    except Exception as e:
        return pd.DataFrame(), 0.0
