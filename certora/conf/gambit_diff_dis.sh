y=1
replace="contracts/rewards/RewardsDistributor.sol"
rm -rf certora/tests/participants
mkdir certora/tests/participants/
for file in gambit_out/mutants/*/contracts/rewards/RewardsDistributor.sol
do
    touch certora/tests/participants/bug$y.patch
    git diff --no-index contracts/rewards/RewardsDistributor.sol $file > certora/tests/participants/bug$y.patch
    sed -i "4s!${file}!${replace}!" certora/tests/participants/bug$y.patch
    y=`expr $y + 1`
done
