y=1
for file in gambit_out/mutants/*/contracts/rewards/RewardsController.sol
do
    touch certora/tests/participants/bug$y.patch
    git diff --no-index contracts/rewards/RewardsController.sol $file > certora/tests/participants/bug$y.patch
    y=`expr $y + 1`
done
