from requests import post, get
from json import loads, dumps
import time
import os
import daemon.s as s

DECIMALS = {
    "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p": 1000000,
    "34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ": 1000000,
    "6XtHjpXbs9RRJP2Sr9GUyVqzACcby9TkThHXnjVC5CDJ": 1000000,
    "AP4Cb5xLYGH6ZigHreCZHoXpQTWDkPsG2BHqfDUx6taJ": 1000000
}

ROME = "AP4Cb5xLYGH6ZigHreCZHoXpQTWDkPsG2BHqfDUx6taJ"
USDT = "9wc3LXNA4TEBsXyKtoLE9mrbDD7WMHXvXrCjZvabLAsi"

distributorAddress = "3PGVUFU9UvRAJ15RHrfKD9PNX83tiguj9tp"
marketAddress = "3P8Df2b7ywHtLBHBe8PBVQYd3A5MdEEJAou"


def get_rome_supply():
    issued = loads(get("https://nodes.wavesnodes.com/assets/details/"+ROME).text)["quantity"]
    out_of_circulation = s.get_token_balance(marketAddress, ROME)

    return {
        "issued": issued,
        "circ": issued - out_of_circulation
    }


def get_rome_price():
    buy_price = 100000000 / s.find_route(ROME+",100000000,"+USDT)["estimatedOut"]
    sell_price = s.find_route(USDT+",100000000,"+ROME)["estimatedOut"] / 100000000
    return {
        "buy100": buy_price,
        "sell100": sell_price
    }


def get_rome_payouts():
    txs_short = loads(get("https://api.wavesplatform.com/v0/transactions/invoke-script?sender={}&dapp={}&function=distribute&sort=desc&limit=30".format(distributorAddress, distributorAddress)).text)["data"]
    tx_ids = [tx["data"]["id"] for tx in txs_short]
    txs = loads(post("https://nodes.wavesnodes.com/transactions/info", json={"ids": tx_ids}).text)

    data = []
    for n in range(len(txs)-1):
        entries = txs[n]["stateChanges"]["data"]
        if "currentRome" not in entries[-1]["key"]:
            entries.append({"key": "stats_distr8_currentRome", "value": 7503383385})

        height = entries[-3]["value"]
        amount = entries[-2]["value"]
        totalRome = entries[-1]["value"]

        heightDiff = height - [n for n in txs[n+1]["stateChanges"]["data"] if "lastDistribution" in n["key"]][0]["value"]
        apr = (525600 / heightDiff) * (amount / totalRome)

        data.append({
            "height": height,
            "timestamp": txs[n]["timestamp"],
            "amount": amount,
            "totalRome": totalRome,
            "apr": apr,
            "id": txs[n]["id"]
        })

    return data


def get_rome_minters():
    # TODO: account sRate and bRate in Puzzle Lend

    state = loads(get("https://nodes.wavesnodes.com/addresses/data/"+marketAddress).text)
    dic = {n["key"]: n["value"] for n in state}

    minters_dic = {}
    for key in dic:
        if "borrowed_"+ROME in key:
            if dic[key] > 1:
                minters_dic[key.split("_")[0]] = {"minted": int(dic[key] * dic[ROME+"_bRate"] / 1e16), "supplied": {}, "collateral": 0}

    oracle_prices = s.get_oracle_prices()
    for key in dic:
        address = key.split("_")[0]

        if "supplied" in key and address in minters_dic and not ROME in key:
            if dic[key] > 1:
                token = key.split("_")[-1]
                amount = int(dic[key] * dic[token+"_sRate"] / 1e16)

                minters_dic[address]["supplied"][token] = amount / 100000000
                minters_dic[address]["collateral"] += oracle_prices[token] * amount / 1e14

    minters_li = []
    for minter in minters_dic:
        item = minters_dic[minter]
        item["address"] = minter
        minters_li.append(item)
    minters_li.sort(key = lambda x: -x["minted"])

    return {"addresses": minters_li[1:], "total": minters_li[0]}


def update_rome_data():
    print("updating ROME stats")

    results = {
        "constants": {
            "collateral": [
                {"assetId": "rZMQ6g31Lr7sPAaAoYc4U2PHCVauTuKUSzUbJtUyPZN", "ticker": "WX USDC-USDT", "url": "https://wx.network/liquiditypools/pools/USDC-ERC20_USDT-ERC20/deposit"},
                {"assetId": "XjdJKWtPYCz585QB7LnxDP76UGRukazedDubUx9DHQH", "ticker": "PZ WEB", "url": "https://puzzleswap.org/pools/web/invest"},
                {"assetId": "6bZbRmou7M7wXBunMXQnZ4Rm66HxZF3KfMEiFwk3wmnA", "ticker": "PZ 5pool", "url": "https://puzzleswap.org/pools/5pool/invest"}
            ],
            "contracts": [
                {"address": "3PGVUFU9UvRAJ15RHrfKD9PNX83tiguj9tp", "name": "Rewards Distributor"},
                {"address": "3P8Df2b7ywHtLBHBe8PBVQYd3A5MdEEJAou", "name": "ROME Market"},
                {"address": "3PQD3xaW4Up2m7e2ZZCfyQs2qGXct65Le2Y", "name": "ROME Issuer"},
                {"address": "3P8d1E1BLKoD52y3bQJ1bDTd2TD1gpaLn9t", "name": "Puzzle Oracle"},
            ]
        },
        "stats": {
            "supply": get_rome_supply(),
            "price": {
                "protocol": 1,
                "market": get_rome_price()
            },
            "payouts": get_rome_payouts(),
            "minters": get_rome_minters(),
            "last_update": time.time() * 1000
        }
    }

    with open(s.link("latest_data.json"), "w") as f:
        f.write(dumps(results))
    return results


def get_last_stats():
    with open(s.link("latest_data.json")) as f:
        data = loads(f.read())
    return data
