import "methods/Methods_base.spec";
using TransferStrategyHarness as TransferStrategy;

// TODO 
// complete configure asset
// getAllUserRewards connection timeouted on multi rewards
// Multi Assets configuration
// Multi Reward configuration
// bug3,5,7,8,10

///////////////// Properties ///////////////////////
/** Properties in consideration
* user reward index should never decrease alongside with reward index all over the contract
*
*/
/*//////////////////////////////////////////////////////////////
                    High Level Properties
//////////////////////////////////////////////////////////////*/

// solvency of reward, sumOfAllReward should greater than equal rewardAccrued of every single user
rule sumOfAllRewardAccrued_GTE_singleReward(
    env e,
    method f, 
    calldataarg args,
    address user, 
    address asset, 
    address reward
) filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    mathint userAccruedBefore =  userAccrued[user][asset][reward];
    require sumOfAllRewardAccrued[asset][reward] >= userAccruedBefore;

    f(e,args);

    mathint userAccruedAfter =  userAccrued[user][asset][reward];
    if claimFunction(f) {
        require userAccruedBefore != userAccruedAfter;
    }
    assert sumOfAllRewardAccrued[asset][reward] >= userAccruedAfter;
}

// reward index cannot be decreased, otherwise user will experienced missing reward and protocol will insolvent
// cause of multiple reward claim
rule indexCannotDecrease(
    env e, 
    method f,
    calldataarg args,
    address asset,
    address reward
)  filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    uint256 indexBefore = getAssetRewardIndex(asset, reward);

    f(e,args);

    uint256 indexAfter = getAssetRewardIndex(asset, reward);

    assert indexAfter >= indexBefore;
}

// user index should always lower than global index
invariant userIndex_LTE_globalIndex(address asset, address reward, address user)
    getAssetRewardIndex(asset, reward) >= getUserAssetIndex(user, asset, reward)
    filtered {
        f -> !f.isView && !harnessFunction(f)
    } 

// user index cannot decreased same as global index
rule userIndexCannotDecrease(
    env e, 
    method f,
    calldataarg args,
    address user,
    address asset,
    address reward
)  filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    requireInvariant userIndex_LTE_globalIndex(asset,reward,user);
    uint256 indexBefore = getUserAssetIndex(user, asset, reward);

    f(e,args);

    uint256 indexAfter = getUserAssetIndex(user, asset, reward);

    assert indexAfter >= indexBefore;
}

// user reward accrued only decreased via several function and only by that user itself or the claimer
rule whoDecreaseRewardsAccrued(
    env e,
    method f,
    calldataarg args,
    address user, 
    address asset,
    address reward
) filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    mathint userAccruedBefore = userAccrued[user][asset][reward];
    f(e, args);
    mathint userAccruedAfter = userAccrued[user][asset][reward];

    assert userAccruedAfter < userAccruedBefore 
        => (e.msg.sender == user
        || e.msg.sender == getClaimer(user))
        && (claimFunction(f));
}

