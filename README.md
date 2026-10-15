# Daily Stock ETL Automation Setup Guide

## 1. Google Sheets API Credentials
You need a `credentials.json` file to authenticate with Google Sheets.
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Enable **Google Sheets API** and **Google Drive API**.
4.  Create a **Service Account**.
5.  Create a JSON key for the service account and download it.
6.  Rename the file to `credentials.json` and place it in `d:\Trading Workflows\`.
7.  **Important**: Share your Google Sheet `Stock Data` with the email address found inside `client_email` in the `credentials.json` file.

## 2. Symbol Mapping File
Upload your symbol mapping file (CSV format) to:
`d:\Trading Workflows\data\symbol_mapping.csv`

The file should have at least these columns:
- `SYMBOL`: The stock symbol (e.g., RELIANCE, TCS).
- `SECTOR`: The sector name.

## 3. Running the Script
Open a terminal in VS Code and run:
```bash
python "d:\Trading Workflows\src\main.py"
```

The script will:
1.  Download the latest available Bhavcopy from NSE and BSE.
2.  Filter for Equity (EQ) series.
3.  Calculate Delivery % (if available).
4.  Map sectors.
5.  Upload the data to a Google Sheet named "Stock Data" (or create it if missing).
