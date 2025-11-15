"""
Lazy Loading and Pagination Utilities
Improves performance for large datasets
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
from math import ceil


class LazyDataLoader:
    """Lazy load large datasets with pagination"""
    
    @staticmethod
    def paginate_dataframe(
        df: pd.DataFrame,
        page_size: int = 20,
        page_key: str = "page"
    ) -> pd.DataFrame:
        """
        Paginate a DataFrame for display
        
        Args:
            df: DataFrame to paginate
            page_size: Number of rows per page
            page_key: Unique key for page state
            
        Returns:
            Subset of DataFrame for current page
        """
        if df.empty:
            return df
        
        total_rows = len(df)
        total_pages = ceil(total_rows / page_size)
        
        # Initialize page number in session state
        page_state_key = f"{page_key}_number"
        if page_state_key not in st.session_state:
            st.session_state[page_state_key] = 1
        
        # Page navigation
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
        
        with col1:
            if st.button("⏮️ First", key=f"{page_key}_first", disabled=st.session_state[page_state_key] == 1):
                st.session_state[page_state_key] = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ Previous", key=f"{page_key}_prev", disabled=st.session_state[page_state_key] == 1):
                st.session_state[page_state_key] -= 1
                st.rerun()
        
        with col3:
            if st.button("Next ▶️", key=f"{page_key}_next", disabled=st.session_state[page_state_key] == total_pages):
                st.session_state[page_state_key] += 1
                st.rerun()
        
        with col4:
            if st.button("Last ⏭️", key=f"{page_key}_last", disabled=st.session_state[page_state_key] == total_pages):
                st.session_state[page_state_key] = total_pages
                st.rerun()
        
        # Page info
        st.markdown(
            f"<div style='text-align: center; padding: 10px 0; color: #b0b0b0;'>"
            f"Page {st.session_state[page_state_key]} of {total_pages} "
            f"({total_rows} total rows, showing {page_size} per page)"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Calculate slice
        start_idx = (st.session_state[page_state_key] - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        return df.iloc[start_idx:end_idx]
    
    @staticmethod
    def render_paginated_table(
        df: pd.DataFrame,
        page_size: int = 20,
        page_key: str = "table",
        columns: List[str] = None
    ):
        """
        Render a paginated table
        
        Args:
            df: DataFrame to display
            page_size: Rows per page
            page_key: Unique key for pagination state
            columns: Optional list of columns to display
        """
        if df.empty:
            st.info("No data to display")
            return
        
        # Filter columns if specified
        if columns:
            df = df[columns]
        
        # Get paginated data
        paginated_df = LazyDataLoader.paginate_dataframe(df, page_size, page_key)
        
        # Display table
        st.dataframe(paginated_df, use_container_width=True)
    
    @staticmethod
    def lazy_expander_sections(
        data_dict: Dict[str, pd.DataFrame],
        section_names: Dict[str, str] = None,
        default_expanded: List[str] = None
    ):
        """
        Create lazy-loaded expander sections
        Data is only rendered when section is expanded
        
        Args:
            data_dict: Dictionary mapping section keys to DataFrames
            section_names: Optional mapping of keys to display names
            default_expanded: List of keys to expand by default
        """
        if section_names is None:
            section_names = {k: k.title() for k in data_dict.keys()}
        
        if default_expanded is None:
            default_expanded = []
        
        for key, df in data_dict.items():
            section_name = section_names.get(key, key.title())
            is_expanded = key in default_expanded
            
            with st.expander(f"📊 {section_name} ({len(df)} rows)", expanded=is_expanded):
                if not df.empty:
                    LazyDataLoader.render_paginated_table(
                        df,
                        page_size=20,
                        page_key=f"lazy_{key}"
                    )
                else:
                    st.info(f"No {section_name.lower()} data available")


class VirtualizedList:
    """Virtualized list for displaying large lists efficiently"""
    
    @staticmethod
    def render_virtualized_list(
        items: List[any],
        render_func: callable,
        window_size: int = 50,
        list_key: str = "vlist"
    ):
        """
        Render a virtualized list with windowing
        
        Args:
            items: List of items to display
            render_func: Function to render each item
            window_size: Number of items to show at once
            list_key: Unique key for state
        """
        if not items:
            st.info("No items to display")
            return
        
        total_items = len(items)
        total_windows = ceil(total_items / window_size)
        
        # Window navigation
        window_key = f"{list_key}_window"
        if window_key not in st.session_state:
            st.session_state[window_key] = 0
        
        # Show items in current window
        start_idx = st.session_state[window_key] * window_size
        end_idx = min(start_idx + window_size, total_items)
        
        for idx in range(start_idx, end_idx):
            render_func(items[idx], idx)
        
        # Navigation
        if total_items > window_size:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬆️ Previous", key=f"{list_key}_prev_window", disabled=st.session_state[window_key] == 0):
                    st.session_state[window_key] -= 1
                    st.rerun()
            
            with col2:
                st.markdown(
                    f"<div style='text-align: center; padding: 10px;'>Showing {start_idx + 1}-{end_idx} of {total_items}</div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                if st.button("Next ⬇️", key=f"{list_key}_next_window", disabled=end_idx >= total_items):
                    st.session_state[window_key] += 1
                    st.rerun()


def optimize_dataframe_display(df: pd.DataFrame, max_rows: int = 100) -> Tuple[pd.DataFrame, bool]:
    """
    Optimize DataFrame for display
    Returns truncated DataFrame and whether it was truncated
    
    Args:
        df: DataFrame to optimize
        max_rows: Maximum rows to display without pagination
        
    Returns:
        (optimized_df, is_truncated)
    """
    if len(df) <= max_rows:
        return df, False
    
    st.warning(f"⚠️ Large dataset detected ({len(df)} rows). Showing first {max_rows} rows. Use pagination below for more.")
    return df.head(max_rows), True


# Example usage
def example_integration():
    """Example of lazy loading integration in dashboard"""
    
    # Create sample data
    large_df = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=1000),
        'Price': [100 + i * 0.1 for i in range(1000)],
        'Volume': [1000000 + i * 1000 for i in range(1000)]
    })
    
    st.title("📊 Lazy Loading Demo")
    
    # Method 1: Paginated Table
    st.markdown("### Method 1: Paginated Table")
    LazyDataLoader.render_paginated_table(
        large_df,
        page_size=20,
        page_key="demo_table"
    )
    
    st.markdown("---")
    
    # Method 2: Lazy Expander Sections
    st.markdown("### Method 2: Lazy Expanders")
    LazyDataLoader.lazy_expander_sections(
        data_dict={
            'historical': large_df.head(200),
            'technical': large_df.head(100),
            'fundamentals': large_df.head(50)
        },
        section_names={
            'historical': 'Historical Prices',
            'technical': 'Technical Indicators',
            'fundamentals': 'Fundamental Data'
        },
        default_expanded=['historical']
    )
    
    st.markdown("---")
    
    # Method 3: Virtualized List
    st.markdown("### Method 3: Virtualized List")
    
    def render_item(item, idx):
        st.markdown(f"**Item {idx + 1}:** {item['Date']} - Price: ${item['Price']:.2f}")
    
    VirtualizedList.render_virtualized_list(
        items=large_df.to_dict('records'),
        render_func=render_item,
        window_size=10,
        list_key="demo_list"
    )


if __name__ == "__main__":
    import streamlit as st
    
    st.set_page_config(page_title="Lazy Loading Demo", layout="wide")
    example_integration()
