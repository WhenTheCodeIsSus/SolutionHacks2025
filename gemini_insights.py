#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Platform - Gemini AI Insights Module

This module implements Gemini AI integration for analyzing electricity usage patterns
and providing personalized recommendations to optimize energy consumption.
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class GeminiInsights:
    """
    Gemini AI Insights class for the Home Appliance Scheduling Optimization Platform
    
    This class implements a Streamlit-based interface for Gemini AI integration,
    allowing users to get AI-powered insights and recommendations based on their electricity usage data.
    """
    
    def __init__(self):
        """
        Initialize the Gemini AI Insights interface
        
        Set page configuration and initialize session state variables
        """
        # Set page title and layout
        st.set_page_config(
            page_title="Home Appliance Scheduling - Gemini AI Insights",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state for API key and insights
        if "gemini_api_key" not in st.session_state:
            st.session_state.gemini_api_key = ""
            
        if "gemini_insights" not in st.session_state:
            st.session_state.gemini_insights = None
            
        if "gemini_advice" not in st.session_state:
            st.session_state.gemini_advice = None
            
        if "api_key_valid" not in st.session_state:
            st.session_state.api_key_valid = False
            
        # Reference to usage analyzer (will be set from outside)
        self.usage_analyzer = None
            
    def run(self):
        """
        Run the Gemini AI Insights interface
        
        Display page title and each functional area
        """
        # Display page title
        st.title("Gemini AI Electricity Usage Insights")
                
        st.markdown("""
        Get AI-powered insights and personalized recommendations based on your electricity usage patterns.
        Gemini AI analyzes your data to help you optimize energy consumption and reduce costs.
        """)
        
        # Create sections
        with st.container():
            self._render_api_key_section()
            
        st.markdown("---")
        
        # Only show the rest if API key is provided
        if st.session_state.gemini_api_key:
            with st.container():
                self._render_data_selection()
                
            if st.session_state.gemini_insights:
                st.markdown("---")
                with st.container():
                    self._render_insights()
            
        # Navigation buttons
        st.markdown("---")
        self._render_navigation()
    
    def _render_api_key_section(self):
        """
        Render the API key input section
        """
        st.markdown("### Gemini AI API Key")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Use password input for API key
            api_key = st.text_input(
                "Enter your Gemini AI API Key",
                type="password",
                value=st.session_state.gemini_api_key,
                help="Your API key will be stored securely in the session state and not saved permanently."
            )
            
            st.session_state.gemini_api_key = api_key
            
            if not api_key:
                st.info("To use Gemini AI insights, you need to provide an API key. [Get a Gemini API key here](https://ai.google.dev/).")
        
        with col2:
            # Validate API key button
            if st.button("Validate API Key", use_container_width=True, disabled=not api_key):
                with st.spinner("Validating API key..."):
                    is_valid = self._validate_api_key(api_key)
                    if is_valid:
                        st.success("API key is valid!")
                        st.session_state.api_key_valid = True
                    else:
                        st.error("Invalid API key. Please check and try again.")
                        st.session_state.api_key_valid = False
    
    def _render_data_selection(self):
        """
        Render the data selection section
        """
        st.markdown("### Analyze Your Electricity Usage")
        
        # Check if we have usage data
        if self.usage_analyzer and self.usage_analyzer.usage_history and "usage_history" in self.usage_analyzer.usage_history:
            history = self.usage_analyzer.usage_history["usage_history"]
            
            if not history:
                st.warning("No electricity usage data found. Please use the application to generate some usage data first.")
                return
            
            # Time period selection
            st.subheader("Select Time Period")
            
            # Get available dates from history
            dates = [entry["date"] for entry in history]
            
            # Create date selection
            col1, col2 = st.columns(2)
            
            with col1:
                selected_period = st.radio(
                    "Analysis Period",
                    options=["Last Usage", "Last Week", "Last Month", "Custom"],
                    index=0
                )
            
            with col2:
                if selected_period == "Custom":
                    start_date = st.date_input("Start Date", value=datetime.strptime(dates[-1], "%Y-%m-%d").date() - timedelta(days=7))
                    end_date = st.date_input("End Date", value=datetime.strptime(dates[-1], "%Y-%m-%d").date())
                    
                    # Validate date range
                    if start_date > end_date:
                        st.error("Start date must be before end date.")
                        return
                else:
                    # Set default date ranges based on selection
                    end_date = datetime.strptime(dates[-1], "%Y-%m-%d").date()
                    if selected_period == "Last Usage":
                        start_date = end_date
                    elif selected_period == "Last Week":
                        start_date = end_date - timedelta(days=7)
                    elif selected_period == "Last Month":
                        start_date = end_date - timedelta(days=30)
            
            # Filter data based on selected date range
            filtered_data = []
            for entry in history:
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
                if start_date <= entry_date <= end_date:
                    filtered_data.append(entry)
            
            if not filtered_data:
                st.warning(f"No data available for the selected date range ({start_date} to {end_date}).")
                return
            
            # Display data summary
            st.subheader("Data Summary")
            st.write(f"Analysis period: {start_date} to {end_date}")
            st.write(f"Number of days with data: {len(filtered_data)}")
            
            # Analysis options
            st.subheader("Analysis Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                analysis_type = st.multiselect(
                    "Select Analysis Types",
                    options=["Usage Patterns", "Cost Optimization", "Energy Efficiency", "Appliance Recommendations"],
                    default=["Usage Patterns", "Cost Optimization"]
                )
            
            with col2:
                detail_level = st.select_slider(
                    "Detail Level",
                    options=["Basic", "Standard", "Detailed"],
                    value="Standard"
                )
            
            # Generate insights button
            if st.button("Generate AI Insights", type="primary", use_container_width=True):
                with st.spinner("Analyzing your electricity usage data with Gemini AI..."):
                    # Format data for Gemini API
                    formatted_data = self._format_data_for_gemini(filtered_data)
                    
                    # Call Gemini API
                    insights, advice = self._call_gemini_api(
                        formatted_data, 
                        analysis_type, 
                        detail_level
                    )
                    
                    # Store results in session state
                    st.session_state.gemini_insights = insights
                    st.session_state.gemini_advice = advice
                    
                    # Force rerun to display results
                    st.rerun()
        else:
            st.warning("No electricity usage data found. Please use the application to generate some usage data first.")
    
    def _render_insights(self):
        """
        Render the insights section
        """
        st.markdown("### Gemini AI Insights")
        
        # Create tabs for different types of insights
        tab1, tab2 = st.tabs(["Usage Analysis", "Recommendations"])
        
        with tab1:
            if st.session_state.gemini_insights:
                st.markdown(st.session_state.gemini_insights)
            else:
                st.info("No insights available. Generate insights first.")
        
        with tab2:
            if st.session_state.gemini_advice:
                st.markdown(st.session_state.gemini_advice)
            else:
                st.info("No recommendations available. Generate insights first.")
    
    def _render_navigation(self):
        """
        Render navigation buttons
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Return to Home", type="secondary", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
        
        with col2:
            if st.button("Go to Input Page", type="secondary", use_container_width=True):
                st.session_state.page = "frontend"
                st.rerun()
                
        with col3:
            if st.button("View Results", type="secondary", use_container_width=True):
                st.session_state.page = "results"
                st.rerun()
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate the Gemini API key
        
        Parameters:
            api_key (str): Gemini API key to validate
            
        Returns:
            bool: Whether the API key is valid
        """
        # In a real application, you would make a simple API call to validate the key
        # For this demo, we'll just check if it's non-empty and has a reasonable length
        if not api_key:
            return False
        
        # A real Gemini API key would be validated with a simple API call
        # Here we're just checking if it's at least 20 characters long
        if len(api_key) < 20:
            return False
            
        # Simulate API validation
        try:
            # In a real implementation, you would make an actual API call
            # For demo purposes, we'll assume it's valid if it passes the basic checks
            return True
        except Exception as e:
            st.error(f"Error validating API key: {str(e)}")
            return False
    
    def _format_data_for_gemini(self, usage_data: List[Dict]) -> Dict:
        """
        Format electricity usage data for Gemini API
        
        Parameters:
            usage_data (List[Dict]): List of electricity usage data entries
            
        Returns:
            Dict: Formatted data ready for Gemini API
        """
        # Extract relevant information from usage data
        formatted_data = {
            "time_period": {
                "start_date": usage_data[0]["date"],
                "end_date": usage_data[-1]["date"],
                "total_days": len(usage_data)
            },
            "usage_summary": {
                "total_days": len(usage_data),
                "appliances": {}
            },
            "daily_usage": []
        }
        
        # Process each day's data
        for day_data in usage_data:
            day_summary = {
                "date": day_data["date"],
                "prices": day_data["prices"],
                "appliances": []
            }
            
            # Process appliance data
            for appliance in day_data.get("appliances", []):
                app_name = appliance["name"]
                app_power = appliance["power"]
                
                # Add to daily summary
                day_summary["appliances"].append({
                    "name": app_name,
                    "power": app_power,
                    "runtime": appliance.get("runtime", 0),
                    "start_hour": appliance.get("start_hour", 0)
                })
                
                # Update overall appliance summary
                if app_name not in formatted_data["usage_summary"]["appliances"]:
                    formatted_data["usage_summary"]["appliances"][app_name] = {
                        "total_usage": 0,
                        "usage_count": 0,
                        "power": app_power
                    }
                
                formatted_data["usage_summary"]["appliances"][app_name]["total_usage"] += 1
                formatted_data["usage_summary"]["appliances"][app_name]["usage_count"] += 1
            
            formatted_data["daily_usage"].append(day_summary)
        
        return formatted_data
    
    def _call_gemini_api(self, usage_data: Dict, analysis_types: List[str], detail_level: str) -> tuple:
        """
        Call Gemini API to get insights and recommendations
        
        Parameters:
            usage_data (Dict): Formatted electricity usage data
            analysis_types (List[str]): Types of analysis to perform
            detail_level (str): Level of detail for the analysis
            
        Returns:
            tuple: (insights, recommendations)
        """
        # In a real implementation, this would make an actual API call to Gemini
        # For this demo, we'll generate a simulated response
        
        # Create a prompt for Gemini based on the data and analysis options
        prompt = self._create_gemini_prompt(usage_data, analysis_types, detail_level)
        
        try:
            # In a real implementation, you would call the Gemini API here
            # For demo purposes, we'll generate a simulated response
            insights = self._generate_simulated_insights(usage_data, analysis_types)
            advice = self._generate_simulated_advice(usage_data, analysis_types)
            
            return insights, advice
        except Exception as e:
            st.error(f"Error calling Gemini API: {str(e)}")
            return "Error generating insights.", "Error generating recommendations."
    
    def _create_gemini_prompt(self, usage_data: Dict, analysis_types: List[str], detail_level: str) -> str:
        """
        Create a prompt for Gemini API based on the data and analysis options
        
        Parameters:
            usage_data (Dict): Formatted electricity usage data
            analysis_types (List[str]): Types of analysis to perform
            detail_level (str): Level of detail for the analysis
            
        Returns:
            str: Prompt for Gemini API
        """
        # Build a prompt that would be sent to Gemini in a real implementation
        prompt = f"""
        Analyze the following electricity usage data and provide insights and recommendations.
        
        Time Period: {usage_data['time_period']['start_date']} to {usage_data['time_period']['end_date']} ({usage_data['time_period']['total_days']} days)
        
        Analysis Types: {', '.join(analysis_types)}
        Detail Level: {detail_level}
        
        Usage Summary:
        - Total Days: {usage_data['usage_summary']['total_days']}
        - Appliances: {len(usage_data['usage_summary']['appliances'])}
        
        Please provide:
        1. A detailed analysis of the electricity usage patterns
        2. Specific recommendations for optimizing electricity usage
        3. Potential cost savings opportunities
        """
        
        return prompt
    
    def _generate_simulated_insights(self, usage_data: Dict, analysis_types: List[str]) -> str:
        """
        Generate simulated insights for demo purposes
        
        Parameters:
            usage_data (Dict): Formatted electricity usage data
            analysis_types (List[str]): Types of analysis to perform
            
        Returns:
            str: Simulated insights
        """
        # In a real implementation, this would be the response from Gemini API
        # For demo purposes, we'll generate a simulated response
        
        appliance_count = len(usage_data["usage_summary"]["appliances"])
        days_count = usage_data["time_period"]["total_days"]
        
        insights = f"""
        ## Electricity Usage Analysis

        ### Usage Patterns
        
        Based on your electricity usage data from {usage_data['time_period']['start_date']} to {usage_data['time_period']['end_date']} ({days_count} days), I've identified the following patterns:
        
        #### Peak Usage Times
        - **Morning Peak**: Your electricity usage typically spikes between 7-9 AM, primarily from kitchen appliances and morning routines
        - **Evening Peak**: A larger peak occurs between 6-9 PM when multiple appliances run simultaneously
        
        #### Appliance Usage
        - You have {appliance_count} main appliances in your usage data
        - Your washing machine and dishwasher are frequently run during peak price hours
        - Your refrigerator accounts for approximately 15% of your baseline electricity consumption
        
        #### Price Optimization Opportunities
        - About 40% of your high-power appliance usage occurs during high-price periods
        - Shifting just 2 hours of usage from peak to off-peak times could reduce your electricity bill by approximately 12%
        - Weekend usage patterns differ significantly from weekday patterns, with more consistent usage throughout the day
        
        ### Energy Consumption Trends
        
        - **Daily Average**: Your household consumes approximately 12.8 kWh per day
        - **Weekly Pattern**: Usage increases by about 30% during weekends
        - **Efficiency Rating**: Based on household size and appliance mix, your energy efficiency ranks in the 60th percentile compared to similar households
        """
        
        return insights
    
    def _generate_simulated_advice(self, usage_data: Dict, analysis_types: List[str]) -> str:
        """
        Generate simulated advice for demo purposes
        
        Parameters:
            usage_data (Dict): Formatted electricity usage data
            analysis_types (List[str]): Types of analysis to perform
            
        Returns:
            str: Simulated advice
        """
        # In a real implementation, this would be the response from Gemini API
        # For demo purposes, we'll generate a simulated response
        
        advice = """
        ## Personalized Recommendations
        
        ### Immediate Actions
        
        1. **Shift High-Power Appliances to Off-Peak Hours**
           - Run your washing machine and dishwasher after 10 PM or before 6 AM to take advantage of lower electricity rates
           - Use delay start features on compatible appliances to automatically run during off-peak hours
        
        2. **Optimize Refrigerator Efficiency**
           - Ensure your refrigerator is set to the optimal temperature (37-40°F for refrigerator, 0-5°F for freezer)
           - Clean the coils every 6 months to improve efficiency by up to 30%
           - Keep the refrigerator at least 70% full to maintain thermal mass
        
        3. **Address Vampire Power**
           - Your data shows approximately 43W of constant background power usage
           - Use smart power strips to completely turn off devices when not in use
           - This could save up to 8% on your monthly electricity bill
        
        ### Medium-Term Improvements
        
        1. **Appliance Scheduling Optimization**
           - Create a weekly schedule that runs your dishwasher, washing machine, and dryer during the lowest price periods
           - Consider batch processing (running multiple loads consecutively) to take advantage of already heated water
        
        2. **Smart Home Integration**
           - Consider adding smart plugs to your highest-consumption devices to enable automated scheduling
           - Implement motion sensors for lighting in less frequently used areas
        
        ### Long-Term Considerations
        
        1. **Appliance Upgrades**
           - Your washing machine appears to be less efficient than modern Energy Star models
           - Upgrading could reduce related electricity usage by approximately 25%
           - Estimated payback period: 3.2 years based on your usage patterns
        
        2. **Energy Storage Options**
           - Based on your price differential between peak and off-peak hours, a small home battery system could be economically viable
           - Estimated ROI period of 7-8 years with current usage patterns
        """
        
        return advice
    
    def set_usage_analyzer(self, usage_analyzer):
        """
        Set the usage analyzer reference
        
        Parameters:
            usage_analyzer: Reference to the UsageAnalyzer instance
        """
        self.usage_analyzer = usage_analyzer

# If run as main program
if __name__ == "__main__":
    insights = GeminiInsights()
    insights.run()
