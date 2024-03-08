#!/bin/bash

# Specify the path to your Python script
PYTHON_SCRIPT="audiocd.py"

# Specify the path to the virtual environment activate script
VENV_ACTIVATE="/home/jay/audiocd/this/venv/bin/activate"

# Specify the directory where the Python script resides
DIRECTORY="/home/jay/audiocd/this"

# Function to execute the Python script within virtual environment
execute_python_script() {
    source $VENV_ACTIVATE
    python3 $PYTHON_SCRIPT
    deactivate
}

# Get the device ID of the CD drive
DEVICE_ID=$(udevadm info --query=property --name=/dev/sr0 | grep ID_SERIAL= | sed 's/ID_SERIAL=//')

# Continuously monitor udev events for the CD drive
udevadm monitor --property --udev -s block | while read -r event
do
    # Check if a new CD has been inserted
    if echo "$event" | grep -q "ID_SERIAL=$DEVICE_ID"
    then
        # Change to the desired directory
        cd $DIRECTORY
        # Execute the Python script within virtual environment
        execute_python_script
    fi
done
