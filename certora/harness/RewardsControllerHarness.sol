// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.10;

import {RewardsController} from '../../contracts/rewards/RewardsController.sol';
import {RewardsDataTypes} from '../../contracts/rewards/libraries/RewardsDataTypes.sol';
import {IEACAggregatorProxy} from '../../contracts/misc/interfaces/IEACAggregatorProxy.sol';

contract RewardsControllerHarness is RewardsController {
    
    constructor(address emissionManager) RewardsController(emissionManager) {}
    // returns an asset's reward index
    function getAssetRewardIndex(address asset, address reward) external view returns (uint256) {
        return _assets[asset].rewards[reward].index;
    }

    function configureAssetsSingle(RewardsDataTypes.RewardsConfigInput memory config) external {
        RewardsDataTypes.RewardsConfigInput[] memory inputs = new RewardsDataTypes.RewardsConfigInput[](1);
        inputs[0] = config;
        this.configureAssets(inputs);
    }

    function getLatestAnswer(IEACAggregatorProxy oracle) external view returns(int256){
        return oracle.latestAnswer();
    }
}