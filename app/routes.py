#!/usr/bin/env python
"""
__author__ = "Guillaume"
__copyright__ = "tbd"
__credits__ = ["Pietro"]
__license__ = "tbd"
__version__ = "0.0.1"
__maintainer__ = "Guillaume"
__email__ = "guillaume.thenaisie@csem.ch"
__status__ = "Development"
"""

# general libraries imports_________________________________________________________
from os import getcwd, path
from urllib.parse import urlencode, parse_qs
# import datetime
from datetime import datetime, timedelta
from math import floor
# Flask-specific libraries + setups_________________________________________________
from flask import render_template,url_for, redirect,  send_file, flash, jsonify, request,abort
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import inspect
from app import app, db, session
from werkzeug.utils import secure_filename
# Home-baked modules_________________________________________________________________
from app.models import *  # database models
from app.forms import *   # webforms

# context processor setup for easier template management_____________________________

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.context_processor
def inject_str():
    return dict(str=str)   

@app.context_processor
def inject_urlencode():
    return dict(urlencode=urlencode)    

@app.context_processor
def inject_floor():
    return dict(floor=floor)  



def gap_filling(A):
        for _ in range(len(A)-1):
            if (A[_+1]['start']-A[_]['end']).days <= 1: #continuous
                pass
            else:
                sched={'state': True, 'start':A[_]['end']+timedelta(days=1), 'end': A[_+1]['start']-timedelta(days=1)}
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
@login_required
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
                if test.end < datetime.today():
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
@login_required
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
@login_required
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

#============SCHEDULE & EQUIPMENT=====================================
@app.route('/schedule', methods=['GET'])
@login_required
def bookig_get():
    current_year, current_week = datetime.today().isocalendar()[:2]
    length =10
    max_week     = current_week + length
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
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    tests = Test.query.filter(Test.end >= today).all()
    for test in tests:
        user  = User.query.filter_by(id=test.user_id).first().username
        type1 = Test_type.query.filter_by(id=test.type_1).first()
        type2 = Test_type.query.filter_by(id=test.type_2).first()
        start = test.start if test.start > today else today
        end = test.end if test.end <today+timedelta(weeks=length) else today+timedelta(weeks=length)
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
                    try:
                        if planning[i]['test']==planning[i-1]['test']:
                            planning[i-1]['len']+= planning[i]['len']
                            del planning[i]
                    except Exception as e:
                        print(e)
                        

    
    return render_template('devices_management.html', data = schedules,current_week=current_week, max_week=max_week,current_year=current_year)


#==========SCHEDULE NEW TEST==========================================
@app.route('/booking', methods=['GET'])
@app.route('/booking/<data>', methods=['GET'])
@login_required
def book_device(data=None):
    forms = {   'addCampaign'  : addCampaignForm(),
                'addProject'   : addProjectForm(partners="No one"),
                'addTest'      : addTestForm(temperature=25),
                'selectDevice' : selectDeviceForm()
            }
# filling forms multiple choices options ______________________
    ## case 1 new Test form _______________________________________
    test_types                               = [(type.id, type.name) for type in Test_type.query.all()]
    forms['addTest'].type_1.choices          = test_types
    test_types2 = test_types.copy()
    # test_types2[0] = (0, "")
    forms['addTest'].type_2.choices          = [(0, "")]+test_types2
    campaigns                                = [(campaign.id, campaign.name) for campaign in Campaign.query.all()]
    forms['addTest'].campaign.choices        = campaigns
    chambers                                 = [("0","None")]+[ (device.id, device.name) for device in [ device for device in Device.query.all() if Device_type.query.filter_by(name = "temperature chamber").first() in device.type]]
    forms['addTest'].chambers.choices        = chambers
    eis                                      = [("0","None")]+[ (device.id, device.name) for device in [ device for device in Device.query.all() if Device_type.query.filter_by(name = "EIS").first() in device.type and len(device.type)==1]]
    forms['addTest'].eis.choices             = eis
    forms['addTest'].chambers.default        = 0
    ## case 2 new Campaign form _______________________________________
    projects                                 = [(project.id, project.name) for project in Project.query.all()]
    forms['addCampaign'].project.choices     = projects
    ## case 3 add channel/device/cell form _______________________________________
    cyclers                                  = [(device.id, device.name) for device in [device for listDev in [ [dev for dev in Device.query.all() if cycler_type in dev.type] for cycler_type in [ typ for typ in Device_type.query.all() if "cycler" in typ.name]] for device in listDev] ]
    forms['selectDevice'].device.choices     = cyclers
    channels                                 = [(channel.id, channel.chan_number) for channel in Channel.query.filter_by(device_id=Device.query.first().id).all()]
    forms['selectDevice'].channel.choices    = channels
    cells                                    = [(cell.id, cell.name) for cell in Cell.query.all()]
    forms['selectDevice'].cell.choices       = cells


    if 'channel_list' in session:
        channelList = session['channel_list']
    else:
        channelList = []

    if data is not None:
        data = parse_qs(data)
    else:
        data = None

    return render_template('book_channel.html', data = data, forms = forms, channelList=channelList)

