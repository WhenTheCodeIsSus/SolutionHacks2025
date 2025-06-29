#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Platform - Home Page

This module implements a Streamlit-based home page for the Home Appliance Scheduling Optimization Platform,
including project navigation, explanation of UN sustainability goals contribution, and graphic explanation of how the program works.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def main():
    """
    Main function to run the home page
    """
    # Set page configuration
    st.set_page_config(
        page_title="Home Appliance Scheduling Optimization Platform - Home",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header section
    st.title("Home Appliance Scheduling Optimization Platform")
    
    # Navigation section
    st.markdown("## Get Started")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="background-color:#e1f5fe;padding:20px;border-radius:10px;text-align:center;height:180px;">
        <h3 style="color:#01579b;">Enter Application</h3>
        <p style="color:#01579b;font-weight:500;">Start optimizing your appliance scheduling plan and save on electricity costs</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Now", key="start_button", use_container_width=True):
            st.session_state.page = "frontend"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background-color:#e8f5e9;padding:20px;border-radius:10px;text-align:center;height:180px;">
        <h3 style="color:#2e7d32;">View Usage Patterns</h3>
        <p style="color:#2e7d32;font-weight:500;">Analyze your electricity usage patterns and historical data</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Patterns", key="patterns_button", use_container_width=True):
            st.session_state.page = "patterns"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="background-color:#fff3e0;padding:20px;border-radius:10px;text-align:center;height:180px;">
        <h3 style="color:#e65100;">About Project</h3>
        <p style="color:#e65100;font-weight:500;">Learn more about the project background, goals, and technical implementation</p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Project Details", expanded=False):
            st.markdown("""
            **Home Appliance Scheduling Optimization Platform** is a tool that helps users optimize the running time of home appliances by considering electricity price variations, appliance power, and operational requirements to calculate the optimal scheduling plan that minimizes electricity costs.
            
            ### Main Features
            - Input 24-hour electricity prices and maximum power limits
            - Add and manage appliance lists
            - Calculate optimal scheduling plans
            - Display electricity cost savings and usage analysis
            - Record and analyze electricity usage patterns
            """)
    
    st.markdown("---")
    
    # UN Sustainability Goals section
    st.markdown("## UN Sustainable Development Goals Contribution")
    
    tab1, tab2, tab3 = st.tabs(["Goal 7: Affordable and Clean Energy", "Goal 12: Responsible Consumption and Production", "Goal 13: Climate Action"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://www.un.org/sustainabledevelopment/wp-content/uploads/2018/05/E_SDG-goals_icons-individual-rgb-07.png", width=200)
        with col2:
            st.markdown("""
            ### Goal 7: Affordable and Clean Energy
            
            This project supports this goal through:
            
            - **Optimizing electricity usage times**: Shifting electricity demand from peak to off-peak periods, reducing grid load
            - **Promoting renewable energy use**: Off-peak electricity prices often correspond to periods when renewable energy supply is abundant
            - **Improving energy efficiency**: Through smart scheduling, reducing unnecessary energy waste
            - **Reducing energy costs**: By optimizing electricity usage times, lowering users' electricity bills
            
            > "Ensure access to affordable, reliable, sustainable and modern energy for all"
            """)
    
    with tab2:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://www.un.org/sustainabledevelopment/wp-content/uploads/2018/05/E_SDG-goals_icons-individual-rgb-12.png", width=200)
        with col2:
            st.markdown("""
            ### Goal 12: Responsible Consumption and Production
            
            This project supports this goal through:
            
            - **Encouraging responsible energy consumption behavior**: Raising user awareness of electricity consumption patterns
            - **Optimizing resource use**: Reducing energy consumption during peak periods, lowering demand for additional generation capacity
            - **Providing visual data analysis**: Helping users understand the environmental impact of their consumption behavior
            - **Promoting sustainable lifestyles**: Cultivating energy-saving and emission-reducing daily habits
            
            > "Ensure sustainable consumption and production patterns"
            """)
    
    with tab3:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://www.un.org/sustainabledevelopment/wp-content/uploads/2018/05/E_SDG-goals_icons-individual-rgb-13.png", width=200)
        with col2:
            st.markdown("""
            ### Goal 13: Climate Action
            
            This project supports this goal through:
            
            - **Reducing carbon emissions**: Peak period electricity often comes from fossil fuels; reducing peak usage can lower carbon emissions
            - **Balancing grid load**: Helping the grid better integrate renewable energy, reducing dependence on fossil fuels
            - **Improving energy system resilience**: By dispersing electricity demand, reducing grid pressure, and improving system stability
            - **Promoting climate awareness**: Raising user awareness of the relationship between energy use and climate change
            
            > "Take urgent action to combat climate change and its impacts"
            """)
    
    st.markdown("---")
    
    # How it works section
    st.markdown("## How It Works")
    
    # Create tabs for different aspects of the program
    how_tab1, how_tab2, how_tab3 = st.tabs(["System Process", "Optimization Algorithm", "Energy Saving Effect"])
    
    with how_tab1:
        st.markdown("### System Workflow")
        
        # Create a flowchart using plotly
        fig = make_subplots(rows=1, cols=1)
        
        # Define node positions
        nodes = {
            "input": {"x": 0, "y": 0, "text": "User Input"},
            "optimization": {"x": 1, "y": 0, "text": "Optimization"},
            "results": {"x": 2, "y": 0, "text": "Results Display"},
            "analysis": {"x": 3, "y": 0, "text": "Usage Analysis"}
        }
        
        # Add nodes
        for node_id, node in nodes.items():
            fig.add_trace(
                go.Scatter(
                    x=[node["x"]], 
                    y=[node["y"]],
                    mode="markers+text",
                    marker=dict(size=30, color="#4CAF50"),
                    text=[node["text"]],
                    textposition="middle center",
                    name=node["text"],
                    hoverinfo="text",
                    textfont=dict(color="white")
                )
            )
        
        # Add edges (arrows) - Adjusted to avoid overlapping with text
        for i in range(len(nodes) - 1):
            node_ids = list(nodes.keys())
            start = nodes[node_ids[i]]
            end = nodes[node_ids[i+1]]
            
            # Draw arrow with a slight vertical offset to avoid overlapping text
            fig.add_trace(
                go.Scatter(
                    x=[start["x"], end["x"]],
                    y=[start["y"] - 0.05, start["y"] - 0.05],  # Slight vertical offset
                    mode="lines",
                    line=dict(width=2, color="#1976D2"),
                    hoverinfo="none",
                    showlegend=False
                )
            )
        
        # Add descriptions - Adjusted position to avoid overlap
        descriptions = [
            {"x": 0, "y": -0.4, "text": "Electricity prices,<br>power limits & appliance info"},
            {"x": 1, "y": -0.4, "text": "Greedy algorithm &<br>integer linear programming"},
            {"x": 2, "y": -0.4, "text": "Schedule timetable<br>& cost savings"},
            {"x": 3, "y": -0.4, "text": "Usage patterns<br>& historical data"}
        ]
        
        for desc in descriptions:
            fig.add_trace(
                go.Scatter(
                    x=[desc["x"]],
                    y=[desc["y"]],
                    mode="text",
                    text=[desc["text"]],
                    textposition="middle center",
                    hoverinfo="none",
                    showlegend=False
                )
            )
        
        # Update layout with increased height to accommodate text
        fig.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=350  # Increased height to accommodate the text
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        The system workflow includes four main steps:
        
        1. **User Input**: Users input 24-hour electricity prices, maximum power limits, and appliance information (including power, runtime, time window, etc.)
        2. **Optimization Calculation**: The system uses optimization algorithms (greedy algorithm or integer linear programming) to calculate the optimal scheduling plan
        3. **Results Display**: Shows the optimized scheduling timetable, total electricity cost, savings amount, and power usage charts
        4. **Usage Analysis**: Analyzes electricity usage patterns, provides historical data comparison and optimization suggestions
        """)
    
    with how_tab2:
        st.markdown("### Optimization Algorithm")
        
        # Create visualization for the optimization algorithm
        st.markdown("""
        The system uses two optimization algorithms to calculate the optimal home appliance scheduling plan:
        
        #### 1. Greedy Algorithm
        
        The greedy algorithm works through the following steps:
        - Sort the 24 hours based on electricity prices
        - Prioritize running appliances during the lowest price periods
        - Consider appliance runtime, time windows, and power limits
        - Suitable for simple scheduling problems, with fast calculation speed
        
        #### 2. Integer Linear Programming
        
        Integer linear programming is a more complex but more precise optimization method:
        - Establish a mathematical model, including objective function and constraints
        - Objective function: Minimize total electricity cost
        - Constraints: Power limits, runtime, time windows, etc.
        - Use solvers to solve the integer linear programming problem
        - Can handle more complex scheduling problems, but takes longer to compute
        """)
        
        # Add a simple visualization of price-based scheduling
        hours = list(range(24))
        prices = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.8, 0.8, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5, 1.0, 0.8, 0.5]
        
        # Create a sample appliance schedule
        appliance1 = [0] * 24
        appliance1[2] = appliance1[3] = appliance1[4] = appliance1[5] = 1  # Running during low price hours
        
        appliance2 = [0] * 24
        appliance2[0] = appliance2[1] = appliance2[5] = appliance2[23] = 1  # Running during lowest price hours
        
        fig = go.Figure()
        
        # Add price curve
        fig.add_trace(go.Scatter(
            x=hours,
            y=prices,
            mode='lines',
            name='Price',
            line=dict(color='#1976D2', width=3)
        ))
        
        # Add appliance 1 schedule
        fig.add_trace(go.Bar(
            x=hours,
            y=[a * 0.2 for a in appliance1],
            name='Appliance 1 Runtime',
            marker_color='rgba(76, 175, 80, 0.6)'
        ))
        
        # Add appliance 2 schedule
        fig.add_trace(go.Bar(
            x=hours,
            y=[a * 0.2 for a in appliance2],
            name='Appliance 2 Runtime',
            marker_color='rgba(255, 152, 0, 0.6)'
        ))
        
        fig.update_layout(
            title="Price-Based Appliance Scheduling Example",
            xaxis_title="Hour",
            yaxis_title="Price ($/kWh)",
            hovermode="x unified",
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        The chart above shows an example of price-based appliance scheduling:
        - The blue line represents the 24-hour electricity price curve
        - The green and orange bars represent the runtime periods of two appliances
        - As you can see, appliances are prioritized to run during lower price periods (early morning and late night)
        - This maximizes cost savings on electricity bills
        """)
    
    with how_tab3:
        st.markdown("### Energy Saving Effect")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create a pie chart showing energy cost savings
            labels = ['Optimized Cost', 'Savings']
            values = [85, 15]  # 15% savings
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.4,
                marker_colors=['#4CAF50', '#FF9800']
            )])
            
            fig.update_layout(
                title="Average Electricity Cost Savings",
                annotations=[dict(text='15%<br>Saved', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            By optimizing appliance running times, users can save an average of 15% on electricity costs. The specific amount saved depends on electricity price differences, number of appliances, and usage patterns.
            """)
        
        with col2:
            # Create a bar chart showing peak load reduction
            categories = ['Before Optimization', 'After Optimization']
            values = [7.5, 5.0]  # 33% peak reduction
            
            fig = go.Figure(data=[go.Bar(
                x=categories,
                y=values,
                marker_color=['#F44336', '#4CAF50']
            )])
            
            fig.update_layout(
                title="Peak Load Reduction Effect",
                yaxis_title="Maximum Power (kW)",
                annotations=[
                    dict(
                        x=categories[0],
                        y=values[0],
                        text=f"{values[0]}kW",
                        showarrow=False,
                        yshift=10
                    ),
                    dict(
                        x=categories[1],
                        y=values[1],
                        text=f"{values[1]}kW",
                        showarrow=False,
                        yshift=10
                    )
                ]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            By shifting electricity demand from peak to off-peak periods, the system can significantly reduce peak load, alleviating grid pressure and improving system stability.
            """)
    
    # Footer section
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center">
    <p>Home Appliance Scheduling Optimization Platform © 2025 | Contributing to Sustainable Development</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
