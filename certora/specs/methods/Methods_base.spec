import "./ERC20_methods.spec";

using DummyERC20_AToken as AToken;
using RewardsDataTypes as _RewardsDataTypes;
using DummyERC20_rewardToken as RewardToken;
/////////////////// Methods ////////////////////////

    methods {
        // 
        function getAssetRewardIndex(address, address) external returns (uint256) envfree;
        function getRewardsData(address, address) external returns (uint256, uint256, uint256, uint256) envfree;
        function getUserAssetIndex(address, address, address) external returns (uint256) envfree;
        
        //internal 

        // AToken functions
        function _.getScaledUserBalanceAndSupply(address) external => DISPATCHER(true);
        function _.scaledTotalSupply() external => DISPATCHER(true);
        function _.handleAction(address, uint256, uint256) external => DISPATCHER(true);

        // TransferStrategyBase functions
        function _.performTransfer(address, address, uint256) external => DISPATCHER(true);

        // Oracle - assume any value 
        function _.latestAnswer() external => CONSTANT;

        // constant 
        function EMISSION_MANAGER() external returns(address) envfree;

        // Harness view
        function isContract(address) external returns(bool) envfree;
        function getAvailableRewardsCount(address) external returns(uint128) envfree;
        function getTotalSupply(address) external returns(uint256) envfree;
        function getEmissionPerSecond(address, address) external returns(uint256) envfree;
        function getAssetsList() external returns(address[] memory) envfree;
        function isRewardEnabled(address) external returns(bool) envfree;

        //envfree functions
        function getRewardsList() external returns (address[] memory) envfree;
        function getUserAccruedRewards(address, address ) external returns(uint256) envfree; 
        function getClaimer(address) external returns (address) envfree;
        function getTransferStrategy(address) external returns (address) envfree;
        function getRewardOracle(address) external returns(address) envfree;
        function getAssetDecimals(address) external returns(uint8) envfree;
        function getRewardsByAsset(address) external returns(address[] memory) envfree;
        function getDistributionEnd(address, address) external returns(uint256) envfree;

        // Reward Token
        function RewardToken.balanceOf(address) external returns(uint256) envfree;
    }

///////////////// DEFINITIONS //////////////////////
definition harnessFunction(method f) returns bool = 
    f.selector == sig:configureAssetsSingle(RewardsDataTypes.RewardsConfigInput).selector
    || f.selector == sig:claimReward(address,uint256,address,address).selector
    || f.selector == sig:claimRewardOnBehalf(address, uint256, address, address, address).selector
    || f.selector == sig:claimRewardToSelf(address, uint256, address).selector
    || f.selector == sig:claimAllReward(address,address).selector
    || f.selector == sig:claimAllRewardOnBehalf(address,address,address).selector
    || f.selector == sig:claimAllRewardToSelf(address).selector
    || f.selector == sig:updateUserData(address,address,address).selector
    || f.selector == sig:updateRewardData(address,address).selector;

definition claimFunction(method f) returns bool =
    f.selector == sig:claimAllRewards(address[],address).selector
    || f.selector == sig:claimAllRewardsOnBehalf(address[],address,address).selector
    || f.selector == sig:claimAllRewardsToSelf(address[]).selector
    || f.selector == sig:claimRewards(address[],uint256,address,address).selector
    || f.selector == sig:claimRewardsOnBehalf(address[],uint256,address,address,address).selector
    || f.selector == sig:claimRewardsToSelf(address[],uint256,address).selector;

////////////////// FUNCTIONS //////////////////////
// setup helper to claimReward function
function claimRewardSetup(env e, env e1,address user, address to, address asset) {
    require e1.msg.sender == AToken;
    require asset == AToken;
    require e.block.timestamp == e1.block.timestamp;

    uint256 userBalance = AToken.scaledBalanceOf(e, user);
    uint256 totalSupply = AToken.scaledTotalSupply(e);
    handleAction(e1, user, totalSupply, userBalance);
}

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