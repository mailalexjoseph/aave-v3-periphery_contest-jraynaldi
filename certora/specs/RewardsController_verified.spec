import "methods/Methods_base.spec";

///////////////// Properties ///////////////////////
/** Properties in consideration
* user reward index should never decrease alongside with reward index all over the contract
*
*/
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

rule handleAction_integrity(
    env e,
    address user, 
    uint256 totalSupply,
    uint256 userBalance
) {
    handleAction(e,user, totalSupply,userBalance)
    assert false
}