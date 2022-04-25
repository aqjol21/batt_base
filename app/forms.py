from curses import flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, IntegerField, DecimalField,RadioField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.fields import FormField, DateField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from wtforms import validators
from flask import url_for
# from wtforms.fields.html5 import DateField
# from app import db
# from app.models import Device, Device_type


from fakeData import *


class selectOtherForm(FlaskForm):
    test = SelectField("Which type of usage?", choices=[(0,"Microscopy"),(1,"PCB test"), (2,"Exhibition"), (3, "Other")],validators=[DataRequired()])
    details = TextAreaField("Additional details")
    selectOther = SubmitField("Confirm test")

class addSingleCellsForm(FlaskForm):
    name                = StringField('Name', validators=[DataRequired()])
    description         = TextAreaField('Comments')
    start               = DateField("Start date",validators=[DataRequired()])
    end                 = DateField("Projected end date",validators=[DataRequired()])
    temperature         = DecimalField('Temperature (leave empty if ambiant)')
    campaign            = SelectField("Select campaign", coerce=int, validators=[DataRequired()])
    type_1              = SelectField("Select type", coerce=int, validators=[DataRequired()])
    type_2              = SelectField("Select additional type (optional)", coerce=int)
    chambers            = RadioField("Select chamber (optional)", coerce=int, validators=[DataRequired()]) 
    eis                 = RadioField("Select additional eis (optional)", coerce=int, validators=[DataRequired()])
    addSingletest       = SubmitField('Schedule test')

class selectDeviceForm(FlaskForm):
    device      = SelectField("Select device", coerce=int, validators=[DataRequired()])
    channel     = SelectMultipleField("Select channel", coerce=int, validators=[DataRequired()])
    cell        = SelectField("Select cell", coerce=int, validators=[DataRequired()])
    submit      = SubmitField('Add channel')

class selectPackForm(FlaskForm):
    device      = SelectField("Select device", coerce=int, validators=[DataRequired()])
    channel     = SelectMultipleField("Select channel", coerce=int, validators=[DataRequired()])
    pack        = SelectField("Select pack", coerce=int, validators=[DataRequired()])
    submit      = SubmitField('Add channel')

class FilterTestsform(FlaskForm):

    campaigns  = SelectMultipleField("Campaigns",  coerce=int )
    status     = SelectField('Status',             coerce=int)
    user       = SelectMultipleField("Users",      coerce=int)
    cell       = SelectMultipleField("Cells",      coerce=int)
    cell_type  = SelectMultipleField("Cell Types", coerce=int)
    type_1     = SelectField('Type 1',             coerce=int)
    type_2     = SelectField('Type 1',             coerce=int)
    device     = SelectMultipleField("Device",     coerce=int)
    channel    = SelectMultipleField("Channel",    coerce=int)
    chamber    = SelectMultipleField("Chamber",    coerce=int)
    eis        = BooleanField("External EIS?")
    start_b    = DateField("Start before")
    start_a    = DateField("Start after")
    end_b      = DateField("End before")
    end_a      = DateField("End after")
    search     = SubmitField("Apply filters")

class FilterCellStockForm(FlaskForm):
    name        = SelectMultipleField("Pack name",  coerce=int)
    cell_type   = SelectMultipleField("Cell Types", coerce=int)
    user        = SelectMultipleField("Users",      coerce=int)
    start_b     = DateField("Purchased/assembled before")
    start_a     = DateField("Purchased/assembled after")
    filterCells = SubmitField("Apply filters")

class FilterPackStockForm(FlaskForm):
    name        = SelectMultipleField("Pack name",  coerce=int )
    cell_type   = SelectMultipleField("Cell Types", coerce=int)
    user        = SelectMultipleField("Users",      coerce=int )
    start_b     = DateField("Purchased/assembled before")
    start_a     = DateField("Purchased/assembled after")
    filterCells = SubmitField("Apply filters")

