from flask import render_template
from app import app

from app.forms import CellTypeForm,CellForm,DeviceForm,StartMeasureForm,EndMeasureForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/cells')
def cells():
    forms = {'type':CellTypeForm(), 'unit':CellForm()}
    return render_template('cells_management.html',forms=forms)

@app.route('/devices')
def devices():
    form = DeviceForm()
    return render_template('devices_management.html',form=form)

@app.route('/measurements')
def measures():
    forms = StartMeasureForm()
    return render_template('devices_management.html',forms=forms)