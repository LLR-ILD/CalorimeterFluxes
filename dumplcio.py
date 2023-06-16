from pyLCIO import UTIL, EVENT, IMPL, IO, IOIMPL
from pyLCIO.io import LcioReader
import sys
infile = sys.argv[1]
rdr = IOIMPL.LCFactory.getInstance().createLCReader( )
rdr.open( infile )
colname = "ECalEndcapSiHitsEven"
print("number of events by Reader: ",rdr.getNumberOfEvents())
for evt in rdr:
    col = evt.getCollection(colname)
    print(evt, len(col))
    #for p in col:
    #    print(p.getEnergy())
rdr = LcioReader.LcioReader( infile )
ev_stop = rdr.getNumberOfEvents()
for i, event in enumerate(rdr):
    if i < 0:
        continue
    if i >= ev_stop:
        break
    col = evt.getCollection(colname)
    print(i, len(col))
    #for p in col:
    #    print(p.getEnergy())