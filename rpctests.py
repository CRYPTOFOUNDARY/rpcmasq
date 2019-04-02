import pprint
from flask_jsonrpc.proxy import ServiceProxy


proxy = ServiceProxy("http://127.0.0.1:5000/")
pprint.pprint(
    proxy.move(
        "d4f3802f8173a978f6f8abf062187806",
        "1da7847d5c8fc95ef8d2bcc25301e425",
        10
    )
)
