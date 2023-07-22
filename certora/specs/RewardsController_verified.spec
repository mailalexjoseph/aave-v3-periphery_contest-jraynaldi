import "methods/Methods_base.spec";

///////////////// Properties ///////////////////////

/*//////////////////////////////////////////////////////////////
                            Unit Test
//////////////////////////////////////////////////////////////*/

rule configureAssetsSingle(
    env e,
    env e1,
    RewardsDataTypes.RewardsConfigInput config
) {
    address reward = config.reward;
    configureAssetsSingle(e,config);
    assert getTransferStrategy(reward) == config.transferStrategy;
    assert getRewardOracle(reward) == config.rewardOracle;
}

rule setTransferStrategy_integrity(
    env e,
    address reward,
    address transferStrategy
) {
    setTransferStrategy(e, reward, transferStrategy);
    assert getTransferStrategy(reward) == transferStrategy <=> e.msg.sender == EMISSION_MANAGER();
}