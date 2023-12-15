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
