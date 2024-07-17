# README for hotlist_main.py

## Summary

`hotlist_main.py` is a Python script designed to manage and manipulate data, save it to an Excel file, and clean up image files from a specified directory. It's a handy tool for data management and file system operations.

## Prerequisites

Before you can run `hotlist_main.py`, you need to have the following installed on your machine:

- Python 3.6 or higher
- pip (Python package installer)

You can check if you have these installed by running the following commands in your terminal:

```bash
python --version
pip --version
```

## Installation

To install the required libraries for this script, navigate to the directory containing `hotlist_main.py` and run the following command:

```bash
./install.sh
```

This command installs all the Python packages listed in the `requirements.txt` file. If the `requirements.txt` file does not exist, you need to create it and list all the required packages there.

## Usage

To run the script, use the following command:

```bash
python hotlist_main.py
```

## Expected Output

Upon successful execution, the script will save the manipulated data to an Excel file and remove all `.jpg` files from the `downloads` directory in the current path. It will also print out the status of these operations.

## Explanation

The script contains two main functions:

- `remove_all_jpg_files`: This function navigates to the `downloads` directory in the current path, iterates over all subdirectories, and removes any `.jpg` files found. It then removes the now-empty directories.

- `run`: This function is used to run the main operations of the script.

## Conclusion

`hotlist_main.py` is a powerful tool for data management and file cleanup. With its easy setup and clear output, it can greatly simplify your work process.

