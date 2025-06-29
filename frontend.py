#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Platform - Frontend Interface Module

This module implements a Streamlit-based interactive frontend interface for users to input electricity prices, power limits, and appliance information.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional, Any
import json


class Frontend:
    """
    Frontend interface class for the Home Appliance Scheduling Optimization Platform
    
    This class implements a Streamlit-based interactive frontend interface for users to input electricity prices, power limits, and appliance information.
    It includes features such as electricity price input, appliance list management, adding appliances, and calculation buttons.
    """
    
    def __init__(self):
        """
        Initialize the frontend interface
        
        Set page configuration and initialize session_state
        """
        # Set page title and layout
        st.set_page_config(
            page_title="Home Appliance Scheduling Optimization Platform",
            page_icon="🔌",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session_state
        if "prices" not in st.session_state:
            # Default price mode: Peak-valley time-of-use pricing
            st.session_state.prices = [
                0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # 0-6 AM (valley price)
                0.8, 0.8, 1.2, 1.2, 1.2, 1.2,  # 6-12 AM (normal/peak price)
                1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 12-18 PM (normal price)
                1.5, 1.5, 1.5, 1.0, 0.8, 0.5   # 18-24 PM (peak/normal/valley price)
            ]
        
        if "max_power" not in st.session_state:
            st.session_state.max_power = 5.0  # Default maximum power limit is 5.0 kW
            
        if "appliances" not in st.session_state:
            st.session_state.appliances = []  # Appliance list
            
        if "next_id" not in st.session_state:
            st.session_state.next_id = 1  # Used to generate unique ID for appliances
            
    def run(self):
        """
        Run the frontend interface
        
        Display page title and each functional area
        """
        # Display page title
        st.title("🔌 Home Appliance Scheduling Optimization Platform")
        st.markdown("""
        This platform helps you optimize the running time of home appliances to minimize electricity costs.
        It calculates the optimal scheduling plan based on electricity price variations, appliance power, and operational requirements.
        """)
        
        # Create three main areas: electricity price input, appliance management, and calculation button
        with st.container():
            st.markdown("## 📊 Electricity Price and Power Settings")
            self.render_electricity_pricing()
            
        st.markdown("---")
        
        with st.container():
            st.markdown("## 📋 Appliance List")
            self.render_appliance_list()
            
        with st.container():
            st.markdown("## ➕ Add New Appliance")
            self.render_add_appliance()
            
        st.markdown("---")
        
        with st.container():
            self.render_calculate_button()
            
    def render_electricity_pricing(self):
        """
        Render electricity price input section
        
        Includes 24-hour electricity price input and global maximum power limit
        """
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 24-Hour Electricity Price Settings")
            st.markdown("Please set the electricity price for each hour (dollars/kWh)")
            
            # Create price chart
            prices = st.session_state.prices
            hours = list(range(24))
            
            # Use Plotly to create interactive chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hours,
                y=prices,
                mode='lines+markers',
                name='Price',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="24-Hour Electricity Price Curve",
                xaxis_title="Hour",
                yaxis_title="Price (dollars/kWh)",
                hovermode="x unified",
                height=400,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            # Set x-axis ticks to integer hours
            fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create electricity price table input
            st.markdown("#### Detailed Price Settings")
            
            # Divide 24 hours into 4 rows, each row has 6 hours
            for row in range(4):
                cols = st.columns(6)
                for col in range(6):
                    hour = row * 6 + col
                    with cols[col]:
                        prices[hour] = st.number_input(
                            f"{hour}:00-{hour+1}:00",
                            min_value=0.0,
                            max_value=10.0,
                            value=float(prices[hour]),
                            step=0.1,
                            format="%.2f",
                            key=f"price_{hour}"
                        )
            
            # Update electricity prices in session_state
            st.session_state.prices = prices
            
            # Provide quick price template selection
            st.markdown("#### Price Templates")
            price_templates = {
                "Peak-Valley Time-of-Use Pricing": [
                    0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # 0-6 AM (valley price)
                    0.8, 0.8, 1.2, 1.2, 1.2, 1.2,  # 6-12 AM (normal/peak price)
                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 12-18 PM (normal price)
                    1.5, 1.5, 1.5, 1.0, 0.8, 0.5   # 18-24 PM (peak/normal/valley price)
                ],
                "Uniform Pricing": [0.8] * 24,
                "Night Discount Pricing": [
                    0.4, 0.4, 0.4, 0.4, 0.4, 0.4,  # 0-6 AM
                    0.8, 0.8, 0.8, 0.8, 0.8, 0.8,  # 6-12 AM
                    0.8, 0.8, 0.8, 0.8, 0.8, 0.8,  # 12-18 PM
                    0.8, 0.8, 0.8, 0.8, 0.4, 0.4   # 18-24 PM
                ]
            }
            
            selected_template = st.selectbox(
                "Select a pre-set price template",
                options=list(price_templates.keys()),
                index=0
            )
            
            if st.button("Apply Template"):
                st.session_state.prices = price_templates[selected_template]
                st.rerun()
        
        with col2:
            st.markdown("### Power Limit")
            st.markdown("Set the maximum power limit for household electricity")
            
            max_power = st.number_input(
                "Maximum Power (kW)",
                min_value=1.0,
                max_value=20.0,
                value=float(st.session_state.max_power),
                step=0.5,
                format="%.1f"
            )
            
            st.session_state.max_power = max_power
            
            st.info(f"""
            #### Current Settings
            - Maximum power limit: **{max_power} kW**
            - Average price: **{sum(st.session_state.prices)/24:.2f} dollars/kWh**
            - Highest price: **{max(st.session_state.prices):.2f} dollars/kWh**
            - Lowest price: **{min(st.session_state.prices):.2f} dollars/kWh**
            """)
            
            st.markdown("""
            ##### Notes
            - Power limit is typically determined by the household's main electrical meter
            - Normal households generally range from 2-10 kW
            - Exceeding the limit may cause circuit breakers to trip
            """)
            
    def render_appliance_list(self):
        """
        Render appliance list section
        
        Display added appliances and their detailed information, and provide delete functionality
        """
        if not st.session_state.appliances:
            st.info("No appliances added yet, please add appliances below")
            return
        
        st.markdown("### Added Appliances")
        
        # Create data frame for appliance list
        appliance_data = []
        for app in st.session_state.appliances:
            # Handle time window display format
            start_hour, end_hour = app['time_window']
            if end_hour < start_hour:  # Overnight case
                time_window = f"{start_hour}:00 - Next day {end_hour}:00"
            else:
                time_window = f"{start_hour}:00 - {end_hour}:00"
                
            appliance_data.append({
                "ID": app['id'],
                "Appliance Name": app['name'],
                "Power (kW)": app['power'],
                "Runtime (hours)": app['runtime'],
                "Available Time Window": time_window,
                "Fixed Runtime": "Yes" if app['fixed_time'] else "No",
                "Priority": app['priority']
            })
        
        df = pd.DataFrame(appliance_data)
        
        # Display appliance list table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID", format="%d", width="small"
                ),
                "Appliance Name": st.column_config.TextColumn(
                    "Appliance Name", width="medium"
                ),
                "Power (kW)": st.column_config.NumberColumn(
                    "Power (kW)", format="%.1f kW", width="small"
                ),
                "Runtime (hours)": st.column_config.NumberColumn(
                    "Runtime (hours)", format="%d hours", width="small"
                ),
                "Available Time Window": st.column_config.TextColumn(
                    "Available Time Window", width="medium"
                ),
                "Fixed Runtime": st.column_config.TextColumn(
                    "Fixed Runtime", width="small"
                ),
                "Priority": st.column_config.NumberColumn(
                    "Priority", format="%d", width="small"
                )
            }
        )
        
        # Delete appliance functionality
        col1, col2 = st.columns([1, 3])
        with col1:
            appliance_to_delete = st.selectbox(
                "Select appliance to delete",
                options=[app['id'] for app in st.session_state.appliances],
                format_func=lambda x: next((app['name'] for app in st.session_state.appliances if app['id'] == x), "")
            )
        
        with col2:
            if st.button("Delete Selected Appliance", type="secondary"):
                # Find and delete the selected appliance
                st.session_state.appliances = [
                    app for app in st.session_state.appliances 
                    if app['id'] != appliance_to_delete
                ]
                st.success(f"Appliance deleted")
                st.rerun()
                
        # Display button to clear all appliances
        if st.button("Clear All Appliances", type="secondary"):
            st.session_state.appliances = []
            st.success("All appliances cleared")
            st.rerun()
            
    def render_add_appliance(self):
        """
        Render add appliance section
        
        Provide a form for users to input new appliance information
        """
        st.markdown("### Add New Appliance")
        
        # Create a form for users to input appliance information
        with st.form(key="add_appliance_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Appliance Name", placeholder="e.g., Washing Machine, Air Conditioner, etc.")
                power = st.number_input(
                    "Power (kW)",
                    min_value=0.1,
                    max_value=10.0,
                    value=1.0,
                    step=0.1,
                    format="%.1f"
                )
                runtime = st.slider(
                    "Runtime (hours)",
                    min_value=1,
                    max_value=24,
                    value=2,
                    step=1
                )
            
            with col2:
                # Time window selector
                st.markdown("##### Available Time Window")
                col_start, col_end = st.columns(2)
                
                with col_start:
                    start_hour = st.selectbox(
                        "Start Time",
                        options=list(range(24)),
                        format_func=lambda x: f"{x}:00"
                    )
                
                with col_end:
                    end_hour = st.selectbox(
                        "End Time",
                        options=list(range(24)),
                        format_func=lambda x: f"{x}:00",
                        index=23
                    )
                
                fixed_time = st.checkbox(
                    "Fixed Runtime",
                    value=False,
                    help="If checked, the appliance will run at the start time of the time window; otherwise, the system will choose the optimal runtime within the time window."
                )
                
                priority = st.slider(
                    "Priority",
                    min_value=0,
                    max_value=10,
                    value=5,
                    step=1,
                    help="Higher value means higher priority. The system will prioritize meeting the demands of high-priority appliances."
                )
            
            # Submit button
            submitted = st.form_submit_button("Add Appliance")
            
            if submitted:
                # Validate input
                if not name:
                    st.error("Please enter an appliance name")
                    return
                
                # Check if the time window is valid
                time_window = (start_hour, end_hour)
                
                # Calculate time window length, handle overnight cases
                if end_hour < start_hour:  # Overnight case
                    window_length = (24 - start_hour) + end_hour
                else:
                    window_length = end_hour - start_hour + 1
                    
                if runtime > window_length:
                    st.error(f"Runtime ({runtime} hours) cannot exceed the length of the time window ({window_length} hours)")
                    return
                
                # Add appliance to list
                new_appliance = {
                    'id': st.session_state.next_id,
                    'name': name,
                    'power': power,
                    'runtime': runtime,
                    'time_window': time_window,
                    'fixed_time': fixed_time,
                    'priority': priority
                }
                
                st.session_state.appliances.append(new_appliance)
                st.session_state.next_id += 1
                
                st.success(f"Added appliance: {name}")
                st.rerun()
        
        # Display appliance addition guide
        with st.expander("Appliance Addition Guide", expanded=False):
            st.markdown("""
            #### Parameter Explanation
            
            - **Appliance Name**: Provide an easily identifiable name for the appliance
            - **Power**: The power of the appliance in kilowatts (kW)
            - **Runtime**: Number of hours the appliance needs to run
            - **Available Time Window**: Time range when the appliance can run
                - If end time is less than start time, it indicates an overnight time window
                - For example: Start time 22:00, End time 5:00, means from 10 PM to 5 AM the next day
            - **Fixed Runtime**: 
                - Checked: The appliance must run at the start time of the time window
                - Unchecked: The system will choose the time with the lowest electricity price within the time window
            - **Priority**: Higher value means higher priority. The system will prioritize meeting the demands of high-priority appliances
            
            #### Reference Power for Common Appliances
            
            | Appliance | Typical Power (kW) |
            | --- | --- |
            | Electric Water Heater | 1.5 - 3.0 |
            | Air Conditioner | 0.7 - 2.5 |
            | Washing Machine | 0.3 - 1.0 |
            | Rice Cooker | 0.5 - 1.0 |
            | Refrigerator | 0.1 - 0.3 |
            | Television | 0.1 - 0.2 |
            | Computer | 0.2 - 0.5 |
            | Electric Vehicle Charging | 3.0 - 7.0 |
            """)
            
    def render_calculate_button(self):
        """
        Render calculation button section
        
        Provide submit button to save all data to session_state
        """
        st.markdown("## 🚀 Calculate Optimal Scheduling Plan")
        
        # Create two-column layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Select optimization algorithm
            optimization_method = st.radio(
                "Select Optimization Algorithm",
                options=["Greedy Algorithm", "Integer Linear Programming"],
                horizontal=True,
                help="Greedy algorithm is fast but may not find the optimal solution; Integer Linear Programming can find the global optimal solution but takes longer to compute."
            )
            
            # Save selection to session_state
            st.session_state.optimization_method = "greedy" if optimization_method == "Greedy Algorithm" else "ilp"
        
        with col2:
            # Calculate button
            calculate_button = st.button(
                "Calculate Optimal Plan",
                type="primary",
                use_container_width=True
            )
        
        if calculate_button:
            # Validate data
            if not self._validate_data():
                return
            
            # Save all data to session_state for results.py to use
            st.session_state.calculation_ready = True
            
            # Display success message
            st.success("Data is ready, calculating optimal plan...")
            
            # Redirect to results page (assuming app.py handles page navigation)
            st.session_state.page = "results"
            
    def _validate_data(self) -> bool:
        """
        Validate all input data
        
        Returns:
            bool: Whether the data is valid
        """
        # Validate electricity price data
        if len(st.session_state.prices) != 24:
            st.error("Electricity price data must contain 24 hours of prices")
            return False
            
        if not all(isinstance(p, (int, float)) and p >= 0 for p in st.session_state.prices):
            st.error("Prices must be non-negative numbers")
            return False
            
        # Validate maximum power
        if not isinstance(st.session_state.max_power, (int, float)) or st.session_state.max_power <= 0:
            st.error("Maximum power must be a positive number")
            return False
            
        # Validate if there are appliances
        if not st.session_state.appliances:
            st.error("Please add at least one appliance")
            return False
            
        return True


# If run as main program
if __name__ == "__main__":
    frontend = Frontend()
    frontend.run()
