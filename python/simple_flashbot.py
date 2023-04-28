"""
Minimal viable example of flashbots usage with dynamic fee transactions.
Sends a bundle of two transactions which transfer some ETH into a random account.

Environment Variables:
- ETH_SENDER_KEY: Private key of account which will send the ETH.
- ETH_SIGNER_KEY: Private key of account which will sign the bundle. 
    - This account is only used for reputation on flashbots and should be empty.
- PROVIDER_URL: HTTP JSON-RPC Ethereum provider URL.
"""
import warnings
from eth_account.signers.local import LocalAccount
from uuid import uuid4
from web3 import Web3, HTTPProvider
from flashbots import flashbot
from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound
from web3.types import TxParams
from eth_account.account import Account
import os
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# change this to `False` if you want to use mainnet
USE_GOERLI = False
CHAIN_ID = 5 if USE_GOERLI else 1

tx_data = "0xd0e30db0"
weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
tx_value = Web3.toWei(0.0004, "ether")
to_address = "0xEf1c6E67703c7BD7107eed8303Fbe6EC2554BF6B"
tate_data = "0x3593564c000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000644b57d300000000000000000000000000000000000000000000000000000000000000020b080000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000016bcc41e900000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000016bcc41e90000000000000000000000000000000000000000000000836a5f21a0d1a5ad5e3f6500000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000a589d8868607b8d79ee4288ce192796051263b64"

fallback_mainnet = os.environ.get("FALLBACK_MAINNET")


def env(key: str) -> str:
    return os.environ.get(key)


def main() -> None:
    # account to send the transfer and sign transactions
    sender: LocalAccount = Account.from_key(env("ETH_SENDER_KEY"))
    # account to receive the transfer
    receiverAddress: str = to_address
    # account to sign bundles & establish flashbots reputation
    # NOTE: this account should not store funds
    signer: LocalAccount = Account.from_key(env("ETH_SIGNER_KEY"))
    w3 = None
    if USE_GOERLI:
        w3 = Web3(HTTPProvider(env("ALCHEMY_PROVIDER")))
        flashbot(w3, signer, "https://relay-goerli.flashbots.net")
    else:
        w3 = Web3(HTTPProvider(env("ALCHEMY_MAINNET")))
        flashbot(w3, signer, "https://relay.flashbots.net")

    print(f"Sender address: {sender.address}")
    print(f"Receiver address: {receiverAddress}")
    print(
        f"Sender account balance: {Web3.fromWei(w3.eth.get_balance(sender.address), 'ether')} ETH"
    )
    print(
        f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiverAddress), 'ether')} ETH"
    )

    # bundle two EIP-1559 (type 2) transactions, pre-sign one of them
    # NOTE: chainId is necessary for all EIP-1559 txns
    # NOTE: nonce is required for signed txns

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

    # keep trying to send bundle until it gets mined
    while True:
        block = w3.eth.block_number
        print(f"Simulating on block {block}")
        # simulate bundle on current block
        try:
            w3.flashbots.simulate(bundle, block)
            print("Simulation successful.")
        except Exception as e:
            print("Simulation error", e)
            return

        # send bundle targeting next block
        print(f"Sending bundle targeting block {block+1}")
        replacement_uuid = str(uuid4())
        print(f"replacementUuid {replacement_uuid}")
        send_result = w3.flashbots.send_bundle(
            bundle,
            target_block_number=block + 1,
            opts={"replacementUuid": replacement_uuid},
        )
        print("bundleHash", w3.toHex(send_result.bundle_hash()))

        stats_v1 = w3.flashbots.get_bundle_stats(
            w3.toHex(send_result.bundle_hash()), block
        )
        print("bundleStats v1", stats_v1)

        stats_v2 = w3.flashbots.get_bundle_stats_v2(
            w3.toHex(send_result.bundle_hash()), block
        )
        print("bundleStats v2", stats_v2)

        send_result.wait()
        try:
            receipts = send_result.receipts()
            print(f"\nBundle was mined in block {receipts[0].blockNumber}\a")
            break
        except TransactionNotFound:
            print(f"Bundle not found in block {block+1}")
            # essentially a no-op but it shows that the function works
            cancel_res = w3.flashbots.cancel_bundles(replacement_uuid)
            print(f"canceled {cancel_res}")

    print(
        f"Sender account balance: {Web3.fromWei(w3.eth.get_balance(sender.address), 'ether')} ETH"
    )
    print(
        f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiverAddress), 'ether')} ETH"
    )


if __name__ == "__main__":
    main()
