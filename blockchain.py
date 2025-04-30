import streamlit as st
from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

# Set page configuration
st.set_page_config(page_title="Mobile Recharge Ledger", layout="centered")

# Environment variables (replace these or use secrets for deployment)
INFURA_URL = "https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID"  # Replace with your Infura Project ID
PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # Replace with your private key (Use secrets in Streamlit Cloud)
PUBLIC_ADDRESS = "YOUR_WALLET_ADDRESS"  # Replace with your wallet address

# Compile Smart Contract
with open("MobileRechargeLedger.sol", "r") as file:
    contract_source = file.read()

install_solc("0.8.0")
compiled = compile_standard({
    "language": "Solidity",
    "sources": {"MobileRechargeLedger.sol": {"content": contract_source}},
    "settings": {
        "outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}
    }
}, solc_version="0.8.0")

# Extract ABI and Bytecode from compiled contract
abi = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["abi"]
bytecode = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["evm"]["bytecode"]["object"]

# Connect to Ethereum (Goerli Testnet) via Infura
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Ensure connected to Ethereum network
if not w3.is_connected():
    st.error("Failed to connect to Ethereum. Please check your Infura URL and network.")
else:
    st.sidebar.success("Connected to Ethereum Goerli ✅")

# Deploy the contract if not deployed yet
@st.cache_resource
def deploy_contract():
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Set up transaction for contract deployment
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
    txn = contract.constructor().build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 6721975,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce
    })
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress

# Deploy contract and get contract address
contract_address = deploy_contract()
contract = w3.eth.contract(address=contract_address, abi=abi)

# Streamlit app UI
st.title("📲 Mobile Recharge Ledger on Blockchain")

menu = st.sidebar.selectbox("Select Action", ["Recharge", "View Recharge History"])

if menu == "Recharge":
    mobile = st.text_input("Enter Mobile Number")
    amount = st.number_input("Recharge Amount", min_value=1)

    if st.button("🔌 Recharge"):
        if mobile and amount:
            try:
                nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
                txn = contract.functions.recharge(mobile, int(amount)).build_transaction({
                    'from': PUBLIC_ADDRESS,
                    'gas': 2000000,
                    'gasPrice': w3.to_wei('20', 'gwei'),
                    'nonce': nonce
                })
                signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                w3.eth.wait_for_transaction_receipt(tx_hash)
                st.success(f"Recharge successful for {mobile} and stored on blockchain!")
            except Exception as e:
                st.error(f"Error while recharging: {str(e)}")
        else:
            st.warning("Please enter both mobile number and amount.")

elif menu == "View Recharge History":
    mobile = st.text_input("Enter Mobile Number to View History")
    if st.button("🔍 View Records"):
        if mobile:
            try:
                records = contract.functions.getRechargeRecordsByMobile(mobile).call()
                if records:
                    for record in records:
                        st.write({
                            "Amount": record[0],
                            "Timestamp": record[1],
                            "Mobile": record[2],
                            "Operator": record[3]
                        })
                else:
                    st.info("No recharge history found for this mobile number.")
            except Exception as e:
                st.error(f"Error fetching records: {str(e)}")
        else:
            st.warning("Please enter a mobile number.")
web3==5.24.0
py-solc-x






