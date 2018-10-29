import pdb, itertools, functools, hashlib, pprint, flask, flask_jsonrpc, toolz, json
from monero import wallet, daemon, transaction
from monero.backends import jsonrpc


__VERSION__ = (0, 0, 1)


app = flask.Flask(__name__)
rpc = flask_jsonrpc.JSONRPC(app, "/json_rpc", enable_web_browsable_api=True)


def wallet_factory():
    return wallet.Wallet(jsonrpc.JSONRPCWallet(
        port=18089,
        user="monerorpc",
        password="moneropassword",
    ))


def daemon_factory():
    return daemon.Daemon(jsonrpc.JSONRPCDaemon(
        host="107.150.28.134",
        port=12561,
    ))


def hash(value, size=16):
    return hashlib.md5(value.encode("utf8")).hexdigest()[:size]


@rpc.method("getinfo")
def getinfo():
    return {
        "name": "RPC Masq v{}.{}.{}".format(*__VERSION__),
        "plugins": ["monero", ],
    }


@rpc.method("listtransactions")
def listtransactions(account, limit=0):
    return [json.loads(json.dumps(_.__dict__, default=str)) for _ in wallet_factory()._backend.transfers_in(0, transaction.PaymentFilter(payment_id=hash(account)))]


@rpc.method("gettransaction")
def gettransaction(id):
    return {"error": "not implemented"}


def accountbalance(account):
    value = str(functools.reduce(
        lambda amount, el: amount + el.amount,
        wallet_factory()._backend.transfers_in(0, transaction.PaymentFilter(payment_id=hash(account))),
        0
    ))
    pprint.pprint(value)
    return value


def balance():
    return wallet_factory().balance()


@rpc.method("getbalance")
def getbalance(account, confirmations=1):
    return "%.12f" % balance() if account == "*" else accountbalance(account)


@rpc.method("getaccountaddress")
def getaccountaddress(account):
    """{
        "payment_id": hash(account),
        "integrated_address": str(wallet_factory()._backend.raw_request("make_integrated_address", {"payment_id": hash(account)})["integrated_address"])
    }"""
    return str(wallet_factory()._backend.raw_request("make_integrated_address", {"payment_id": hash(account)})["integrated_address"])


app.run(debug=True)
