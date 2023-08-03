# take first input from user and use it as the path to the folder that contains the patch files
# apply all patches in to munged using git apply and run all scripts in ../scripts/ against each patch file

echo "Applying $2"
git apply certora/tests/$1/$2.patch
echo "Running jobs"
for conf in certora/conf/*_verified.conf
do
    echo "Running $conf"
    certoraRun $conf --send_only --msg "$2 verify using $conf"
done
echo "Reverting $2"
git apply -R certora/tests/$1/$2.patch