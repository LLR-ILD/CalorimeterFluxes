#!/bin/bash

BASE_PATH=${1}
PROCESS=${2}
 
# Loop over directories matching the pattern
for dir in "$BASE_PATH/$PROCESS"; do
    # Ensure the matched name is a directory
    if [[ -d "$dir" ]]; then
        # Get the name of the directory
        dir_name=$(basename "$dir")
        echo "Processing directory $dir_name..."

        # Find the gz file in the directory
        gz_file=$(find "$dir" -name '*.gz' -print -quit)
        if [[ -n "$gz_file" ]]; then
            # Decompress the file and rename it
            echo "Decompressing $gz_file..."
            gunzip -c "$gz_file" > "$dir/$dir_name.stdhep"
            rm "$gz_file"
        else
            echo "No .gz file found in $dir_name!"
        fi
    fi
done

echo "Done!"
