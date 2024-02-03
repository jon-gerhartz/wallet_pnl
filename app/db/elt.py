from connect import execute_query
from datetime import datetime
from dotenv import load_dotenv
import os
from queries import create_stg_price_history, drop_stg_price_history, load_stg_price_history, load_src_price_history, create_src_elt_log, insert_elt_log
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, InvalidURL
import time

# Load environment variables from the .env file
load_dotenv()

COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')

coingecko_api_base = 'https://api.coingecko.com/api/v3'
endpoints = {
    'coins_market_cap_desc': '/coins/markets',
    'market_data': '/coins/{id}/market_chart'
}


def extract_data(base, endpoint, key, retries=3, delay=60, **kwargs):
    """
    Make a GET request and return the JSON response.

    Parameters:
    - base (str): Base URL of the API you want to call.
    - endpoint (str): API endpoint.
    - key (str): API key for authentication.
    - retries (int): Number of retries for rate limit errors.
    - delay (int): Delay between retries in seconds.
    - **kwargs: Additional query parameters.

    Returns:
    dict: Parsed JSON response from the GET request or None on failure.
    """
    headers = {'x-cg-api-key': key}
    url = f"{base}{endpoint}"
    params = kwargs

    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            # handle rate limit error
            if resp.status_code == 429:
                print(f"Rate limit reached. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"HTTP error occurred: {e}")
                return None
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException) as e:
            # Handle other requests-related errors
            print(f"Error occurred: {e}")
            return None
        delay += delay
    print("Max retries exceeded.")
    return None


def load_data(coin_id, price_data):
    """
    Load extracted price data from API into STG table.

    Parameters:
    - coin_id (str): Coin being loaded
    - price_data (str): Extracted api price data

    Returns:
    None
    """
    drop_stg_result = execute_query(drop_stg_price_history)
    create_stg_result = execute_query(create_stg_price_history)
    price_asset_data = [{'unix_time': ts, 'price': price,
                         'asset': coin_id} for ts, price in price_data]
    insert_data_result = execute_query(
        load_stg_price_history, price_asset_data)


def transform_data(job_start_ts):
    """
    Execute query to transform raw data and load into SRC table. 
    Insert job_start_ts into SRC table for job run tracking and use by API.

    Parameters:
    - job_start_ts (datetime.datetime): timestamp when job was started

    Returns:
    None
    """
    formated_load_src_price_history = load_src_price_history.format(
        job_start_ts=job_start_ts)
    load_src_result = execute_query(formated_load_src_price_history)


def log_job_run(job_start_ts, status, error):
    """
    Log job meta data to log table in database

    Parameters:
    - job_start_ts (datetime.datetime): Coin being loaded
    - status (str): Status of job run (success or error)
    - error (str): Error message returned from. Is none if job runs succssfully

    Returns:
    None
    """
    job_data = [{'job_start_ts': job_start_ts,
                 'status': status, 'error': error}]
    load_job_data = execute_query(insert_elt_log, job_data)


def main(api_base_url, endpoints, api_key):
    """
    Run ELT flow:
        - Extract market cap data from Coingecko API
        - Extract top 10 coins in market cap from market cap data
        - For each coin in top 10:
            - Extract 7 day hourly price data for each coin in top 10 market cap list
            - Load price data to table in STG schema
            - Transform STG data and load price data to SRC table via SQL query
        -Log flow result to DB table

    Parameters:
    - api_base_url (str): Base url for API calls
    - endpoints (dict): Dictionary of Coingecko endpoints 
    - apikey (str): Coingecko API key

    Returns:
    None
    """
    job_start_ts = datetime.now()
    try:
        coin_data = extract_data(api_base_url,
                                 endpoints['coins_market_cap_desc'], api_key, vs_currency='usd', order='market_cap_desc')
        top_10 = coin_data[:10]
        coin_ids = [i['id'] for i in top_10]

        for coin_id in coin_ids:
            formatted_endpoint = endpoints['market_data'].format(id=coin_id)
            data = extract_data(
                api_base_url, formatted_endpoint, api_key, vs_currency='usd', days='7')
            price_data = data['prices']
            price_data_len = len(price_data)
            # remove last element in list which is not an hourly candle
            hourly_price_data = price_data[:price_data_len]
            load_data(coin_id, price_data)
            print(f"loaded data for {coin_id}")

            transform_data(job_start_ts)
        print("Data loaded to SRC")
        status = 'success'
        error = ''
    except Exception as e:
        error = e
        status = 'error'

    log_job_run(job_start_ts, status, error)


if __name__ == '__main__':
    main(coingecko_api_base, endpoints, COINGECKO_API_KEY)
