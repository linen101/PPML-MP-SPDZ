#!/bin/bash

# Number of parties
NUM_PARTIES=2  # Change this as needed
PROGRAM="bench_matrix"  # Name of your compiled MP-SPDZ program

# Step 1: Compile the program
echo "Compiling $PROGRAM..."
./compile.py $PROGRAM || { echo "Compilation failed"; exit 1; }

# Step 2: Run parties in parallel
echo "Running $NUM_PARTIES parties in parallel..."
for ((i=0; i<NUM_PARTIES; i++)); do
    ./lowgear-party.x -N $NUM_PARTIES -p $i $PROGRAM &> party_$i.log &
    PIDS[$i]=$!
done

# Step 3: Wait for all parties to finish
echo "Waiting for all parties to complete..."
for pid in "${PIDS[@]}"; do
    wait $pid
done

echo "All parties finished execution."
