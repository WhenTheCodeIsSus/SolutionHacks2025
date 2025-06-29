#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Platform - Usage Pattern Analyzer

This module implements functionality for storing, analyzing, and identifying patterns in electricity usage data.
It provides insights on usage patterns and optimization suggestions based on historical data.
"""

import os
import json
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Optional, Any


class UsageAnalyzer:
    """
    Usage Pattern Analyzer for Home Appliance Scheduling

    This class implements functionality for storing, analyzing, and identifying patterns in electricity usage data.
    It can identify time-based patterns, appliance usage patterns, and consumption patterns.
    """
    
    def __init__(self, data_file: str = "usage_history.json"):
        """
        Initialize the Usage Analyzer
        
        Parameters:
            data_file (str): Path to the JSON file for storing usage history
        """
        self.data_file = data_file
        self.usage_history = self._load_history()
        
    def _load_history(self) -> Dict:
        """
        Load usage history from the JSON file
        
        Returns:
            Dict: Usage history data or empty structure if file doesn't exist
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Return empty structure if file is corrupted or can't be read
                return {"usage_history": []}
        else:
            # Create new empty history structure
            return {"usage_history": []}
    
    def _save_history(self) -> bool:
        """
        Save usage history to the JSON file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.usage_history, f, indent=2)
            return True
        except IOError:
            return False
    
    def add_usage_data(self, schedule: Dict[str, int], appliances: List[Dict], prices: List[float]) -> bool:
        """
        Add new usage data to the history
        
        Parameters:
            schedule (Dict[str, int]): Scheduling result, format {appliance_name: start_hour}
            appliances (List[Dict]): List of appliance information dictionaries
            prices (List[float]): List of 24-hour electricity prices
            
        Returns:
            bool: True if successful, False otherwise
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Create daily usage entry
        daily_usage = {
            "date": today,
            "prices": prices,
            "appliances": []
        }
        
        # Add appliance usage data
        for appliance in appliances:
            name = appliance['name']
            # Only include appliances that were scheduled
            if name in schedule:
                start_hour = schedule[name]
                daily_usage["appliances"].append({
                    "name": name,
                    "power": appliance['power'],
                    "start_time": start_hour,
                    "runtime": appliance['runtime'],
                    "priority": appliance['priority'],
                    "fixed_time": appliance['fixed_time'],
                    "time_window": list(appliance['time_window'])  # Convert tuple to list for JSON serialization
                })
        
        # Add to history
        self.usage_history["usage_history"].append(daily_usage)
        
        # Save updated history
        return self._save_history()
    
    def get_usage_dataframe(self) -> pd.DataFrame:
        """
        Convert usage history to pandas DataFrame for analysis
        
        Returns:
            pd.DataFrame: Usage data in a flat, tabular format
        """
        flat_data = []
        
        for day in self.usage_history["usage_history"]:
            date = day["date"]
            prices = day["prices"]
            
            for app in day["appliances"]:
                # Calculate end time
                start_time = app["start_time"]
                runtime = app["runtime"]
                end_time = (start_time + runtime) % 24
                
                # Calculate cost
                cost = sum(prices[(start_time + h) % 24] * app["power"] for h in range(runtime))
                
                # Add flattened record
                flat_data.append({
                    "date": date,
                    "appliance": app["name"],
                    "power": app["power"],
                    "start_time": start_time,
                    "end_time": end_time,
                    "runtime": runtime,
                    "priority": app["priority"],
                    "fixed_time": app["fixed_time"],
                    "cost": cost
                })
        
        return pd.DataFrame(flat_data)
    
    def analyze_time_patterns(self) -> Dict[str, Any]:
        """
        Analyze time-based usage patterns
        
        Returns:
            Dict: Analysis results including:
                - peak_hours: Hours with highest usage frequency
                - weekday_vs_weekend: Comparison of weekday and weekend patterns
                - hourly_distribution: Usage distribution by hour
        """
        df = self.get_usage_dataframe()
        if df.empty:
            return {"error": "No usage data available for analysis"}
        
        results = {}
        
        # Add date information
        df['date_obj'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date_obj'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6])  # 5=Saturday, 6=Sunday
        
        # Expand hourly usage
        hourly_usage = []
        for _, row in df.iterrows():
            start = row['start_time']
            end = row['end_time']
            if end < start:  # Handle overnight
                hours = list(range(start, 24)) + list(range(0, end))
            else:
                hours = list(range(start, end))
            
            for hour in hours:
                hourly_usage.append({
                    'date': row['date'],
                    'day_of_week': row['day_of_week'],
                    'is_weekend': row['is_weekend'],
                    'hour': hour,
                    'appliance': row['appliance'],
                    'power': row['power']
                })
        
        hourly_df = pd.DataFrame(hourly_usage)
        
        # Identify peak hours
        hour_counts = hourly_df.groupby('hour').size()
        peak_hours = hour_counts.nlargest(3).index.tolist()
        results['peak_hours'] = peak_hours
        
        # Compare weekday vs weekend
        weekday_hourly = hourly_df[~hourly_df['is_weekend']].groupby('hour').size()
        weekend_hourly = hourly_df[hourly_df['is_weekend']].groupby('hour').size()
        
        # Normalize to get percentages
        if not weekday_hourly.empty:
            weekday_hourly = weekday_hourly / weekday_hourly.sum() * 100
        if not weekend_hourly.empty:
            weekend_hourly = weekend_hourly / weekend_hourly.sum() * 100
            
        results['weekday_vs_weekend'] = {
            'weekday': {int(k): v for k, v in weekday_hourly.to_dict().items()},
            'weekend': {int(k): v for k, v in weekend_hourly.to_dict().items()}
        }
        
        # Get hourly distribution - ensure integer keys
        results['hourly_distribution'] = {int(k): v for k, v in hour_counts.to_dict().items()}
        
        return results
    
    def analyze_appliance_patterns(self) -> Dict[str, Any]:
        """
        Analyze appliance usage patterns
        
        Returns:
            Dict: Analysis results including:
                - frequent_appliances: Most frequently used appliances
                - appliance_timing: Typical usage times for each appliance
                - co_occurring_appliances: Appliances often used together
        """
        df = self.get_usage_dataframe()
        if df.empty:
            return {"error": "No usage data available for analysis"}
            
        results = {}
        
        # Most frequently used appliances
        app_counts = df['appliance'].value_counts()
        results['frequent_appliances'] = app_counts.to_dict()
        
        # Typical usage times for each appliance
        app_timing = {}
        for app, group in df.groupby('appliance'):
            app_timing[app] = {
                'avg_start_time': group['start_time'].mean(),
                'common_start_time': group['start_time'].mode()[0] if not group['start_time'].mode().empty else None,
                'avg_runtime': group['runtime'].mean(),
                'fixed_time_pct': (group['fixed_time'] == True).mean() * 100
            }
        results['appliance_timing'] = app_timing
        
        # Co-occurring appliances (used on the same day)
        co_occurrence = {}
        for date, group in df.groupby('date'):
            apps = group['appliance'].unique()
            if len(apps) > 1:
                for i, app1 in enumerate(apps):
                    for app2 in apps[i+1:]:
                        pair = tuple(sorted([app1, app2]))
                        co_occurrence[pair] = co_occurrence.get(pair, 0) + 1
        
        # Convert to sorted list
        co_occur_list = [{'appliances': list(k), 'count': v} for k, v in co_occurrence.items()]
        co_occur_list = sorted(co_occur_list, key=lambda x: x['count'], reverse=True)
        results['co_occurring_appliances'] = co_occur_list[:5]  # Top 5
        
        return results
    
    def analyze_consumption_patterns(self) -> Dict[str, Any]:
        """
        Analyze electricity consumption patterns
        
        Returns:
            Dict: Analysis results including:
                - peak_power_periods: Time periods with highest power consumption
                - consumption_trends: Trends in electricity consumption over time
                - cost_analysis: Analysis of electricity costs
        """
        df = self.get_usage_dataframe()
        if df.empty:
            return {"error": "No usage data available for analysis"}
            
        results = {}
        
        # Add date information
        df['date_obj'] = pd.to_datetime(df['date'])
        
        # Expand hourly usage with power
        hourly_usage = []
        for _, row in df.iterrows():
            start = row['start_time']
            end = row['end_time']
            if end < start:  # Handle overnight
                hours = list(range(start, 24)) + list(range(0, end))
            else:
                hours = list(range(start, end))
            
            for hour in hours:
                hourly_usage.append({
                    'date': row['date'],
                    'date_obj': row['date_obj'],
                    'hour': hour,
                    'appliance': row['appliance'],
                    'power': row['power']
                })
        
        hourly_df = pd.DataFrame(hourly_usage)
        
        # Calculate total power by hour
        power_by_hour = hourly_df.groupby('hour')['power'].sum()
        peak_power_hour = power_by_hour.idxmax()
        results['peak_power_periods'] = {
            'peak_hour': int(peak_power_hour),
            'peak_power': float(power_by_hour.max()),
            'hourly_power': {int(k): v for k, v in power_by_hour.to_dict().items()}
        }
        
        # Analyze consumption trends over time
        if len(df['date'].unique()) > 1:
            daily_consumption = hourly_df.groupby('date')['power'].sum()
            results['consumption_trends'] = {
                'daily_consumption': daily_consumption.to_dict(),
                'trend': 'increasing' if daily_consumption.iloc[-1] > daily_consumption.iloc[0] else 'decreasing'
            }
        
        # Cost analysis
        results['cost_analysis'] = {
            'total_cost': float(df['cost'].sum()),
            'average_cost_per_day': float(df.groupby('date')['cost'].sum().mean()),
            'cost_by_appliance': df.groupby('appliance')['cost'].sum().to_dict()
        }
        
        return results
    
    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """
        Generate optimization suggestions based on usage patterns
        
        Returns:
            Dict: Optimization suggestions including:
                - time_shifting: Suggestions for shifting usage to different times
                - appliance_grouping: Suggestions for grouping appliance usage
                - general_tips: General optimization tips
        """
        time_patterns = self.analyze_time_patterns()
        appliance_patterns = self.analyze_appliance_patterns()
        consumption_patterns = self.analyze_consumption_patterns()
        
        # Check if we have enough data for analysis
        if 'error' in time_patterns or 'error' in appliance_patterns or 'error' in consumption_patterns:
            return {"error": "Insufficient data for generating optimization suggestions"}
        
        suggestions = {}
        
        # Time shifting suggestions
        peak_hours = time_patterns.get('peak_hours', [])
        hourly_dist = time_patterns.get('hourly_distribution', {})
        
        # Find lowest usage hours
        all_hours = list(range(24))
        usage_hours = {h: hourly_dist.get(h, 0) for h in all_hours}
        low_usage_hours = sorted(all_hours, key=lambda h: usage_hours[h])[:5]
        
        suggestions['time_shifting'] = {
            'peak_hours_to_avoid': peak_hours,
            'recommended_hours': low_usage_hours,
            'specific_suggestions': []
        }
        
        # Appliance-specific suggestions
        app_timing = appliance_patterns.get('appliance_timing', {})
        for app, timing in app_timing.items():
            avg_start = timing.get('avg_start_time')
            if avg_start is not None and int(avg_start) in peak_hours:
                better_hours = [h for h in low_usage_hours if h not in peak_hours]
                if better_hours:
                    suggestions['time_shifting']['specific_suggestions'].append({
                        'appliance': app,
                        'current_avg_start': int(avg_start),
                        'recommended_start': better_hours[0],
                        'potential_benefit': 'Reduced electricity cost and lower peak demand'
                    })
        
        # Appliance grouping suggestions
        co_occurring = appliance_patterns.get('co_occurring_appliances', [])
        frequent_apps = appliance_patterns.get('frequent_appliances', {})
        
        suggestions['appliance_grouping'] = {
            'co_occurring_sets': co_occurring,
            'suggested_groups': []
        }
        
        # Find appliances that could be grouped but usually aren't
        top_apps = sorted(frequent_apps.items(), key=lambda x: x[1], reverse=True)[:5]
        top_app_names = [app for app, _ in top_apps]
        
        # Check which top appliances don't commonly co-occur
        existing_pairs = set()
        for pair_dict in co_occurring:
            pair = tuple(sorted(pair_dict['appliances']))
            existing_pairs.add(pair)
        
        for i, app1 in enumerate(top_app_names):
            for app2 in top_app_names[i+1:]:
                pair = tuple(sorted([app1, app2]))
                if pair not in existing_pairs:
                    suggestions['appliance_grouping']['suggested_groups'].append({
                        'appliances': list(pair),
                        'reason': 'These frequently used appliances could be scheduled together to optimize power usage'
                    })
        
        # General optimization tips
        suggestions['general_tips'] = [
            {
                'tip': 'Shift non-time-critical appliances to low-cost hours',
                'explanation': 'Running appliances like dishwashers and washing machines during off-peak hours can reduce electricity costs.'
            },
            {
                'tip': 'Group appliances to minimize peak power demand',
                'explanation': 'Avoid running multiple high-power appliances simultaneously to prevent exceeding power limits.'
            },
            {
                'tip': 'Prioritize fixed-time appliances',
                'explanation': 'Schedule flexible appliances around fixed-time ones to optimize overall electricity usage.'
            }
        ]
        
        return suggestions
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive insights report based on all analyses
        
        Returns:
            Dict: Complete insights report with all analysis results and suggestions
        """
        report = {
            'generated_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_points': len(self.usage_history.get("usage_history", [])),
            'time_patterns': self.analyze_time_patterns(),
            'appliance_patterns': self.analyze_appliance_patterns(),
            'consumption_patterns': self.analyze_consumption_patterns(),
            'optimization_suggestions': self.get_optimization_suggestions()
        }
        
        # Add overall insights summary
        has_error = any('error' in report[key] for key in ['time_patterns', 'appliance_patterns', 'consumption_patterns'])
        
        if has_error:
            report['summary'] = {
                'status': 'incomplete',
                'message': 'Insufficient data for comprehensive analysis. Please add more usage data.'
            }
        else:
            # Extract key insights
            peak_hours = report['time_patterns'].get('peak_hours', [])
            frequent_app = max(report['appliance_patterns'].get('frequent_appliances', {}).items(), 
                              key=lambda x: x[1])[0] if report['appliance_patterns'].get('frequent_appliances') else 'None'
            peak_power_hour = report['consumption_patterns'].get('peak_power_periods', {}).get('peak_hour', 'Unknown')
            
            report['summary'] = {
                'status': 'complete',
                'message': f'Analysis complete based on {report["data_points"]} days of usage data.',
                'key_insights': [
                    f'Peak usage typically occurs at {", ".join([f"{h}:00" for h in peak_hours])}',
                    f'Most frequently used appliance is {frequent_app}',
                    f'Highest power consumption occurs at {peak_power_hour}:00'
                ]
            }
        
        return report


# Usage example
if __name__ == "__main__":
    analyzer = UsageAnalyzer("usage_history.json")
    
    # Example of adding sample data
    sample_schedule = {
        "Washing Machine": 14,
        "Air Conditioner": 18
    }
    
    sample_appliances = [
        {
            'name': "Washing Machine",
            'power': 1.0,
            'runtime': 2,
            'time_window': (8, 22),
            'fixed_time': False,
            'priority': 2
        },
        {
            'name': "Air Conditioner",
            'power': 1.5,
            'runtime': 5,
            'time_window': (12, 22),
            'fixed_time': False,
            'priority': 1
        }
    ]
    
    sample_prices = [
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # 0-6 AM
        0.8, 0.8, 1.2, 1.2, 1.2, 1.2,  # 6-12 AM
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 12-18 PM
        1.5, 1.5, 1.5, 1.0, 0.8, 0.5   # 18-24 PM
    ]
    
    # Add sample data
    analyzer.add_usage_data(sample_schedule, sample_appliances, sample_prices)
    
    # Generate insights report
    report = analyzer.generate_insights_report()
    print(json.dumps(report, indent=2))
