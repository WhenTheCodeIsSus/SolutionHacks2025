#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Home Appliance Scheduling Optimization Module

This module implements algorithms for optimizing home appliance scheduling to minimize electricity costs.
It includes both greedy algorithm and integer linear programming optimization methods.
"""

import warnings
from typing import Dict, List, Tuple, Union, Optional


class Optimizer:
    """
    Home Appliance Scheduler Optimizer

    This class implements algorithms for optimizing home appliance scheduling to minimize electricity costs.
    It considers constraints such as electricity price variations, appliance power, runtime, time windows, and priorities.
    """

    def __init__(self, prices: List[float], max_power: float):
        """
        Initialize the optimizer

        Parameters:
            prices (List[float]): List of 24-hour electricity prices (dollars/kWh)
            max_power (float): Maximum power limit per hour (kW)
        """
        if len(prices) != 24:
            raise ValueError("The price list must contain 24 hours of prices")
        
        if not all(isinstance(p, (int, float)) and p >= 0 for p in prices):
            raise ValueError("Prices must be non-negative numbers")
            
        if not isinstance(max_power, (int, float)) or max_power <= 0:
            raise ValueError("Maximum power must be a positive number")
        
        # Store 24-hour electricity prices
        self.prices = prices
        # Store maximum power limit per hour
        self.max_power = max_power
        # Store appliance information
        self.appliances = []
        # Store optimized scheduling results
        self.schedule = {}
        # Store hourly power usage
        self.hourly_usage = [0] * 24
        
    def add_appliance(self, name: str, power: float, runtime: int, 
                     time_window: Tuple[int, int], fixed_time: bool = False, 
                     priority: int = 0):
        """
        Add an appliance to the optimizer

        Parameters:
            name (str): Appliance name
            power (float): Appliance power (kW)
            runtime (int): Required running hours
            time_window (tuple): Available runtime window, format (start_hour, end_hour)
            fixed_time (bool): Whether the runtime is fixed, if True, must run at the start time specified in time_window
            priority (int): Priority, higher value means higher priority

        Returns:
            Optimizer: Returns the optimizer instance, supports chain calls
            
        Exceptions:
            ValueError: Thrown when input parameters are invalid
        """
        # Validate parameters
        if not isinstance(name, str) or not name:
            raise ValueError("Appliance name must be a non-empty string")
            
        if not isinstance(power, (int, float)) or power <= 0:
            raise ValueError("Appliance power must be a positive number")
            
        if not isinstance(runtime, int) or runtime <= 0 or runtime > 24:
            raise ValueError("Runtime must be an integer between 1 and 24")
            
        if not isinstance(time_window, tuple) or len(time_window) != 2:
            raise ValueError("Time window must be a tuple containing two elements")
            
        start_hour, end_hour = time_window
        if not isinstance(start_hour, int) or not isinstance(end_hour, int):
            raise ValueError("Start and end times of the time window must be integers")
            
        if start_hour < 0 or start_hour > 23 or end_hour < 0 or end_hour > 23:
            raise ValueError("Time window must be between 0 and 23")
        
        # Calculate time window length, handle overnight cases
        if end_hour < start_hour:  # Overnight case, e.g., (22, 5) means from 10 PM to 5 AM the next day
            window_length = (24 - start_hour) + end_hour
        else:
            window_length = end_hour - start_hour + 1
            
        if runtime > window_length:
            raise ValueError("Runtime cannot exceed the length of the time window")
        
        # Add appliance information
        self.appliances.append({
            'name': name,
            'power': power,
            'runtime': runtime,
            'time_window': time_window,
            'fixed_time': fixed_time,
            'priority': priority
        })
        
        return self
        
    def optimize(self) -> Dict[str, int]:
        """
        Optimize appliance scheduling using a greedy algorithm
        
        Greedy strategy:
        1. Sort appliances by priority (higher priority first)
        2. For each appliance, find the consecutive time period with lowest cost within its time window
        3. If the time period satisfies power constraints, schedule the appliance to run during that period
        4. Otherwise, try other time periods or mark as unschedulable
        
        Returns:
            Dict[str, int]: Scheduling result, format {appliance_name: start_hour}
        """
        # Reset scheduling results and power usage
        self.schedule = {}
        self.hourly_usage = [0] * 24
        
        # Sort appliances by priority (higher priority first)
        sorted_appliances = sorted(self.appliances, key=lambda x: x['priority'], reverse=True)
        
        for appliance in sorted_appliances:
            name = appliance['name']
            power = appliance['power']
            runtime = appliance['runtime']
            start_hour, end_hour = appliance['time_window']
            fixed_time = appliance['fixed_time']
            
            # Handle overnight time windows
            hours_to_check = []
            if end_hour < start_hour:  # Overnight case
                hours_to_check = list(range(start_hour, 24)) + list(range(0, end_hour + 1))
            else:
                hours_to_check = list(range(start_hour, end_hour + 1))
            
            # If fixed time running, schedule directly at the start of the time window
            if fixed_time:
                start_time = start_hour
                end_time = (start_hour + runtime) % 24
                
                # Check if power constraints are satisfied
                can_schedule = True
                for h in range(runtime):
                    hour = (start_hour + h) % 24
                    if self.hourly_usage[hour] + power > self.max_power:
                        can_schedule = False
                        break
                
                if can_schedule:
                    # Update schedule and power usage
                    self.schedule[name] = start_hour
                    for h in range(runtime):
                        hour = (start_hour + h) % 24
                        self.hourly_usage[hour] += power
                else:
                    warnings.warn(f"Cannot schedule appliance {name} because power exceeds limit during fixed time period")
                
                continue
            
            # For non-fixed time appliances, find the time period with lowest cost
            best_start = -1
            min_cost = float('inf')
            
            # Try each possible start time
            for i in range(len(hours_to_check) - runtime + 1):
                start_time = hours_to_check[i]
                total_cost = 0
                can_schedule = True
                
                # Calculate the cost of running during this time period and check power constraints
                for r in range(runtime):
                    hour = (start_time + r) % 24
                    total_cost += self.prices[hour] * power
                    
                    if self.hourly_usage[hour] + power > self.max_power:
                        can_schedule = False
                        break
                
                if can_schedule and total_cost < min_cost:
                    min_cost = total_cost
                    best_start = start_time
            
            if best_start != -1:
                # Found a feasible scheduling plan
                self.schedule[name] = best_start
                
                # Update power usage
                for r in range(runtime):
                    hour = (best_start + r) % 24
                    self.hourly_usage[hour] += power
            else:
                warnings.warn(f"Cannot schedule appliance {name} because no time period satisfies power constraints")
        
        return self.schedule
    
    def optimize_ilp(self) -> Dict[str, int]:
        """
        Optimize appliance scheduling using Integer Linear Programming (ILP)
        
        Uses the PuLP library to implement integer linear programming, defining decision variables, objective function, and constraints to find the optimal scheduling plan.
        
        Returns:
            Dict[str, int]: Scheduling result, format {appliance_name: start_hour}
        
        Exceptions:
            ImportError: Thrown when PuLP library is not installed
        """
        try:
            import pulp
        except ImportError:
            raise ImportError("Please install the PuLP library to use the integer linear programming method: pip install pulp")
        
        # Reset scheduling results and power usage
        self.schedule = {}
        self.hourly_usage = [0] * 24
        
        # Create problem instance
        problem = pulp.LpProblem("Appliance_Scheduling", pulp.LpMinimize)
        
        # Create decision variables: x[i][t] = 1 means appliance i starts running at time t
        x = {}
        for i, appliance in enumerate(self.appliances):
            x[i] = {}
            start_hour, end_hour = appliance['time_window']
            runtime = appliance['runtime']
            
            # Handle overnight time windows, calculate all possible start times
            possible_starts = []
            if end_hour < start_hour:  # Overnight case
                possible_starts = list(range(start_hour, 24)) + list(range(0, end_hour - runtime + 2))
            else:
                possible_starts = list(range(start_hour, end_hour - runtime + 2))
            
            for t in possible_starts:
                x[i][t] = pulp.LpVariable(f"x_{i}_{t}", cat=pulp.LpBinary)
        
        # Objective function: minimize total electricity cost
        objective = pulp.lpSum(
            self.prices[(t + h) % 24] * self.appliances[i]['power'] * x[i][t]
            for i in range(len(self.appliances))
            for t in x[i].keys()
            for h in range(self.appliances[i]['runtime'])
        )
        problem += objective
        
        # Constraint 1: Each appliance must run exactly once
        for i in range(len(self.appliances)):
            if x[i]:  # Ensure there are possible start times
                problem += pulp.lpSum(x[i][t] for t in x[i].keys()) == 1
        
        # Constraint 2: Total power per hour cannot exceed maximum power limit
        for h in range(24):
            power_sum = pulp.lpSum(
                self.appliances[i]['power'] * x[i][t]
                for i in range(len(self.appliances))
                for t in x[i].keys()
                if any((t + r) % 24 == h for r in range(self.appliances[i]['runtime']))
            )
            problem += power_sum <= self.max_power
        
        # Constraint 3: Fixed time appliances must start running at the specified time
        for i, appliance in enumerate(self.appliances):
            if appliance['fixed_time']:
                start_hour = appliance['time_window'][0]
                if start_hour in x[i]:
                    problem += x[i][start_hour] == 1
        
        # Solve the problem
        solver = pulp.PULP_CBC_CMD(msg=False)
        problem.solve(solver)
        
        # Check if a feasible solution was found
        if pulp.LpStatus[problem.status] != 'Optimal':
            warnings.warn("Could not find an optimal solution, constraints may be too strict")
            return {}
        
        # Extract results and update schedule and power usage
        for i, appliance in enumerate(self.appliances):
            name = appliance['name']
            power = appliance['power']
            runtime = appliance['runtime']
            
            for t in x[i].keys():
                if pulp.value(x[i][t]) == 1:
                    self.schedule[name] = t
                    
                    # Update power usage
                    for r in range(runtime):
                        hour = (t + r) % 24
                        self.hourly_usage[hour] += power
                    break
        
        return self.schedule
    
    def get_schedule(self) -> Dict[str, int]:
        """
        Get the current scheduling plan
        
        Returns:
            Dict[str, int]: Scheduling result, format {appliance_name: start_hour}
        """
        return self.schedule
    
    def get_total_cost(self) -> float:
        """
        Calculate the total electricity cost of the current scheduling plan
        
        Returns:
            float: Total electricity cost
        """
        total_cost = 0
        
        for name, start_hour in self.schedule.items():
            # Find the corresponding appliance information
            appliance = next(a for a in self.appliances if a['name'] == name)
            power = appliance['power']
            runtime = appliance['runtime']
            
            # Calculate running cost
            for r in range(runtime):
                hour = (start_hour + r) % 24
                total_cost += self.prices[hour] * power
        
        return total_cost
    
    def get_hourly_usage(self) -> List[float]:
        """
        Get hourly power usage
        
        Returns:
            List[float]: 24-hour power usage
        """
        return self.hourly_usage


# Usage example
if __name__ == "__main__":
    # Sample electricity price data (dollars/kWh)
    prices = [
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # 0-6 AM (valley price)
        0.8, 0.8, 1.2, 1.2, 1.2, 1.2,  # 6-12 AM (normal/peak price)
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 12-6 PM (normal price)
        1.5, 1.5, 1.5, 1.0, 0.8, 0.5   # 6-12 PM (peak/normal/valley price)
    ]
    
    # Maximum power limit (kW)
    max_power = 5.0
    
    # Create optimizer instance
    optimizer = Optimizer(prices, max_power)
    
    # Add appliances
    optimizer.add_appliance(
        name="Washing Machine", 
        power=1.0, 
        runtime=2, 
        time_window=(8, 22),
        priority=2
    )
    
    optimizer.add_appliance(
        name="Electric Water Heater", 
        power=2.0, 
        runtime=3, 
        time_window=(6, 10),
        fixed_time=True,
        priority=3
    )
    
    optimizer.add_appliance(
        name="Air Conditioner", 
        power=1.5, 
        runtime=5, 
        time_window=(12, 22),
        priority=1
    )
    
    # Optimize using greedy algorithm
    schedule = optimizer.optimize()
    print("\nGreedy Algorithm Optimization Results:")
    for appliance, start_time in schedule.items():
        print(f"{appliance}: Start running at {start_time} o'clock")
    print(f"Total electricity cost: {optimizer.get_total_cost():.2f} dollars")
    
    # Optimize using integer linear programming (if PuLP library is installed)
    try:
        schedule_ilp = optimizer.optimize_ilp()
        print("\nInteger Linear Programming Optimization Results:")
        for appliance, start_time in schedule_ilp.items():
            print(f"{appliance}: Start running at {start_time} o'clock")
        print(f"Total electricity cost: {optimizer.get_total_cost():.2f} dollars")
    except ImportError as e:
        print(f"\n{e}")
