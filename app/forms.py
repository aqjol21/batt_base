from curses import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, IntegerField, DecimalField,RadioField
from wtforms.validators import DataRequired
from wtforms.fields import FormField, DateField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from wtforms import validators
from flask import url_for
# from wtforms.fields.html5 import DateField
from app import db
# from app.models import Device, Device_type


class LoginForm(FlaskForm):
    username    = StringField('Username', validators=[DataRequired()])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me<br>")
    submit      = SubmitField('Sign In')


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
    purchase_date = DateField("Purchase date",validators=[DataRequired()])
    id            = IntegerField("Cell id (from sticker)")
    location      = SelectField("Storage location", coerce=int, validators=[DataRequired()])
    submit        = SubmitField('Add cell')


class EndMeasureForm(FlaskForm):
    submit        = SubmitField('start cell')


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

class addTestForm(FlaskForm):
    name                = StringField('Name', validators=[DataRequired()])
    description         = TextAreaField('Comments')
    start               = DateField("Start date",validators=[DataRequired()])
    end                 = DateField("Projected end date",validators=[DataRequired()])
    temperature         = DecimalField('Temperature (only account for if chamber selected)', validators=[DataRequired()])
    campaign            = SelectField("Select campaign", coerce=int, validators=[DataRequired()])
    type_1              = SelectField("Select type", coerce=int, validators=[DataRequired()])
    type_2              = SelectField("Select additional type (optional)", coerce=int)
    chambers            = RadioField("Select chamber (optional)", coerce=int) 
    eis                 = RadioField("Select additional eis (optional)", coerce=int)
    submit              = SubmitField('Schedule test')

class selectDeviceForm(FlaskForm):
    device      = SelectField("Select device", coerce=int, validators=[DataRequired()])
    channel     = SelectField("Select channel", coerce=int, validators=[DataRequired()])
    cell        = SelectField("Select cell", coerce=int, validators=[DataRequired()])
    submit      = SubmitField('Add channel')

class testTestForm(FlaskForm):
    name                = StringField('Name', validators=[DataRequired()])
    description         = TextAreaField('Comments')
    start               = DateField("Start date",validators=[DataRequired()])
    end                 = DateField("Projected end date",validators=[DataRequired()])
    # temperature         = DecimalField('Temperature (leave empty if ambiant)')
    campaign            = SelectField("Select campaign", coerce=int, validators=[DataRequired()])
    type_1              = SelectField("Select type", coerce=int, validators=[DataRequired()])
    type_2              = SelectField("Select additional type (optional)", coerce=int)
    chambers            = RadioField("Select chamber (optional)", coerce=int, validators=[DataRequired()]) 
    eis                 = RadioField("Select additional eis (optional)", coerce=int, validators=[DataRequired()])
    # book_chamber        = SelectField("Select temperature chamber (optional)", coerce=int)
    # book_additional_eis = SelectField("Select additional EIS (optional)", coerce=int)
    submit              = SubmitField('Schedule test')
