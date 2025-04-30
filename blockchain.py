import streamlit as st
from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

st.set_page_config(page_title="Mobile Recharge Ledger", layout="centered")

# Environment Variables (replace or load securely)
INFURA_URL = "https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID"
PRIVATE_KEY = "YOUR_PRIVATE_KEY"
PUBLIC_ADDRESS = "YOUR_WALLET_ADDRESS"

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

abi = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["abi"]
bytecode = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["evm"]["bytecode"]["object"]

# Connect to Infura
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
st.sidebar.success("Connected to Ethereum Goerli ✅" if w3.is_connected() else "❌ Not Connected")

# Deploy contract if not already deployed
@st.cache_resource
def deploy_contract():
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
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

contract_address = deploy_contract()
contract = w3.eth.contract(address=contract_address, abi=abi)

# Streamlit App UI
st.title("📲 Mobile Recharge Ledger on Blockchain")

menu = st.sidebar.selectbox("Select Action", ["Recharge", "View Recharge History"])

if menu == "Recharge":
    mobile = st.text_input("Enter Mobile Number")
    amount = st.number_input("Recharge Amount", min_value=1)

    if st.button("🔌 Recharge"):
        nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
        txn = contract.functions.recharge(mobile, int(amount)).build_transaction({
            'from': PUBLIC_ADDRESS,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce
        })
        signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        st.success("Recharge successful and stored on blockchain!")

elif menu == "View Recharge History":
    mobile = st.text_input("Enter Mobile Number to View History")
    if st.button("🔍 View Records"):
        try:
            records = contract.functions.getRechargeRecordsByMobile(mobile).call()
            if not records:
                st.info("No recharge history found.")
            for record in records:
                st.write({
                    "Amount": record[0],
                    "Timestamp": record[1],
                    "Mobile": record[2],
                    "Operator": record[3]
                })
        except Exception as e:
            st.error(f"Error fetching records: {str(e)}")
streamlit
web3
py-solc-x



