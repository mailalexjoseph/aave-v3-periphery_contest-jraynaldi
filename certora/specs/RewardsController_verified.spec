import "methods/Methods_base.spec";
using TransferStrategyHarness as TransferStrategy;
///////////////// Properties ///////////////////////
/** Properties in consideration
* user reward index should never decrease alongside with reward index all over the contract
*
*/
/*//////////////////////////////////////////////////////////////
                                MISC
//////////////////////////////////////////////////////////////*/
ghost mapping(address => mapping(address => mapping(address => mathint))) userAccrued {
    init_state axiom forall address asset. forall address reward. forall address user. userAccrued[user][asset][reward] == 0;
}

ghost mapping(address => mapping(address => mathint)) sumOfAllRewardAccrued {
    init_state axiom forall address asset. forall address reward. sumOfAllRewardAccrued[asset][reward] == 0;
}


hook Sload uint128 val _assets[KEY address asset].rewards[KEY address reward].usersData[KEY address user].accrued STORAGE{
    require userAccrued[user][asset][reward] == to_mathint(val);
}

hook Sstore _assets[KEY address asset].rewards[KEY address reward].usersData[KEY address user].accrued uint128 val (uint128 oldVal) STORAGE{
    userAccrued[user][asset][reward] = to_mathint(val);
    sumOfAllRewardAccrued[asset][reward] = sumOfAllRewardAccrued[asset][reward] + val - oldVal;
}

/*//////////////////////////////////////////////////////////////
                    High Level Properties
//////////////////////////////////////////////////////////////*/

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

/*//////////////////////////////////////////////////////////////
                            Unit Test
//////////////////////////////////////////////////////////////*/

//TODO not completed 
rule configureAssetsSingle(
    env e,
    env e1,
    RewardsDataTypes.RewardsConfigInput config
) {
    address reward = config.reward;
    configureAssetsSingle(e,config);
    uint256 index;
    uint256 emissionPerSecond;
    uint256 lastUpdateTimestamp;
    uint256 distributionEnd;
    index, emissionPerSecond, lastUpdateTimestamp, distributionEnd = getRewardsData(config.asset, config.reward);
    assert getTransferStrategy(reward) == config.transferStrategy;
    assert getRewardOracle(reward) == config.rewardOracle;
    assert to_mathint(lastUpdateTimestamp) == to_mathint(e.block.timestamp);
    assert to_mathint(emissionPerSecond) == to_mathint(config.emissionPerSecond);
    assert to_mathint(distributionEnd) == to_mathint(config.distributionEnd);
}

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

function claimRewardSetup(env e, env e1,address user, address to, address reward, address asset) {
    require e1.msg.sender == AToken;
    require reward == RewardToken;
    require asset == AToken;
    require e.msg.sender == currentContract;
    require e.block.timestamp == e1.block.timestamp;
    require to != TransferStrategy;

    uint256 userBalance = AToken.scaledBalanceOf(e, user);
    uint256 totalSupply = AToken.scaledTotalSupply(e);
    handleAction(e1, user, totalSupply, userBalance);

}

rule claimReward_integrity(
    env e,
    env e1,
    address asset,
    uint256 amount,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, to,reward,asset);

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    claimReward(e, asset, amount, to, reward);

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

rule claimRewardOnBehalf(
    env e,
    env e1,
    address asset,
    uint256 amount,
    address user,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,user, to,reward,asset);

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[user][asset][reward];
    require userAccruedBefore >= 0;

    claimRewardOnBehalf(e, asset, amount, user, to, reward);

    mathint userAccruedAfter = userAccrued[user][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == userAccruedBefore - amount 
        <=> userAccruedBefore >= to_mathint(amount) || amount == 0;
    assert userAccruedAfter == 0 <=> userAccruedBefore <= to_mathint(amount);
    if (to_mathint(amount) < userAccruedBefore) {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + amount 
            <=> currentContract == getClaimer(user);
    } else {
        assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore
            <=> currentContract == getClaimer(user);
    }
}

rule claimRewardToSelf(
    env e,
    env e1,
    address asset,
    uint256 amount,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, e.msg.sender,reward,asset);

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, e.msg.sender);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    claimRewardToSelf(e, asset, amount,  reward);

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

rule claimAllReward(
    env e,
    env e1,
    address asset,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, to,reward,asset);

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    claimAllReward(e, asset, to);


    mathint userAccruedAfter = userAccrued[e.msg.sender][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == 0;
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

rule claimAllRewardOnBehalf(
    env e,
    env e1,
    address asset,
    address user,
    address to,
    address reward
) {
    claimRewardSetup(e,e1,user, to,reward,asset);

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[user][asset][reward];
    require userAccruedBefore >= 0;

    claimAllRewardOnBehalf(e, asset,user, to);


    mathint userAccruedAfter = userAccrued[user][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, to);

    assert userAccruedAfter == 0 <=> currentContract == getClaimer(user);
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

rule claimAllRewardToSelf(
    env e,
    env e1,
    address asset,
    address reward
) {
    claimRewardSetup(e,e1,e.msg.sender, e.msg.sender,reward,asset);

    address[] rewards = getRewardsList();
    require rewards[0] == reward;
    require rewards.length == 1; 

    uint256 rewardBalanceBefore = RewardToken.balanceOf(e, e.msg.sender);
    mathint userAccruedBefore = userAccrued[e.msg.sender][asset][reward];
    require userAccruedBefore >= 0;

    claimAllRewardToSelf(e, asset);

    mathint userAccruedAfter = userAccrued[e.msg.sender][asset][reward];
    uint256 rewardBalanceAfter = RewardToken.balanceOf(e, e.msg.sender);

    assert userAccruedAfter == 0;
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

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

    uint256 totalSupply = getTotalSupply(asset);
    uint256 decimal = getAssetDecimals(asset);

    uint256 oldIndex;
    uint256 newIndex;
    oldIndex, newIndex = getAssetIndex(e, asset, reward);

    uint256 currentTimestamp = e.block.timestamp > distributionEnd ? distributionEnd : e.block.timestamp;

    mathint firstTirm = (emissionPerSecond * (currentTimestamp - lastUpdateTimestamp) * 10 ^ decimal);

    assert oldIndex == assetIndex;
    assert oldIndex == newIndex 
        <=> e.block.timestamp == lastUpdateTimestamp
        || emissionPerSecond == 0
        || lastUpdateTimestamp >= distributionEnd
        || totalSupply == 0
        || firstTirm < to_mathint(totalSupply);
}