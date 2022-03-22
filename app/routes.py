from flask import render_template,url_for, redirect,  send_file
from app import app

from os import getcwd, path
from urllib.parse import urlencode, parse_qs

from app.forms import CellTypeForm,CellForm,DeviceForm,StartMeasureForm,EndMeasureForm, displayScheduleControl

###### DESIGN & DEBUG #########
from app.fakeData import device, campain, cell, schedule
##############################

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.context_processor
def inject_str():
    return dict(str=str)   

@app.context_processor
def inject_urlencode():
    return dict(urlencode=urlencode)    

#============INDEX===============================================
@app.route('/')
@app.route('/index')
def index():    
    devices = device.getDevices()
    return render_template('index.html', title='Home', devices = devices)

#============TEST===============================================
@app.route('/tests_list', methods=['GET'])
def tests_list_get():
    campains = campain.get_campains()
    return render_template('test_list.html', title="Test details", campains = campains)

@app.route('/tests_list', methods=['POST'])
def tests_list_post():
    return redirect(url_for('tests_list_get'))

#============CELLS===============================================
@app.route('/cells', methods=['GET'])
def cells_get():
    forms = {'type':CellTypeForm(), 'unit':CellForm()}
    cells = cell.get_cells()
    return render_template('cells_management.html',forms=forms, cells=cells)

@app.route('/cells', methods=['POST'])
def cells_post():
    return redirect(url_for('cells_get'))



@app.route('/cell_details<id>', methods=['GET'])
def cell_details_get(id):
    cell = []
    model = []
    campains= [{'name':'c1', 'description': "blablablabl"} for _ in range(3)]
    tests   = [[{'name':"test1",'description':"a test", 'start':"2022-02-01",'end':"2022-02-15", "user":"Me", "Channel":"Arbin 18"}for __ in range(5)] for _ in range(3)]
    return render_template('cell_details.html',model= model, cell=cell, campains= campains, tests=tests)



@app.route('/cell_scan<id>', methods=['GET'])
def cell_scan_get(id):
    #existing cells gnagnagn check, here if id > 4, cell is a new one
    if id <= 4 :
        #cell already registered
        return redirect(url_for('tests_list_get'))
    else:
        form = CellForm()
        return render_template('add_cell.html', title="Register cell", form = form)


#============ Download files ==================================
@app.route('/download/<id>')
def download_datafile(id):
    path_  = path.join("files", id)
    return send_file(path_, as_attachment=True)




#============Equipement===============================================
@app.route('/schedule', methods=['GET'])
def bookig_get():
    schedules = schedule.get_schedules()
    return render_template('devices_management.html', data = schedules)


#=============End measure
@app.route('/schedule/end/<data>', methods=['GET'])
def endMesure_get(data):
    data = parse_qs(data)
    endMeasure = EndMeasureForm()
    return render_template('end_measure.html', data=data,endMeasure=endMeasure)


#============Bookings=================================================
@app.route('/booking', methods=['GET'])
@app.route('/booking/<data>', methods=['GET'])
def book_device(data=None):
    if data is not None:
        data = parse_qs(data)
    else:
        data = None
    return render_template('book_channel.html', data = data)


#============Test===============================================

@app.route('/test', methods=['GET'])
@app.route('/test/<data>', methods=['GET'])
def test(data=None):
    if data is not None:
        variables = parse_qs(data)
        
    else:
        variables = None
    dic = { "first_name": "Brian", "last_name": "Corbin","email": "corbinbs@example.com", "date_of_birth": "01/01/1970" }
    return render_template('test.html', variables=variables, dic = dic)

@app.route('/test2')
def test2():
    variables = { "first_name": "Brian", "last_name": "Corbin","email": "corbinbs@example.com", "date_of_birth": "01/01/1970" }

    return(url_for("test", data = urlencode(variables)))