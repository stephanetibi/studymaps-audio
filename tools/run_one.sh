#!/bin/bash
# run_one.sh <batch> : waits for the NaturalReader zip in Downloads, then processes it
b=$1; f=$(ls batches/Gen_EN_B$(printf %02d $b)_*.txt); n=$(basename "$f" .txt); z="$HOME/mnt/Downloads/$(echo $n | tr -d '_-').zip"
for i in $(seq 1 50); do [ -f "$z" ] && break; sleep 3; done
[ -f "$z" ] || { echo "no zip $z yet"; exit 1; }
sleep 2; python3 process_batch_EN.py $b "$z"
