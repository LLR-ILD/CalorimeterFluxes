How to use
=============
The Whizard cards are integrated with Pythia for hadronization through [EventProducer]([https://www.example.com](https://github.com/HEP-FCC/EventProducer#eventproducer)https://github.com/HEP-FCC/EventProducer#eventproducer) package.
To run it, follow the ```Read.md``` file on the GitHub repository of the package. First, clone it and source ./init.sh as explained there after which run it using the follwing command:
``` 
python3 ~/EventProducer/bin/run.py --FCCee --STDHEP --send --local --typestdhep wzp6 -p <process> -n <number of events> -N <number of jobs> -q <queue> --prodtag <prodtag> >> /path/to/luminosity_log_files_directory/<process>.log 2>&1 &
```
The package is more generic but we have made some specifcations: 
1) The jobs are sent locally, not on the grid.
2) The produced format of the output files is STDHEP.
3) The input format is wzp6 for using Whizard cards.

It must be noted that [EventProducer]([https://www.example.com](https://github.com/HEP-FCC/EventProducer#eventproducer)https://github.com/HEP-FCC/EventProducer#eventproducer) must have some modifications as described in the ```Read.md``` files of the package like placing the whizard cards in ```/eos/experiment/fcc/ee/generation/gridpacks/``` and adding the desired processes in ```config/param_FCCee.py```. Any other local directories for the outputs and the inputs are ok as well. 
