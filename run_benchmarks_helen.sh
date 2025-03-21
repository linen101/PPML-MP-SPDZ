#!/bin/bash

# Default values
parties=(2)            # Number of parties
D_LIST="25,50,75,100"  # Features list

PROGRAM="bench_helen"

# Check fo provided command-line arguments
if [ $# -ge 1 ]; then parties=$1; fi

if [ $# -ge 2 ]; then D_LIST=$4; fi

for p in "${parties[@]}"; do

    # Step 1: Compile the program (No extra arguments passed)
    echo "Compiling $PROGRAM..."
    ./compile.py $PROGRAM $p "$D_LIST" || { echo "Compilation failed"; exit 1; }

    # Step 2: Run parties in parallel with dynamic arguments
    echo "Running $p parties in parallel with parameters: n=$N, d=$D"

    # Generate the correct executable name
    EXECUTABLE="${PROGRAM}-${p}-${D_LIST}"

    for ((i=0; i<p; i++)); do
        ./lowgear-party.x -N $p -p $i $EXECUTABLE  &> party_$i-parties-$p-helen.log &
        PIDS[$i]=$!
    done
    # Step 3: Wait for all parties to complete
    echo "Waiting for all parties to complete..."
    for pid in "${PIDS[@]}"; do
        wait $pid
    done
    echo "All parties finished execution."

done
