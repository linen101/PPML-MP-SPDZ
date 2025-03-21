#!/bin/bash

# Default values
parties=(3 4)          # Number of parties
N_LIST="1000,10000,100000" # Samples list
PROGRAM="median_mpc"

# Check fo provided command-line arguments
if [ $# -ge 1 ]; then parties=$1; fi
if [ $# -ge 2 ]; then N_LIST=$2; fi


for p in "${parties[@]}"; do

# Step 1: Compile the program (No extra arguments passed)
    echo "Compiling $PROGRAM..."
    ./compile.py $PROGRAM $p "$N_LIST" || { echo "Compilation failed"; exit 1; }

    # Step 2: Run parties in parallel with dynamic arguments
    echo "Running $p parties in parallel with parameters: n=$N_LIST"

    # Generate the correct executable name
    EXECUTABLE="${PROGRAM}-${p}-${N_LIST}"

    for ((i=0; i<p; i++)); do
        ./lowgear-party.x -N $p -p $i $EXECUTABLE  &> median_mpc_party_$i-parties-$p.log &
        PIDS[$i]=$!
    done

    # Step 3: Wait for all parties to complete
    echo "Waiting for all parties to complete..."
    for pid in "${PIDS[@]}"; do
        wait $pid
    done

    echo "All parties finished execution."
done
