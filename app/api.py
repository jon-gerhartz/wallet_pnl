from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
import os
from lib import run_pnl_flow

load_dotenv()

# load env vars
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
API_PORT = os.getenv("API_PORT")

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


@app.route('/get-pnl', methods=['GET'])
def serve_pnl():
    wallet_address = request.args.get('wallet_address')
    data = {}

    if not wallet_address:
        message = 'Missing required parameter: asset'
        status_code = 422
    else:
        try:
            data = run_pnl_flow(wallet_address)
            message = 'Success'
            status_code = 200
        except ValueError as e:
            message = str(e)
            status_code = 400
        except Exception as e:
            message = 'Internal server error'
            status_code = 500
            print(e)

    resp_data = {'data': data, 'message': message}
    response = make_response(jsonify(resp_data), status_code)
    return response


if __name__ == '__main__':
    app.run(debug=True, port=API_PORT)
