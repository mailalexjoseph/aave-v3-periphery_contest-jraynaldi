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
    || f.selector == sig:claimAllRewardToSelf(address).selector;

definition claimFunction(method f) returns bool =
    f.selector == sig:claimAllRewards(address[],address).selector
    || f.selector == sig:claimAllRewardsOnBehalf(address[],address,address).selector
    || f.selector == sig:claimAllRewardsToSelf(address[]).selector
    || f.selector == sig:claimRewards(address[],uint256,address,address).selector
    || f.selector == sig:claimRewardsOnBehalf(address[],uint256,address,address,address).selector
    || f.selector == sig:claimRewardsToSelf(address[],uint256,address).selector;

////////////////// FUNCTIONS //////////////////////