//if certain function called it should update the index
rule claimShouldUpdate(
    env e,
    method f,
    calldataarg args,
    address user,
    address to,
    uint256 amount,
    address[] assets, 
    address reward
) filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    require assets.length == 1;
    require amount != 0;
    uint256 oldIndex;
    uint256 newIndex;
    oldIndex, newIndex = getAssetIndex(e, assets[0], reward);

    address[] rewardsList = getRewardsList();
    require rewardsList[0] == reward;
    require rewardsList.length == 1; 

    address[] assetRewards = getRewardsByAsset(assets[0]);
    require assetRewards[0] == reward;
    require assetRewards.length == 1;

    uint256 indexBefore = getAssetRewardIndex(assets[0], reward);

    if f.selector == sig:claimAllRewards(address[],address).selector {
        claimAllRewards(e, assets,to);
    } else if f.selector == sig:claimAllRewardsOnBehalf(address[],address,address).selector {
        claimAllRewardsOnBehalf(e,assets,user,to);
    } else if f.selector == sig:claimAllRewardsToSelf(address[]).selector {
        claimAllRewardsToSelf(e,assets);
    } else if f.selector == sig:claimRewards(address[],uint256,address,address).selector {
        claimRewards(e, assets, amount, to,  reward);
    } else if f.selector == sig:claimRewardsOnBehalf(address[],uint256,address,address,address).selector {
        claimRewardsOnBehalf(e, assets, amount, user, to, reward);
    } else if f.selector == sig:claimRewardsToSelf(address[],uint256,address).selector {
        claimRewardsToSelf(e, assets, amount, reward);
    } else { 
        f(e,args);
    }

    uint256 indexAfter = getAssetRewardIndex(assets[0], reward);
    assert claimFunction(f) => (indexAfter != indexBefore 
        <=> oldIndex != newIndex);
    assert amount == 0 
        && (
            f.selector == sig:claimRewardsToSelf(address[],uint256,address).selector
            || f.selector == sig:claimRewards(address[],uint256,address,address).selector
            || f.selector == sig:claimRewardsOnBehalf(address[],uint256,address,address,address).selector
        )=> indexAfter == indexBefore;
}

// cannot transfer reward to address 0 
invariant addressZeroNoReward()
    RewardToken.balanceOf(0) == 0
    filtered {
        f -> !f.isView && !harnessFunction(f)
    } 
    {
        preserved with (env e) {
            require e.msg.sender != 0;
        }
    }

// cannot claim rewards from address 0 
rule addressZeroNoClaim( 
    env e, 
    method f, 
    calldataarg args, 
    address asset, 
    address reward
) filtered {
        f -> !f.isView && !harnessFunction(f)
} {
    require e.msg.sender != 0;
    mathint rewardAccruedBefore = userAccrued[0][asset][reward];

    f(e,args);

    mathint rewardAccruedAfter = userAccrued[0][asset][reward];
    assert rewardAccruedAfter >= rewardAccruedBefore;
}

rule lastUpdateTimestamp_LTE_blockTimestamp_distributionEnd(
    env e,
    method f,
    calldataarg args,
    address asset,
    address reward
) filtered {
    f-> !f.isView && !harnessFunction(f)
} {
    uint256 _lastUpdateTimestamp;
    uint256 _distributionEnd;

    _,_, _lastUpdateTimestamp, _distributionEnd = getRewardsData(asset, reward);

    require _lastUpdateTimestamp <= _distributionEnd;
    require _lastUpdateTimestamp <= e.block.timestamp;

    f(e, args);

    uint256 lastUpdateTimestamp_;
    uint256 distributionEnd_;

    _,_, lastUpdateTimestamp_, distributionEnd_ = getRewardsData(asset, reward);

    assert _lastUpdateTimestamp <= _distributionEnd;
    assert _lastUpdateTimestamp <= e.block.timestamp;
}

// only emission manager can change several variable inside the contract
rule onlyEmissionManager(
    env e ,
    method f, 
    calldataarg args,
    address asset, 
    address reward,
    address user
) filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    address _transferStrategyAddress = getTransferStrategy(reward);
    address _rewardOracleAddress = getRewardOracle(reward);
    uint256 _distributionEnd = getDistributionEnd(asset, reward);
    uint256 _emissionPerSecond = getEmissionPerSecond(asset,reward);
    address _authorizedClaimers = getClaimer(user);

    f(e, args);

    address transferStrategyAddress_ = getTransferStrategy(reward);
    address rewardOracleAddress_ = getRewardOracle(reward);
    uint256 distributionEnd_ = getDistributionEnd(asset, reward);
    uint256 emissionPerSecond_ = getEmissionPerSecond(asset,reward);
    address authorizedClaimers_ = getClaimer(user);

    assert _transferStrategyAddress != transferStrategyAddress_ => e.msg.sender == EMISSION_MANAGER();
    assert _rewardOracleAddress != rewardOracleAddress_ => e.msg.sender == EMISSION_MANAGER();
    assert _distributionEnd != distributionEnd_ => e.msg.sender == EMISSION_MANAGER();
    assert _emissionPerSecond != emissionPerSecond_ => e.msg.sender == EMISSION_MANAGER(); 
    assert _authorizedClaimers != authorizedClaimers_ => e.msg.sender == EMISSION_MANAGER(); 
}

