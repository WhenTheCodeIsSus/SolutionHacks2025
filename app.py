#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Platform - Main Application

This module integrates the home page, frontend interface, results display interface, and Gemini AI insights, 
implementing a complete home appliance scheduling optimization platform.
"""

import streamlit as st
from frontend import Frontend
from results import Results
from home import main as home_main
from gemini_insights import GeminiInsights
from usage_analyzer import UsageAnalyzer

def main():
    """
    Main function, runs the home appliance scheduling optimization platform
    
    Determines which interface to display based on the page parameter in session_state
    """
    # Initialize session_state
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # Create usage analyzer instance (shared between components)
    usage_analyzer = UsageAnalyzer()
    
    # Determine which interface to display based on the page parameter
    if st.session_state.page == "home":
        home_main()
    elif st.session_state.page == "frontend":
        frontend = Frontend()
        frontend.run()
    elif st.session_state.page == "results":
        results = Results()
        results.run()
    elif st.session_state.page == "patterns":
        # Create a patterns-only view
        results = Results()
        results.render_usage_patterns_page()
    elif st.session_state.page == "gemini_insights":
        # Create Gemini Insights view
        insights = GeminiInsights()
        insights.set_usage_analyzer(usage_analyzer)
        insights.run()

if __name__ == "__main__":
    main()
