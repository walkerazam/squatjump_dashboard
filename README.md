# squatjump_dashboard
[![Python Package using Conda](https://github.com/walkerazam/squatjump_dashboard/actions/workflows/python-package-conda.yml/badge.svg)]

This repository contains files used to create the Squat Jump dashboard for CSE 583.

### How to Launch (Locally):

Please ensure you have `streamlit` installed and other necessary libraries (`pandas`, `numpy`, `matplotlib`, `scipy`, and `plotly`). Please check environment.yml to check for all necessary libraries and versions!

Run `streamlit run 1_Home.py` from root of directory after cloning (/Users/.../squatjump_dashboard) to locally launch dashboard.

### Files:

1. 1_Home.py : Contains Streamlit code used to create the home/landing page for the dashboard
2. squat_jump_utils.py : Contains helper functions utilized in 1_Home.py
3. data : Contains data files of jumps collected from Force Plates
4. pages -> 2_About.py : Contains About Page code
5. .streamlit -> config.toml : Configuration information (Theme) for dashboard
6. environment.yml : virtual environment libraries
7. preProcess.py : A python file containing helper functions used by process_data.py to clean and pre-process read data.
8. process_data.py : A python file containing functions to calculate important jump metrics.
9. test_squat_jump_utils.py : File contains unittests for squat_jump_utils.py. Can be run in root directory calling `python -m unittest`.

**Team Members**: Andrew Ba, Seoyeon Hong, Walker Azam, John Cheng
