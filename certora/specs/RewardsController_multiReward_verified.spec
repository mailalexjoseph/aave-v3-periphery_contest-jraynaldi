import "methods/Methods_base.spec";
using TransferStrategyMultiRewardHarnessWithLinks as TransferStrategyMulti;
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

rule claimAllRewardOnBehalf_MultiReward(
    env e,
    env e1,
    address asset,
    address user,
    address to
) {
    claimRewardSetup(e,e1,user, to,asset);

    require to != TransferStrategyMulti;


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


// rule getAllUserRewardsConnection (

// )