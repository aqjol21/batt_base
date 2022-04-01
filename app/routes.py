from datetime import date, datetime
from flask import render_template,url_for, redirect,  send_file, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from sqlalchemy import inspect

from app import app, db
from app.models import User, Cell_type, Cell, Channel, Device, Test, Campaign, Test_type, Project, SingleTest, Device_type, Location

from os import getcwd, path
from urllib.parse import urlencode, parse_qs
import datetime

from app.forms import CellTypeForm,CellForm,DeviceForm,StartMeasureForm,EndMeasureForm, displayScheduleControl

###### DESIGN & DEBUG #########
from app.fakeData import schedule
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


def gap_filling(A):
        for _ in range(len(A)-1):
            if (A[_+1]['start']-A[_]['end']).days <= 1: #continuous
                pass
            else:
                sched={'state': True, 'start':A[_]['end']+datetime.timedelta(days=1), 'end': A[_+1]['start']-datetime.timedelta(days=1)}
                A.insert(_+1, sched)
                gap_filling(A)

'''___________________________________________________________________________________________________________________________________
                Display functions

    Contains
    index()
        displays the main home page
    tests_list_get()
        list of every tests ran, on going and schedules
    cells_get()
        list of every cells purchased
    cell_details_get()
        list of details available for a specific cell
        parameters
        ==========
        id : int, id of the cell of which the details must be displayed
    bookig_get()
___________________________________________________________________________________________________________________________________'''


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
                test_[ 'cell' ]   = Cell.query.filter_by(id=single.cell_id).first().name
                if test.end < datetime.datetime.today():
                    test_[ 'cycler']  = single.cycler_file
                    test_[ 'cms']     = single.prototype_file
                else:
                    test_[ 'cycler']  = None
                    test_[ 'cms']     = None
                tests.append(test_)
        campaign_['tests']=tests
        campaings.append(campaign_)
    return render_template('test_list.html', title="Test details", campains = campaings)

#============CELLS===============================================
@app.route('/cells', methods=['GET'])
def cells_get():
    cellTypes = [(type_.id, type_.maker+" "+type_.model) for type_ in Cell_type.query.all() ]
    forms = {'type':CellTypeForm(), 'unit':CellForm()}
    forms['unit'].model.choices = cellTypes
    locations = [(location.id, location.name) for location in Location.query.all()]
    forms['unit'].location.choices = locations

    cells =[]
    for cell in Cell.query.all():
        cell_ ={'id':cell.id, 'name':cell.name, 
        'location': Location.query.filter_by(id = cell.location).first(), 
        'type':Cell_type.query.filter_by(id=cell.model_id).first().model, 
        'under_use':cell.under_use }
        single  = SingleTest.query.filter_by(cell_id=cell.id).order_by(SingleTest.id.desc()).first() #fifo by default -> order by id descending
        if single != None : # has been used before
            test    = Test.query.filter_by(id=single.test_id).first()
            channel = Channel.query.filter_by(id=single.channel_id).first()
            device  = Device.query.filter_by(id=channel.device_id).first()
            user    = User.query.filter_by(id=test.user_id).first()
            cell_['user']=user.username
            cell_['device']=device.name
            cell_['end'] = test.end
        else:
            cell_['end'] = "never used"
        cells.append(cell_)

    return render_template('cells_management.html',forms=forms, cells=cells)

@app.route('/cell_details<id>', methods=['GET'])
def cell_details_get(id):
    cell = Cell.query.filter_by(id=id).first()
    model = Cell_type.query.filter_by(id=cell.model_id).first()

    singles   = SingleTest.query.filter_by(cell_id=cell.id).all()
    tests_    = [ Test.query.filter_by(id=single.test_id).first() for single in singles ]
    tests_    = [ test.__dict__ for test in tests_]
    campaigns = list(dict.fromkeys([ Campaign.query.filter_by(id=test['campaign_id']).first() for test in tests_]))  
    channels  = [Channel.query.filter_by(id=single.channel_id).first() for single in singles]
    devices   = [Device.query.filter_by(id=channel.device_id).first() for channel in channels]
    details   = [ "device: "+devices[_].name+" channel: "+str(channels[_].chan_number) for _ in range(len(devices)) ]
    for t, test in enumerate(tests_):
        test['device']=details[t]
    tests = [ [ {'name':test_['name'],'start':test_['start'],'end': test_['end'],
             'user':User.query.filter_by(id=test_['user_id']).first().username, 'device':test_['device']  } 
                for test_ in tests_ if test_['campaign_id'] == campaign.id ] for campaign in campaigns]
    cell_ = {'id':cell.id, 'name':cell.name, 
        'location': Location.query.filter_by(id = cell.location).first(), 
        'type':Cell_type.query.filter_by(id=cell.model_id).first().model, 
        'under_use':cell.under_use } 
    return render_template('cell_details.html',model= model, cell=cell_, campains= campaigns, tests=tests)

