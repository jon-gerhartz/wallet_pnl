from dotenv import load_dotenv
import os
import pandas as pd
import streamlit as st
import requests

load_dotenv()


def gen_viz(wallet_address):
    API_BASE_URL = os.getenv("API_BASE_URL")
    ENDPOINT = f'/get-pnl?wallet_address={wallet_address}'
    API_PORT = os.getenv("API_PORT")
    url = API_BASE_URL + ':' + API_PORT + ENDPOINT

    data = requests.get(url).json()['data']

    for coin in data:
        st.header(coin)
        df = pd.DataFrame.from_dict(data[coin])
        df['hour_of'] = pd.to_datetime(
            df['hourly_ts'], format='%a, %d %b %Y %H:%M:%S GMT', utc=True)
        sorted = df[['hour_of', 'balance_actual', 'price',
                     'usd_value', 'PnL']].sort_values(by='hour_of')

        st.subheader('Data')
        st.dataframe(sorted, hide_index=True)

        st.subheader('Chart')
        st.line_chart(sorted, x='hour_of')
        st.divider()


st.title('Crypto Wallet PnL Machine')
st.divider()
wallet_address = st.text_input(
    'Enter your wallet address to see PnL data', 'Your wallet address...')

if wallet_address:
    with st.spinner("Loading wallet data..."):
        gen_viz(wallet_address)
