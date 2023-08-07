import "methods/Methods_base.spec";
using TransferStrategyMultiRewardHarnessWithLinks as TransferStrategy;
using DummyERC20_rewardTokenB as RewardTokenB;

///////////////// Properties ///////////////////////

// integrity of setEmissionPerSecond to changed emission per second of rewards configuration
rule setEmissionPerSecond_integrity(
    env e,
    address asset,
    address[] rewards,
    uint88[] emissionPerSeconds
) {
    require rewards.length == 2;
    require rewards[0] != rewards[1];
    uint256 lastUpdateTimestamp;
    _,_,lastUpdateTimestamp,_ = getRewardsData(asset,rewards[0]);
    uint256 decimal = getAssetDecimals(asset);
    setEmissionPerSecond(e, asset, rewards, emissionPerSeconds);
    assert getEmissionPerSecond(asset, rewards[0]) == assert_uint256(emissionPerSeconds[0]) 
        <=> rewards.length == emissionPerSeconds.length
        && decimal != 0
        && lastUpdateTimestamp !=0
        && e.msg.sender == EMISSION_MANAGER();
    assert getEmissionPerSecond(asset, rewards[1]) == assert_uint256(emissionPerSeconds[1]);
}

//integrity of claimAllRewardsOnBehalf on the case of multi reward system
rule claimAllRewardOnBehalf_MultiReward(
    env e,
    env e1,
    address asset,
    address user,
    address to
) {
    claimRewardSetup(e,e1,user, to,asset);

    require to != TransferStrategy;


    uint256 numAvailableReward = getAvailableRewardsCount(asset);
    require numAvailableReward == 2;

    address[] assetsRewards = getRewardsByAsset(asset);
    require assetsRewards.length == 2;

    address[] rewards = getRewardsList();
    require rewards.length == 2; 

    require assetsRewards[0] == rewards[0];
    require assetsRewards[1] == rewards[1];
    require rewards[0] == RewardToken;
    require rewards[1] == RewardTokenB;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    uint256 rewardBalanceBefore = RewardTokenB.balanceOf(e, to);
    mathint userAccruedBefore = userAccrued[user][asset][rewards[1]];
    require userAccruedBefore >= 0;

    claimAllRewardsOnBehalf(e, assets,user, to);

    mathint userAccruedAfter = userAccrued[user][asset][rewards[1]];
    uint256 rewardBalanceAfter = RewardTokenB.balanceOf(e, to);

    assert userAccruedAfter == 0 <=> e.msg.sender == getClaimer(user);
    assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + userAccruedBefore;
}

//TODO timeouted
rule getAllUserRewardsConnection (
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
    require getAssetDecimals(asset) == 6;

    uint256 numAvailableReward = getAvailableRewardsCount(asset);
    require numAvailableReward == 2;

    address[] assetsRewards = getRewardsByAsset(asset);
    require assetsRewards.length == 2;

    address[] rewards = getRewardsList();
    require rewards.length == 2; 

    require assetsRewards[0] == rewards[0];
    require assetsRewards[1] == rewards[1];
    require rewards[0] == RewardToken;
    require rewards[1] == RewardTokenB;

    uint256[] unclaimedAmounts;

    address[] assets;
    require assets[0] == asset;
    require assets.length == 1;

    _, unclaimedAmounts = getAllUserRewards(e, assets, user);
    require unclaimedAmounts.length == 2;

    // uint256 rewardBalanceBefore = RewardTokenB.balanceOf(e, to);

    // claimAllRewardsOnBehalf(e, assets,user, to);

    // uint256 rewardBalanceAfter = RewardTokenB.balanceOf(e, to);

    // assert to_mathint(rewardBalanceAfter) == rewardBalanceBefore + unclaimedAmounts[1];

    require e1.msg.sender == AToken;
    require asset == AToken;
    require e.block.timestamp == e1.block.timestamp;

    uint256 userBalance = AToken.scaledBalanceOf(e, user);
    uint256 totalSupply = AToken.scaledTotalSupply(e);
    handleAction(e1, user, totalSupply, userBalance);

    assert to_mathint(unclaimedAmounts[1]) == userAccrued[user][asset][rewards[1]];
}


//integrity of claimRewardsOnBehalf on the case of multi assets system
rule claimRewardOnBehalf_MultiAsset(
    env e,
    env e1,
    uint256 amount,
    address user,
    address to,
    address reward
) {
    address[] assets;
    require assets.length == 2;

    claimRewardSetup(e,e1,user, to,assets[0]);
    claimRewardSetup(e,e1,user, to,assets[1]);

    require to != TransferStrategy;

    mathint userAccruedBefore = userAccrued[user][assets[1]][reward];
    require userAccruedBefore >= 0;

    claimRewardsOnBehalf(e, assets, amount, user, to, reward);

    mathint userAccruedAfter = userAccrued[user][assets[1]][reward];

    assert userAccruedAfter == userAccruedBefore - amount 
        <=> userAccruedBefore >= to_mathint(amount) || amount == 0;
    assert userAccruedAfter == 0 <=> userAccruedBefore <= to_mathint(amount);
}

//integrity of claimAllRewardsOnBehalf on the case of multi assets system
rule claimAllRewardOnBehalf_MultiAsset(
    env e,
    env e1,
    address user,
    address to
) {

    address[] assets;
    require assets.length == 2;

    claimRewardSetup(e,e1,user, to,assets[0]);
    claimRewardSetup(e,e1,user, to,assets[1]);

    require to != TransferStrategy;

    uint256 numAvailableReward = getAvailableRewardsCount(assets[0]);
    require numAvailableReward == 1;
    uint256 numAvailableReward_2 = getAvailableRewardsCount(assets[1]);
    require numAvailableReward_2 == 1;

    address[] assetsRewards = getRewardsByAsset(assets[0]);
    require assetsRewards.length == 1;
    address[] assetsRewards_2 = getRewardsByAsset(assets[1]);
    require assetsRewards_2.length == 1;

    address[] rewards = getRewardsList();
    require rewards.length == 1; 

    require assetsRewards[0] == rewards[0];
    require rewards[0] == RewardToken;

    mathint userAccruedBefore = userAccrued[user][assets[1]][rewards[0]];
    require userAccruedBefore >= 0;

    claimAllRewardsOnBehalf(e, assets,user, to);

    mathint userAccruedAfter = userAccrued[user][assets[1]][rewards[0]];

    assert userAccruedAfter == 0 <=> e.msg.sender == getClaimer(user);
}