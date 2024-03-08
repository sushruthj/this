#!/bin/bash

# Define the path to the Python script and virtual environment
PYTHON_SCRIPT="/home/jay/audiocd/this/audiocd.py"
VIRTUAL_ENV="/home/jay/audiocd/this/venv/bin/activate"
LOG_FILE="/home/jay/audiocd/cd_monitor.log"

# Function to run Python script in virtual environment
run_python_script() {
    source $VIRTUAL_ENV || { echo "Failed to activate virtual environment" >> $LOG_FILE; return 1; }
    python3 $PYTHON_SCRIPT >> $LOG_FILE 2>&1 &
    PID=$!
    echo "Python script running with PID: $PID" >> $LOG_FILE
}

# Function to stop Python script and deactivate virtual environment
stop_python_script() {
    if [ ! -z "$PID" ]; then
        kill $PID
        wait $PID 2>/dev/null
        unset PID
        deactivate || echo "Failed to deactivate virtual environment" >> $LOG_FILE
        echo "Python script stopped" >> $LOG_FILE
    fi
}

# Clean up resources on script exit
cleanup() {
    stop_python_script
    rm -f "$LOCK_FILE"
}

# Set up trap to ensure cleanup on script exit
trap cleanup EXIT

# Ensure log file exists
touch $LOG_FILE || { echo "Failed to create log file" >> $LOG_FILE; exit 1; }

# Monitor CD insertion and ejection using udev
udevadm monitor --udev --subsystem-match=block --property | \
while read -r -- _ _ event devpath _; do
    if [[ "$event" == "change" && "$devpath" == "/devices/*/block/sr0" ]]; then
        # Check if CD is inserted
        if udevadm info -q property -n "$devpath" | grep -q ID_CDROM_MEDIA; then
            echo "CD inserted" >> $LOG_FILE
            # Check if Python script is already running
            if [ -z "$PID" ]; then
                run_python_script || echo "Failed to run Python script" >> $LOG_FILE
            fi
        else
            # Check if Python script is running
            if [ ! -z "$PID" ]; then
                stop_python_script
            fi
            echo "CD ejected" >> $LOG_FILE
        fi
    fi
done