class FilterPcbStockForm(FlaskForm):
    name        = SelectMultipleField("PCB name",         coerce=int )
    cell_type   = SelectMultipleField("PCB Types",        coerce=int)
    user        = SelectMultipleField("Users",            coerce=int )
    start_b     = DateField("Manufactured before")
    start_a     = DateField("Manufactured after")
    firmware    = SelectMultipleField("Firmware version", coerce=int )
    filterCells = SubmitField("Apply filters")


class AssemblePackForm(FlaskForm):
    name          = StringField('Name')
    purchase_date = DateField("Assemble date",validators=[DataRequired()])
    cells         = SelectMultipleField("Cells", coerce=int, validators=[DataRequired()])
    id            = IntegerField("pack id (from sticker)")
    cms           = SelectField("CMS used for the pack", coerce=int, validators=[DataRequired()])
    location      = SelectField("Storage location", coerce=int, validators=[DataRequired()])
    submit        = SubmitField('Assemble pack')

class PackForm(FlaskForm):
    name          = StringField('Name')
    model         = SelectField("cell model", coerce=int, validators=[DataRequired()])
    purchase_date = DateField("Purchase date",validators=[DataRequired()])
    id            = IntegerField("Pack id (from sticker)")
    location      = SelectField("Storage location", coerce=int, validators=[DataRequired()])
    submit        = SubmitField('Add pack')


class CellTypeForm(FlaskForm):
    model              = StringField('Model', validators=[DataRequired()])
    maker              = StringField('Maker', validators=[DataRequired()])
    anode              = StringField('Anode material', validators=[DataRequired()])
    cathode            = StringField('Cathode material', validators=[DataRequired()])
    package            = StringField('Package', validators=[DataRequired()])
    capacity           = DecimalField('Capacity (in A.h.)', validators=[DataRequired()])
    max_dc_current     = DecimalField('Max DC current (in A)', validators=[DataRequired()])
    max_peak_current   = DecimalField('Max peak current (in A)', validators=[DataRequired()])
    min_voltage        = DecimalField('Min voltage (in V)', validators=[DataRequired()])
    max_voltage        = DecimalField('Max voltage (in V)', validators=[DataRequired()])
    min_temperature    = DecimalField('Min temperature (in K)', validators=[DataRequired()])
    max_temperature    = DecimalField('Max temperature (in K)', validators=[DataRequired()])
    note               = TextAreaField('Additional note if necessary')
    submit   = SubmitField('Add new type')

class CellForm(FlaskForm):
    name          = StringField('Name')
    model         = SelectField("cell model", coerce=int, validators=[DataRequired()])
    purchase_date = DateField("Purchase/manufacture date",validators=[DataRequired()])
    in_house      = BooleanField("In-house made cell?")
    mother_cell   = IntegerField("If coin cell, mother cell id (from sticker), if not cell id (from sticker)")
    location      = SelectField("Storage location", coerce=int, validators=[DataRequired()])
    submit        = SubmitField('Add cell')

class addCampaignForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Comments')
    project     = SelectField("Select project", coerce=int, validators=[DataRequired()])
    submit      = SubmitField('Add campaign')

class addProjectForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Comments')
    partners    = StringField('Partners', validators=[DataRequired()])
    submit      = SubmitField('Add project')

class addPCBModelForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])
    project     = SelectField("Select project", coerce=int, validators=[DataRequired()])
    description = TextAreaField('Comments')

class addPCBBoardForm(FlaskForm):
    name          = StringField('Name')
    model         = SelectField("CMS model", coerce=int, validators=[DataRequired()])
    purchase_date = DateField("Manufacture date",validators=[DataRequired()])
    id            = IntegerField("Board id (from sticker)")
    location      = SelectField("Storage location", coerce=int, validators=[DataRequired()])
    comment       = TextAreaField("Comments")
    submit        = SubmitField('Add board')