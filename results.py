#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Platform - Results Display Module

This module implements a Streamlit-based interactive results display interface for showing the optimization results of appliance scheduling.
It includes total electricity cost calculation results, appliance scheduling timetable, power usage charts, appliance runtime timeline, and warning messages.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Optional, Any
import warnings

# Import optimizer and analyzer modules
from optimizer import Optimizer
from usage_analyzer import UsageAnalyzer

class Results:
    """
    Results display interface class for the Home Appliance Scheduling Optimization Platform
    
    This class implements a Streamlit-based interactive results display interface for showing the optimization results of appliance scheduling.
    It includes total electricity cost calculation results, appliance scheduling timetable, power usage charts, appliance runtime timeline, and warning messages.
    """
    
    def __init__(self):
        """
        Initialize the results display interface
        
        Set page configuration and capture warning messages
        """
        # Set page title and layout
        st.set_page_config(
            page_title="Home Appliance Scheduling Optimization Results",
            page_icon="🔌",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize warning list to capture warnings during optimization
        self.warnings = []
        
        # Initialize usage analyzer
        self.usage_analyzer = UsageAnalyzer()
        
        # Capture warning messages
        warnings.filterwarnings("always")
        self._original_showwarning = warnings.showwarning
        warnings.showwarning = self._capture_warning
    
    def _capture_warning(self, message, category, filename, lineno, file=None, line=None):
        """
        Capture warning messages
        
        Parameters:
            message: Warning message
            category: Warning category
            filename: File name
            lineno: Line number
            file: File object
            line: Line content
        """
        self.warnings.append(str(message))
        self._original_showwarning(message, category, filename, lineno, file, line)
        
    def run(self):
        """
        Run the results display interface
        
        Display page title, calculate optimal scheduling plan, and show results
        """
        # Display page title
        st.title("Home Appliance Scheduling Optimization Results")
        
        # Check if calculation data is ready
        if "calculation_ready" not in st.session_state or not st.session_state.calculation_ready:
            st.error("No valid calculation data found, please return to the input page.")
            if st.button("Return to Input Page"):
                st.session_state.page = "frontend"
                st.rerun()
            return
        
        # Calculate optimal scheduling plan
        with st.spinner("Calculating optimal scheduling plan..."):
            optimizer, schedule = self.calculate_optimal_schedule()
            
            # Save usage data if schedule is found
            if schedule:
                self.usage_analyzer.add_usage_data(
                    schedule, 
                    st.session_state.appliances,
                    st.session_state.prices
                )
        
        # If no feasible scheduling plan is found
        if not schedule:
            st.error("Cannot find a feasible scheduling plan, constraints may be too strict.")
            self.render_warnings()
            self.render_navigation()
            return
        
        # Display results
        with st.container():
            self.render_summary(optimizer, schedule)
            
        st.markdown("---")
        
        with st.container():
            self.render_schedule_table(optimizer, schedule)
            
        st.markdown("---")
        
        with st.container():
            self.render_power_usage_chart(optimizer)
            
        st.markdown("---")
        
        with st.container():
            self.render_timeline(optimizer, schedule)
            
        st.markdown("---")
        
        with st.container():
            self.render_usage_patterns()
            
        # Display warning messages
        if self.warnings:
            st.markdown("---")
            self.render_warnings()
        
        # Display navigation buttons
        st.markdown("---")
        self.render_navigation()
    
    def calculate_optimal_schedule(self):
        """
        Call methods in optimizer.py to calculate the optimal scheduling plan
        
        Returns:
            Tuple[Optimizer, Dict[str, int]]: Optimizer instance and scheduling plan
        """
        # Get data from session_state
        prices = st.session_state.prices
        max_power = st.session_state.max_power
        appliances = st.session_state.appliances
        optimization_method = st.session_state.optimization_method
        
        # Create optimizer instance
        optimizer = Optimizer(prices, max_power)
        
        # Add appliances to optimizer
        for appliance in appliances:
            optimizer.add_appliance(
                name=appliance['name'],
                power=appliance['power'],
                runtime=appliance['runtime'],
                time_window=appliance['time_window'],
                fixed_time=appliance['fixed_time'],
                priority=appliance['priority']
            )
        
        # Optimize based on selected method
        try:
            if optimization_method == "greedy":
                schedule = optimizer.optimize()
            else:  # "ilp"
                schedule = optimizer.optimize_ilp()
        except Exception as e:
            st.error(f"Error during optimization: {str(e)}")
            return optimizer, {}
        
        return optimizer, schedule
        
    def render_summary(self, optimizer, schedule):
        """
        Render summary information, including total electricity cost and number of successfully/failed scheduled appliances
        
        Parameters:
            optimizer (Optimizer): Optimizer instance
            schedule (Dict[str, int]): Scheduling plan
        """
        st.markdown("## Optimization Results Summary")
        
        # Create three-column layout
        col1, col2, col3 = st.columns(3)
        
        # Calculate total electricity cost
        total_cost = optimizer.get_total_cost()
        
        # Calculate number of successfully and failed scheduled appliances
        total_appliances = len(optimizer.appliances)
        scheduled_appliances = len(schedule)
        failed_appliances = total_appliances - scheduled_appliances
        
        # Display total electricity cost
        with col1:
            st.metric(
                label="Total Electricity Cost",
                value=f"{total_cost:.2f} dollars",
                help="Total electricity cost calculated based on the optimized scheduling plan"
            )
        
        # Display number of successfully scheduled appliances
        with col2:
            st.metric(
                label="Successfully Scheduled Appliances",
                value=f"{scheduled_appliances} / {total_appliances}",
                delta=f"{scheduled_appliances/total_appliances*100:.1f}%" if total_appliances > 0 else None,
                help="Ratio of successfully scheduled appliances to total appliances"
            )
        
        # Display number of failed scheduled appliances
        with col3:
            if failed_appliances > 0:
                st.metric(
                    label="Failed Scheduled Appliances",
                    value=f"{failed_appliances} / {total_appliances}",
                    delta=f"-{failed_appliances/total_appliances*100:.1f}%",
                    delta_color="inverse",
                    help="Ratio of appliances that cannot be scheduled to total appliances"
                )
            else:
                st.metric(
                    label="Failed Scheduled Appliances",
                    value="0",
                    delta="0%",
                    delta_color="off",
                    help="Ratio of appliances that cannot be scheduled to total appliances"
                )
        
        # Display optimization method
        optimization_method = "Greedy Algorithm" if st.session_state.optimization_method == "greedy" else "Integer Linear Programming"
        st.info(f"Optimization method used: **{optimization_method}**")
        
    def render_schedule_table(self, optimizer, schedule):
        """
        Render scheduling timetable, showing start time and end time for each appliance
        
        Parameters:
            optimizer (Optimizer): Optimizer instance
            schedule (Dict[str, int]): Scheduling plan
        """
        st.markdown("## Appliance Scheduling Timetable")
        
        if not schedule:
            st.warning("No feasible scheduling plan")
            return
        
        # Create scheduling timetable data
        schedule_data = []
        for name, start_hour in schedule.items():
            # Find corresponding appliance information
            appliance = next(a for a in optimizer.appliances if a['name'] == name)
            power = appliance['power']
            runtime = appliance['runtime']
            end_hour = (start_hour + runtime) % 24
            
            # Calculate electricity cost for this appliance
            cost = sum(optimizer.prices[(start_hour + h) % 24] * power for h in range(runtime))
            
            # Handle overnight cases
            if end_hour < start_hour:
                time_range = f"{start_hour}:00 - Next day {end_hour}:00"
            else:
                time_range = f"{start_hour}:00 - {end_hour}:00"
            
            schedule_data.append({
                "Appliance Name": name,
                "Power (kW)": power,
                "Runtime (hours)": runtime,
                "Start Time": f"{start_hour}:00",
                "End Time": f"{end_hour}:00" if end_hour > start_hour else f"Next day {end_hour}:00",
                "Running Period": time_range,
                "Electricity Cost (dollars)": round(cost, 2)
            })
        
        # Create DataFrame and display table
        df = pd.DataFrame(schedule_data)
        
        # Display scheduling timetable
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Appliance Name": st.column_config.TextColumn("Appliance Name", width="medium"),
                "Power (kW)": st.column_config.NumberColumn("Power (kW)", format="%.1f kW", width="small"),
                "Runtime (hours)": st.column_config.NumberColumn("Runtime (hours)", format="%d hours", width="small"),
                "Start Time": st.column_config.TextColumn("Start Time", width="small"),
                "End Time": st.column_config.TextColumn("End Time", width="small"),
                "Running Period": st.column_config.TextColumn("Running Period", width="medium"),
                "Electricity Cost (dollars)": st.column_config.NumberColumn("Electricity Cost (dollars)", format="%.2f dollars", width="small")
            }
        )
        
    def render_power_usage_chart(self, optimizer):
        """
        Render power usage chart, showing hourly power usage
        
        Parameters:
            optimizer (Optimizer): Optimizer instance
        """
        st.markdown("## Hourly Power Usage")
        
        # Get hourly power usage
        hourly_usage = optimizer.get_hourly_usage()
        
        # Create power usage data for each appliance in each hour
        appliance_schedule = {}
        for name, start_hour in optimizer.get_schedule().items():
            appliance = next(a for a in optimizer.appliances if a['name'] == name)
            for h in range(appliance['runtime']):
                hour = (start_hour + h) % 24
                if hour not in appliance_schedule:
                    appliance_schedule[hour] = []
                appliance_schedule[hour].append((name, appliance['power']))
        
        # Create stacked bar chart data
        appliance_names = sorted(list(set(a['name'] for a in optimizer.appliances if a['name'] in optimizer.get_schedule())))
        appliance_data = {name: [0] * 24 for name in appliance_names}
        
        for hour in range(24):
            if hour in appliance_schedule:
                for name, power in appliance_schedule[hour]:
                    appliance_data[name][hour] = power
        
        # Create chart data
        fig = go.Figure()
        
        # Add power usage for each appliance
        for name in appliance_names:
            fig.add_trace(go.Bar(
                x=list(range(24)),
                y=appliance_data[name],
                name=name
            ))
        
        # Add maximum power limit line
        fig.add_trace(go.Scatter(
            x=list(range(24)),
            y=[optimizer.max_power] * 24,
            mode='lines',
            name=f'Maximum Power Limit ({optimizer.max_power} kW)',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Add electricity price curve (using secondary y-axis)
        fig.add_trace(go.Scatter(
            x=list(range(24)),
            y=optimizer.prices,
            mode='lines+markers',
            name='Electricity Price (dollars/kWh)',
            line=dict(color='orange', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        # Update layout
        fig.update_layout(
            title='Hourly Power Usage and Electricity Price Comparison',
            xaxis_title='Hour',
            yaxis_title='Power (kW)',
            yaxis2=dict(
                title='Electricity Price (dollars/kWh)',
                overlaying='y',
                side='right',
                range=[0, max(optimizer.prices) * 1.2]
            ),
            barmode='stack',
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        # Set x-axis ticks to integer hours
        fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Display power usage statistics
        st.markdown("### Power Usage Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_usage = max(hourly_usage)
            max_usage_hour = hourly_usage.index(max_usage)
            st.metric(
                label="Maximum Power Usage",
                value=f"{max_usage:.2f} kW",
                delta=f"Peak time: {max_usage_hour}:00",
                help="Maximum power usage in a day and when it occurs"
            )
        
        with col2:
            avg_usage = sum(hourly_usage) / 24
            st.metric(
                label="Average Power Usage",
                value=f"{avg_usage:.2f} kW",
                delta=f"{avg_usage / optimizer.max_power * 100:.1f}% Utilization",
                help="Average power usage in a day and its percentage of maximum power"
            )
        
        with col3:
            unused_hours = sum(1 for usage in hourly_usage if usage == 0)
            st.metric(
                label="Hours with No Power Usage",
                value=f"{unused_hours} hours",
                delta=f"{unused_hours / 24 * 100:.1f}% Idle time",
                help="Number of hours with no power usage and its percentage"
            )
    
    def render_timeline(self, optimizer, schedule):
        """
        Render timeline to visually display appliance running time
        
        Parameters:
            optimizer (Optimizer): Optimizer instance
            schedule (Dict[str, int]): Scheduling plan
        """
        st.markdown("## Appliance Runtime Timeline")
        
        if not schedule:
            st.warning("No feasible scheduling plan")
            return
        
        # Create timeline data
        timeline_data = []
        for name, start_hour in schedule.items():
            # Find corresponding appliance information
            appliance = next(a for a in optimizer.appliances if a['name'] == name)
            power = appliance['power']
            runtime = appliance['runtime']
            end_hour = (start_hour + runtime) % 24
            
            # Handle overnight cases
            if end_hour < start_hour:
                end_hour += 24
            
            # Add timeline data
            timeline_data.append({
                "Appliance": name,
                "Start Time": start_hour,
                "End Time": end_hour,
                "Power (kW)": power
            })
        
        # Create DataFrame
        df = pd.DataFrame(timeline_data)
        
        # Sort by appliance name for a more organized chart
        df = df.sort_values(by="Appliance")
        
        # Create a custom timeline chart using go.Bar instead of px.timeline
        fig = go.Figure()
        
        # Add a bar for each appliance
        for i, row in df.iterrows():
            fig.add_trace(go.Bar(
                x=[row['End Time'] - row['Start Time']],  # Width = duration
                y=[row['Appliance']],                    # Y position = appliance name
                orientation='h',                         # Horizontal bar
                base=row['Start Time'],                  # Start position
                marker=dict(
                    color=row['Power (kW)'],             # Color based on power
                    colorscale='Viridis',                # Use Viridis color scale
                    colorbar=dict(title="Power (kW)")    # Add color bar
                ),
                hovertemplate=f"Appliance: {row['Appliance']}<br>" +
                              f"Start: {row['Start Time']}:00<br>" +
                              f"End: {row['End Time']}:00<br>" +
                              f"Power: {row['Power (kW)']} kW<br>" +
                              f"Duration: {row['End Time'] - row['Start Time']} hours"
            ))
        
        # Update layout
        fig.update_layout(
            title="Appliance Runtime Timeline",
            xaxis=dict(
                title="Hour",
                tickmode='linear',
                tick0=0,
                dtick=1,
                range=[0, 24]
            ),
            yaxis=dict(
                title="Appliance"
            ),
            height=500,
            margin=dict(l=50, r=50, b=100, t=100, pad=4),
            autosize=True,
            barmode='overlay'  # Ensure bars don't stack
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Add timeline chart explanation
        st.info("""
        **Timeline Chart Explanation:**
        - The horizontal axis represents 24 hours
        - The vertical axis represents different appliances
        - Color intensity indicates appliance power
        - The length of each bar represents appliance runtime
        """)
        
    def render_warnings(self):
        """
        Render warning messages, showing appliances that cannot be scheduled and reasons
        """
        st.markdown("## ⚠️ Warning Messages")
        
        if not self.warnings:
            st.success("No warning messages found, all appliances have been successfully scheduled.")
            return
        
        # Display warning messages
        st.warning("The following warning messages were found during optimization:")
        
        for i, warning in enumerate(self.warnings):
            st.markdown(f"**Warning {i+1}**: {warning}")
        
        # Provide possible solutions
        st.markdown("### Possible Solutions")
        st.markdown("""
        If there are appliances that cannot be scheduled, you can try the following solutions:
        
        1. **Increase maximum power limit**: If warnings indicate power exceeds limit, consider increasing the maximum power limit
        2. **Expand time window**: Provide a larger available runtime window for appliances to increase scheduling flexibility
        3. **Reduce runtime**: If possible, reduce the runtime of certain appliances
        4. **Adjust priorities**: Increase the priority of important appliances and decrease the priority of less important ones
        5. **Try different optimization algorithms**: If using the greedy algorithm, try switching to integer linear programming, or vice versa
        """)
    
    def render_usage_patterns(self):
        """
        Render usage pattern analysis and optimization suggestions
        """
        st.markdown("## AI Pattern Analysis")
        
        # Check if we have enough data for analysis
        report = self.usage_analyzer.generate_insights_report()
        data_points = report.get('data_points', 0)
        
        if data_points <= 1:
            st.info("Not enough historical data for meaningful pattern analysis. As you use the system more, AI insights will be generated here.")
            
            # Show sample insights
            with st.expander("See sample insights (demo only)", expanded=False):
                self._render_sample_insights()
            return
        
        # Display summary
        summary = report.get('summary', {})
        if summary.get('status') == 'complete':
            st.success(summary.get('message', 'Analysis complete'))
            
            # Show key insights
            st.markdown("### Key Insights")
            for insight in summary.get('key_insights', []):
                st.markdown(f"- {insight}")
        else:
            st.warning(summary.get('message', 'Analysis incomplete due to insufficient data'))
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs(["Time Patterns", "Appliance Patterns", "Consumption Patterns"])
        
        with tab1:
            self._render_time_patterns(report)
            
        with tab2:
            self._render_appliance_patterns(report)
            
        with tab3:
            self._render_consumption_patterns(report)
            
        # Add option to delete all history
        st.markdown("---")
        with st.container():
            st.markdown("### Data Management")
            
            # Initialize the confirmation state if not exists
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            
            # Show delete button or confirmation based on state
            if not st.session_state.confirm_delete:
                if st.button("Delete All Analytics History", type="secondary"):
                    st.session_state.confirm_delete = True
                    st.rerun()
            else:
                st.warning("Are you sure you want to delete all analytics history? This action cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete Everything", type="primary"):
                        # Call the clear_history method
                        if self.usage_analyzer.clear_history():
                            st.success("All analytics history has been deleted successfully.")
                            st.session_state.confirm_delete = False
                            # Force refresh the page
                            st.rerun()
                        else:
                            st.error("Failed to delete analytics history. Please try again.")
                with col2:
                    if st.button("Cancel", type="secondary"):
                        st.session_state.confirm_delete = False
                        st.rerun()
    
    def _render_time_patterns(self, report):
        """
        Render time-based usage patterns
        """
        st.markdown("### Time-Based Usage Patterns")
        
        time_patterns = report.get('time_patterns', {})
        if 'error' in time_patterns:
            st.info(time_patterns['error'])
            return
            
        # Peak hours
        peak_hours = time_patterns.get('peak_hours', [])
        st.markdown(f"**Peak usage hours:** {', '.join([f'{h}:00' for h in peak_hours])}")
        
        # Hourly distribution
        hourly_dist = time_patterns.get('hourly_distribution', {})
        if hourly_dist:
            hours = list(range(24))
            # Fix: Use integer keys instead of string keys
            values = [hourly_dist.get(h, 0) for h in hours]
            
            # Check if we have any non-zero values
            if any(values):
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=hours,
                    y=values,
                    name='Usage Frequency',
                    marker_color='blue'
                ))
                
                fig.update_layout(
                    title='Hourly Usage Distribution',
                    xaxis_title='Hour of Day',
                    yaxis_title='Usage Frequency',
                    xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                    height=500,
                    margin=dict(l=50, r=50, b=100, t=100, pad=4),
                    autosize=True
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("No usage data available for this chart.")
        
        # Weekday vs Weekend
        weekday_weekend = time_patterns.get('weekday_vs_weekend', {})
        if weekday_weekend and 'weekday' in weekday_weekend and 'weekend' in weekday_weekend:
            weekday_data = weekday_weekend['weekday']
            weekend_data = weekday_weekend['weekend']
            
            if weekday_data and weekend_data:
                hours = list(range(24))
                # Fix: Use integer keys instead of string keys
                weekday_values = [weekday_data.get(h, 0) for h in hours]
                weekend_values = [weekend_data.get(h, 0) for h in hours]
                
                # Check if we have any non-zero values
                if any(weekday_values) or any(weekend_values):
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hours,
                        y=weekday_values,
                        mode='lines+markers',
                        name='Weekday Usage',
                        line=dict(color='blue', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hours,
                        y=weekend_values,
                        mode='lines+markers',
                        name='Weekend Usage',
                        line=dict(color='red', width=2)
                    ))
                    
                    fig.update_layout(
                        title='Weekday vs Weekend Usage Patterns',
                        xaxis_title='Hour of Day',
                        yaxis_title='Usage Percentage',
                        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                        height=500,
                        margin=dict(l=50, r=50, b=100, t=100, pad=4),
                        autosize=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                else:
                    st.info("No weekday vs weekend data available for this chart.")
    
    def _render_appliance_patterns(self, report):
        """
        Render appliance usage patterns
        """
        st.markdown("### Appliance Usage Patterns")
        
        appliance_patterns = report.get('appliance_patterns', {})
        if 'error' in appliance_patterns:
            st.info(appliance_patterns['error'])
            return
            
        # Frequent appliances
        frequent_apps = appliance_patterns.get('frequent_appliances', {})
        if frequent_apps:
            st.markdown("**Most Frequently Used Appliances:**")
            
            # Convert to list and sort
            app_list = [(app, count) for app, count in frequent_apps.items()]
            app_list.sort(key=lambda x: x[1], reverse=True)
            
            # Create a bar chart
            apps = [app for app, _ in app_list]
            counts = [count for _, count in app_list]
            
            # Check if we have any non-zero values
            if any(counts):
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=apps,
                    y=counts,
                    marker_color='green'
                ))
                
                fig.update_layout(
                    title='Appliance Usage Frequency',
                    xaxis_title='Appliance',
                    yaxis_title='Usage Count',
                    height=500,
                    margin=dict(l=50, r=50, b=100, t=100, pad=4),
                    autosize=True
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("No appliance frequency data available for this chart.")
        
        # Appliance timing
        app_timing = appliance_patterns.get('appliance_timing', {})
        if app_timing:
            st.markdown("**Typical Usage Times:**")
            
            timing_data = []
            for app, timing in app_timing.items():
                timing_data.append({
                    "Appliance": app,
                    "Avg Start Time": f"{timing.get('avg_start_time', 'N/A'):.1f}",
                    "Common Start Time": timing.get('common_start_time', 'N/A'),
                    "Avg Runtime (hours)": f"{timing.get('avg_runtime', 'N/A'):.1f}",
                    "Fixed Time (%)": f"{timing.get('fixed_time_pct', 'N/A'):.1f}%"
                })
            
            st.dataframe(timing_data, use_container_width=True)
        
        # Co-occurring appliances
        co_occurring = appliance_patterns.get('co_occurring_appliances', [])
        if co_occurring:
            st.markdown("**Appliances Often Used Together:**")
            
            for pair in co_occurring:
                apps = pair.get('appliances', [])
                count = pair.get('count', 0)
                st.markdown(f"- {' & '.join(apps)}: Used together {count} times")
    
    def _render_consumption_patterns(self, report):
        """
        Render electricity consumption patterns
        """
        st.markdown("### Electricity Consumption Patterns")
        
        consumption_patterns = report.get('consumption_patterns', {})
        if 'error' in consumption_patterns:
            st.info(consumption_patterns['error'])
            return
            
        # Peak power periods
        peak_power = consumption_patterns.get('peak_power_periods', {})
        if peak_power:
            peak_hour = peak_power.get('peak_hour')
            peak_power_val = peak_power.get('peak_power')
            
            st.markdown(f"**Peak power consumption:** {peak_power_val:.2f} kW at {peak_hour}:00")
            
            # Hourly power chart
            hourly_power = peak_power.get('hourly_power', {})
            if hourly_power:
                hours = list(range(24))
                # Fix: Use integer keys instead of string keys
                power_values = [hourly_power.get(h, 0) for h in hours]
                
                # Check if we have any non-zero values
                if any(power_values):
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=hours,
                        y=power_values,
                        marker_color='orange'
                    ))
                    
                    fig.update_layout(
                        title='Hourly Power Consumption',
                        xaxis_title='Hour of Day',
                        yaxis_title='Power (kW)',
                        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                        height=500,
                        margin=dict(l=50, r=50, b=100, t=100, pad=4),
                        autosize=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                else:
                    st.info("No power consumption data available for this chart.")
        
        # Cost analysis
        cost_analysis = consumption_patterns.get('cost_analysis', {})
        if cost_analysis:
            total_cost = cost_analysis.get('total_cost', 0)
            avg_daily_cost = cost_analysis.get('average_cost_per_day', 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Total Electricity Cost",
                    value=f"{total_cost:.2f} dollars"
                )
            
            with col2:
                st.metric(
                    label="Average Daily Cost",
                    value=f"{avg_daily_cost:.2f} dollars"
                )
            
            # Cost by appliance
            cost_by_app = cost_analysis.get('cost_by_appliance', {})
            if cost_by_app:
                st.markdown("**Cost by Appliance:**")
                
                # Convert to list and sort
                cost_list = [(app, cost) for app, cost in cost_by_app.items()]
                cost_list.sort(key=lambda x: x[1], reverse=True)
                
                # Create a pie chart
                apps = [app for app, _ in cost_list]
                costs = [cost for _, cost in cost_list]
                
                # Check if we have any non-zero values
                if any(costs):
                    fig = go.Figure(data=[go.Pie(
                        labels=apps,
                        values=costs,
                        hole=.3
                    )])
                    
                    fig.update_layout(
                        title='Electricity Cost Distribution by Appliance',
                        height=500,
                        margin=dict(l=50, r=50, b=100, t=100, pad=4),
                        autosize=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                else:
                    st.info("No cost distribution data available for this chart.")
    
    
    def _render_sample_insights(self):
        """
        Render sample insights for demonstration purposes
        """
        st.markdown("### Sample Time Patterns")
        st.markdown("**Peak usage hours:** 7:00, 18:00, 19:00")
        
        # Sample hourly distribution chart
        hours = list(range(24))
        sample_values = [1, 0, 0, 0, 0, 2, 3, 5, 4, 3, 2, 2, 3, 4, 3, 2, 3, 5, 5, 4, 3, 2, 1, 1]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hours,
            y=sample_values,
            marker_color='blue'
        ))
        
        fig.update_layout(
            title='Sample Hourly Usage Distribution',
            xaxis_title='Hour of Day',
            yaxis_title='Usage Frequency',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            height=500,
            margin=dict(l=50, r=50, b=100, t=100, pad=4),
            autosize=True
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    def render_usage_patterns_page(self):
        """
        Render a standalone page for usage pattern analysis
        """
        # Display page title
        st.title("🔌 Home Appliance Usage Pattern Analysis")
        st.markdown("""
        This page shows AI-powered analysis of your electricity usage patterns.
        """)
        
        # Render the usage patterns section
        self.render_usage_patterns()
        
        # Display navigation buttons
        st.markdown("---")
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Return to Input Page", type="secondary"):
                    st.session_state.page = "frontend"
                    st.rerun()
            with col2:
                if st.button("View Latest Optimization Results", type="primary"):
                    st.session_state.page = "results"
                    st.rerun()
            with col3:
                if st.button("Return to Home", type="secondary"):
                    st.session_state.page = "home"
                    st.rerun()
    
    def render_navigation(self):
        """
        Render navigation buttons, allowing users to navigate between different pages
        """
        # Display navigation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Return to Input Page", type="secondary"):
                # Reset calculation state
                st.session_state.calculation_ready = False
                
                # Switch back to frontend page
                st.session_state.page = "frontend"
                st.rerun()
                
        with col2:
            if st.button("View Usage Pattern Analysis", type="primary"):
                st.session_state.page = "patterns"
                st.rerun()
                
        with col3:
            if st.button("Return to Home", type="secondary"):
                # Switch to home page
                st.session_state.page = "home"
                st.rerun()


# If run as main program
if __name__ == "__main__":
    results = Results()
    results.run()
