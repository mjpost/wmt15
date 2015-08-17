#!/bin/bash

# Usage:
# for lang in $(ls data/wmt15*csv | cut -d. -f2); do
#   qsub script/run-1000.sh $lang
# done

#$ -S /bin/bash -V -cwd
#$ -o /dev/null -j y
#$ -l h_rt=0:10:00
#$ -t 1:1000

. ~/.bashrc
export PYTHONPATH=.:$PYTHONPATH:$(pwd)/wmt-trueskill/src/trueskill

set -u

lang=$1
model=$2

dir=results/$lang/$model/$SGE_TASK_ID
[[ ! -d "$dir" ]] && mkdir -p "$dir"

if [[ $model = "ts" ]]; then
    cat data/wmt15.$lang.csv | ./wmt-trueskill/src/infer_TS.py -n 2 -d 0 -s 2 $dir/wmt15
elif [[ $model = "ew" ]]; then
    cat data/wmt15.$lang.csv | ./wmt-trueskill/src/infer_EW.py -p 1.0 -s 2 $dir/wmt15
elif [[ $model = "hm" ]]; then
    echo "not implemented"
#    cat data/wmt15.$lang.csv | ./wmt-trueskill/src/infer_HM.py -p 1.0 -s 2 t $dir/wmt15
fi
