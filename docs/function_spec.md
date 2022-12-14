## Background:

Computing metrics from movement from a subset of human subjects can be difficult as all humans have their own habitual movement patterns. This can go for any type of movement (running, jumping, throwing, etc.). In some cases, calculating these metrics may require a manual interface to select the exact range of data to analyze. For this project, the motivation was to configure a web application that allows users to analyze force data derived from squat jumps with minimal to little interface from the user. This means the program should be able to identify all critical events the user requires. In addition, because the data used was taken from patients recovering from ACL reconstruction, the users identified were not required to have any coding knowledge whatsover.

## Data Sources
The only data required to run this program is force plate data in a csv format. To help create this program, unidentified squat jump data taken from a blood-flow restriction study was used.

## User Types

### User Type 1: Dr. Jane (Main User)

**User Need**: Jane is a physician who wants to visualize force data from the jumping force plates. She wants to be able to see the numerical differences between the two legs using graphs.

**Use Case**: She will be using the web app to analyze patient progress and relay medical information to the patients in a straightforward way.

0. Identify patient
1. Identify the information required for care (i.e., which metrics are needed?)
2. Calculate the metrics
3. Perform visualization on the calculated metrics

**Skill Level**: Can understand the data but cannot program/code themselves.



### User Type 2: John Doe (Administrative Role)

**User Need**: John is the doctor's assistant. He uploads specific datasets for the software to aid the physician in providing a more informed care for the patient.

**Use Case**: John will be using this tool to upload data for creating visualizations and curate relevant visualization to deliver to the physician.

1. Collect new patient data as CSV
2. Upload collected data to the web app
3. If any issues come up, ensure that data is clean and that tool outputs appropriate visualizations. 

**Skill Level**: Familiar with the datasets used. Not great at interpreting the results at a medical level.

