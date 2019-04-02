import pdb, itertools, functools, hashlib, pprint, flask, flask_jsonrpc, toolz, json, logging, coloredlogs, os
import api
import pprint


logger = logging.getLogger(__name__)
coloredlogs.install(fmt="%(asctime)-15s %(message)s", datefmt="%m/%d %H:%M:%S")


def main():
    state = api.get_state()
    payments = api.get_bulk_payments(min_block_height=state["height"])
    for payment in payments:
        api.store_payment(payment)
        state["height"] = payment["block_height"]
        api.set_state(state)
    logger.info("Height is %s", state["height"])


main()
