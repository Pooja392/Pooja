web3==5.24.0
py-solc-x
streamlit
import streamlit as st
from web3 import Web3
from solcx import compile_standard, install_solc
import json

# Install solc version 0.8.0
install_solc('0.8.0')

# Set up the Ethereum connection (Infura - Goerli testnet)
INFURA_URL = st.secrets["INFURA_URL"]  # Your Infura URL
PRIVATE_KEY = st.secrets["PRIVATE_KEY"]  # Your private key (should not be exposed!)
PUBLIC_ADDRESS = st.secrets["PUBLIC_ADDRESS"]  # Your Ethereum public address (Wallet Address)

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Check if connected to Ethereum
if w3.isConnected():
    st.sidebar.success("Connected to Ethereum Network!")
else:
    st.sidebar.error("Failed to connect to Ethereum. Please check your Infura URL.")

# Solidity contract source code
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

# Compile the contract
compiled = compile_standard({
    "language": "Solidity",
    "sources": {"MobileRechargeLedger.sol": {"content": contract_source}},
    "settings": {
        "outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}
    }
}, solc_version="0.8.0")

# Get ABI and Bytecode
abi = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["abi"]
bytecode = compiled["contracts"]["MobileRechargeLedger.sol"]["MobileRechargeLedger"]["evm"]["bytecode"]["object"]

# Deploy the contract
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

# Deploy the contract
contract_address = deploy_contract()
contract = w3.eth.contract(address=contract_address, abi=abi)

# Streamlit interface
st.title("📲 Mobile Recharge Ledger on Blockchain")

# Recharge Input
mobile_number = st.text_input("Enter Mobile Number")
recharge_amount = st.number_input("Enter Recharge Amount", min_value=1)

# Button to make a recharge
if st.button("Recharge"):
    if mobile_number and recharge_amount:
        try:
            # Send transaction to smart contract
            nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
            txn = contract.functions.recharge(mobile_number, int(recharge_amount)).build_transaction({
                'from': PUBLIC_ADDRESS,
                'gas': 2000000,
                'gasPrice': w3.to_wei('20', 'gwei'),
                'nonce': nonce
            })

            signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            st.success(f"Recharge successful for {mobile_number}!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter both mobile number and amount.")

# Fetch Recharge Records
if st.button("View Recharge History"):
    if mobile_number:
        try:
            records = contract.functions.getRechargeRecordsByMobile(mobile_number).call()
            if records:
                for record in records:
                    st.write(f"Amount: {record[0]} | Timestamp: {record[1]} | Operator: {record[3]}")
            else:
                st.info("No recharge records found for this mobile number.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a mobile number to view recharge history.")








