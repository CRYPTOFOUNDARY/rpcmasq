import os, datetime, time, pprint, pymongo, hashlib, functools
from flakechain import wallet, daemon, transaction
from flakechain.backends import jsonrpc
from flakechain.numbers import from_atomic


__VERSION__ = (4, 0, 1)
__DEFAULT_DATABASE__ = "flakechain"
__DEFAULT_STATE__ = {
    "_id": None, # not persisted yet
    "height": 0
}


def to_payment_id(value, size=16):
    return hashlib.md5(value.encode("utf8")).hexdigest()[:size]


def wallet_factory():
    return wallet.Wallet(jsonrpc.JSONRPCWallet(
        port=int(os.environ["MONERO_WALLET_PORT"]),     
        user=os.environ["MONERO_WALLET_USER"],
        password=os.environ["MONERO_WALLET_PASS"],
    ))


def daemon_factory():
    return daemon.Daemon(jsonrpc.JSONRPCDaemon(
        host=os.environ["MONERO_DAEMON_HOST"],
        port=int(os.environ["MONERO_DAEMON_PORT"]),
    ))


def storage_factory():
    return pymongo.MongoClient(host="127.0.0.1")[
        os.environ.get("STORAGE_DATABASE", __DEFAULT_DATABASE__)
    ]


def get_state():
    return storage_factory().state.find_one() or __DEFAULT_STATE__


def set_state(state):
    return storage_factory().state.update_one({}, {"$set": state}, True)


def get_bulk_payments(min_block_height=0):
    return wallet_factory()._backend.raw_request(
        "get_bulk_payments",
        {
            "min_block_height": min_block_height
        }
    ).get("payments", [])


def store_payment(payment):
    storage_factory().payments.update_one(
        {"tx_hash": payment["tx_hash"]},
        {"$set": dict(
            created_at=datetime.datetime.utcnow(),
            **payment
        )},
        upsert=True
    )


def get_account_address(account):
    return str(
        wallet_factory()
            ._backend
            .raw_request(
                "make_integrated_address",
                {"payment_id": to_payment_id(account)})["integrated_address"]
    )


def get_total_balance():
    return float(wallet_factory().balance())


def get_account_balance(account):
    return float(functools.reduce(
        lambda amount, el: amount + el.amount,
        wallet_factory()._backend.transfers_in(0, transaction.PaymentFilter(payment_id=to_payment_id(account))),
        0
    ))


def tx(data):
    return {
        "amount": float(from_atomic(data["amount"])),
        "confirmations": wallet_factory().height() - data["block_height"],
        "txid": data["tx_hash"],
        "time": int(time.mktime(data["created_at"].timetuple())),
        "timereceived": int(time.mktime(data["created_at"].timetuple()))
    }


def account_tx(account, address, type, data):
    return {
        "account": account,
        "address": address, # data["address"],
        "category": type,
        "amount": float(from_atomic(data["amount"])),
        "confirmations": wallet_factory().height() - data["block_height"],
        "txid": data["tx_hash"],           
        "time": int(time.mktime(data["created_at"].timetuple())),
        "timereceived": int(time.mktime(data["created_at"].timetuple()))
    }


def get_transactions(account, limit=0):
    return storage_factory().payments.find(
        {"payment_id": "{:<064s}".format(to_payment_id(account))}
    )
