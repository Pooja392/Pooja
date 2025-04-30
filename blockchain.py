import streamlit as st
from web3 import Web3
from solcx import compile_standard, install_solc
import json

# Set page config
st.set_page_config(page_title="Mobile Recharge Ledger", layout="centered")

# Infura URL and Private Key from Streamlit Secrets
INFURA_URL = st.secrets["INFURA_URL"]
PRIVATE_KEY = st.secrets["PRIVATE_KEY"]
PUBLIC_ADDRESS = st.secrets["PUBLIC_ADDRESS"]

# Web3 connection
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if w3.is_connected():
    st.sidebar.success("Connected to Ethereum Goerli ✅")
else:
    st.sidebar.error("Failed to connect to Ethereum. Check your Infura URL or network.")

# Compile the contract (you can upload your contract here)
contract_source = """
pragma solidity ^0.8.0;

contract MobileRechargeLedger {
    struct RechargeRecord {
        uint256 rechargeAmount;
        uint256 timestamp;
        string mobileNumber;
        address operator;
    }

    RechargeRecord[] public rechargeRecords;
    mapping(string => RechargeRecord[]) public recordsByMobile;

    event RechargeMade(string mobileNumber, uint256 amount, uint256 timestamp, address operator);

    function recharge(string memory _mobileNumber, uint256 _rechargeAmount) public {
        RechargeRecord memory newRecord = RechargeRecord({
            rechargeAmount: _rechargeAmount,
            timestamp: block.timestamp,
            mobileNumber: _mobileNumber,
            operator: msg.sender
        });

        rechargeRecords.push(newRecord);
        recordsByMobile[_mobileNumber].push(newRecord);

        emit RechargeMade(_mobileNumber, _rechargeAmount, block.timestamp, msg.sender);
    }

    function getRechargeRecordsByMobile(string memory _mobileNumber) public view returns (RechargeRecord[] memory) {
        return recordsByMobile[_mobileNumber];
    }

    function getTotalRechargeRecords() public view returns (uint256) {
        return rechargeRecords.length;
    }
}
"""

install_solc("0.8.0")
compiled = compile_standard({
    "language": "Solidity",
    "sources": {"MobileRechargeLedger.sol": {"content": contract_source}},
    "settings": {
        "outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}
    }
}, solc_version="0.8.0")

# Extract ABI and Bytecode
abi = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["abi"]
bytecode = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["evm"]["bytecode"]["object"]

# Deploy contract (same code as previously)
def deploy_contract():
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
    
    transaction = contract.constructor().build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 6721975,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce
    })
    
    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress

# Deploy the contract and get the address
contract_address = deploy_contract()
contract = w3.eth.contract(address=contract_address, abi=abi)

# Interface with Streamlit UI
st.title("📲 Mobile Recharge Ledger on Blockchain")
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
            st.success(f"Recharge successful for {mobile} and stored on blockchain!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter both mobile number and amount.")







