import time
from datetime import datetime
import daemon

tokens = daemon.s.get_tokens()


def prettify_number(n, decimals=2):
    n = int(n * 10 ** decimals) / 10 ** decimals
    n = str(n).split(".")
    if len(n[0]) > 3:
        n[0] = n[0][:-3] + "," + n[0][-3:]
    if len(n[-1]) == decimals-1:
        n[-1] += "0"
    return ".".join(n)


def prettify_apr(n):
    return prettify_number(n * 100) + "%"


def get_pretty_apy(apr):
    apy = (1 + apr / 365) ** 365 - 1
    return prettify_apr(apy)


def pretty_time(timestamp):
    t = datetime.fromtimestamp(int(timestamp / 1000))
    return t.strftime("%d.%m.%Y %H:%M")


def pretty_address(address):
    return address[:6] + "..." + address[-4:]


def pretty_balances(dic):
    li = []
    for token in dic:
        li.append(prettify_number(dic[token], 4) + " " + tokens[token])
    return ", ".join(li)
