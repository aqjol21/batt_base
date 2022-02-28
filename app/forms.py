from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, IntegerField, DecimalField
from wtforms.validators import DataRequired
from wtforms.fields import FormField, DateField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from wtforms import validators
from flask import url_for

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit   = SubmitField('Sign In')


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
    model         =  SelectField("cell model", coerce=int, validators=[DataRequired()])
    purchase_date =  DateField("Purchase date",validators=[DataRequired()])
    submit        = SubmitField('Add cell')

class DeviceForm(FlaskForm):
    name            = StringField('Name', validators=[DataRequired()])
    number_channels = IntegerField('How many channels? (min 1)', validators=[DataRequired()])
    company         = SelectField("Which manufacturer?", choices=[('0','Arbin'),('1','Biologics'),('2','EIS_name')])
    submit          = SubmitField('Add device')

class StartMeasureForm(FlaskForm):
    name          = StringField('Name', validators=[DataRequired()])
    description   = TextAreaField('Comments')
    start_data    = DateField("Start date",validators=[DataRequired()])
    end_date      = DateField("Projected end date")
    channel_id    = SelectField("Select channel", coerce=int, validators=[DataRequired()])
    submit        = SubmitField('start cell')

class EndMeasureForm(FlaskForm):
    submit        = SubmitField('start cell')