@app.route('/booking/channel/<device>')
@login_required
def channels(device):
    channels =[ {'id':channel.id, 'name':channel.chan_number} for channel in Channel.query.filter_by(device_id=int(device)).all() ]
    return jsonify({'channels':channels})

@app.route('/booking/channel/cancel/<line>')
@login_required
def remove_channel(line):
    if 'channel_list' in session:
        channelList = session['channel_list']
        del channelList[int(line)]
        session['channel_list'] = channelList
        session.modified = True

    return redirect(url_for('book_device'))
# @app.route('/booking/type/<test_type>')
# def types(test_type):
#     type_1 = Device.query.filter_by(id=int(test_type)).first()
#     print(type_1)
#     types = [ typ for typ in[ {'id':typ.id, 'name':typ.name} for typ in Test_type.query.all()] if typ['id']!=test_type]
#     print("type changed ", test_type, types)
#     return jsonify({'types':types})
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
@login_required
def tests_list_post():
    return redirect(url_for('tests_list_get'))

#============CELLS===============================================

@app.route('/cells', methods=['POST'])
@login_required
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
@login_required
def bookig_post():
    return redirect(url_for('bookig_get'))

#============ Download files ==================================
@app.route('/download/<id>')
@login_required
def download_datafile(id):
    path_  = path.join("files", id)
    return send_file(path_, as_attachment=True)

#============ Upload files ==================================
@app.route('/upload/<id>', methods=['GET', 'POST'])
# @login_required
def upload_datafile(id):
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            abort(400)
        uploaded_file.save(path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))

#=============End measure =============================================
@app.route('/schedule/end/<data>', methods=['GET'])
@login_required
def endMesure_get(data):
    data = parse_qs(data)
    print(data)
    print(data['test'])
    endMeasure = EndMeasureForm()
    return render_template('end_measure.html', data=data,endMeasure=endMeasure)

@app.route('/schedule/end/<data>', methods=['POST'])
@login_required
def endMesure_post(data=None):
    if data is not None:
        data = parse_qs(data)
        print(data)
    endMeasure = EndMeasureForm()
    if endMeasure.validate():
        print(EndMeasureForm.file)
        # filename = secure_filename(EndMeasureForm.file.data)
        # print(filename)
    return redirect(url_for('index'))

@app.route('/schedule/cancel/<data>', methods=['GET', 'POST'])
@login_required
def cancel(data=None):
    if data is not None:
        data = parse_qs(data)
    print(data)
    test = Test.query.filter_by(id=int(data['test'][0])).first()
    singles = SingleTest.query.filter_by(test_id=test.id).all()
    channels = [Channel.query.filter_by(id=single.channel_id).first() for single in singles]
    devices  = [Device.query.filter_by(id=channel.device_id).first() for channel in channels]
    cells    = [Cell.query.filter_by(id=single.cell_id).first() for single in singles]
    elements = [{'device':devices[_].name, 'channel':channels[_].chan_number,'cell':cells[_].name} for _ in range(len(singles))]
    form = SimpleValidateForm()
    if form.validate():
        print("delete test; ", test)
        SingleTest.query.filter_by(test_id=test.id).delete()
        Test.query.filter_by(id=int(data['test'][0])).delete()
        db.session.commit()
        return redirect(url_for('bookig_get'))
        # filename = secure_filename(EndMeasureForm.file.data)
        # print(filename)
    return render_template("cancel.html", test=test,elements=elements, form = form)

