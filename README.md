# squatjump_dashboard
![Python Package using Conda](https://github.com/walkerazam/squatjump_dashboard/actions/workflows/python-package-conda.yml/badge.svg)

**Team Members**: Andrew Ba, Seoyeon Hong, Walker Azam, John Cheng

This repository contains files used to create the Squat Jump dashboard for CSE 583 (Fall 2022)

---------------------------------------
### Web App on Streamlit:
[ACL Squat Jump Analysis](https://walkerazam-squatjump-dashboard-1--home-deployment-build-9t4zjn.streamlit.app/)

---------------------------------------

### Project Information:

**Abstract**:

The purpose of this project was to configure a web application that allows users to analyze force data derived from squat jumps. These squat jumps were done by subjects recovering from ACL-reconstruction surgery. Users are able to interact with the analysis program through the dashboard in Streamlit.

Jump data in the form of a CSV can be dragged and dropped in the dash. Metrics, such as peak force, jump height, and timestamps are calculated in the back-end and returned to the user via multiple visualizations. The calculation results can be downloaded as a CSV for further analysis/comparision.

**Motivation**:

The key motivation was to make an analysis program that is constructive and accessible for users who can diagnose ACL injuries or work with people recovering from ACL reconstruction. These users most likely do not have enough knowledge or time to compute the jump metrics themselves, or are not able to create an automated program from scratch.

Another motivation was to create a program that could accurately identify timestamps of jump events in order to automate calculations without user input.

---------------------------------------

### How to Launch (Locally):

Please ensure you have `streamlit` installed and other necessary libraries (`pandas`, `numpy`, `matplotlib`, `scipy`, `plotly`, etc...). Please check environment.yml to check for all necessary libraries and versions!

Run `streamlit run 1_Home.py` from root of directory after cloning (/Users/.../squatjump_dashboard) to locally launch dashboard.


---------------------------------------

### Deployment Details:

This web app is deployed using `share.streamlit.io`. For deployment a seperate branch, 'deployment' was used since the build required slightly different demands. 

Deployment uses `requirements.txt` instead of `environment.yml` to function and launch correctly. As a result, the deployment branch will not include `environment.yml`. Deployment also uses Python version 10 instead of Python version 7 (which was used to build the app). Due to these differences, the deployment branch is not expected to pass the workflow tests utilized in 'master' branch.


---------------------------------------

### Running Tests:

Test files exist for the functions and submodules used in this project. Tests are automatically run when pushed to GitHub using github workflows. To run unittests locally, clone the repository and at the root run `python -m unittest discover`.

---------------------------------------

### Project Structure:

```bash
.
├── 1_🏠_Home.py
├── LICENSE.md
├── README.md
├── data
│   └── ...
├── docs
│   ├── README.md
│   └── design.md
├── environment.yml
├── pages
│   └── 2_📑_About.py
└── squatjump_dashboard
    ├── __init__.py
    ├── preProcess
    │   ├── __init__.py
    │   └── preProcess.py
    ├── process_data
    │   ├── __init__.py
    │   └── process_data.py
    ├── squat_jump_utils
    │   ├── __init__.py
    │   └── squat_jump_utils.py
    └── tests
        ├── __init__.py
        ├── test_process_data.py
        └── test_squat_jump_utils.py
```

### File Descriptions:

1. 1_🏠_Home.py : Contains Streamlit code used to create the home/landing page for the dashboard. This is the entrypoint file for the project.
2. data : Contains sample data files of jumps collected from Force Plates.
3. pages -> 2_📑_About.py : Contains About Page code
4. docs -> design.md: contains project information such as Use Case and Target Users.
5. .streamlit -> config.toml : Configuration information (Theme) for dashboard
6. environment.yml : virtual environment libraries


squatjump_dashboard: a module containing submodules used to process and run the 1_🏠_Home.py file.

1. squat_jump_utils.py : Module that contains helper functions utilized in 1_Home.py (mainly visualization code)
2. preProcess.py : Module that contains python file used by process_data.py to clean and pre-process read data. 
3. process_data.py : Module that contains python file used to calculate important jump metrics. Called by 1_🏠_Home.py.
9. tests : A directory containing unittests for the modules included in squatjump_dashboard. Each submodule has its own dedicated test python file. Unittests can be run in root directory calling `python -m unittest`.

