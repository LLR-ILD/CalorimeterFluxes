ILCSOFT_VERSION=v02-02-02

#STDHEP_PATH="/eos/experiment/fcc/ee/generation/stdhep/winter2023/"
#INPUT_FILE="wzp6_ee_qqH_ecm240/events_088604297.stdhep.gz"
#STDHEP_PATH="/eos/experiment/fcc/ee/generation/hepmc/p8_ee_Zud_ecm91/"
#INPUT_FILE="events_noVtxSmear.hepmc"
STDHEP_PATH="data/StdHep/FCC/output1/"
INPUT_FILE="output1.hepevt"
NEVENTS=${1:-10}
SKIPEVTS=${2:-0}

OUTPUT_PATH="data/StdHep/FCC/"
OUTPUT_FILE="fullSim1_${SKIPEVTS}+${NEVENTS}.slcio"

#GEOM_XML="/afs/cern.ch/work/l/lportale/public/fcc_studies/FCCDetectors/Detector/DetFCCeeCLD/compact/FCCee_o2_v02/FCCee_o2_v02.xml"
GEOM_XML=./ILD_l5_v02.xml
STEERING="./ddsim_steer.py"

source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/${ILCSOFT_VERSION}/init_ilcsoft.sh

ddsim --inputFiles ${STDHEP_PATH}${INPUT_FILE} --outputFile ${OUTPUT_PATH}${OUTPUT_FILE} \
	--compactFile ${GEOM_XML} \
    --numberOfEvents ${NEVENTS} \
	--skipNEvents ${SKIPEVTS} \
	--steeringFile ${STEERING} # > ${OUTPUT_PATH}${OUTPUT_FILE}.log 2>&1 &