#============Bookings=================================================

@app.route('/booking', methods=['POST'])
@app.route('/booking/<data>', methods=['POST'])
@login_required
def book_device_post(data=None):
    forms = {   'addCampaign'  : addCampaignForm(),
                'addProject'   : addProjectForm(partners="No one"),
                
                'selectDevice' : selectDeviceForm()
            }
    # filling forms multiple choices options ______________________
    ## case 1 new Test form _______________________________________
    test_types                               = [(type.id, type.name) for type in Test_type.query.all()]
    campaigns                                = [(campaign.id, campaign.name) for campaign in Campaign.query.all()]
    chambers                                 = [("0","None")]+[ (device.id, device.name) for device in [ device for device in Device.query.all() 
                                                if Device_type.query.filter_by(name = "temperature chamber").first() in device.type]]
    eis                                      = [("0","None")]+[ (device.id, device.name) for device in [ device for device in Device.query.all() 
                                                if Device_type.query.filter_by(name = "EIS").first() in device.type and len(device.type)==1]]
    forms['addTest'] = addTestForm(temperature=25,
    )
    forms['addTest'].eis.choices             = eis
    forms['addTest'].type_1.choices          = test_types
    forms['addTest'].type_2.choices          = [(0, "")]+test_types
    forms['addTest'].campaign.choices        = campaigns
    forms['addTest'].chambers.choices        = chambers


    
    # forms['addTest'].temperature.data     = 25
    ## case 2 new Campaign form _______________________________________
    projects                                 = [(project.id, project.name) for project in Project.query.all()]
    forms['addCampaign'].project.choices     = projects
    ## case 3 add channel/device/cell form _______________________________________
    cyclers                                  = [(device.id, device.name) for device in [device for listDev in [ [dev for dev in Device.query.all() if cycler_type in dev.type] for cycler_type in [ typ for typ in Device_type.query.all() if "cycler" in typ.name]] for device in listDev] ]
    forms['selectDevice'].device.choices     = cyclers
    channels                                 = [(channel.id, channel.chan_number) for channel in Channel.query.filter_by(device_id=Device.query.first().id).all()]
    forms['selectDevice'].channel.choices    = channels
    cells                                    = [(cell.id, cell.name) for cell in Cell.query.all()]
    forms['selectDevice'].cell.choices       = cells

    if 'channel_list' in session:
        channelList = session['channel_list']
    else:
        channelList = []

    if forms['selectDevice'].validate():
        # flash("device validated")
        device = Device.query.filter_by(id = forms['selectDevice'].device.data).first()
        channel = Channel.query.filter_by(id =forms['selectDevice'].channel.data ).first()
        cell    = Cell.query.filter_by(id = forms['selectDevice'].cell.data).first()
        if len(channelList)> 0:
            for chan in channelList:
                if chan['device'] == device.name and chan['channel']==channel.chan_number :
                    print("device channel already in the list")
                    break
                elif chan['cell']== cell.name:
                    print("cell already in the list")
                    break
                else:
                    channelList.append({'device':device.name,
                                        'channel':channel.chan_number,
                                        'cell':cell.name,
                                        'channel_id':channel.id,
                                        'cell_id':cell.id})
        else:
            channelList.append({'device':device.name,
                                        'channel':channel.chan_number,
                                        'cell':cell.name,
                                        'channel_id':channel.id,
                                        'cell_id':cell.id})
        print(channelList)
        session['channel_list'] = channelList
        session.modified = True
    
    if forms['addTest'].validate_on_submit():
        # flash("test validated")
        if len(channelList)<1:
            print("channel list empty")
        else:
            print("started test registration")
            test = Test(
                name        = forms['addTest'].name.data,
                description = forms['addTest'].description.data if forms['addTest'].description.data else None,
                start       = forms['addTest'].start.data,
                end         = forms['addTest'].end.data,
                active      = True if forms['addTest'].start.data == datetime.today() else False,
                type_1      = forms['addTest'].type_1.data,
                type_2      = forms['addTest'].type_2.data 
                if (forms['addTest'].type_2.data!="" 
                and forms['addTest'].type_2.data!=forms['addTest'].type_1.data) else None,
                campaign_id = forms['addTest'].campaign.data,
                user_id     = current_user.id,
            )
            

            if forms['addTest'].eis.data:
                eis_device = Device.query.filter_by(id=forms['addTest'].eis.data).first()
                test.devices.append(eis_device)
                print("we added an eis")

            if forms['addTest'].chambers.data:
                chamber_device = Device.query.filter_by(id=forms['addTest'].chambers.data).first()
                test.devices.append(chamber_device)
                print("we added a temp chamber")
                test.temp = forms['addTest'].temperature.data
            
            db.session.add(test)
            db.session.commit()
            
            for channel in channelList:
                single_test = SingleTest(
                    channel_id=channel['channel_id'],
                    cell_id=channel['cell_id'],
                    test_id = test.id
                )
                # ADD check of devices and cell availability
                db.session.add(single_test)
            db.session.commit()
    #ADD cleaning session after submit
    if forms['addCampaign'].validate():
        # flash ("campaign added")
        campaign_names = [campaign.name for campaign in Campaign.query.all()]
        if forms['addCampaign'].name.data in campaign_names:
            print("Error campaign name already exists")
        else:
            campaign = Campaign(name = forms['addCampaign'].name.data,
                                project=forms['addCampaign'].project.data)
            campaign.description = forms['addCampaign'].description.data if forms['addCampaign'].description.data else None
            db.session.add(campaign)
            db.session.commit()
            print("campaign added")
            # flash("sucess", "sucess")

    if forms['addProject'].validate():
        # flash ("project added")
        projects_names = [project.name for project in Project.query.all()]
        if forms['addProject'].name.data in projects_names:
            print("Error project name already exists")
        else:
            project = Project(name = forms['addProject'].name.data)
            project.description = forms['addProject'].description.data if forms['addProject'].description.data else None
            project.partners = forms['addProject'].partners.data
            db.session.add(project)
            db.session.commit()
            print("project added")

    return redirect(url_for('book_device'))
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




