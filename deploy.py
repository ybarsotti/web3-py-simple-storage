import json
import os

from dotenv import load_dotenv
from solcx import compile_standard, install_solc

from web3 import Web3

load_dotenv()

with open('./SimpleStorage.sol', 'r') as file:
    simple_storage_file = file.read()
install_solc("0.6.0")

compiled_sol = compile_standard({
    'language': 'Solidity',
    'sources': {"SimpleStorage.sol": {"content": simple_storage_file}},
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", 'evm.bytecode', "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.6.0")

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = \
compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to ganache
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/f1d0cb757fdb4307903b41d76ba0f8e1"))
chain_id = 4
my_address = "0x15328f2c40d44aAF44c1a9b8D0c0736225526b2b"
private_key = os.getenv("PRIVATE_KEY")

# Create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build transaction
# 2. Sign a transaction
# 3. Send a transction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce})
signed_txn = w3.eth.account.sign_transaction(transaction,
                                             private_key=private_key)

# send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed contract!")

# Working with the contract, you always need
# Contract address
# Contract abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value
# Transaction -> Actually make a state change

# Initial value of favorite number
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce + 1,
})

signed_store_txn = w3.eth.account.sign_transaction(store_transaction,
                                                    private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")