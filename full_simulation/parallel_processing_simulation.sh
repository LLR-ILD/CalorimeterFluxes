#!/bin/bash

ILCSOFT_VERSION=v02-02-02

PROCESS=${1}
NEVENTS=${2:-150}
SKIPEVTS=${3:-9600}

STDHEP_PATH="/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/stdhep/GeV365/${PROCESS}/" #replace with the path to the stdhep file.
INPUT_FILE="${PROCESS}.stdhep"

OUTPUT_PATH="/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/${PROCESS}/" #replace with the path to the output slcio files.
OUTPUT_FILE="fullSim_${PROCESS}_${SKIPEVTS}+${NEVENTS}.slcio"

GEOM_XML="/home/llr/ilc/hassouna/script2/CalorimeterFluxes/full_simulation/parameters/ILD_l5_v02.xml"
STEERING="/home/llr/ilc/hassouna/script2/CalorimeterFluxes/full_simulation/parameters/ddsim_steer.py"

source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/${ILCSOFT_VERSION}/init_ilcsoft.sh

# Ensure that the OUTPUT_PATH directory exists
mkdir -p "${OUTPUT_PATH}"

# Parallel processing
NPROCS=1
EVENTS_PER_PROC=$((NEVENTS / NPROCS))

for i in $(seq 0 $((NPROCS-1))); do
    current_skip=$((SKIPEVTS + i * EVENTS_PER_PROC))
    current_output="${OUTPUT_PATH}partial_${i}_${OUTPUT_FILE}"
    current_log="${OUTPUT_PATH}partial_${i}_${OUTPUT_FILE}.log"

    ddsim --inputFiles ${STDHEP_PATH}${INPUT_FILE} --outputFile ${current_output} \
    --compactFile ${GEOM_XML} \
    --numberOfEvents ${EVENTS_PER_PROC} \
    --skipNEvents ${current_skip} \
    --steeringFile ${STEERING} > ${current_log} 2>&1 &
done