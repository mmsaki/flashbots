# flashbots

## Python implementation

Dependencies:

- [Web3.py Flashbots](https://github.com/flashbots/web3-flashbots)

Submit bundle transactions to flashbots relayer

```zsh
cd python
python simple_flashbot.py
```

Example of transactions:

```python
nonce = w3.eth.get_transaction_count(sender.address)

tx1: TxParams = {
    "to": fallback_mainnet,
    "value": 0,
    "gas": 42000,
    "data": "0x",
    "maxFeePerGas": Web3.toWei(50, "gwei"),
    "maxPriorityFeePerGas": Web3.toWei(2, "gwei"),
    "nonce": nonce,
    "chainId": CHAIN_ID,
    "type": 2,
}

tx1_signed = sender.sign_transaction(tx1)

tx2: TxParams = {
    "to": receiverAddress,
    "value": Web3.toWei(0.0005, "ether"),
    "gas": 21000,
    "maxFeePerGas": Web3.toWei(200, "gwei"),
    "maxPriorityFeePerGas": Web3.toWei(50, "gwei"),
    "nonce": nonce + 1,
    "chainId": CHAIN_ID,
    "type": 2,
}

bundle = [
    {"signed_transaction": tx1_signed.rawTransaction},
    {"signer": sender, "transaction": tx2},
]
```

## Typescript

Dependencies:

- Flasbots Bundle Provider `@flashbots/ethers-provider-bundle`

```zsh
cd src
ts-node index.ts
```
