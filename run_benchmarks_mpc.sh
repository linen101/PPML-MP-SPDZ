#!/bin/bash

# Default values
M=2            # Number of parties
N=500        # Number of samples
D=100          # Number of features
D_LIST="25,50,75,100,150,200,300"  # Features list
N_LIST="1000,10000,100000,1000000" # Samples list
PROGRAM="bench_matrix"

# Check fo provided command-line arguments
if [ $# -ge 1 ]; then M=$1; fi
if [ $# -ge 2 ]; then N=$2; fi
if [ $# -ge 3 ]; then D=$3; fi
if [ $# -ge 4 ]; then D_LIST=$4; fi
if [ $# -ge 5 ]; then N_LIST=$5; fi

# Step 1: Compile the program (No extra arguments passed)
echo "Compiling $PROGRAM..."
./compile.py $PROGRAM $M $N $D "$D_LIST" "$N_LIST" || { echo "Compilation failed"; exit 1; }

# Step 2: Run parties in parallel with dynamic arguments
echo "Running $M parties in parallel with parameters: n=$N, d=$D"

# Generate the correct executable name
EXECUTABLE="${PROGRAM}-${M}-${N}-${D}-${D_LIST}-${N_LIST}"

for ((i=0; i<M; i++)); do
    ./lowgear-party.x -N $M -p $i $EXECUTABLE  &> party_$i-parties-$M-samples$N.log &
    PIDS[$i]=$!
done

# Step 3: Wait for all parties to complete
echo "Waiting for all parties to complete..."
for pid in "${PIDS[@]}"; do
    wait $pid
done

echo "All parties finished execution."
