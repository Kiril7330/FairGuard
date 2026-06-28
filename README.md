# FairGuards

A dedicated, automated shift management system built for The Courts Guard.

FairGuards tracks active guards, manages shift history, and mathematically calculates the fairest next-in-line assignment for specific posts to eliminate scheduling conflicts and ensure equal rotation.

## Features

- **Smart Roster Management:** Add or remove guards from the master database with integrated validation.
- **Active Shift Pool:** Build the daily team using quick autocomplete search.
- **Algorithmic Assignment:** Automatically calculate the next available guard for posts (e.g., Scanning, Judges' Parking) based on historical timestamp data.
- **History Ledger:** View the last 50 assignments or flush the database cleanly.

## Developer Setup

### Prerequisites

- Python 3.10 or higher
- PyQt6
- Pillow (for icon processing)

### Installation

1. Clone the repository to your local machine.
2. Create and activate a virtual environment:
   `python -m venv venv`
   `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
3. Install the required dependencies:
   `pip install -r requirements.txt`
4. Run the application:
   `python main.py`

## Compiling for Production

To build a standalone executable for the deployment machine, run PyInstaller from within the active virtual environment.

**For Windows:**
`pyinstaller --noconsole --windowed --icon=assets/guard_logo.jpg --add-data "assets;assets" main.py`

**For Mac:**
`pyinstaller --noconsole --windowed --icon=assets/guard_logo.jpg --add-data "assets:assets" main.py`

## Author

Made by Kiril Shamis
