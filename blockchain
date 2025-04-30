// SPDX-License-Identifier: MIT
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

    function getTotalRechargeRecords() public view returns (uint256) {
        return rechargeRecords.length;
    }

    function getRechargeRecordsByMobile(string memory _mobileNumber) public view returns (RechargeRecord[] memory) {
        return recordsByMobile[_mobileNumber];
    }
}

