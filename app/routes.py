from flask import render_template,url_for, redirect,  send_file
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from sqlalchemy import inspect

from app import app, db
from app.models import User, Cell_type, Cell, Channel, Device, Test, Campaign, Test_type, Project, SingleTest, Device_type

from os import getcwd, path
from urllib.parse import urlencode, parse_qs

from app.forms import CellTypeForm,CellForm,DeviceForm,StartMeasureForm,EndMeasureForm, displayScheduleControl

###### DESIGN & DEBUG #########
from app.fakeData import cell, schedule
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
    devices= Device.query.all()
    devices_ = []
    for device in devices:
        device_ = {}
        device_['name'] = device.name
        channels = Channel.query.filter_by(device_id=device.id).all()
        channels_ = []
        for channel in channels:
            channel_ = {}
            channel_ ['status']=channel.status
            if channel.status == True:
                current_tests = Test.query.filter_by(active=True).all()
                for test in current_tests:
                    singletests = SingleTest.query.filter_by(test_id=test.id).all()
                    for singletest in singletests:
                        if singletest != None:
                            the_test = test
                            channel_['user'] = User.query.filter_by(id=the_test.user_id).first().username 
                            break
            channels_.append(channel_)
        device_['channels']=channels_
        device_['utilization']= sum(1 for d in device_['channels'] if d.get('status') == True)/len(device_['channels'])*100
        devices_.append(device_)

    return render_template('index.html', title='Home', devices = devices_)

#============TEST===============================================
@app.route('/tests_list', methods=['GET'])
def tests_list_get():
    campaings = []
    for campaign in Campaign.query.all():
        campaign_ = {'name':campaign.name, 'project':campaign.project}
        tests = []
        for test in Test.query.filter_by(campaign_id=campaign.id):
            test_ = {}
            for device in test.devices:            
                if "chamber" in str(device.type[0]):
                    test_['chamber'] = device.name
                elif "EIS" in str(device.type[0]):
                    test_['eis']=device.name
            for single in SingleTest.query.filter_by(test_id=test.id).all():
                channel = Channel.query.filter_by(id =single.channel_id).first()
                try:
                    test_[ 'type_1']  = Test_type.query.filter_by(id=test.type_1).first().name
                except:
                    pass
                try:
                    test_[ 'type_2']  = Test_type.query.filter_by(id=test.type_2).first().name
                except:
                    pass
                test_[ 'start' ]  = test.start
                test_[ 'end'   ]  = test.end
                test_[ 'user'  ]  = test.user
                test_[ 'temp'  ]  = test.temp
                test_[ 'channel'] = channel
                test_[ 'device']  = Device.query.filter_by(id=channel.device_id).first().name
                test_[ 'cycler']  = single.cycler_file
                test_[ 'cms']     = single.prototype_file
                test_[ 'cell' ]   = Cell.query.filter_by(id=single.cell_id).first().name
                tests.append(test_)
        campaign_['tests']=tests
        campaings.append(campaign_)
    return render_template('test_list.html', title="Test details", campains = campaings)

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
    form = StartMeasureForm()
    return render_template('book_channel.html', data = data, form = form)

#============Admin==============================================


admin = Admin(app, name='Dashboard')  
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Project, db.session))
admin.add_view(ModelView(Cell_type, db.session))
admin.add_view(ModelView(Cell, db.session))
admin.add_view(ModelView(Channel, db.session))
admin.add_view(ModelView(Device, db.session))
admin.add_view(ModelView(Device_type, db.session))
admin.add_view(ModelView(Test_type, db.session))
admin.add_view(ModelView(SingleTest, db.session))
admin.add_view(ModelView(Test, db.session))
admin.add_view(ModelView(Campaign, db.session))



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