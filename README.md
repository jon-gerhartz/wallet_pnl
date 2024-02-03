# Wallet PnL Machine
Python API and ETL for PnL calculation on crypto wallets

## Prerequisites

Before you begin, ensure you have installed the following requirements:
- Python 3.12.0
- PostgreSQL 15

##Start Postgres 15 Server
1. Follow directions at link below to start postgres server:
https://www.postgresql.org/docs/current/server-start.html
2. Start server, note DB_USER, DB_HOST, DB_PW (if any). You will need to set these as environment variables in your .env file

## Setup

To set up the project environment, follow these steps:
1. Clone the repository:

  ```bash
  git clone https://github.com/jon-gerhartz/wallet_pnl.git
```

2. Change into wallet_pnl directory

  ```bash
  cd wallet_pnl
  ```

3. Install the required Python packages:

  ```bash
  pip install -r requirements.txt
  ```

4. Create a .env file based on sample.env provided. Adjust the values according to your environment:

  ```bash
  cp sample.env .env
  ```
5. Ensure you have created all required environment variables as specified in sample.env.
6. Initialize the database:
   
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

4. Access the API endpoint by navigating to http://127.0.0.1:9999/get-pnl?wallet_address=<your_wallet_address> in your browser, replacing <your_wallet_address> with your actual wallet address.

## Calling the API
1. Access the API endpoint by navigating to http://127.0.0.1:9999/get-pnl?wallet_address=<your_wallet_address> in your browser
2. Replace <your_wallet_address> with a wallet you are looking to get PnL on
3. To call the API via python or another language, make a get request to http://127.0.0.1:9999/get-pnl and pass {'wallet_address': '<your_wallet_address>'} as a query parameter
4. The API only supports ETH based wallets. You can pass wallets which contain more than one ETH based coin. This will return PnL data for all coins where price and balance data is available
5. PnL data is limited to price data and balance data. Balance data is always for last 7 days from when API call is made. Price data is from 7 days of last ELT pipeline run. 

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
