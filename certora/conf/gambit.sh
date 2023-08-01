gambit mutate --filename contracts/rewards/RewardsController.sol \
    --solc_remappings @aave=node_modules/@aave \
    --num_mutants 10 \
    --mutations binary-op-mutation \
