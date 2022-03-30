from flask_sqlalchemy import SQLAlchemy
#import logging as lg
from app import app,  db#,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# test_cell_identifier=db.Table('test_cell_identifier', db.Model.metadata,
#     db.Column('cell_id', db.Integer, db.ForeignKey('cell.id')),
#     db.Column('test_id', db.Integer, db.ForeignKey('test.id'))
# )

device_type_identifier=db.Table('association', db.Model.metadata,
    db.Column('device_id', db.Integer, db.ForeignKey('device.id')),
    db.Column('device_type_id', db.Integer, db.ForeignKey('device_type.id'))
)

device_enaged_identifier=db.Table('association2', db.Model.metadata,
    db.Column('device_id', db.Integer, db.ForeignKey('device.id')),
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'))
)


class User(db.Model):
    """Defintion of the users' table in the database
    Attributes
    ----------
    id : String64
        the unique id of each user for databse cross referencement, not seen by the user itself
    username : String64
        name of the user, must be unique as well, user for identification
    password_hash : String64
        hash of the user password stored in the table for authentication and login
    Methods
    -------
    __repr__(self)
        Define the representation of the element when called as it
    __init__(self, username, password_hash)
        Init function of the class, defining the user name and its login
    set_password(self, password)
        set the user password
    check_passwd(self, passwd)
        verify the user's password when login-in
    """
    __tablename__  = 'user'
    id             =  db.Column(db.Integer,primary_key=True)
    username       = db.Column(db.String(64),index=True,unique=True)
    password_hash  = db.Column(db.String(64))

    test_id      = db.relationship('Test', backref='user',lazy='dynamic',foreign_keys="Test.user_id")
    
    def __repr__(self):
        return '{}'.format(self.username) 

    # def __init__(self, username, password_hash):
    #     self.username        = username
    #     self.password_hash   = password_hash    

    def set_passwd(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_passwd(self, password):
        return(check_password_hash(self.password_hash,password))


class Cell_type(db.Model):
    """Defintion of the table in the database contiqning all the models of the cells
    Attributes
    ----------
    id : String64
        the unique id of each model
    model : String64
        model identifier, provided by the manufacturer
    maker : String64
        name of the manufacturer
    anode : String64
        composition of the anode
    cathode : String64
        composition of the cathode
    package : Integer
        type of package
    capacity : float
        battery nominal rated capacity in kWh
    max_dc_current : float
        battery max continuous current in A, according to the datasheet
    max_peak_current : float
        battery max continuous current in A, according to the datasheet
    min_voltage : float
        battery max continuous current in A, according to the datasheet
    max_voltage : float
        battery max continuous current in A, according to the datasheet
    min_temperature : float
        battery max continuous current in A, according to the datasheet
    max_temperature : float
        battery max continuous current in A, according to the datasheet
    note : String256
        battery max continuous current in A, according to the datasheet
    
    """
    __tablename__      = 'cell_type'
    id                 = db.Column(db.Integer,primary_key=True)
    model              = db.Column(db.String(64),index=True,unique=True)
    maker              = db.Column(db.String(64))
    anode              = db.Column(db.String(64))
    cathode            = db.Column(db.String(64))
    package            = db.Column(db.String(64))
    capacity           = db.Column(db.Float)
    max_dc_current     = db.Column(db.Float)
    max_peak_current   = db.Column(db.Float)
    min_voltage        = db.Column(db.Float)
    max_voltage        = db.Column(db.Float)
    min_temperature    = db.Column(db.Float)
    max_temperature    = db.Column(db.Float)
    note               = db.Column(db.String(256))
    
    model_id           = db.relationship('Cell', backref='cell_type',lazy='dynamic',foreign_keys="Cell.model_id")
    def __repr__(self):
        return '{}'.format(self.maker)  + " " +'{}'.format(self.model)

class Cell(db.Model):
    __tablename__ = 'cell'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64),unique=True)
    model_id      = db.Column(db.Integer, db.ForeignKey('cell_type.id'))
    purchase_date = db.Column(db.DateTime(timezone=True))
    under_use     = db.Column(db.Boolean)

    def __repr__(self):
        return '{}'.format(self.name)  
    

