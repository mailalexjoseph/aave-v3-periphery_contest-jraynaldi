import "methods/Methods_base.spec";

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