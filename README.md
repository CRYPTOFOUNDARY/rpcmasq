# RPCMASQ #1

Transparent Bitcoin RPC API to Monero RPC API proxy server.

## The idea

A lot of projects including exchanges already works with Bitcoin RPC API but when you want to add new coin engine for example Monero or Ethereum you need to develop new integration and change every peace of code using RPC. It may be difficult specially when target project source is not too good or when project is too complex and large.

Another option is to hide real implementation (Monero RPC) by already well known Bitcoin RPC API. Just translate calls from one API to another internally and cache needed info to serve request despite the difference of implementations.

## Little example

There is `getaccountaddress` RPC method in Bitcoin API. It accepts `account` as single parameter. And there is `make_integrated_address` RPC method in Monero API and it accepts `payment_id` as single parameter. We can hash `account` into `payment_id` and return `integrated_address` like this is Bitcoin fork API but internally query Monero Daemon to generate it from Monero Primary address and `payment_id` hashed from `account` (as `payment_id` is 16-letters and `account` may be random).

## Implemented translations

```
    RPC method     Description
    ~~~~~~~~~~     ~~~~~~~~~~~
    getinfo                      ->  RPCMASQ info
    getaccountaddress(account)   ->  make_integrated_address(payment_id(account))
    getbalance([account], [cnf]) -> get_balance([payment_id(account)])
    gettransaction(id)           -> /get_transactions([id])
    listtransactions(account)    -> transfers_in(payment_id(account))
```

## Online demo

At `ForkFork` Exchange all Monero forks are connected through `RPCMASQ`:

https://fork.pw

## Copyrights

&copy; 2018 0xA01 and CRYPTOFOUNDARY Contributors