//user without balance never update their reward
rule userNoBalanceNoIncreaseReward(
    env e ,
    method f,
    calldataarg args,
    address user, 
    address asset, 
    address reward
) filtered {
    f -> !f.isView && !harnessFunction(f)
} {
    require asset == AToken;
    mathint accruedBefore = userAccrued[user][asset][reward];
    uint256 userBalance = AToken.scaledBalanceOf(e, user);

    f(e,args);

    mathint accruedAfter = userAccrued[user][asset][reward];
    assert userBalance == 0 && f.selector != sig:handleAction(address, uint256, uint256).selector => accruedBefore >= accruedAfter;
}
/*//////////////////////////////////////////////////////////////
                            Unit Test
//////////////////////////////////////////////////////////////*/

//TODO not completed Update Reward Data needed
rule configureAssetsSingle(
    env e,
    env e1,
    RewardsDataTypes.RewardsConfigInput config
) {
    address reward = config.reward;
    address asset = config.asset;
    uint128 _availableRewardsCount = getAvailableRewardsCount(config.asset);
    bool isRewardEnabledBefore = isRewardEnabled(reward);
    uint256 _decimals = getAssetDecimals(asset);
    uint256 _index;
    uint256 _emissionPerSecond;
    uint256 _lastUpdateTimestamp;
    uint256 _distributionEnd;
    _index, _emissionPerSecond, _lastUpdateTimestamp, _distributionEnd = getRewardsData(config.asset, config.reward);
    uint256 newIndex;
    _, newIndex = getAssetIndex(e, asset, reward);
    
    configureAssetsSingle(e,config);

    address[] rewardList = getRewardsList();
    address[] assetsList = getAssetsList();
    require assetsList.length > 0;
    require rewardList.length > 0;
    uint256 decimals_ = getAssetDecimals(asset);
    uint128 availableRewardsCount_ = getAvailableRewardsCount(config.asset);
    address[] rewardsByAsset = getRewardsByAsset(config.asset);
    uint256 index;
    uint256 emissionPerSecond;
    uint256 lastUpdateTimestamp;
    uint256 distributionEnd;
    index, emissionPerSecond, lastUpdateTimestamp, distributionEnd = getRewardsData(config.asset, config.reward);
    require _decimals == decimals_ || _decimals == 0;

    assert getTransferStrategy(reward) == config.transferStrategy;
    assert getRewardOracle(reward) == config.rewardOracle;
    assert to_mathint(lastUpdateTimestamp) == to_mathint(e.block.timestamp);
    assert to_mathint(emissionPerSecond) == to_mathint(config.emissionPerSecond);
    assert to_mathint(distributionEnd) == to_mathint(config.distributionEnd);
    assert _decimals != 0 => index == newIndex;
    assert isRewardEnabled(reward);
    assert !isRewardEnabledBefore => rewardList[assert_uint256(rewardList.length - 1)] == reward;
    assert _decimals == 0 => assetsList[assert_uint256(assetsList.length - 1)] == config.asset;
    assert _lastUpdateTimestamp == 0 
        <=> to_mathint(availableRewardsCount_) == _availableRewardsCount + 1 
        && rewardsByAsset[_availableRewardsCount] == reward;
}

// integrity of setTransferStrategy to set tansferStrategy address
rule setTransferStrategy_integrity(
    env e,
    address reward,
    address transferStrategy
) {
    setTransferStrategy(e, reward, transferStrategy);
    assert getTransferStrategy(reward) == transferStrategy 
        <=> e.msg.sender == EMISSION_MANAGER()
        && isContract(transferStrategy) 
        && transferStrategy != 0;
}

