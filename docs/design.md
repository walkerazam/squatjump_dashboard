# Design:

## User Types

### User Type 1: Dr. Jane (Main User)

**User Need**: Jane is a physician who wants to visualize force data from the jumping force plates. She wants to be able to see the numerical differences between the two legs using graphs.

**Use Case**: She will be using this tool to analyze patient progress and relay medical information to the patients in a straightforward way.

0. Identify patient
1. Identifying the information required for care (i.e., which metrics are needed?)
2. Calculate the metrics
3. Perform visualization on the calculated metrics

**Skill Level**: Can understand the data but cannot program/code themselves.


### User Type 2: John Doe (Administrative Role)

**User Need**: John is the doctor's assistant. He uploads specific datasets for the softward to aid the physician in providing a more informed care for the patient.

**Use Case**: John will be using this tool to upload data for creating visualizations and curate relevant visualization to deliver to the physician.

1. Collect new patient data as csv
2. Upload collected data to the tool
3. (If any) If issues come up, ensure that data is clean and that tool outputs appropriate visualizations. 

**Skill Level**: Familiar with the datasets used. Not great at interpreting the results at a medical level.

## Components

### List of Components

**1. Raw Data** 

*Description*: The raw CSV file containing numeric values (ordered by time, partitioned by patient)

**2. Clean Data**

*Description*: Cleaned raw data ready for processing (i.e., calculating metrics)

**3. Processed Data** 

*Description*: DataFrame containing the calculated metrics to be used for visualization, created from Clean Data

**4. Keyboard**

*Description*: For users to interact with the software.

**5. Git/GitHub**

*Description*: Version Control software for collaboration and hosting data/data-tools.

**5. Scientific Stack (Python Libraries: Pandas/NumPy/Math)**

*Description*: Scientific stack of Python Libraries to be used in data cleaning, and metric calculations.

**6. Utils Functions**

*Description*: Python script containing utility functions to be used in data processing (i.e., metrics calculation).

**7. Visualization Functions**

*Description*: Used to create the visualizations

**8. Streamlit**

*Description*: Web Interface to display visualizations of our data.

**9. Screen**

*Description*: For users to view the visualizations and interact with the dashboard


## Use Cases (with Components)

### 1: Data Cleaning and Pre-Processing
*Purpose*: To import and clean the raw data that are retrieved from the force plates (which extracts the biomechanical data on patients' squat jumps)

**Input Components**
1. Raw Data: CSV file

*Tools*:
- Keyboard
- Git/GitHub
- Scientific Stack (Python Libraries)
- Screen 

**Output Components**
1. Clean Dataset: NumPy Array
2. Status Report: Boolean value representing Success/Failure

### 2: Data Processing
*Purpose*: To calculate clinically interpretable metrics to be used in data visualization from the biomechanical features in the Cleaned Data 

**Input Components**
1. Clean Dataset: NumPy Array

*Tools*:
- Utils Functions
- Scientific Stack (Python Libraries)

**Output Components**
1. Processed Dataframe: Pandas DataFrame
2. Status Report: Boolean value representing Success/Failure

### 3: Data Visualization
*Purpose*: To visualize the calculated biomechanical metrics into a dashboard

**Input Components**
1. Processed Dataframe: Pandas DataFrame

*Tools*:
- Visualization Functions
- Streamlit
- Python Libraries (e.g., Seaborn, Plotly)
- Git/GitHub (to launch the Streamlit App)

**Output Components**
1. Streamlit Dashboard
