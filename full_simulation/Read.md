Full Simulation
================
After generating the physics processes at the generator level in step 1, a full simulation (detector-level simulation) is applied here. The initial input is in ```.stdhep.gz``` extension which is what is obtained from running the [EventProducer](https://github.com/HEP-FCC/EventProducer#eventproducer) package package and the output is in ```.slcio``` extension which gives the file format of [LCIO](https://github.com/iLCSoft/LCIO) package (Event-Data Model). 

How to use
================
Initially, navigate to this directory. 

__Step 1:__ Change the extension from ```.stdhep.gz``` to ```.stdhep```.  <br>
Run the bash script ```gunzip.sh```. It is structured such that there is a parent directory containing daughter directories. The daughter directories contain the ```.stdhep.gz``` files such that each daughter directory corresponds to a separate process. It is to be run with 2 arguments: the first one is the path to the parent directory and the second one is the name of the selected daughter directory (the directory containing a specific process generator-level simulation with ```.stdhep.gz``` extension). Use the following command:
```
 bash gunzip.sh /path/to/the/parent/directory <process (daughter directory) name>
```
__Step 2:__ Running the full simulation.  <br>
Run the bash script ```parallel_processing_simulation.sh```. The script is written such that it runs the simulation in parallel processing to reduce the running time. The script is to be run with 6 arguments.  <br>
1. The parent directory in which the ```.stdhep``` file is saved which is the same as the parent directory of step 1. 
2. The parent diectory in which the outputs of all processes would go. 
3. The process name. This is the same as the process name of step 1 which is the daughter directory name distinct for distinct processes. The output will have each process in a subdirectory with the name of the process. All the subdieectories of the outputs will go in the parent directory of the outputs (argument 2). Thus, the process name is common for the subdirectories of the inputs and the outputs. 
4. Total number of events to be simulated. This shouldn't exceed the number of events simulated at the generator level.
5. The number of events to be skipped. This is usually set to 0 unless for special circumstances, the user wants to skip some events from the ```.stdhep``` file.
6. Number of parallel process. This depends on how many processors the user has. It must be noted that the number per process would be equal to (the total number / the number of processes) so that the number of parallel processes must be chosen such that it divides the total number (gives and integer from the formula above).
The command would be like this:
```
bash parallel_processing_simulation.sh <inputs parent directory> <inputs parent directory> <The process name> <Total number of events> <skipped events number> <number of parallel processes>
```
It is preferred to run it in a screen because the full simulation takes hours or days to finish for large numbers of events. For each parallel process, a ```.slcio``` file is produced along with a log file so that the user can follow the progress. 

__Step 3:__ Cross-checking.  <br>
Sometimes, some problems arise in the simulation especially because the running time is huge and there are many parallel processes to handle. Thus, it is important to cross-check that all the produced ```.slcio``` files are as expected. For example, let's say that in step 2, 10000 events were generated in 25 parallel processes. The expected results is 25 ```.slscio``` files with 400 events each (10000/25). To check this, run the ```counter.py``` script with the following 5 arguments:
1. parent path of the output files (argument 2 in step 2)
2. process name (argument 3 in step 2)
3. skipped events (argument 5 in step 2)
4. total events (argument 4 in step 2)
5. number of parallel processes (argument 6 in step 2). 
Arguments 3 and 4 affect how the ```.slcio``` files are named. Now, the script with this command:
```
python counter.py <parent path> <process name> <skipped events> <total events> <parallel processes number>
```
would print the slcio files names each with the contained events. If you find the number to be less than the expected, you need to get complementary ```.slcio``` files to substitute the missing events. 

__Step 4:__ Producing the complementary files.  <br>
If no problems happened and the cross-chekc produced the expected results, you are done. If not, you need to produce the complementary files. Run the ```complementary_simulation.py``` script with exactly the same arguments as counter.py but with the additional argument at the end (6th argument) of the parent directory of the ```.stdhep``` file (argument 1 in step 2).

__Step 5:__ Cross-cheking.  <br>
Cross check using ```counter_total.py``` script. Run it using exactly the same arguments as ```counter.py```. This script will give you a list of the total events of the initially ```.slcio``` files added with their complementary counterparts produced in step 4. 