class Channel(db.Model):
    __tablename__ = 'channel'
    id            = db.Column(db.Integer,primary_key=True)
    chan_number   = db.Column(db.Integer)
    status        = db.Column(db.Boolean)
    device_id     = db.Column(db.Integer, db.ForeignKey('device.id'))

    single_test_id = db.relationship('SingleTest', backref='channel_test',lazy='dynamic',foreign_keys="SingleTest.channel_id")

    def __repr__(self):
        return 'channel :{}'.format(self.chan_number)  +' device: {}'.format(self.device_id)
    

class Device(db.Model):
    __tablename__   = 'device'
    id              = db.Column(db.Integer,primary_key=True)
    name            = db.Column(db.String(64),index=True,unique=True)
    number_channels = db.Column(db.Integer)
    company         = db.Column(db.String(64))
    datasheet_link  = db.Column(db.String(64))
    details         = db.Column(db.String(64))

    type            = db.relationship("Device_type", secondary=device_type_identifier)
    channel_id      = db.relationship('Channel', backref='device_channel',lazy='dynamic',foreign_keys="Channel.device_id")

    def __repr__(self):
        return '{}'.format(self.name)  



class Test(db.Model):
    __tablename__ = 'test'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64))
    
    description   = db.Column(db.String(512))    
    start         = db.Column(db.DateTime(timezone=True))
    end           = db.Column(db.DateTime(timezone=True))
    temp          = db.Column(db.Float)
    active        = db.Column(db.Boolean)

    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'))
    campaign_id   = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    type_2        = db.Column(db.Integer, db.ForeignKey('test_type.id'))
    type_1        = db.Column(db.Integer, db.ForeignKey('test_type.id'))

    devices       = db.relationship("Device", secondary=device_enaged_identifier)
    singleTests   = db.relationship('SingleTest', backref='batch_list',lazy='dynamic',foreign_keys="SingleTest.test_id")
    
    def __repr__(self):
        return '{}'.format(self.name) 
    

class SingleTest(db.Model):
    __tablename__  = 'singletest'
    id             = db.Column(db.Integer,primary_key=True)
    # device_id      = db.Column(db.Integer, db.ForeignKey('device.id'))
    channel_id     = db.Column(db.Integer, db.ForeignKey('channel.id'))
    cell_id        = db.Column(db.Integer, db.ForeignKey('cell.id'))
    test_id        = db.Column(db.Integer, db.ForeignKey('test.id'))
    cycler_file    = db.Column(db.String(64))
    prototype_file = db.Column(db.String(64))

    def __repr__(self):
            return 'Batch {}'.format(self.id) 

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64),index=True)
    description   = db.Column(db.String(512))
    project       = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    campaign_id      = db.relationship('Test', backref='test_campaign',lazy='dynamic',foreign_keys="Test.campaign_id")
    
    
    def __repr__(self):
        return '{}'.format(self.name) 

class Test_type(db.Model):
    __tablename__ = 'test_type'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64),index=True)
    type1_id      = db.relationship('Test', backref='test_type1',lazy='dynamic',foreign_keys="Test.type_1")
    type2_id      = db.relationship('Test', backref='test_type2',lazy='dynamic',foreign_keys="Test.type_2")

    def __repr__(self):
        return '{}'.format(self.name) 

class Device_type(db.Model):
     __tablename__ = 'device_type'
     id            = db.Column(db.Integer,primary_key=True)
     name          = db.Column(db.String(64),index=True)
    #  type1_id      = db.relationship('Device', backref='type_id',lazy='dynamic',foreign_keys="Device.type")
     def __repr__(self):
        return '{}'.format(self.name)

class Project(db.Model):
    __tablename__ = 'project'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64),index=True,unique=True)
    partners      = db.Column(db.String(512))
    description   = db.Column(db.String(512))

    singleTests_i = db.relationship('Campaign', backref='project_id',lazy='dynamic',foreign_keys="Campaign.project")
    def __repr__(self):
        return '{}'.format(self.name)  

db.create_all()