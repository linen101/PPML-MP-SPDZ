#!/bin/bash

# Default values
M=2           # Number of parties
N_LIST="500,5000,50000" # Samples list
PROGRAM="median_mpc"

# Check fo provided command-line arguments
if [ $# -ge 1 ]; then M=$1; fi
if [ $# -ge 2 ]; then N_LIST=$5; fi

# Step 1: Compile the program (No extra arguments passed)
echo "Compiling $PROGRAM..."
./compile.py $PROGRAM $M "$N_LIST" || { echo "Compilation failed"; exit 1; }

# Step 2: Run parties in parallel with dynamic arguments
echo "Running $M parties in parallel"

# Generate the correct executable name
EXECUTABLE="${PROGRAM}-${M}-${N_LIST}"

for ((i=0; i<M; i++)); do
    ./lowgear-party.x -N $M -p $i $EXECUTABLE  &> median_mpc_party_$i-parties-$M.log &
    PIDS[$i]=$!
done

# Step 3: Wait for all parties to complete
echo "Waiting for all parties to complete..."
for pid in "${PIDS[@]}"; do
    wait $pid
done

echo "All parties finished execution."
