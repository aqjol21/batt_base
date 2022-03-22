"""Generation of fake data for the first level debugf of the interface
    __author__ : guillaume
    __date__   : 11 03 2022 
"""


import random
from unicodedata import name
import time
from xml.dom.pulldom import START_DOCUMENT
import datetime
import pandas as pd
from os import getcwd, path, listdir

users        = ["Pietro", "Emil", "Enrico","Shubham","Chiara","Guillaume"]
devicesNames = ["BCS-A","BCS-B","BCS-C","BCS-D","Arbin","DM-200","DM-340","ESPEC", "ITECH-1", "ITECH-2","REGATRON"]
channels     = [8,8,8,8, 20, 1, 1, 1 ,1 ,1 ,1 ]
test_type    = ['performance', 'cycling', 'eis', "" ]
cell_type    = ['kokam', 'LG-pouch', 'Samsung18650','SK-prismatic']
fileNames    = [ fileName for fileName in listdir(path.join("app","files")) if path.isfile(path.join("app","files", fileName)) ]




class schedule():
    def __init__(self, deviceNb, lastWeeknB):
        # current_week = datetime.datetime.today().isocalendar()[1]
        weeks = lastWeeknB -datetime.datetime.today().isocalendar()[1]
        # for chanel in range(channels[deviceNb]):
    
    

    @staticmethod
    def get_schedules():
        # current_week = datetime.datetime.today().isocalendar()[1]
        
        def get_sched():
            lim = [random.randint(1,3)]
            for _ in range(random.randint(0,4)):
                lim.append(random.randint(1,3))
            return( [{'len': lim[_], 'state': lim[_]%2== 0,'test_name':random.choice(fileNames), 'test_type':random.choice(test_type[:-1]), 'test_id':random.randint(1,255) ,'user':random.choice(users) } for _ in range(len(lim)) ], sum(lim)  )

        schedules = []
        for d,device_ in enumerate(devicesNames):
            device_ = {'name': device_, 'channels':[], 'maxWeek':0}
            for chan in range(channels[d]):
                sched, length = get_sched()
                device_['channels'].append(sched)
                device_['maxWeek'] = device_['maxWeek'] if device_['maxWeek'] > length else length

            

            schedules.append(device_)  
        return(schedules)
    	


class device():
    def __init__(self, name, channels, users):
        self.name    = name
        self.channels = [ {"State":True, "User" : random.choice(users)}  if random.random()>0.5 else {"State":False, "User" :""} for _ in range(channels)]
        self.utilization = sum([1 for channel in self.channels if channel['State'] == True]) / channels *100

    @staticmethod
    def getDevices():
        return( [ device(devicesNames[_], channels[_],users) for _ in range (len(devicesNames)) ] )



class test():
    def __init__(self, type_1, device, channel, start, end, temp, cell, id_, file, type_2,device2=None,device3=None ):
        self.type_1  = type_1
        self.type_2  = type_2
        self.channel = channel
        self.device  = device
        self.device2  = device2
        self.device3  = device3
        self.start   = start
        self.end     = end
        self.temp    = temp
        self.cell    = cell
        self.id      = id_
        self.file    = file

    @staticmethod
    def get_tests(testnumber):
        tests = []
        for _ in range(testnumber):
            type_1     = test_type[random.randrange(len(test_type)-1)]
            type_2     = test_type[random.randrange(len(test_type))]
            if type_2 == type_1:
                type_2 = test_type[-1]
            dev_index  = random.randrange(5)
            device     = devicesNames[dev_index]
            device2    = devicesNames[random.randint(5,8)] if random.random() > 0.5 else None
            device3    = devicesNames[random.randint(8,len(devicesNames)-1)] if (type_1 == 'eis' or type_2=='eis') else None
            channel    =  random.randrange(channels[dev_index])
            start_date = random_date("1/1/2022 9:00 AM", "31/12/2022 7:00 PM", random.random())
            end_date   =  random_date(start_date, "31/12/2022 7:00 PM", random.random())
            temp       = random.randint(-40,120)
            cell       = random.randint(0,4096)
            id_        = random.randint(0,256)
            file       = random.choice(fileNames)

            tests.append( test(type_1,device,channel,start_date,end_date,temp,cell, id_, file, type_2, device2, device3 ) )
        return(tests)

class campain():
    def __init__(self, name, tests, user):
        self.name = name
        self.tests = tests
        self.user = user
        check = False
        for test in tests:
            if datetime.datetime.today() < datetime.datetime.strptime( test.end, '%d/%m/%Y %I:%M %p'):
                check = True
        self.status = check

    @staticmethod
    def get_campains():
        campains = []
        for _ in range (10):
            campains.append(campain("campain_"+str(_),test.get_tests(random.randint(1,5)),random.choice(users)))
        return(campains)

class cell():
    def __init__(self):
        self.id       = random.randint(0,4096)
        self.type     = random.choice(cell_type)
        self.device   = random.choice(devicesNames)
        self.user     = random.choice(users)
        self.last     = random_date("1/1/2021 9:00 AM", "31/12/2021 7:00 PM", random.random())
        self.end      = random_date("1/5/2022 9:00 AM", "31/12/2022 7:00 PM", random.random())
        self.location = "shelf_"+str(random.randint(1,10))

    @staticmethod
    def get_cells():
        return([ cell() for _ in range(random.randint(0,50))])  




# class schedule():
#     @staticmethod
#     def format_schedule():
#         # dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Resource="Alex"),
#         # dtype = [('task','U25' ),('Start','U25' ),('Finish','U25' ),('Resource','U25' )]
#         table = []
#         booking = 0
#         for d, device in enumerate(devicesNames):
#             for channel in range(channels[d]):
#                 start = (datetime.datetime.today() +datetime.timedelta(days=random.randint(2,10))) .strftime('%Y-%m-%d')
#                 for _ in range(random.randint(2,5)):
#                     end = (datetime.datetime.strptime( start, '%Y-%m-%d')+datetime.timedelta(days=random.randint(2,10))).strftime('%Y-%m-%d')
#                     table.append(dict(Task = "Job "+str(booking), Start = start, Finish = end, Resource = device+": channel "+str(channel)))
#                     booking += 1
#                     start = (datetime.datetime.strptime( end, '%Y-%m-%d')+datetime.timedelta(days=random.randint(2,10))).strftime('%Y-%m-%d')
#                 end = (datetime.datetime.strptime( start, '%Y-%m-%d')+datetime.timedelta(days=random.randint(2,10))).strftime('%Y-%m-%d')
#                 table.append(dict(Task = "Job "+str(booking), Start = start, Finish = end, Resource = device+": channel "+str(channel)))
#         return(pd.DataFrame( table))


        
#         #    )   for _ in range(random.randrange(1, 7, 2))]


def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d/%m/%Y %I:%M %p', prop)


def random_string():
    rd_string = ''
    for _ in range(10):
        random_integer = random.randint(0, 255)
        rd_string += (chr(random_integer))
    return(rd_string+".csv")


