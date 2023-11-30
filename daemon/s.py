from requests import post, get
from json import loads, dumps
import time
import os


def link(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def get_tokens():
    dic = loads(get("https://api.keeper-wallet.app/api/v1/assets").text)
    dic = {n["id"]: n["ticker"] for n in dic}
    dic.update({
        "rZMQ6g31Lr7sPAaAoYc4U2PHCVauTuKUSzUbJtUyPZN": "WX USDC-USDT",
        "6bZbRmou7M7wXBunMXQnZ4Rm66HxZF3KfMEiFwk3wmnA": "PZ 5pool",
        "XjdJKWtPYCz585QB7LnxDP76UGRukazedDubUx9DHQH": "PZ WEB"
    })
    return dic


def get_oracle_prices():
    data = loads(get("https://nodes-puzzle.wavesnodes.com/addresses/data/3P8d1E1BLKoD52y3bQJ1bDTd2TD1gpaLn9t").text)
    dic = {}
    for n in data:
        if "_twap5B" in n["key"]:
            dic[n["key"].split("_")[0]] = n["value"]
    return dic


def get_portfolio_from_keeper(address):
    return loads(post("https://api.keeper-wallet.app/api/v1/portfolio",
                      json={"addresses": [address]}).text)


def get_balances(address):
    return loads(get("https://nodes-keeper.wavesnodes.com/assets/balance/"+address).text)["balances"]


def get_token_balance(address, token):
    balances = get_balances(address)
    try:
        return [n["balance"] for n in balances if n["assetId"] == token][0]
    except IndexError:
        return 0


def find_route(s="Ajso6nTTjptu2UHLx6hfSXVtHFtRBJCkKYd5SAyj7zf5,100000000,34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ"):
    asset0, amount0, asset1 = s.split(",")
    try:
        data = loads(get("https://waves.puzzle-aggr-api.com/aggregator/calc?token0={}&token1={}&amountIn={}&routes=1".format(asset0, asset1, str(amount0)), headers={'Authorization': 'Bearer IIqbbwzJLdDKiOWvVTwaBEVSXzAjtd'}).text)
    except Exception:
        raise "cannot find the route"
    return data