#============Equipement===============================================
@app.route('/schedule', methods=['GET'])
def bookig_get():
    current_week = datetime.datetime.today().isocalendar()[1]
    length =10
    max_week     = current_week + length

    # schedules = []
    # for device in Device.query.all():
    #     device_ ={'name':device.name, 'channels':[]}
    #     devtype = [type_.name for type_ in device.type]
    #     if "cycler" in devtype[0]:
            
    #         for channel in Channel.query.filter_by(device_id=device.id).all():
    #             singletests = SingleTest.query.filter_by(channel_id=channel.id).all()
    #             schedule = [ {'state':True, 'len':1} for _ in range(length*7+1)]
    #             today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    #             for test in [Test.query.filter_by(id=single.test_id).first() for single in singletests]:
    #                 if test.end > today:
    #                     user  = User.query.filter_by(id=test.user_id).first().username
    #                     type1 = Test_type.query.filter_by(id=test.type_1).first()
    #                     type2 = Test_type.query.filter_by(id=test.type_2).first()
    #                     start = test.start if test.start > today else today
    #                     end = test.end if test.end <today+datetime.timedelta(weeks=length) else today+datetime.timedelta(weeks=length)
    #                     # print(start, end)
    #                     xstart = (start-today).days
    #                     xend   = (end-today).days
    #                     # print(xstart,xend)
    #                     # for x in range (xstart, xend):
    #                     #     schedule[x]['start']=x
    #                     #     schedule[x]['end']=x+1
    #                     #     schedule[x]['state']=False
    #                     #     schedule[x]['test']=test.id
    #                     #     schedule[x]['name']=test.name
    #                     #     schedule[x]['user']=user
    #                     #     schedule[x]['type']=type1.name + " "+ type2.name if type2 != None else type1.name


    #                     for x in range (xstart+1, xend+1,-1): del schedule[x]
    #                     schedule[xstart]['state']=False
    #                     schedule[xstart]['test']=test.id
    #                     schedule[xstart]['name']=test.name
    #                     schedule[xstart]['user']=user
    #                     schedule[xstart]['type']=type1.name + " "+ type2.name if type2 != None else type1.name
    #                     schedule[xstart]['len']= xend+1-xstart
    #                     schedule[xstart]['type']=type1.name + " "+ type2.name if type2 != None else type1.name

    #             device_['channels'].append(schedule)
                
                
    #         schedules.append(device_)
    length = 10
    # Init the table
    schedules = []
    for device in Device.query.all():
        device_ ={'name':device.name, 'channels':[], 'len': 1}
        for channel in Channel.query.filter_by(device_id=device.id).all():
            schedule = [ {'booked':False, 'len':1} for _ in range(length*7+1)]
            device_['channels'].append(schedule)
        schedules.append(device_)
    # print(schedules[0])

    # modify the content based on tests
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    tests = Test.query.filter(Test.end >= today).all()
    for test in tests:
        user  = User.query.filter_by(id=test.user_id).first().username
        type1 = Test_type.query.filter_by(id=test.type_1).first()
        type2 = Test_type.query.filter_by(id=test.type_2).first()
        start = test.start if test.start > today else today
        end = test.end if test.end <today+datetime.timedelta(weeks=length) else today+datetime.timedelta(weeks=length)
        # print(start, end)
        xstart = (start-today).days
        xend   = (end-today).days
        # book chamber if used
        for device in test.devices:
            for x in range(xstart, xend+1):
                cell = schedules[next((i for i, dev in enumerate(schedules) if dev['name']==device.name),None)]['channels'][0][x]
                cell['booked']=True
                cell['test']=test.id                                                    
                cell['name']=test.name                                                      
                cell['user']=user                                                          
                cell['type']=type1.name + " "+ type2.name if type2 != None else type1.name
        # book cyclers
        for single in SingleTest.query.filter_by(test_id=test.id).all():
            channel = Channel.query.filter_by(id=single.channel_id).first()
            device = Device.query.filter_by(id=channel.device_id).first()
            for x in range(xstart, xend+1):
                channel = Channel.query.filter_by(id=single.channel_id).first()
                device  = Device.query.filter_by(id=channel.device_id).first()
                for x in range(xstart, xend+1):
                    cell = schedules[next((i for i, dev in enumerate(schedules) if dev['name']==device.name),None)]['channels'][channel.chan_number][x]
                    cell['booked']=True
                    cell['test']=test.id                                                    
                    cell['name']=test.name                                                      
                    cell['user']=user                                                          
                    cell['type']=type1.name + " "+ type2.name if type2 != None else type1.name

    # regroup the table into element only
    for device in schedules:
        for planning in device['channels']:
            print(device['name'])
            for i in range( len(planning)-1,0,-1):
                if planning[i]['booked'] ==planning[i-1]['booked'] and planning[i]['booked']==False:
                    planning[i-1]['len']+= planning[i]['len']
                    del planning[i]
                elif planning[i]['booked']==True:
                    if planning[i]['test']==planning[i-1]['test']:
                        planning[i-1]['len']+= planning[i]['len']
                        del planning[i]

    
    return render_template('devices_management.html', data = schedules,current_week=current_week, max_week=max_week)

