from flask_sqlalchemy import SQLAlchemy
#import logging as lg
from app import app,  db#,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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
    
    def __repr__(self):
        return '<User {}>'.format(self.username) 

    def __init__(self, username, password_hash):
        self.username        = username
        self.password_hash   = password_hash    

    def set_passwd(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_passwd(self, password):
        return(check_password_hash(self.password_hash,password))


class Cell_type(db.Model):
    """Defintion of the table in the database contiqning qll the models of the cells

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


class Cell(db.Model):
    __tablename__ = 'cell'
    id            = db.Column(db.Integer,primary_key=True)
    model_id      = db.Column(db.Integer, db.ForeignKey('cell_type.id'))
    purchase_date = db.Column(db.DateTime(timezone=True))
    under_use     = db.Column(db.Boolean)

class Channel(db.Model):
    __tablename__ = 'channel'
    id            = db.Column(db.Integer,primary_key=True)
    chan_number   = db.Column(db.Integer)
    status        = db.Column(db.Integer)
    device_id     = db.Column(db.Integer, db.ForeignKey('device.id'))
    

class Device(db.Model):
    __tablename__   = 'device'
    id              = db.Column(db.Integer,primary_key=True)
    name            = db.Column(db.String(64),index=True,unique=True)
    number_channels = db.Column(db.Integer)
    company         = db.Column(db.String(64))
    # specifications?


class Test(db.Model):
    __tablename__ = 'measurement'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64),index=True)
    description   = db.Column(db.String(512))
    type_2        = db.Column(db.Integer)
    type_1        = db.Column(db.Integer)
    start         = db.Column(db.DateTime(timezone=True))
    end           = db.Column(db.DateTime(timezone=True))
    temp          = db.Column(db.Float)
    file          = db.Column(db.String(64))
    channel       = db.Column(db.Integer, db.ForeignKey('channel.id'))
    device        = db.Column(db.Integer, db.ForeignKey('device.id'))
    device2       = db.Column(db.Integer, db.ForeignKey('device.id'))
    device3       = db.Column(db.Integer, db.ForeignKey('device.id'))
    cell          = db.Column(db.Integer, db.ForeignKey('cell.id'))
    user          = db.Column(db.Integer, db.ForeignKey('user.id'))



class Campain(db.Model):
    __tablename__ = 'campain'
    id            = db.Column(db.Integer,primary_key=True)
    name          = db.Column(db.String(64),index=True)
    description   = db.Column(db.String(512))