// integrity of setRewardOracle to set rewardOracle address
rule setRewardOracle_integrity(
    env e,
    address reward,
    address rewardOracle
) {
    mathint latestAnswer = getLatestAnswer(e, rewardOracle);
    setRewardOracle(e, reward, rewardOracle);
    assert getRewardOracle(reward) == rewardOracle 
        <=> e.msg.sender == EMISSION_MANAGER()
        && latestAnswer > 0 ;
}

// integrity handleAction to msg.sender update their reward data to global rewards
rule handleAction_integrity_global(
    env e,
    address user, 
    uint256 totalSupply,
    uint256 userBalance
) {
    require getAvailableRewardsCount(e.msg.sender) == 1; 
    require getAssetDecimals(e.msg.sender) > 0; 
    uint256 oldIndex;
    uint256 newIndex; 
    address[] rewards = getRewardsByAsset(e.msg.sender);
    oldIndex, newIndex = getAssetIndex(e, e.msg.sender, rewards[0]);
    uint256 oldTotalSupply = getTotalSupply(e.msg.sender);

    uint256 oldIndexCalc;
    uint256 newIndexCalc;
    oldIndexCalc, newIndexCalc = getAssetIndex(e, e.msg.sender, rewards[0], totalSupply);

    handleAction(e,user, totalSupply,userBalance);

    uint256 lastUpdateTimestamp;
    _,_,lastUpdateTimestamp,_ = getRewardsData(e.msg.sender, rewards[0]);
    uint256 newRewardIndex = getAssetRewardIndex(e.msg.sender, rewards[0]);

    assert oldTotalSupply == totalSupply => newRewardIndex == newIndex;  
    assert newIndexCalc == newRewardIndex;
    assert lastUpdateTimestamp == e.block.timestamp;
}

// integrity of handleAction to msg.sender update their data on user rewards
rule handleAction_integrity_user(
    env e,
    address user, 
    uint256 totalSupply,
    uint256 userBalance
) {
    require getAvailableRewardsCount(e.msg.sender) == 1; 
    uint8 decimals = getAssetDecimals(e.msg.sender);
    require decimals > 0; 
    address[] rewards = getRewardsByAsset(e.msg.sender);

    uint256 oldIndexCalc;
    uint256 newIndexCalc;
    oldIndexCalc, newIndexCalc = getAssetIndex(e, e.msg.sender, rewards[0], totalSupply);
    uint256 oldUserIndex = getUserAssetIndex(user, e.msg.sender, rewards[0]);
    mathint userAccruedBefore = userAccrued[user][e.msg.sender][rewards[0]];

    handleAction(e,user, totalSupply,userBalance);

    uint256 newUserIndex = getUserAssetIndex(user, e.msg.sender, rewards[0]);
    mathint userAccruedAfter = userAccrued[user][e.msg.sender][rewards[0]];

    assert newUserIndex == newIndexCalc;
    assert userAccruedAfter == userAccruedBefore + ((userBalance * (newIndexCalc - oldUserIndex)) / 10 ^ decimals);
    assert userAccruedAfter != userAccruedBefore => userBalance != 0;
    assert userAccruedAfter != userAccruedBefore => oldUserIndex != newIndexCalc;
}

// integrity of claimReward to claim porpotion reward of msg.sender than send to `to` address
rule claimReward_integrity(
    env e,
    env e1,
    address asset,
    uint256 amount,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, to,asset);

    require to != TransferStrategy;

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    claimRewards(e, assets, amount, to, reward);

    mathint userAccruedAfter = userAccrued[e.msg.sender][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == userAccruedBefore - amount 
        <=> userAccruedBefore >= to_mathint(amount) || amount == 0;
    assert userAccruedAfter == 0 <=> userAccruedBefore <= to_mathint(amount);
    if (to_mathint(amount) < userAccruedBefore) {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + amount;
    } else {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
    }
}

