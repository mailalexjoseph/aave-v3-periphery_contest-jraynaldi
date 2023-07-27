// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.10;

import {RewardsController} from '../../contracts/rewards/RewardsController.sol';
import {RewardsDataTypes} from '../../contracts/rewards/libraries/RewardsDataTypes.sol';
import {IEACAggregatorProxy} from '../../contracts/misc/interfaces/IEACAggregatorProxy.sol';
import {IScaledBalanceToken} from '@aave/core-v3/contracts/interfaces/IScaledBalanceToken.sol';

contract RewardsControllerHarness is RewardsController {
    
    constructor(address emissionManager) RewardsController(emissionManager) {}
    // returns an asset's reward index
    function getAssetRewardIndex(address asset, address reward) external view returns (uint256) {
        return _assets[asset].rewards[reward].index;
    }

    function getEmissionPerSecond(address asset, address reward) external view returns(uint256){
        return _assets[asset].rewards[reward].emissionPerSecond;
    }

    function configureAssetsSingle(RewardsDataTypes.RewardsConfigInput memory config) external {
        RewardsDataTypes.RewardsConfigInput[] memory inputs = new RewardsDataTypes.RewardsConfigInput[](1);
        inputs[0] = config;
        this.configureAssets(inputs);
    }

    function getLatestAnswer(IEACAggregatorProxy oracle) external view returns(int256){
        return oracle.latestAnswer();
    }

    function isContract(address addr) external view returns(bool){
        return _isContract(addr);
    }

    function getAvailableRewardsCount(address asset) external view returns(uint128) {
        return _assets[asset].availableRewardsCount;
    } 

    function getTotalSupply(address asset) external view returns(uint256) {
        return IScaledBalanceToken(asset).scaledTotalSupply();
    }

    function getAssetIndex(address asset, address reward, uint256 totalSupply) 
        external 
        view 
        returns(uint256, uint256)
    {
    RewardsDataTypes.RewardData storage rewardData = _assets[asset].rewards[reward];
    return
        _getAssetIndex(
            rewardData,
            totalSupply,
            10**_assets[asset].decimals
        );
    }

    function claimReward(
        address asset,
        uint256 amount,
        address to,
        address reward
    ) external {
        address[] memory assets = new address[](1);
        assets[0] = asset;
        this.claimRewards(assets, amount,to, reward);
    }

    function claimRewardOnBehalf(
        address asset,
        uint256 amount,
        address user,
        address to,
        address reward
    ) external {
        address[] memory assets = new address[](1);
        assets[0] = asset;
        this.claimRewardsOnBehalf(assets, amount, user, to ,reward);
    }

    function claimRewardToSelf(
        address asset,
        uint256 amount,
        address reward
    ) external {
        address[] memory assets = new address[](1);
        assets[0] = asset;
        this.claimRewardsToSelf(assets, amount,reward);
    }

    function claimAllReward(
        address asset,
        address to
    ) external {        
        address[] memory assets = new address[](1);
        assets[0] = asset;
        this.claimAllRewards(assets, to);
    }

    function claimAllRewardOnBehalf(
        address asset,
        address user,
        address to
    ) external {        
        address[] memory assets = new address[](1);
        assets[0] = asset;
        this.claimAllRewardsOnBehalf(assets,user, to);
    }

    function claimAllRewardToSelf(
        address asset
    ) external {        
        address[] memory assets = new address[](1);
        assets[0] = asset;
        this.claimAllRewardsToSelf(assets);
    }
}