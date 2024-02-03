from datetime import datetime, timedelta
from db.connect import execute_pd
from db.queries import get_src_prices
from dotenv import load_dotenv
import math
import os
import pandas as pd
import requests
import time

load_dotenv()

ALLIUM_API_KEY = os.getenv('ALLIUM_API_KEY')

allium_query_run_api_url = 'https://api.allium.so/api/v1/explorer/queries/UWHFUe3BPTFpd7EDVIiI/run-async'
allium_status_api_url = 'https://api.allium.so/api/v1/explorer/query-runs/{run_id}/status'
allium_results_api_url = 'https://api.allium.so/api/v1/explorer/query-runs/{run_id}/results?f=json'


def post_query(query_url, wallet_address, headers):
    """
    Makes post request to Allium run query api.
    Runs saved SQL query to last 1000 balance records from wallet.

    Parameters:
    - query_url (str): Query run api endpoint full url.
    - wallet_address (str): Wallet address to return balance records from.
    - headers (dict): Headers dictionary to pass api_key in post request.

    Returns:
    Str: Run_id of the query that was run
    """
    params = {'address': wallet_address}
    run_config = {'limit': '100'}

    resp = requests.post(
        query_url, json={'parameters': params, 'run_config': run_config}, headers=headers)

    run_id = resp.json()['run_id']
    return run_id


def wait_for_status(run_id, status_url, headers, check_interval=1, timeout=1200):
    """
    Makes get request to Allium query status api. Checks status of query at 
    set check_interval while run time is less than timeout. 
    Prints status updates while status is not a final status.
    When a final status is received, the while loop is broken.

    Parameters:
    - run_id (str): Run_id of query that was run in post_query function.
    - status_url (str): Full url of Allium query_status endpoint.
    - headers (dict): Headers dictionary to pass api_key in post request.
    - check_interval (int): Optional argument, default 1. Time to sleep in between status checks.
    - timeout (int): Optional argument, default 1200. Time to wait for query to reach final status.

    Returns:
    None
    """
    formatted_status_url = status_url.format(run_id=run_id)
    start = time.time()
    while time.time() < start + timeout:
        resp = requests.get(formatted_status_url, headers=headers)
        status = resp.json()
        if status not in ['created', 'queued', 'running']:
            print(f"Query finished running. Status: {status}")
            break
        else:
            print(
                f"Query status: {status}. Rechecking in {check_interval} second(s).")
            time.sleep(check_interval)

    if time.time() > start + timeout:
        print("Query timed out before reaching final status")


def get_results(run_id, results_url, headers):
    """
    Makes get request to Allium query results api. Returns results in json format.

    Parameters:
    - run_id (str): Run_id of query that was run in post_query function.
    - results_url (str): Full url of Allium query results endpoint.
    - headers (dict): Headers dictionary to pass api_key in post request.

    Returns:
    JSON response: Results_data, response from Allium query results api.
    """
    formatted_results_url = results_url.format(run_id=run_id)
    results_resp = requests.get(
        formatted_results_url,  headers=headers
    )
    results_data = results_resp.json()
    return results_data


def get_wallet_data(wallet_address):
    """
    Runs above functions in flow to get results of query run.

    Parameters:
    - wallet_address (str): wallet address to calculate PNL for

    Returns:
    List: Data array from Allium query results api JSON response.
    """
    headers = {
        'X-API-Key': ALLIUM_API_KEY
    }
    try:
        run_id = post_query(allium_query_run_api_url, wallet_address, headers)
        wait_for_status(run_id, allium_status_api_url, headers)
        results_data = get_results(run_id, allium_results_api_url, headers)
        print(results_data)
        return results_data['data']
    except Exception as e:
        print(f"Failed to get wallet data: {e}")


def get_prices(asset):
    """
    Run SQL query and return pandas dataframe with results.
    Gets most recent job run of hourly coin price data from last 7 days.

    Parameters:
    - asset (str): Asset to return prices for

    Returns:
    Dataframe: Price data dataframe from database
    """
    formatted_get_src_prices = get_src_prices.format(asset=asset)
    prices_df = execute_pd(formatted_get_src_prices)
    return prices_df


