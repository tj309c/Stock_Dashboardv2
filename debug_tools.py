import streamlit as st

def display_session_state(container):
    """
    Creates an expandable section in the UI to display the current
    contents of Streamlit's session state.
    """
    with container.expander("🕵️‍♂️ Session State Inspector"):
        st.write("Current state of `st.session_state`:")
        
        # Filter out internal Streamlit keys for a cleaner view
        state_to_show = {k: v for k, v in st.session_state.items() if not k.startswith('__')}
        
        if state_to_show:
            st.json(state_to_show)
        else:
            st.info("Session state is currently empty.")

def display_cache_manager(container):
    """
    Creates a UI section with buttons to clear Streamlit's caches.
    """
    with container.expander("🧹 Cache Manager"):
        st.write("Use these buttons to clear cached data and force a full data reload on the next run.")
        
        if st.button("Clear Data Cache (`@st.cache_data`)"):
            st.cache_data.clear()
            st.success("Cleared the data cache. Rerunning app...")
            st.rerun()
            
        st.info("Clearing the cache will make the next app load slower as all data will be re-fetched from APIs.")