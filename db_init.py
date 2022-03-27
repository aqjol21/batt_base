from unicodedata import name
from app import db
from app.models import Device, Channel,Test_type
from tqdm import tqdm

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()


def db_init():
    f = open("devices_init.csv", 'r')
    lines = f.readlines()
    devices = [line.replace("\n","").split(",") for line in lines]
    for device in tqdm(devices, desc="Filling devices table"):
        dev = Device(name = device[0], number_channels= int(device[1]), company= device[2], datasheet_link=device[3], details = device[4])
        db.session.add(dev)
        db.session.commit()
        print("added ", device)

    devices = Device.query.all()
    for device in tqdm(devices, desc="Filling channel table"):
        for channel in range(device.number_channels):
            chan = Channel(chan_number = channel, status=True, device_id=device.id)
            db.session.add(chan)
            db.session.commit()
    
    test_types = ['performance', 'cycling', 'eis', 'aging' ]
    for type in tqdm(test_types, desc="Filling test_type table"):
        test = Test_type(name=type)
        db.session.add(test)
        db.session.commit()

if __name__ == "__main__":
    
    print("Filling up default data")
    db_init()
    print("Done")