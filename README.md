# Home Appliance Scheduling Optimization Platform

## Project Overview

The Home Appliance Scheduling Optimization Platform is a Streamlit-based application designed to help users optimize the running times of home appliances to minimize electricity costs. By considering electricity price variations, appliance power requirements, and operational needs, the system can calculate optimal scheduling plans while contributing to sustainable development.

## Features

- **Electricity Price Input**: Supports 24-hour electricity price input with various pricing templates
- **Appliance Management**: Add and manage appliance lists, set power, runtime, and time windows
- **Optimization Calculation**: Uses greedy algorithm or integer linear programming to calculate optimal scheduling plans
- **Results Display**: Shows scheduling timetable, total costs, savings, and power usage charts
- **Usage Analysis**: Analyzes electricity usage patterns, provides historical data comparison and optimization suggestions
- **Gemini AI Insights**: Provides AI-powered analysis of electricity usage and personalized recommendations
- **Sustainable Development**: Supports UN Sustainable Development Goals, including affordable and clean energy, responsible consumption and production, and climate action

## File Structure

- `home.py`: Project homepage, including project navigation, UN sustainability goals contribution explanation, and program workflow visualization
- `app.py`: Main application entry point, integrating different interfaces
- `frontend.py`: Frontend interface for inputting electricity prices, power limits, and appliance information
- `optimizer.py`: Optimization algorithms for minimizing electricity costs through appliance scheduling
- `results.py`: Results display interface for showing optimization results
- `usage_analyzer.py`: Usage analyzer for storing, analyzing, and identifying electricity usage patterns
- `gemini_insights.py`: Gemini AI integration for analyzing electricity usage and providing personalized recommendations

## Running the Application

1. Ensure you have the required Python libraries installed:
   ```
   pip install streamlit pandas numpy plotly
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

3. Access the application in your browser (typically at http://localhost:8501)

## Usage Flow

1. Enter the application from the homepage
2. Set electricity prices and appliance information in the frontend interface
3. Click the "Calculate Optimal Plan" button to calculate the optimal scheduling plan
4. View the scheduling timetable and cost savings on the results page
5. Check the usage analysis page for electricity usage patterns and historical data
6. Use the Gemini AI Insights feature to get AI-powered analysis and personalized recommendations

## Sustainable Development Contribution

This project supports multiple UN Sustainable Development Goals:

- **Goal 7: Affordable and Clean Energy**
  - Optimizes electricity usage times, reducing grid load
  - Promotes renewable energy use
  - Improves energy efficiency

- **Goal 12: Responsible Consumption and Production**
  - Encourages responsible energy consumption behavior
  - Optimizes resource use
  - Promotes sustainable lifestyles

- **Goal 13: Climate Action**
  - Reduces carbon emissions
  - Balances grid load
  - Improves energy system resilience

## Technical Implementation

- **Frontend**: Uses Streamlit to create an interactive user interface
- **Data Visualization**: Uses Plotly to create dynamic charts
- **Optimization Algorithms**: Implements greedy algorithm and integer linear programming
- **Data Analysis**: Uses pandas and numpy for data processing and analysis
- **AI Integration**: Uses Gemini AI API to provide intelligent analysis and personalized recommendations
