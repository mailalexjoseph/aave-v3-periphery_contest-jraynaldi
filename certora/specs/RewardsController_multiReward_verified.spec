import "methods/Methods_base.spec";

///////////////// Properties ///////////////////////

//TODO add more condition that will revert
rule setEmissionPerSecond_integrity(
    env e,
    address asset,
    address[] rewards,
    uint88[] emissionPerSeconds
) {
    require rewards.length == 2;
    require rewards[0] != rewards[1];
    setEmissionPerSecond(e, asset, rewards, emissionPerSeconds);
    assert getEmissionPerSecond(asset, rewards[0]) == assert_uint256(emissionPerSeconds[0]);
    assert getEmissionPerSecond(asset, rewards[1]) == assert_uint256(emissionPerSeconds[1]);
}