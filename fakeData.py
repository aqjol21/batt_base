"""Generation of fake data for the first level debugf of the interface
    __author__ : guillaume
    __date__   : 11 03 2022 
"""


import random
from unicodedata import name
import time
from xml.dom.pulldom import START_DOCUMENT
import datetime
# import pandas as pd
from os import getcwd, path, listdir
import os

users         = ["PII", "SBH", "CBO"]
devicesNames  = ["BCS-A","BCS-B","BCS-C","BCS-D","Arbin","DM-200","DM-340","ESPEC", "ITECH-1", "ITECH-2","REGATRON"]
channels      = [8,8,8,8, 20, 1, 1, 1 ,1 ,1 ,1 ]
test_types    = ["",'performance', 'cycling', 'eis']
cell_types    = ['kokam', 'LG-pouch', 'Samsung18650','SK-prismatic']
cell_names    = [ cell_types[i%len(cell_types)][:2]+str(random.randint(1,5)) for i in range (50)]
fileNames     = [ fileName for fileName in listdir(path.join("app","files")) if path.isfile(path.join("app","files", fileName)) ]
projects      = ["PhD pii","PhD sbh","Batman","Spartacus ","Spet_characterization","Spet_performance","Apple_pie","Ice_cream"]
chambers      = ['ESPEC-ARU1100', 'ACS-DM1200T','ACS-DM340C']
campaigns     = ['0017','0032', '0016','0025','0008','0007','1001','2001']
locations     = ["box_"+str(i) for i in range(10)]
pcbs_type     = ["Battman (v1)", "Robin (v2)", "Spartacus (v3)"]


def deviceIndex():
    devices = [ {'name'       : devicesNames[i],
                 'utilization': random.randrange(0,100,1),
                 'channels'   : [ 
                                  {'status': bool(random.randint(0,1)), 
                                   'user'  : random.choice(users)} for i in range(channels[i])]
                                   } 
                                  for i in range (len(devicesNames))]
    return(devices)

def testTestlist(nbSamples=100):
    start = datetime.datetime.today()
    tests = [ { 'name'       : "test_"+str(i), 
                'type_1'     : random.choice(test_types[1:]),
                'type_2'     : random.choice(test_types),
                'user'       : random.choice(users),
                'project'    : random.choice(projects),
                'start'      : start,
                'end'        : start if random.randint(0,1) else start+datetime.timedelta(days=random.randint(0,15)),
                'device'     : devicesNames[i%len(devicesNames)],
                'channel'    : random.randint(0, channels[i%len(devicesNames)]),
                'chamber'    : random.choice(chambers) if random.randint(0,1) else "",
                'eis'        : "Regatron TC.GSS.20.600.400.S" if random.randint(0,1) else "",
                'cell_type'  : cell_types[i%len(cell_types)],
                'cell_name'  : random.choice(cell_names),
                'campaign'   : random.choice(campaigns),
                'status'     : True,
                'temp'       : -255,
                'cycler'     : random.choice(os.listdir("app/files")),
                'cms'        : random.choice(os.listdir("app/files"))
                                }

              for i in range(nbSamples)]
    for test in tests:
        if test['end'] == test['start']:
            test['status'] = False
        if test['chamber'] != "":
            test['temp'] = random.randint(-40,120)

    return(tests)

def cellList():
    cells = [{ 'id'           : i,
               'name'         : cell_names[i],
               'type'         : cell_types[i%len(cell_types)],
               'under_use'    : bool(random.randint(0,1)),
               'end'          : datetime.datetime.today()-datetime.timedelta(days=random.randint(1,10)),
               'device'       : devicesNames[i%len(devicesNames)],
               'channel'      : random.randint(0, channels[i%len(devicesNames)]), 
               'user'         : random.choice(users),
               'location'     : random.choice(locations)
            }
    for i in range(len(cell_names))]
    return(cells)

def pcbList():
    pcbs = [{   'id'        : i,
                'type'      : pcbs_type[i%len(pcbs_type)],
                'name'      : pcbs_type[i%len(pcbs_type)][:3]+"_"+str(i),
                'under_use' : bool(random.randint(0,1)),
                'end'       : datetime.datetime.today()-datetime.timedelta(days=random.randint(1,10)),
                'user'      : random.choice(users),
                'location'  : random.choice(locations),
                'firmware'  : str(random.randint(1,3))+"_"+str(random.randint(0,4))+"_"+str(random.randint(1,5))
    }
    for i in range(20)]
    return(pcbs)
def scheduleList():
    schedules = [{  'name'     : devicesNames[i],
                    'channels' : [ { 'booked' : bool(random.randint(0,1)),
                                     'type'   : random.choice(test_types),
                                     'user'   : random.choice(users),
                                     'name'   : "a name later"
                                    } for chan in range(channels[i]) ],
                    'start'    : datetime.datetime.today(),
                    'end'      : datetime.datetime.today()+datetime.timedelta(days=random.randint(0,5))
                        
                  }
                 for i in range(len(devicesNames)) ]


    schedules.extend( [{  'name'     : devicesNames[i],
                    'channels' : [ { 'booked' : bool(random.randint(0,1)),
                                     'type'   : random.choice(test_types),
                                     'user'   : random.choice(users),
                                     'name'   : "a name later"
                                    } for chan in range(channels[i]) ],
                    'start'    : schedules[i]['start']+ datetime.timedelta(days=random.randint(0,5)),
                    'end'      : schedules[i]['end']+datetime.timedelta(days=random.randint(5,8))
                        
                  }
                 for i in range(len(devicesNames)) ] )


  
    return(schedules)