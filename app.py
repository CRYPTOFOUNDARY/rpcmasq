import pdb, itertools, functools, hashlib, pprint, flask, flask_jsonrpc, toolz, json, logging, coloredlogs, os, api


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coloredlogs.install(fmt="%(asctime)-15s %(message)s", datefmt="%m/%d %H:%M:%S", logger=logger)
app = flask.Flask(__name__)
rpc = flask_jsonrpc.JSONRPC(app, "/", enable_web_browsable_api=True)


@rpc.method("getinfo")
def getinfo():
    logger.info("info")
    logger.warning("warn")
    logger.error("err")
    return {
        "name": "RPC Masq v{}.{}.{}".format(*api.__VERSION__),
        "plugins": ["monero", ],
    }


@rpc.method("listtransactions")
def listtransactions(account, limit=0):
    return [
        api.account_tx(account, api.get_account_address(account), "receive", data)
        for data in api.get_transactions(account)
    ]


@rpc.method("move")
def move(fromaccount, toaccount, amount, minconf=1, comment=None):
    logger.warning("@move")
    payments = api.storage_factory().payments
    from_payments = list(
        payments.find(
            {"payment_id": "{:<064s}".format(
                api.to_payment_id(fromaccount)
            )}
        )
    )
    move_payments = []
    change = float(amount)

    while change > 0 and from_payments:
        move_payments.append(from_payments.pop())
        change -= float(api.from_atomic(move_payments[-1]["amount"]))
    logger.error("Change(%f, %s)", change, type(change))
    if change == 0.0:
        logger.error("@@move")
        for payment in move_payments:
            logger.info(pprint.pformat(payment))
            api.storage_factory().payments.update_one(
                {"_id": payment["_id"]},
                {
                    "$set": {
                        "payment_id": "{:<064s}".format(
                            api.to_payment_id(toaccount)
                        )
                    }
                }
            )
        return "success"

    return None


@rpc.method("gettransaction")
def gettransaction(tx_hash):
    return api.tx(
        api.storage_factory().payments.find_one({"tx_hash": tx_hash})
    )


@rpc.method("getbalance")
def getbalance(account="*", confirmations=1):
    return api.get_total_balance() if account == "*" else api.get_account_balance(account)


@rpc.method("getaccountaddress")
def getaccountaddress(account):
    return api.get_account_address(account)


logger.info("Starting rpcMASQ v{}.{}.{}".format(*api.__VERSION__))
app.run(debug=True)
