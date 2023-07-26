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

        //envfree functions
        function getRewardsList() external returns (address[] memory) envfree;
        function getUserAccruedRewards(address, address ) external returns(uint256) envfree; 
        function getClaimer(address) external returns (address) envfree;
        function getTransferStrategy(address) external returns (address) envfree;
        function getRewardOracle(address) external returns(address) envfree;
        function getAssetDecimals(address) external returns(uint8) envfree;
        function getRewardsByAsset(address) external returns(address[] memory) envfree;
    }

///////////////// DEFINITIONS //////////////////////

////////////////// FUNCTIONS //////////////////////