// integrity of claimRewardOnBehalf to claim porpotion reward of a user than 
// send to `to` address by another user that have permission
rule claimRewardOnBehalf(
    env e,
    env e1,
    address asset,
    uint256 amount,
    address user,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,user, to,asset);

    require to != TransferStrategy;

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[user][asset][reward];
    require userAccruedBefore >= 0;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    claimRewardsOnBehalf(e, assets, amount, user, to, reward);

    mathint userAccruedAfter = userAccrued[user][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == userAccruedBefore - amount 
        <=> userAccruedBefore >= to_mathint(amount) || amount == 0;
    assert userAccruedAfter == 0 <=> userAccruedBefore <= to_mathint(amount);
    if (to_mathint(amount) < userAccruedBefore) {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + amount 
            <=> e.msg.sender == getClaimer(user);
    } else {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore
            <=> e.msg.sender == getClaimer(user);
    }
}

// integrity of claimRewardsToSelf to claim porpotion reward of msg.sender than send to self
rule claimRewardToSelf(
    env e,
    env e1,
    address asset,
    uint256 amount,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, e.msg.sender,asset);

    require e.msg.sender != TransferStrategy;

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, e.msg.sender);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    claimRewardsToSelf(e, assets, amount,  reward);

    mathint userAccruedAfter = userAccrued[e.msg.sender][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, e.msg.sender);

    assert userAccruedAfter == userAccruedBefore - amount 
        <=> userAccruedBefore >= to_mathint(amount) || amount == 0;
    assert userAccruedAfter == 0 <=> userAccruedBefore <= to_mathint(amount);
    if (to_mathint(amount) < userAccruedBefore) {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + amount;
    } else {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
    }
}

// integrity of claimAllRewards to claim all reward of msg.sender than send to `to` address
rule claimAllReward(
    env e,
    env e1,
    address asset,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, to, asset);

    require to != TransferStrategy;

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    claimAllRewards(e, assets, to);


    mathint userAccruedAfter = userAccrued[e.msg.sender][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == 0;
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

// integrity of claimAllRewardsOnBehalf to claim porpotion reward of user that 
// send to `to` address by other user that have permission
rule claimAllRewardOnBehalf(
    env e,
    env e1,
    address asset,
    address user,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,user, to,asset);

    require to != TransferStrategy;

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 


    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;


    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[user][asset][reward];
    require userAccruedBefore >= 0;

    claimAllRewardsOnBehalf(e, assets,user, to);

    mathint userAccruedAfter = userAccrued[user][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == 0 <=> e.msg.sender == getClaimer(user);
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

// getUserRewards should sync with other rewards getter. 
rule getUserRewardsConnection(
    env e,
    env e1, 
    address asset,
    address user,
    address to,
    address reward
) {
    require reward == RewardToken;
    require asset == AToken;
    require to != TransferStrategy;

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 

    address[] assetRewards = getRewardsByAsset(asset);
    require assetRewards[0] == reward;
    require assetRewards.length == 1; 

    require getAvailableRewardsCount(asset) == 1;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    uint256 userRewards = getUserRewards(e, assets, user, reward);

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);

    claimAllRewardsOnBehalf(e, assets,user, to);

    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userRewards;
}

// integrity of claimAllRewardsToSelf to claim porpotion reward of msg.sender send to self
rule claimAllRewardToSelf(
    env e,
    env e1,
    address asset,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, e.msg.sender,asset);

    require e.msg.sender != TransferStrategy;

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, e.msg.sender);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    claimAllRewardsToSelf(e, assets);

    mathint userAccruedAfter = userAccrued[e.msg.sender][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, e.msg.sender);

    assert userAccruedAfter == 0;
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

// integrity of setDistributionEnd to setting distributionEnd of a reward
rule setDistributionEnd_integrity(
    env e, 
    address asset,
    address reward,
    uint32 newDistributionEnd
) {
    setDistributionEnd(e, asset, reward, newDistributionEnd);
    assert getDistributionEnd(asset, reward) == assert_uint256(newDistributionEnd)
        <=> e.msg.sender == EMISSION_MANAGER();
}

