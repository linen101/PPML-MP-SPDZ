#!/bin/bash

# Default values
M=2            # Number of parties
PROGRAM="benchmark-fhe"


# Check fo provided command-line arguments
if [ $# -ge 1 ]; then M=$1; fi


# Step 1: Compile the program (No extra arguments passed)
echo "Compiling $PROGRAM..."
./compile.py --mixed --edabit -F 200 -P 6427752177035961102167848369364650410088811975131171341205571 $PROGRAM $M  || { echo "Compilation failed"; exit 1; }
#./compile.py -F 200 $PROGRAM $M  || { echo "Compilation failed"; exit 1; }

# Step 2: Run parties in parallel with dynamic arguments
echo "Running $M parties in parallel for fhe"

# Generate the correct executable name
EXECUTABLE="${PROGRAM}-${M}"

for ((i=0; i<M; i++)); do
    ./malicious-shamir-party.x --bucket-size 5 -N $M -p $i $EXECUTABLE  &
    PIDS[$i]=$!
done

# Step 3: Wait for all parties to complete
echo "Waiting for all parties to complete..."
for pid in "${PIDS[@]}"; do
    wait $pid
done

echo "All parties finished execution."