'''___________________________________________________________________________________________________________________________________
                Action functions from forms

    Contains
    tests_list_post()

    cells_post()
        allows to add a new cell type
        allows to add  a new cell unit
___________________________________________________________________________________________________________________________________'''
#============TEST===============================================
@app.route('/tests_list', methods=['POST'])
def tests_list_post():
    return redirect(url_for('tests_list_get'))

#============CELLS===============================================

@app.route('/cells', methods=['POST'])
def cells_post():
    forms = {'type':CellTypeForm(), 'unit':CellForm()}
    cellTypes = [(type_.id, type_.maker+" "+type_.model) for type_ in Cell_type.query.all() ]
    forms = {'type':CellTypeForm(), 'unit':CellForm()}
    forms['unit'].model.choices = cellTypes
    locations = [(location.id, location.name) for location in Location.query.all()]
    forms['unit'].location.choices = locations

    if forms['type'].validate_on_submit():
        if Cell_type.query.filter_by(model=forms['type'].modeldata).first() is not None:
            flash("Model already in database")
        else:
            try: 
                type = Cell_type(
                    model           =forms['type'].model           .data,
                    maker           =forms['type'].maker           .data,
                    anode           =forms['type'].anode           .data,
                    cathode         =forms['type'].cathode         .data,
                    package         =forms['type'].package         .data,
                    capacity        =forms['type'].capacity        .data,
                    max_dc_current  =forms['type'].max_dc_current  .data,
                    max_peak_current=forms['type'].max_peak_current.data,
                    min_voltage     =forms['type'].min_voltage     .data,
                    max_voltage     =forms['type'].max_voltage     .data,
                    min_temperature =forms['type'].min_temperature .data,
                    max_temperature =forms['type'].max_temperature .data,
                    note            =forms['type'].note            .data
                )
                db.session.add(type)
                db.session.commit()
                flash("Added new cell type {} to database.".format(forms['type'].model.data))
            except Exception  as e:
                flash("failed, error code "+e)
    elif forms['unit'].validate_on_submit():
        if Cell.query.filter_by(id=forms['unit'].id.data).first() is not None:
            flash('Cell id already in the database')
        else:
            try:
                cell = Cell(
                    name         =forms['unit'].name.data,
                    model_id     =forms['unit'].model.data,
                    purchase_date=forms['unit'].purchase_date.data,
                    under_use    =False,
                    location     =forms['unit'].location.data
                )
                db.session.add(cell)
                db.session.commit()
            except Exception as e:
                 flash("failed, error code "+e)
        
    return redirect(url_for('cells_get'))





#============Equipement===============================================
@app.route('/schedule', methods=['POST'])
def bookig_post():
    return redirect(url_for('bookig_get'))


#============ Download files ==================================
@app.route('/download/<id>')
def download_datafile(id):
    path_  = path.join("files", id)
    return send_file(path_, as_attachment=True)


#=============End measure =============================================
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

# ==========================================================> function for QR code
# @app.route('/cell_scan<id>', methods=['GET'])
# def cell_scan_get(id):
#     #existing cells gnagnagn check, here if id > 4, cell is a new one
#     if id <= 4 :
#         #cell already registered
#         return redirect(url_for('tests_list_get'))
#     else:
#         form = CellForm()
#         return render_template('add_cell.html', title="Register cell", form = form)

#============Admin==============================================


admin = Admin(app, name='Dashboard')  
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Project, db.session))
admin.add_view(ModelView(Cell_type, db.session))
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Cell, db.session))
admin.add_view(ModelView(Channel, db.session))
admin.add_view(ModelView(Device, db.session))
admin.add_view(ModelView(Device_type, db.session))
admin.add_view(ModelView(Test_type, db.session))
admin.add_view(ModelView(SingleTest, db.session))
admin.add_view(ModelView(Test, db.session))
admin.add_view(ModelView(Campaign, db.session))


