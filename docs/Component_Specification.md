# Component Specification

## Software Components

### List of Components

**1. Scientific Stack**

*Description*: Scientific stack of Python Libraries to be used in Utils and Visulization Functions.  
*Inputs*: Python Libraries: Pandas/NumPy/Scipy/Pyplot/Matplotlib  
*Outputs*: Library functions  

**2. Utils Functions**

*Description*: Python script containing utility functions to be used in data cleaning, timestamps extractions and metric calculations.  
*Inputs*: Python Library functions
*Outputs*: Function returns, integers or floats  

**3. Raw Data** 

*Description*: The raw CSV file containing numeric squat jump data for left and right feet (ordered by time, partitioned by patient).  
*Inputs*: Jump data, a CSV file  
*Outputs*: Raw data, a pandas dataframe  

**4. Clean Data**

*Description*: A filtered, catogirized and integrated dataframe ready for metric calculation.  
*Inputs*: Utils functions, python script  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Raw data, a pandas dataframe  
*Outputs*: Clean Data, a pandas dataframe  

**5. Index table**

*Description*: A dataframe which store the timestamps for each jump, created from Clean Data.  
*Inputs*: Utils functions, python script  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Clean data, a pandas dataframe  
*Outpus*: Index table, a pandas dataframe  

**6. Calculation Results** 

*Description*: A DataFrame containing the calculated metrics to be used for visualization, created from Clean Data.  
*Inputs*: Utils functions, python script  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Clean data, a pandas dataframe   
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Index table, a pandas dataframe  
*Outpus*: Calculation results, a pandas dataframe  

**7. Visualization Functions**

*Description*: Python and JSHTML script to create the visualizations and animations.  
*Inputs*: Python library functions
*Outpus*: Function returns, figure object or pandas dataframe  

**8. Streamlit**

*Description*: Python script to integrate inputs and genrate visulizations.  
*Inputs*: Visulization functions, python script  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Clean data, a pandas dataframe  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Index table, a pandas dataframe  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Calculation result, a pandas dataframe  
*Outpus*: Visuliation results  

**9. Keyboard**

*Description*: For users to interact with the web app and the dashboard.  
*Inputs*: Manual operation  
*Outpus*: Keyboard commends  

**10. The Dashboard**

*Description*: Web Interface, the dashboard to display visualizations and interactive features.  
*Inputs*: Keyboard commends  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Visulization results from Streamlit  
*Outputs*: Information to show on screen  
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Downloadable file, a CSV file  

**11. Screen**

*Description*: For users to view the visualizations.  
*Inputs*: Information from dash board  
*Outpus*: Visual display  

## Interactions To Accomplish Use Cases

### Use Case 1: Data Analysis Request

**User story**: Dr. Jane wants to analyze the recovery progress of a new patient.  

*User Action:*    
&ensp;&ensp;&ensp;&ensp;Upload a CSV jump data.  
*System Response:*  
&ensp;&ensp;&ensp;&ensp;[if correct] Create a new patient data.  
&ensp;&ensp;&ensp;&ensp;[if incorrect] Pop up an exception message.  

*User Action:*  
&ensp;&ensp;&ensp;&ensp;Select the new patient data to analyze.  
*System Response:*  
&ensp;&ensp;&ensp;&ensp;Presence the visualization of the patient.  

*User Action:*  
&ensp;&ensp;&ensp;&ensp;Select a certain jump or diagram to take a careful look.  
*System Response:*  
&ensp;&ensp;&ensp;&ensp;Show the image or animation of the request.  

### Use Case 2: Documentation Request

**User story**: John received a large among of new data and want to gather the analysis results for documentation.

*User Action:*  
&ensp;&ensp;&ensp;&ensp;Upload a new CSV jump data.  
*System Response:*  
&ensp;&ensp;&ensp;&ensp;[if correct] Create a new patient data.  
&ensp;&ensp;&ensp;&ensp;[if incorrect] Pop up an exception message.  

*User Action:*  
&ensp;&ensp;&ensp;&ensp;Check the corectness of the data.  
*System Response:*  
&ensp;&ensp;&ensp;&ensp;Presence the visualization of the processed data.  

*User Action:*  
&ensp;&ensp;&ensp;&ensp;Download the analysis results.  
*System Response:*  
&ensp;&ensp;&ensp;&ensp;Generate a downloadable CSV file.  

## Preliminary Plan

![Alt text](./Interaction_Diagram1.png?raw=true)
