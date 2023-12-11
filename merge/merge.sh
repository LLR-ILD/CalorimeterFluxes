 # Initialize an empty array
file_list=()

# Loop through numbers 1 to 100
for i in {1..2}
do
    # Construct the filename with the current number
    file_name="/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/Machine/beamstrahlung_FCCee@91GeV/ILD_l5_v11gamma/pairs-${i}_ZatIP_tpcTimeKeepMC_keep_microcurlers_10MeV_30mrad_ILD_l5_v11gamma.slcio"

    # Check if the file exists
    if [ -f "$file_name" ]; then
        # Add the file to the array
        file_list+=("$file_name")
    fi
done

# If you want to print the list of files
# echo "List of files:"
# printf '%s\n' "${file_list[@]}"

lcio_merge_files output_file.slcio $file_list