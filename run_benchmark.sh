#!/bin/bash

# Default values
M=2
N=5000
D=200
D_LIST="25,50,75,100,150,200,300"
N_LIST="1000,10000,100000,1000000"
PROGRAM="bench_matrix"
RESULTS_FILE="mp_spdz_results_dimensions.log"

# Check for provided command-line arguments
if [ $# -ge 1 ]; then M=$1; fi
if [ $# -ge 2 ]; then N=$2; fi
if [ $# -ge 3 ]; then D=$3; fi
if [ $# -ge 4 ]; then D_LIST=$4; fi
if [ $# -ge 5 ]; then N_LIST=$5; fi

# Step 1: Compile the program
echo "Compiling $PROGRAM..."
./compile.py $PROGRAM || { echo "Compilation failed"; exit 1; }

# Step 2: Run parties in parallel with dynamic arguments
echo "Running $M parties in parallel with parameters: n=$N, d=$D_LIST"
echo "Results saved in $RESULTS_FILE"

# Clear the results file before running
echo "===== MP-SPDZ Benchmark Results =====" > $RESULTS_FILE

for ((i=0; i<M; i++)); do
    ./lowgear-party.x -N $M -p $i $PROGRAM $M $N $D "$D_LIST" "$N_LIST" >> $RESULTS_FILE 2>&1 &
    PIDS[$i]=$!
done

# Step 3: Wait for all parties to complete
for pid in "${PIDS[@]}"; do
    wait $pid
done

echo "All parties finished execution. Results saved in $RESULTS_FILE"
