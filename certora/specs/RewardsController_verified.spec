import "methods/Methods_base.spec";

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

hook Sload uint128 val _assets[KEY address asset].rewards[KEY address reward].usersData[KEY address user].accrued STORAGE{
    require userAccrued[user][asset][reward] == to_mathint(val);
}

hook Sstore _assets[KEY address asset].rewards[KEY address reward].usersData[KEY address user].accrued uint128 val (uint128 oldVal) STORAGE{
    userAccrued[user][asset][reward] = to_mathint(val);
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