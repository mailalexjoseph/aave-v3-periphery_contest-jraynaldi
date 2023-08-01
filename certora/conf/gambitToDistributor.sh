gambit mutate --filename contracts/rewards/RewardsDistributor.sol \
    --solc_remappings @aave=node_modules/@aave \
    --num_mutants 10 \
    --mutations binary-op-mutation \
