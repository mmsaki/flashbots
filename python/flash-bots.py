from eth_account import Account
from web3 import Web3
from flashbots import Flashbots
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your Ethereum node URL
w3 = Web3(Web3.HTTPProvider(os.environ.get("QUICKNODE_PROVIDER")))

# Replace with your private key
private_key = "YOUR_PRIVATE_KEY"
account = Account.from_key(private_key)

# Replace with the Uniswap V2 pool contract address and ABI
uniswap_v2_pool_address = "UNISWAP_V2_POOL_CONTRACT_ADDRESS"
uniswap_v2_pool_abi = [...]

# Set up the Flashbots object
flashbots_provider = Flashbots(w3, account)

# Build your transaction
uniswap_v2_pool_contract = w3.eth.contract(
    address=uniswap_v2_pool_address, abi=uniswap_v2_pool_abi
)

# Replace with your desired transaction data
transaction_data = uniswap_v2_pool_contract.functions.swapExactTokensForTokens(
    ...  # Add your desired parameters here
).buildTransaction(
    {
        "from": account.address,
        "gas": 150000,
        "gasPrice": w3.toWei("2", "gwei"),
        "nonce": w3.eth.getTransactionCount(account.address),
    }
)

# Sign the transaction
signed_transaction = account.sign_transaction(transaction_data)

# Submit the transaction using Flashbots
response = flashbots_provider.send_transaction(signed_transaction.rawTransaction)
print("Transaction submitted:", response)
