import pdb, itertools, functools, hashlib, pprint, flask, flask_jsonrpc, toolz, json, logging, coloredlogs, os, api


logger = logging.getLogger(__name__)
coloredlogs.install(fmt="%(asctime)-15s %(message)s", datefmt="%m/%d %H:%M:%S")


# def test_get_transactions(payment_id):
#     api.get_transactions(payment_id)

def test_get_transactions(account):
    # pprint.pprint(list(api.get_transactions(account)))
    for tx in api.get_transactions(account):
        print(tx["tx_hash"])


def test_get_account_address(account):
    print(api.get_account_address(account))


def test_tx(account):
    pprint.pprint(
        api.tx(
            account,
            api.get_account_address(account),
            "receive",
            api.get_transactions(account)[0]
        )
    )


# test_get_transactions("d4f3802f8173a978f6f8abf062187806") #"9acb03eff24688d7")
# test_get_account_address("d4f3802f8173a978f6f8abf062187806")
test_tx("d4f3802f8173a978f6f8abf062187806")