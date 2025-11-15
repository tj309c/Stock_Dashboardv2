"""
Economic Data Pipeline
Fetches macro economic data from Federal Reserve (FRED), Bureau of Labor Statistics (BLS), 
and Energy Information Administration (EIA).

Free APIs:
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html (Unlimited, instant approval)
- BLS: https://www.bls.gov/developers/ (No key needed for public data, 500 series/query limit)
- EIA: https://www.eia.gov/opendata/register.php (Free, instant approval)
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    
try:
    import eia
    EIA_AVAILABLE = True
except ImportError:
    EIA_AVAILABLE = False

import requests

logger = logging.getLogger(__name__)


class EconomicDataPipeline:
    """
    Aggregates macroeconomic data from multiple free government APIs.
    Use cases:
    - Correlate CPI with growth stock valuations
    - Model interest rate impact on REITs and utilities
    - Track oil prices vs energy sector performance
    - Monitor unemployment vs consumer discretionary stocks
    """
    
    def __init__(self):
        """Initialize with API keys from Streamlit secrets or environment variables."""
        self.fred_client = None
        self.eia_api_key = None
        
        # Try to get API keys
        try:
            if hasattr(st, 'secrets'):
                fred_key = st.secrets.get('FRED_API_KEY')
                self.eia_api_key = st.secrets.get('EIA_API_KEY')
            else:
                import os
                fred_key = os.getenv('FRED_API_KEY')
                self.eia_api_key = os.getenv('EIA_API_KEY')
                
            if fred_key and FRED_AVAILABLE:
                self.fred_client = Fred(api_key=fred_key)
                logger.info("FRED API initialized successfully")
            else:
                logger.warning("FRED API key not found or fredapi not installed")
                
            if self.eia_api_key and EIA_AVAILABLE:
                eia.api_key = self.eia_api_key
                logger.info("EIA API initialized successfully")
            else:
                logger.warning("EIA API key not found or eia-python not installed")
                
        except Exception as e:
            logger.error(f"Error initializing economic data APIs: {e}")
    
    # =========================================================================
    # FRED API Methods (Federal Reserve Economic Data)
    # =========================================================================
    
    def get_inflation_data(self, years: int = 10) -> Optional[pd.DataFrame]:
        """Get inflation data (mode-aware)"""
        from src.config.performance_config import should_fetch_economic, get_adjusted_ttl
        
        if not should_fetch_economic():
            return None
        
        ttl = get_adjusted_ttl(86400)  # Base 24 hours
        return self._get_inflation_data_cached(years, ttl)
    
    @st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
    def _get_inflation_data_cached(_self, years: int, ttl: int) -> Optional[pd.DataFrame]:
        """
        Fetch Consumer Price Index (CPI) data - core inflation metric.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, cpi, yoy_change
        """
        if not _self.fred_client:
            st.warning("⚠️ FRED API not configured. Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
            return None
            
        try:
            # CPIAUCSL = Consumer Price Index for All Urban Consumers: All Items
            series_id = 'CPIAUCSL'
            start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
            
            data = _self.fred_client.get_series(series_id, observation_start=start_date)
            
            df = pd.DataFrame({
                'date': data.index,
                'cpi': data.values
            })
            
            # Calculate year-over-year change
            df['yoy_change'] = df['cpi'].pct_change(periods=12) * 100  # Monthly data, so 12 periods = 1 year
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Error fetching CPI data: {e}")
            st.error(f"❌ Error fetching inflation data: {str(e)}")
            return None
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_interest_rate_data(_self, years: int = 10) -> Optional[pd.DataFrame]:
        """
        Fetch Federal Funds Rate - the rate banks charge each other for overnight loans.
        Critical for REIT valuations, bond yields, mortgage rates.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, fed_funds_rate
        """
        if not _self.fred_client:
            return None
            
        try:
            # FEDFUNDS = Effective Federal Funds Rate
            series_id = 'FEDFUNDS'
            start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
            
            data = _self.fred_client.get_series(series_id, observation_start=start_date)
            
            df = pd.DataFrame({
                'date': data.index,
                'fed_funds_rate': data.values
            })
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Error fetching interest rate data: {e}")
            return None
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_unemployment_data(_self, years: int = 10) -> Optional[pd.DataFrame]:
        """
        Fetch Unemployment Rate - critical labor market indicator.
        High unemployment = consumer weakness = bad for consumer discretionary stocks.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, unemployment_rate
        """
        if not _self.fred_client:
            return None
            
        try:
            # UNRATE = Civilian Unemployment Rate
            series_id = 'UNRATE'
            start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
            
            data = _self.fred_client.get_series(series_id, observation_start=start_date)
            
            df = pd.DataFrame({
                'date': data.index,
                'unemployment_rate': data.values
            })
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Error fetching unemployment data: {e}")
            return None
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_gdp_data(_self, years: int = 10) -> Optional[pd.DataFrame]:
        """
        Fetch Real GDP - the total economic output.
        GDP growth = bullish for equities, GDP contraction = recession risk.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, gdp, yoy_change
        """
        if not _self.fred_client:
            return None
            
        try:
            # GDPC1 = Real Gross Domestic Product (Billions of Chained 2017 Dollars, Quarterly)
            series_id = 'GDPC1'
            start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
            
            data = _self.fred_client.get_series(series_id, observation_start=start_date)
            
            df = pd.DataFrame({
                'date': data.index,
                'gdp': data.values
            })
            
            # Calculate year-over-year change
            df['yoy_change'] = df['gdp'].pct_change(periods=4) * 100  # Quarterly data, so 4 periods = 1 year
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Error fetching GDP data: {e}")
            return None
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_10year_treasury_yield(_self, years: int = 10) -> Optional[pd.DataFrame]:
        """
        Fetch 10-Year Treasury Yield - risk-free rate used in DCF models.
        Rising yields = lower stock valuations (higher discount rate).
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, treasury_10y
        """
        if not _self.fred_client:
            return None
            
        try:
            # DGS10 = 10-Year Treasury Constant Maturity Rate
            series_id = 'DGS10'
            start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
            
            data = _self.fred_client.get_series(series_id, observation_start=start_date)
            
            df = pd.DataFrame({
                'date': data.index,
                'treasury_10y': data.values
            })
            
            # Remove NaN values (market holidays)
            df = df.dropna()
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Error fetching 10-year treasury data: {e}")
            return None
    
    # =========================================================================
    # BLS API Methods (Bureau of Labor Statistics)
    # =========================================================================
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_bls_employment_data(_self, years: int = 5) -> Optional[pd.DataFrame]:
        """
        Fetch detailed employment data from BLS.
        No API key required for basic access.
        
        Args:
            years: Number of years of historical data (max 10 without registration)
            
        Returns:
            DataFrame with employment metrics
        """
        try:
            # BLS Series ID: LNS11300000 = Labor Force Participation Rate
            series_id = 'LNS11300000'
            
            start_year = datetime.now().year - years
            end_year = datetime.now().year
            
            url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
            
            payload = {
                'seriesid': [series_id],
                'startyear': str(start_year),
                'endyear': str(end_year)
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Results' in data and 'series' in data['Results']:
                    series = data['Results']['series'][0]['data']
                    
                    df = pd.DataFrame(series)
                    df['date'] = pd.to_datetime(df['year'] + '-' + df['period'].str.replace('M', '') + '-01')
                    df['labor_force_participation'] = pd.to_numeric(df['value'])
                    
                    return df[['date', 'labor_force_participation']].sort_values('date').reset_index(drop=True)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching BLS data: {e}")
            return None
    
    # =========================================================================
    # EIA API Methods (Energy Information Administration)
    # =========================================================================
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_crude_oil_prices(_self, years: int = 5) -> Optional[pd.DataFrame]:
        """
        Fetch WTI Crude Oil prices from EIA.
        Correlates with XLE (energy sector ETF) and inflation expectations.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, wti_price
        """
        if not _self.eia_api_key or not EIA_AVAILABLE:
            st.warning("⚠️ EIA API not configured. Get free key at: https://www.eia.gov/opendata/register.php")
            return None
            
        try:
            # Series ID for WTI Spot Price (Dollars per Barrel)
            series_id = 'PET.RWTC.W'
            
            url = f'https://api.eia.gov/v2/petroleum/pri/spt/data/'
            
            params = {
                'api_key': _self.eia_api_key,
                'frequency': 'weekly',
                'data[0]': 'value',
                'facets[series][]': 'RWTC',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': years * 52  # Weekly data
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and 'data' in data['response']:
                    records = data['response']['data']
                    
                    df = pd.DataFrame(records)
                    df['date'] = pd.to_datetime(df['period'])
                    df['wti_price'] = pd.to_numeric(df['value'])
                    
                    return df[['date', 'wti_price']].sort_values('date').reset_index(drop=True)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching oil price data: {e}")
            return None
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_natural_gas_prices(_self, years: int = 5) -> Optional[pd.DataFrame]:
        """
        Fetch Natural Gas prices from EIA.
        Important for utilities sector and European energy crisis monitoring.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            DataFrame with columns: date, nat_gas_price
        """
        if not _self.eia_api_key or not EIA_AVAILABLE:
            return None
            
        try:
            url = f'https://api.eia.gov/v2/natural-gas/pri/fut/data/'
            
            params = {
                'api_key': _self.eia_api_key,
                'frequency': 'daily',
                'data[0]': 'value',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': years * 252  # Daily trading data
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and 'data' in data['response']:
                    records = data['response']['data']
                    
                    df = pd.DataFrame(records)
                    df['date'] = pd.to_datetime(df['period'])
                    df['nat_gas_price'] = pd.to_numeric(df['value'])
                    
                    return df[['date', 'nat_gas_price']].sort_values('date').reset_index(drop=True)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching natural gas data: {e}")
            return None
    
    # =========================================================================
    # Aggregation Methods
    # =========================================================================
    
    def get_all_macro_data(self, years: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Fetch all available macro data and return as dictionary.
        
        Args:
            years: Number of years of historical data
            
        Returns:
            Dictionary with keys: 'inflation', 'interest_rates', 'unemployment', 
            'gdp', 'treasury_10y', 'oil', 'natgas'
        """
        data_dict = {}
        
        with st.spinner("Fetching macroeconomic data..."):
            # FRED data
            data_dict['inflation'] = self.get_inflation_data(years)
            data_dict['interest_rates'] = self.get_interest_rate_data(years)
            data_dict['unemployment'] = self.get_unemployment_data(years)
            data_dict['gdp'] = self.get_gdp_data(years)
            data_dict['treasury_10y'] = self.get_10year_treasury_yield(years)
            
            # BLS data
            data_dict['labor_participation'] = self.get_bls_employment_data(years)
            
            # EIA data
            data_dict['oil'] = self.get_crude_oil_prices(years)
            data_dict['natgas'] = self.get_natural_gas_prices(years)
        
        # Filter out None values
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
        
        return data_dict
    
    def get_current_snapshot(self) -> Dict[str, float]:
        """
        Get the most recent value for each macro indicator.
        Useful for quick dashboard display.
        
        Returns:
            Dictionary with current values
        """
        snapshot = {}
        
        try:
            # Get latest data points
            inflation_df = self.get_inflation_data(years=1)
            if inflation_df is not None and len(inflation_df) > 0:
                snapshot['cpi'] = inflation_df['cpi'].iloc[-1]
                snapshot['inflation_yoy'] = inflation_df['yoy_change'].iloc[-1]
            
            rates_df = self.get_interest_rate_data(years=1)
            if rates_df is not None and len(rates_df) > 0:
                snapshot['fed_funds_rate'] = rates_df['fed_funds_rate'].iloc[-1]
            
            unemployment_df = self.get_unemployment_data(years=1)
            if unemployment_df is not None and len(unemployment_df) > 0:
                snapshot['unemployment_rate'] = unemployment_df['unemployment_rate'].iloc[-1]
            
            treasury_df = self.get_10year_treasury_yield(years=1)
            if treasury_df is not None and len(treasury_df) > 0:
                snapshot['treasury_10y'] = treasury_df['treasury_10y'].iloc[-1]
            
            oil_df = self.get_crude_oil_prices(years=1)
            if oil_df is not None and len(oil_df) > 0:
                snapshot['wti_oil'] = oil_df['wti_price'].iloc[-1]
                
        except Exception as e:
            logger.error(f"Error getting current snapshot: {e}")
        
        return snapshot


# Convenience function for easy import
def get_economic_data_pipeline() -> EconomicDataPipeline:
    """Factory function to get configured pipeline instance."""
    return EconomicDataPipeline()
