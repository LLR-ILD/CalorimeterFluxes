#!/bin/bash

ILCSOFT_VERSION=v02-02-02

OUTPUT_PATH=${1}
PROCESS=${2}
PROCESSLOG=${3}
NEVENTS=${4}
SKIPEVTS=${5}
NPROCS=${6}
BASE_PATH=${7}

# STDHEP_PATH="$BASE_PATH/$PROCESS"
STDHEP_PATH="$BASE_PATH/" 
INPUT_FILE="${PROCESS}.stdhep"

OUTPUT_PATH="${OUTPUT_PATH}/${PROCESSLOG}/"
OUTPUT_FILE="fullSim_${PROCESS}_${SKIPEVTS}+${NEVENTS}.slcio"

GEOM_XML="parameters/ILD_l5_v02.xml"
STEERING="parameters/ddsim_steer.py"

source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/${ILCSOFT_VERSION}/init_ilcsoft.sh

# Ensure that the OUTPUT_PATH directory exists
mkdir -p "${OUTPUT_PATH}"

# Parallel processing
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