// integrity of getAssetIndex to show the real value of asset index before and after update
rule getAssetIndex_integrity(
    env e,
    address asset, 
    address reward
) {
    uint256 emissionPerSecond;
    uint256 lastUpdateTimestamp;
    uint256 assetIndex;
    uint256 distributionEnd;
    assetIndex, emissionPerSecond, lastUpdateTimestamp, distributionEnd = getRewardsData(asset, reward);
    require lastUpdateTimestamp <= e.block.timestamp;
    require lastUpdateTimestamp <= distributionEnd;

    uint256 totalSupply = getTotalSupply(asset);
    uint256 decimal = getAssetDecimals(asset);

    uint256 oldIndex;
    uint256 newIndex;
    oldIndex, newIndex = getAssetIndex(e, asset, reward);

    uint256 currentTimestamp = e.block.timestamp > distributionEnd ? distributionEnd : e.block.timestamp;

    mathint firstTirm = (emissionPerSecond * (currentTimestamp - lastUpdateTimestamp) * 10 ^ decimal);
    mathint changes = totalSupply == 0 ? 0 : firstTirm / totalSupply;

    assert oldIndex == assetIndex;
    assert oldIndex == newIndex 
        <=> e.block.timestamp == lastUpdateTimestamp
        || emissionPerSecond == 0
        || lastUpdateTimestamp >= distributionEnd
        || totalSupply == 0
        || firstTirm < to_mathint(totalSupply);
    assert to_mathint(newIndex) == oldIndex + (changes);
}

// integrity of _updateRewardData that must return true if index changed
rule updatingShouldEmitEvent_global(
    env e, 
    address asset, 
    address reward
) {
    uint256 oldIndex = getAssetRewardIndex(asset, reward);

    uint256 index;
    bool updated;

    index, updated = updateRewardData(e, asset, reward);

    assert index != oldIndex <=> updated;
}

// integrity of _updateUserData that must return true if index changed
rule updatingShouldEmitEvent_user(
    env e, 
    address user,
    address asset, 
    address reward
) {
    uint256 oldIndex = getUserAssetIndex(user, asset, reward);

    uint256 accrued;
    bool updated;

    accrued, updated = updateUserData(e, user, asset, reward);


    uint256 newIndex = getUserAssetIndex(user, asset, reward);

    assert newIndex != oldIndex <=> updated;
}

//integrity of getUserAccriedRewards to show total of accrued reward of an user
rule getUserAccruedRewards_integrity(
    env e,
    address user, 
    address reward
) {
    address[] assets = getAssetsList();
    require assets.length == 2;
    require assets[0] != assets[1];

    uint256 totalAccrued = getUserAccruedRewards(user, reward);

    assert to_mathint(totalAccrued) == userAccrued[user][assets[0]][reward] + userAccrued[user][assets[1]][reward];
}

// integrity of getAllUserRewards to sync with other function and get the correct show to the real value that other function called
rule getAllUserRewardsConnection_single(
    env e,
    env e1,
    address asset,
    address user,
    address to
) {
    require to != TransferStrategy;
    require asset == 111;
    require user == 333;
    require to == 444;

    uint256 numAvailableReward = getAvailableRewardsCount(asset);
    require numAvailableReward == 1;

    address[] assetsRewards = getRewardsByAsset(asset);
    require assetsRewards.length == 1;

    address[] rewards = getRewardsList();
    require rewards.length == 1; 

    require assetsRewards[0] == rewards[0];
    require rewards[0] == RewardToken;

    uint256[] unclaimedAmounts;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    _, unclaimedAmounts = getAllUserRewards(e, assets, user);
    require unclaimedAmounts.length == 1;

    require e1.msg.sender == AToken;
    require asset == AToken;
    require e.block.timestamp == e1.block.timestamp;

    uint256 userBalance = AToken.scaledBalanceOf(e, user);
    uint256 totalSupply = AToken.scaledTotalSupply(e);
    handleAction(e1, user, totalSupply, userBalance);

    assert to_mathint(unclaimedAmounts[0]) == userAccrued[user][asset][rewards[0]];
}