#============Login user========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))
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



@app.route("/test", methods=['POST', 'GET'])
def test():
    
    # form     =  testTestForm()
    forms = {   'addCampaign'  : addCampaignForm(),
                'addProject'   : addProjectForm(),
                'addTest'      : testTestForm(),
                'selectDevice' : selectDeviceForm()
            }
    # filling forms multiple choices options ______________________
    ## case 1 new Test form _______________________________________
    test_types                               = [(type.id, type.name) for type in Test_type.query.all()]
    forms['addTest'].type_1.choices          = test_types
    test_types2 = test_types.copy()
    # test_types2[0] = (0, "")
    forms['addTest'].type_2.choices          = test_types2
    campaigns                                = [(campaign.id, campaign.name) for campaign in Campaign.query.all()]
    forms['addTest'].campaign.choices        = campaigns
    chambers                                 = [("0","None")]+[ (device.id, device.name) for device in [ device for device in Device.query.all() if Device_type.query.filter_by(name = "temperature chamber").first() in device.type]]
    forms['addTest'].chambers.choices        = chambers
    eis                                      = [("0","None")]+[ (device.id, device.name) for device in [ device for device in Device.query.all() if Device_type.query.filter_by(name = "EIS").first() in device.type and len(device.type)==1]]
    forms['addTest'].eis.choices             = eis



    # ## case 2 new Campaign form _______________________________________
    projects                                 = [(project.id, project.name) for project in Project.query.all()]
    forms['addCampaign'].project.choices     = projects
    # ## case 3 add channel/device/cell form _______________________________________
    cyclers                                  = [(device.id, device.name) for device in [device for listDev in [ [dev for dev in Device.query.all() if cycler_type in dev.type] for cycler_type in [ typ for typ in Device_type.query.all() if "cycler" in typ.name]] for device in listDev] ]
    forms['selectDevice'].device.choices     = cyclers
    channels                                 = [(channel.id, channel.chan_number) for channel in Channel.query.filter_by(device_id=Device.query.first().id).all()]
    forms['selectDevice'].channel.choices    = channels
    cells                                    = [(cell.id, cell.name) for cell in Cell.query.all()]
    forms['selectDevice'].cell.choices       = cells

    for key in forms.keys():
        if forms[key].validate():
            print(key, "  validated")


    return render_template('test.html', forms=forms)