def get_pnl(wallet_balance_df_all, asset):
    """
    Use pandas to merge together the wallet balance data, a range of hourly timestamps from
    now - 7 days to now and the price data from the database. 
    Calculate running balance for entire time range. Calulate running USD value by combining 
    running balance and price. Calculate PnL by comparing start USD value of wallet to 
    running USD value of wallet.

    Parameters:
    - asset (str): Asset to calculate PnL for.

    Returns:
    Dict: PnL data for the last week - any data missing since last run of price data pipeline.
    """
    wallet_balance_df = wallet_balance_df_all[wallet_balance_df_all['token_id'] == asset]

    # reformat timestamp columns and create hourly timestamps
    wallet_balance_df['timestamp_dt'] = pd.to_datetime(
        wallet_balance_df['block_timestamp'], format='%Y-%m-%dT%H:%M:%S')
    wallet_balance_df['hourly_ts'] = pd.to_datetime(
        wallet_balance_df['timestamp_dt'].dt.strftime("%Y-%m-%d %H:00:00"))

    # create list of hours between now and now - 7 days
    dt_now = datetime.now().replace(minute=0, second=0, microsecond=0)
    dt_now_minus_7_days = dt_now - timedelta(days=7)
    hour_range = pd.date_range(dt_now_minus_7_days, dt_now, freq='H')

    # get the starting balance for the hour range df
    min_hour = hour_range.min()
    max_wallet_balance_before_hour_range = wallet_balance_df[
        wallet_balance_df['timestamp_dt'] <= min_hour]['timestamp_dt'].max()
    last_balance_before_hour_range = wallet_balance_df[
        wallet_balance_df['timestamp_dt'] == max_wallet_balance_before_hour_range]
    last_balance_before_hour_range['join_col'] = min_hour

    # create df from hourly range list, merge hourly range df and starting balance
    hourly_range_df = pd.DataFrame(hour_range, columns=['hourly_ts'])
    merged_start_bal = hourly_range_df.merge(
        last_balance_before_hour_range[['join_col', 'balance']], how='left', left_on='hourly_ts', right_on='join_col')

    # merge wallet balance data with hourly range df
    merged_balances = merged_start_bal.merge(
        wallet_balance_df, how='left', on='hourly_ts')

    # calculate running balance, fill in blank balance rows
    for i, v in merged_balances.fillna(0).iterrows():
        balance_null = v['balance_x'] == 0

        if balance_null:
            merged_balances.loc[i,
                                'balance_x'] = merged_balances.loc[i-1, 'balance_x']

        if v['balance_y'] != 0:
            current_balance = merged_balances.loc[i, 'balance_y']
            merged_balances.loc[i, 'balance_x'] = current_balance
        else:
            current_balance = merged_balances.loc[i, 'balance_x']

        merged_balances.loc[i, 'balance_actual'] = current_balance

    # merge running balances with prices
    prices_df = get_prices(asset)
    merged_balances['token_id'] = asset
    merged_prices = merged_balances.merge(
        prices_df, how='left', on=['hourly_ts', 'token_id'])

    # calculate usd_value and pnl
    merged_prices['usd_value'] = merged_prices['balance_actual'] * \
        merged_prices['price']
    start_value = merged_prices['usd_value'][0]
    merged_prices['PnL'] = merged_prices['usd_value'] - start_value

    # clean up df, convert to dict to return
    clean_merged_prices = merged_prices[[
        'hourly_ts', 'balance_actual', 'price', 'usd_value', 'PnL']]
    clean_merged_prices_dict = clean_merged_prices.to_dict(orient='records')
    return clean_merged_prices_dict


def run_pnl_flow(wallet_address):
    """
    Call get_wallet_data function to get data from Allium api. 
    Check if data is returned from Allium, raise error for invalid/unsupported wallet,
    Handle wallets with several coin balances.

    Parameters:
    - wallet_address (str): Wallet address to calculate PnL for

    Returns:
    Dict:
        PnL data for all supported coins in the wallet. 
        All data for the last week minus any data missing since last run of price data pipeline.
    """
    wallet_balance_data = get_wallet_data(wallet_address)
    wallet_balance_df_all = pd.DataFrame.from_dict(wallet_balance_data)
    if len(wallet_balance_df_all) == 0:
        raise ValueError("Invalid or unsupported wallet address")

    else:
        assets = wallet_balance_df_all['token_id'].unique()
        all_assets_pnl = {}
        for asset in assets:
            try:
                asset_pnl_data = get_pnl(wallet_balance_df_all, asset)
                all_assets_pnl[asset] = asset_pnl_data
            except Exception as e:
                print(f'Missing data for {asset}')

        return all_assets_pnl
