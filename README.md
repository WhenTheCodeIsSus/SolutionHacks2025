# Home Appliance Scheduling Optimization Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.20.0%2B-red)

An intelligent platform for optimizing the scheduling of home appliances to minimize electricity costs based on time-of-use pricing.

## Overview

The Home Appliance Scheduling Optimization Platform is a Streamlit-based application that helps users optimize their electricity usage by intelligently scheduling home appliances. By considering time-varying electricity prices, appliance power requirements, and user preferences, the platform generates optimal scheduling plans to minimize electricity costs.

### Key Features

- **Interactive UI**: Easy-to-use interface for inputting electricity pricing and appliance information
- **Flexible Optimization**: Supports both greedy algorithm and integer linear programming approaches
- **Detailed Results**: Comprehensive visualization of scheduling results and cost analysis
- **Usage Pattern Analysis**: AI-powered analysis of electricity usage patterns over time
- **Data Visualization**: Interactive charts and graphs for better understanding of electricity usage

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/home-appliance-scheduler.git
cd home-appliance-scheduler
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

### Setting Up Electricity Pricing

1. Enter the electricity prices for each hour of the day
2. Choose from preset pricing templates or customize your own
3. Set the maximum power limit for your household

### Adding Appliances

1. Enter appliance details including:
   - Name
   - Power consumption (kW)
   - Required runtime (hours)
   - Available time window
   - Priority level
   - Whether the start time is fixed or flexible

### Generating Optimal Schedule

1. Choose between greedy algorithm (faster) or integer linear programming (more optimal)
2. Click "Calculate Optimal Plan" to generate the schedule
3. View the results including:
   - Total electricity cost
   - Appliance scheduling timetable
   - Hourly power usage chart
   - Appliance runtime timeline

### Analyzing Usage Patterns

The platform includes an AI-powered usage pattern analysis feature that:
- Identifies time-based patterns in electricity usage
- Analyzes appliance usage frequency and timing
- Provides insights on power consumption trends
- Shows cost distribution among different appliances

## System Architecture

The platform consists of four main modules:

1. **app.py**: Main application that integrates all components
2. **frontend.py**: Handles the user interface for data input
3. **optimizer.py**: Implements the optimization algorithms
4. **results.py**: Manages result visualization and analysis
5. **usage_analyzer.py**: Analyzes historical usage patterns

## Optimization Methods

### Greedy Algorithm

The greedy algorithm prioritizes appliances based on user-defined priority levels and finds the lowest-cost time slots within each appliance's time window. This approach is fast but may not always find the globally optimal solution.

### Integer Linear Programming (ILP)

The ILP approach formulates the scheduling problem as a mathematical optimization problem, considering all constraints simultaneously. This method guarantees finding the global optimum if one exists but may take longer to compute for complex scenarios.

## Data Analysis

The usage pattern analysis feature employs statistical methods to:
- Identify peak usage hours
- Compare weekday vs. weekend usage patterns
- Analyze appliance usage frequency and timing
- Track consumption trends over time
- Provide cost analysis by appliance

## Configuration Options

The platform offers several configuration options:

- **Electricity pricing templates**: Pre-defined pricing schemes including peak-valley time-of-use pricing, uniform pricing, and night discount pricing
- **Optimization method**: Choice between greedy algorithm and integer linear programming
- **Visualization settings**: Various chart types and data representations

## Technical Details

- **Frontend**: Streamlit for interactive web interface
- **Data Analysis**: Pandas and NumPy for data manipulation
- **Visualization**: Plotly for interactive charts
- **Optimization**: PuLP for integer linear programming implementation
- **Storage**: JSON for storing usage history

---

Made for a more energy-efficient future
