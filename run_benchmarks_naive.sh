#!/bin/bash

# Default values
parties=(2 4 8)   # Number of parties
N=100000       # Number of samples
D=10          # Number of features
D_LIST="10,100"  # Features list
N_LIST="10000" # Samples list
PROGRAM="bench_naive"

# Check fo provided command-line arguments
if [ $# -ge 1 ]; then parties=$1; fi
if [ $# -ge 2 ]; then N=$2; fi
if [ $# -ge 3 ]; then D=$3; fi
if [ $# -ge 4 ]; then D_LIST=$4; fi
if [ $# -ge 5 ]; then N_LIST=$5; fi



for p in "${parties[@]}"; do
    # Step 1: Compile the program (No extra arguments passed)
    echo "Compiling $PROGRAM..."
    ./compile.py $PROGRAM $p $N $D "$D_LIST" "$N_LIST" || { echo "Compilation failed"; exit 1; }

    # Step 2: Run parties in parallel with dynamic arguments
    echo "Running $p parties in parallel with parameters: n=$N, d=$D"

    # Generate the correct executable name
    EXECUTABLE="${PROGRAM}-${p}-${N}-${D}-${D_LIST}-${N_LIST}"
    for ((i=0; i<p; i++)); do
        ./lowgear-party.x -N $p -p $i $EXECUTABLE  &> NAIVE-PROTOCOL-party_$i-parties-$p-samples$N.log &
        PIDS[$i]=$!
    done

    # Step 3: Wait for all parties to complete
    echo "Waiting for all parties to complete..."
    for pid in "${PIDS[@]}"; do
        wait $pid
    done

    echo "All parties finished execution."
done
