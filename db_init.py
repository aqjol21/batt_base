from unicodedata import name
from app import db
from app.models import Campaign, Device, Channel,Test_type,Cell_type, User, Cell, Test, Project, SingleTest,Device_type, Location
from tqdm import tqdm

import calendar, random, datetime

def randomdate(year, month):
    dates = calendar.Calendar().itermonthdates(year, month)
    return random.choice([date for date in dates if date.month == month])

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()


def db_init():
    deviceTypes = ["cell cycler","module cycler", "pack cycler", "temperature chamber", "EIS"]
    for deviceType in tqdm(deviceTypes,desc="Filling device types table"):
        type_ = Device_type(name = deviceType)
        db.session.add(type_)
        db.session.commit()

    f = open("devices_init.csv", 'r')
    lines = f.readlines()
    devices = [line.replace("\n","").split(",") for line in lines]
    for device in tqdm(devices, desc="Filling devices table"):
        dev = Device(name = device[0], number_channels= int(device[1]), company= device[2], datasheet_link=device[3], details = device[4])
        types = device[5:]
        
        for type_ in types:
            type__ = Device_type.query.filter_by(name=type_).first()
            if type__ != None:
                dev.type.append(type__)
        db.session.add(dev)
        db.session.commit()

    devices = Device.query.all()
    for device in tqdm(devices, desc="Filling channel table"):
        for channel in range(device.number_channels):
            chan = Channel(chan_number = channel, status=False, device_id=device.id)
            db.session.add(chan)
            db.session.commit()
    
    locations = [ "box_"+str(i) for i in range (5) ]
    for location in tqdm(locations, desc="Filling locations"):
        loc = Location(name=location)
        db.session.add(loc)
        db.session.commit()

    test_types = ['performance', 'cycling', 'EIS', 'aging',"cycling","characterization" ]
    for type in tqdm(test_types, desc="Filling test_type table"):
        test = Test_type(name=type)
        db.session.add(test)
        db.session.commit()

    users = ['pii', 'sbh', 'cbo']
    for user in tqdm(users, desc="Filling users table"):
        us = User(username=user)
        us.set_password("1111")
        db.session.add(us)
        db.session.commit()

    projects = ["PhD pii","PhD sbh","Batman","Spartacus ","Spet_characterization","Spet_performance","Apple_pie","Ice_cream"]
    for project in tqdm(projects, desc="Filling projects table"):
        pr = Project(name = project)
        db.session.add(pr)
        db.session.commit()

    cell_types =[ ["LG chem"," INR21700 M50"], ["Kokam"," SLPB065070180"], ["Leclanche"," 936A03"],["Samsung ","INR21700-50E"]]
    for type in tqdm(cell_types, desc="Filling cell types table"):
        cell = Cell_type(model = type[1], maker=type[0])
        db.session.add(cell)
        db.session.commit()
    

    cell_types = Cell_type.query.all()
    cells = [["L03", "L26","L17","L16","L20","L34","L38","L29","L39","L31","L27","LG01","LG02","LG03","LG04","LG05","LG06","LG20"],
             ["KOK05","KOK02","KOK13","03","04","05","06","07","08","09","10","11","12"],
             ["LecNMC25","LecNMC26","LecNMC27","LecNMC99"],
             ["SA02","SA03","SA01","SA04","SA05","SA06"]]
    for i, type in enumerate(tqdm(cell_types, desc="Filling cells units")):
        for cell in cells[i]:
            ce = Cell(model_id=type.id, name=cell,purchase_date=randomdate(2021,random.randint(1,12)),under_use=False) 
            db.session.add(ce)
            db.session.commit()
    
    campaigns = ['0017','0032', '0016','0025','0008','0007','1001','2001']
    for campaign in tqdm(campaigns, desc="Filling campain"):
        camp = Campaign(name=campaign)
        db.session.add(camp)
        db.session.commit()
    
    campaigns = Campaign.query.all()
    tests     = [ ['6_2'],['1_2'],['3_3'],['1_4'],['2_1'],['3_1'],['1_1'],['3_2'] ]
    authors    = ["pii","sbh","cbo","cbo","pii","cbo","pii","pii"]
    projects    = [ "PhD pii", "PhD sbh", "Batman", "Spartacus ", "Spet_characterization", "Spet_performance", "Apple_pie", "Ice_cream" ]
    temps       = [20,20,5,None,40,0,180,-20]
    starts      = ["2/16/2022","2/16/2022","2/26/2021","5/28/2021","2/9/2019","2/22/2019","3/16/2022","3/16/2022"]
    ends        = ["5/18/2022","2/18/2022","3/3/2021","6/3/2021","2/21/2019","3/5/2019","9/16/2022","3/16/2022"]
    types1      = ["cycling","characterization","characterization","characterization","performance","characterization","performance","cycling"]
    types2      = [None,"EIS","EIS","EIS",None,"EIS","EIS",None]
    chambers    = ["ACS-DM1200T","ACS-DM340C","ACS-DM1200T","","ACS-DM1200T","ACS-DM1200T","ESPEC-ARU1100","ESPEC-ARU1100"]
    eiss        = ["","","","","","", 'Regatron TC.GSS.20.600.400.S', "Regatron TC.GSS.20.600.400.S"]

    cells     = [[ "L03", "L26", "L17","L16","L20","L34","L38","L29","L39","L31","L27"],
                [ "KOK05","KOK02","KOK13"],
                ["LecNMC25","LecNMC26","LecNMC27"],
                ["03","04","05","06","07","08","09","10","11","12"],
                ["SA02","SA03","SA01"],
                ["LG01","LG02","LG03"],
                ["SA04","SA05","SA06"],
                ["LG04","LG05","LG06"],
                ["LG20","LG20"],
                ["LecNMC99"]]
    filesnames = [["FD1cv_100d","FD1cv_100d","FD1cv_100d","FD1cv_100d","FD1cv_100d","Rcv_100d","R_100d","FD1cv_50d","FC05cv_100d","FC05_100d" ,"FC05cv_50d"],
                ["0032_ocv_mapping_kok_3ch_160222","0032_ocv_mapping_kok_3ch_160222","0032_ocv_mapping_kok_3ch_160222"],
                ["0016_ct_lecNMC_SoC-T","0016_ct_lecNMC_SoC-T","0016_ct_lecNMC_SoC-T"],
                ["0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct","0025_1_4_spartacus_ct"],
                ["0008_sa_2ch_090219","0008_sa_2ch_090219","0008_sa_4ch_090219"],
                ["0008_lg_4ch_090219","0008_lg_2ch_090219","0008_lg_2ch_090219"],
                ["0007_ct_0_sa_090219","0007_ct_0_sa_090219","0007_ct_0_lg_080219"],
                ["0007_ct_0_lg_080219","0007_ct_0_lg_080219","0007_ct_0_sa_090219"],
                ["grandma_apple_pie","grandma_apple_pie"],
                ["grandpa_ice_cream"]]
    devices    = [["BCS-D", "BCS-D","BCS-C","BCS-B","BCS-A","BCS-A","BCS-A","BCS-B","BCS-B","BCS-C","BCS-C"],
                ["BCS-D","BCS-D","BCS-B"],
                ["BCS-A","BCS-C","BCS-D"],
                ["BCS-C","BCS-C","BCS-C","BCS-C","BCS-C","BCS-C","BCS-D","BCS-D","BCS-A","BCS-A"],
                ["BCS-B","BCS-A","BCS-B"],
                ["BCS-C","BCS-C","BCS-A"],
                ["BCS-A","BCS-A","BCS-B"],
                ["BCS-C","BCS-C","BCS-B"],
                ["Arbin LBT21044HC","Arbin LBT21044HC"],
                ["ITECH IT900"]]
    channels   = [[1,2,3,3,3,1,2,1,2,1,2],
                    [6,7,6],
                    [1,1,5],
                    [3,4,5,6,7,8,1,2,7,8],
                    [5,3,1],
                    [1,5,1],
                    [7,8,7],
                    [7,8,8],
                    [1,9],
                    [1]]
    

    for i, campaign in enumerate(tqdm(campaigns, desc="Filling tests table")):
    # for i, campaign in enumerate(campaigns):
        campaign.project =Project.query.filter_by(name=projects[i]).first().id
        db.session.commit()
        for _ , test in enumerate(tqdm(tests[i],desc="Creating tests for campaign "+str(i))): 
        # for _ , test in enumerate(tests[i]):  
            
            author = User.query.filter_by(username=authors[i]).first()
            
            start  = datetime.datetime.strptime(starts[i],"%m/%d/%Y")
            type1  = Test_type.query.filter_by(name=types1[i]).first()
            test   = Test(name=test,
                            campaign_id=campaign.id, 
                            user_id=author.id, 
                            start=start,
                            type_1=type1.id)

            if temps[i]  != None: test.temp = temps[i]
            if ends[i]   == None and test.start < datetime.datetime.today() :
                test.active = True
            else: 
                test.end = datetime.datetime.strptime(ends[i],"%m/%d/%Y")
                if test.end > datetime.datetime.today():
                    test.active = True
                else:
                    test.active = False
            if types2[i] != None: test.type_2 =  Test_type.query.filter_by(name=types2[i]).first().id
            

            db.session.add(test)
            db.session.commit()

            if chambers[i] != "": 
                chamber        = Device.query.filter_by(name=chambers[i]).first() 
                channel        = Channel.query.filter_by(device_id=chamber.id).first()
                channel.status = True
                test.devices.append(chamber)

            if eiss[i] != "": 
                eis            = Device.query.filter_by(name=eiss[i]).first()
                channel        = Channel.query.filter_by(device_id=eis.id).first()
                channel.status = True
                test.devices.append(eis)


            
            for __, cell in enumerate(tqdm(cells[i], desc="Adding batches to test "+str(_))):
            # for __, cell in enumerate(cells[i]):
                cell_          = Cell.query.filter_by(name=cell).first()
                device         = Device.query.filter_by(name=devices[i][__]).first()
                channel        = Channel.query.filter_by(device_id=device.id).filter_by(chan_number=channels[i][__]-1).first() 
                # print(campaign, test,  channel, device, cell, channels[i][__]-1 )
                if test.active == True:
                    channel.status = True
                    cell_.under_use = True
                else: 
                    channel.status = False   
                    cell_.under_use = False   
                    cell_.location=random.choice([loc.id for loc in Location.query.all()])
                cycler_file    = filesnames[i][__]+".csv"
                prototype_file = filesnames[i][__]+"_cms.csv"
                element        = SingleTest(channel_id=channel.id,cell_id=cell_.id,test_id=test.id,cycler_file=cycler_file,prototype_file=prototype_file)
                db.session.add(element)
                db.session.commit()
       
                    

    
if __name__ == "__main__":
    

    print("Filling up default data")
    db_init()
    print("Done")


