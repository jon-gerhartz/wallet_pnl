# wallet_pnl
Python API and ETL for PnL calculation on crypto wallets

# Project Title

Brief description of your project.

## Prerequisites

Before you begin, ensure you have installed the following requirements:
- Python 3.12.0
- PostgreSQL 15

## Setup

To set up the project environment, follow these steps:
1. Clone the repository:

  ```bash
  git clone https://github.com/jon-gerhartz/wallet_pnl.git
```

2. Install the required Python packages:

  ```bash
  pip install -r requirements.txt
  ```

3. Create a .env file based on sample.env provided. Adjust the values according to your environment:

  ```bash
  cp sample.env .env
  ```
4. Ensure you have created all required environment variables as specified in sample.env.
5. Initialize the database:
6. 
  ```bash 
  cd app/db
  python db_init.py
  ```

## Running the ELT Pipeline
To run the ETL pipeline, follow these steps:

1. Ensure you have set the COINGECKO_API_KEY in your .env file.
2. Navigate to the db directory:
   
  ```bash
  cd app/db
  ```

3. Execute the ELT script:

  ```bash
  python elt.py
  ```

## Running the API Server
To start the API server, follow these instructions:

1. Navigate to the app directory:

  ```bash
  cd app
  ```

2. Make sure the FLASK_SECRET_KEY environment variable is set in your .env file.
3. Start the API server:

  ```bash
  python api.py
  ```

1. Access the API endpoint by navigating to http://127.0.0.1:9999/get-pnl?wallet_address=<your_wallet_address> in your browser, replacing <your_wallet_address> with your actual wallet address.

## Running the Streamlit App
To run the Streamlit application, ensure the following:

1. Navigate to the app directory (if not already there):

  ```bash
  cd app
  ```

2. Confirm the API_BASE_URL environment variable is set in your .env file.
3. Verify that the API server is running. If not, see the steps above for "Run API Server".
4. Start the Streamlit app:

  ```bash
  streamlit run streamlit.py
  ```

## Additional Information
Make sure to replace placeholder values in the .env file and commands with actual values specific to your setup.
For more details on configuring the environment variables and understanding the project structure, refer to the sample.env file and project documentation.
