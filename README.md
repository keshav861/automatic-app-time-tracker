# Activity Tracker

A PyQt5 application to track user activity on various applications and websites, including real-time tracking and generating reports.

## Features

- Track active window/application in real-time.
- Log duration of time spent on each window/application.
- Remind users to take breaks.
- Generate and download detailed logs and summary reports.
- Real-time activity tracking with an intuitive user interface.

## Requirements

- Python 3.x
- PyQt5
- psutil
- pynput
- pandas
- matplotlib

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/keshav861/automatic-app-time-tracker.git
    cd automatic-app-time-tracker
    ```

2. **Create a virtual environment and activate it (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the application:**

    ```bash
    python tracker.py
    ```

2. **Features:**

    - **Log & Report:** Click this button to view the activity log and download detailed logs and summary reports.
    - **Real-Time Tracker:** Click this button to open a window displaying real-time tracking of active windows/applications.
    - **Break Reminder:** A reminder will appear every hour to encourage the user to take a break.

3. **Close the application:**

    - The application will automatically stop the mouse and keyboard listeners when closed.

## File Structure

```plaintext
automatic-app-time-tracker/
├── icons/
│   ├── download_icon.png
│   ├── download_report_icon.png
│   ├── report_icon.png
│   └── tracker_icon.png
├── tracker.py
├── requirements.txt
└── README.md
