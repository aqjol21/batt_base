#!/usr/bin/env python
"""
__author__ = "Guillaume"
__copyright__ = "tbd"
__credits__ = ["Pietro", "Claudio"]
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
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
# from flask_login import current_user, login_user, logout_user, login_required
# from sqlalchemy import inspect
from app import app, session # ,db
from werkzeug.utils import secure_filename
# Home-baked modules_________________________________________________________________
# from app.models import *  # database models
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



'''___________________________________________________________________________________________________________________________________
                Display functions

___________________________________________________________________________________________________________________________________'''


############## debug only  ###############################################################################
from fakeData import *
tests_      = testTestlist()
devices_    = deviceIndex()
cells_      = cellList()
packs_      = cellList() 
schedules_  = scheduleList()
channelList = []
pcbs_       = pcbList()

############## debug only  ###############################################################################

#============INDEX===============================================
@app.route('/')
@app.route('/index')
def index():    
    
    return render_template('index.html', title='Home', devices = devices_)

#============TEST===============================================
@app.route('/tests_list', methods=['GET'])
# @login_required
def tests_list_get():
    filter_form = FilterTestsform()   
    ##### DEBUG
    filter_form.campaigns.choices = [ (i, campaigns[i])    for i in range(len (campaigns))    ]
    filter_form.status.choices    = [ (0,""),(1,'On-going'),(2,'Completed')                   ]
    filter_form.user.choices      = [ (i, users[i])        for i in range(len (users))        ]
    filter_form.cell.choices      = [ (i, cell_names[i])   for i in range(len (cell_names))   ]
    filter_form.cell_type.choices = [ (i, cell_types[i])   for i in range(len (cell_types))   ]
    filter_form.type_1.choices    = [ (i, test_types[i]) for i in range(len(test_types))      ]
    filter_form.type_2.choices    = [ (i, test_types[i])   for i in range(len(test_types))    ]
    filter_form.device.choices    = [ (i, devicesNames[i]) for i in range(len (devicesNames)) ]
    filter_form.channel.choices   = [ (i, str(i+1))        for i in range(20)                 ]
    filter_form.chamber.choices   = [ (i, chambers[i])     for i in range(len (chambers))     ]
    return render_template('test_list.html', title="Test details", tests = tests_, filter_form=filter_form)

@app.route('/tests_list', methods=['POST'])
# @login_required
def tests_list_post():
    filter_form = FilterTestsform() 

    return redirect(url_for(tests_list_get()))

#============INVENTORY MANAGEMENT===============================================
@app.route('/inventory/cells', methods=['GET'])
# @login_required
def cells_get():
    forms = {'type':CellTypeForm(), 'unit':CellForm(),  
             'filter':FilterCellStockForm()}

    ##### DEBUG
    forms['unit'].model.choices            = [ (i, cell_types[i]) for i in range(len (cell_types)) ]
    forms['unit'].location.choices         = [ (i, locations[i])  for i in range(len (locations))  ]
    forms['filter'].cell_type.choices      = [ (i, cell_types[i]) for i in range(len (cell_types)) ]
    forms['filter'].name.choices           = [ (i, cell_names[i]) for i in range(len (cell_names)) ]
    forms['filter'].user.choices           = [ (i, users[i])      for i in range(len (users))      ]


    return render_template('inventory.html',forms=forms, elements=cells_, type= "cell")


@app.route('/inventory/packs', methods=['GET'])
# @login_required
def packs_get():
    forms = {'type':AssemblePackForm(), 'unit':PackForm(),  
             'filter':FilterPackStockForm()}

    ##### DEBUG
    forms['unit'].model.choices            = [ (i, cell_types[i])    for i in range(len (cell_types)) ]
    forms['unit'].location.choices         = [ (i, locations[i])     for i in range(len (locations))  ]
    forms['type'].cells.choices            = [ (i, cell_names[i])    for i in range(len (cell_names)) ]
    forms['type'].location.choices         = [ (i, locations[i])     for i in range(len (locations))  ] 
    forms['type'].cms.choices              = [ (i, pcbs_[i]['name']) for i in range(len (pcbs_))      ] 
    forms['filter'].cell_type.choices      = [ (i, cell_types[i])    for i in range(len (cell_types)) ]
    forms['filter'].name.choices           = [ (i, cell_names[i])    for i in range(len (cell_names)) ]
    forms['filter'].user.choices           = [ (i, users[i])         for i in range(len (users))      ]


    return render_template('inventory.html',forms=forms, elements=packs_, type= "pack")

@app.route('/inventory/pcbs', methods=['GET'])
# @login_required
def pcbs_get():
    forms = {'type':addPCBModelForm(), 'unit':addPCBBoardForm(), 
             'filter':FilterPcbStockForm()}

    ##### DEBUG
    forms['unit'].model.choices            = [ (i, pcbs_type[i])        for i in range(len (pcbs_type)) ]
    forms['unit'].location.choices         = [ (i, locations[i])         for i in range(len (locations)) ]
    forms['type'].project.choices          = [ (i, projects[i])         for i in range(len (projects))   ]
    forms['filter'].cell_type.choices      = [ (i, pcbs_type[i])        for i in range(len (pcbs_type)) ]
    forms['filter'].name.choices           = [ (i, pcbs_[i]['name'])     for i in range(len (pcbs_))     ]
    forms['filter'].user.choices           = [ (i, users[i])             for i in range(len (users))     ]
    forms['filter'].firmware.choices       = [ (i, pcbs_[i]['firmware']) for i in range(len (users))     ]

    return render_template('inventory.html',forms=forms, elements=pcbs_, type= "pcb")

@app.route('/inventory/cells', methods=['POST'])
# @login_required
def cells_post():
    forms = {'type':CellTypeForm(), 'unit':CellForm(), 'assemble':AssemblePackForm(), 'pack':PackForm(),'filter':FilterCellStockForm()}

    return redirect(url_for(cells_get()))

@app.route('/inventory/packs', methods=['POST'])
# @login_required
def packs_post():
    forms = {'type':CellTypeForm(), 'unit':CellForm(), 'assemble':AssemblePackForm(), 'pack':PackForm(),'filter':FilterPackStockForm()}

    return redirect(url_for(cells_get()))

@app.route('/inventory/pcbs', methods=['POST'])
# @login_required
def pcbs_post():
    forms = {'type':CellTypeForm(), 'unit':CellForm(), 'assemble':AssemblePackForm(), 'pack':PackForm(),'filter':FilterCellStockForm()}

    return redirect(url_for(cells_get()))

@app.route('/inventory/cell_details<id>', methods=['GET'])
# @login_required
def cell_details_get(id):
    cell      = cells_[int(id)]
    model     = {'model':cell['type']}
    tests     = []
    campaigns = []
    return render_template('element_details.html',model= model, element=cell, campains= campaigns, tests=tests, type = 'cell')

@app.route('/inventory/pack_details<id>', methods=['GET'])
# @login_required
def pack_details_get(id):
    pack      = packs_[int(id)]
    model     = {'model':pack['type']}
    tests     = []
    campaigns = []
    return render_template('element_details.html',model= model, element=pack, campains= campaigns, tests=tests, type ='pack')

@app.route('/inventory/pcb_details<id>', methods=['GET'])
# @login_required
def pcb_details_get(id):
    pcb       = pcbs_[int(id)]
    model     = {'model':pcb['type']}
    tests     = []
    campaigns = []
    return render_template('element_details.html',model= model, element=pcb, campains= campaigns, tests=tests, type='pcb')

#============SCHEDULE & EQUIPMENT=====================================
@app.route('/schedule', methods=['GET'])
# @login_required
def schedule_get(): 
    
    current_year, current_week = datetime.datetime.today().isocalendar()[:2]
    length =10
    max_week     = current_week + length

    return render_template('devices_management.html', data = schedules_,current_week=current_week, max_week=max_week,current_year=current_year)

@app.route('/booking/singlecells', methods=['GET'])
@app.route('/booking/singlecells/<data>', methods=['GET'])
# @login_required
def book_device_cells_get(data=None):
    forms = {'addTest'      : addSingleCellsForm(),
             'selectDevice' : selectDeviceForm(),
             'addCampaign'  : addCampaignForm(),
             'addProject'   : addProjectForm(partners="No one")}

    ## DEBUG
    forms['addTest'].type_1.choices       = [ (i, test_types[i]) for i in range(len(test_types)) ]
    forms['addTest'].type_2.choices       = [ (i, test_types[i]) for i in range(len(test_types)) ]
    forms['addTest'].campaign.choices     = [ (i, campaigns[i])  for i in range(len (campaigns)) ]
    forms['addTest'].chambers.choices     = [ (i, chambers[i])   for i in range(len (chambers))  ]
    forms['addCampaign'].project.choices  = [ (i, projects[i])   for i in range(len (projects))  ]
    forms['selectDevice'].device.choices  = [ (i, devicesNames[i]) for i in range(len(devicesNames)) ]
    forms['selectDevice'].channel.choices = [ (i, i) for i in range(channels[0]) ]
    return render_template('book_channel.html', data = data, forms = forms, channelList=channelList, type='cell')

@app.route('/booking/packs', methods=['GET'])
@app.route('/booking/packs/<data>', methods=['GET'])
# @login_required
def book_device_packs_get(data=None):
    forms = {'addTest'      : addSingleCellsForm(),
             'selectDevice' : selectPackForm(),
             'addCampaign'  : addCampaignForm(),
             'addProject'   : addProjectForm(partners="No one")}

    ## DEBUG
    forms['addTest'].type_1.choices      = [ (i, test_types[i]) for i in range(len(test_types)) ]
    forms['addTest'].type_2.choices      = [ (i, test_types[i]) for i in range(len(test_types)) ]
    forms['addTest'].campaign.choices    = [ (i, campaigns[i])  for i in range(len (campaigns)) ]
    forms['addTest'].chambers.choices    = [ (i, chambers[i])   for i in range(len (chambers))  ]
    forms['addCampaign'].project.choices = [ (i, projects[i])   for i in range(len (projects))  ]
    forms['selectDevice'].device.choices = [ (i, devicesNames[i]) for i in range(len(devicesNames)) ]
    forms['selectDevice'].channel.choices = [ (i, i) for i in range(channels[0]) ]

    return render_template('book_channel.html', data = data, forms = forms, channelList=channelList,type='pack')

@app.route('/booking/other', methods=['GET'])
# @login_required
def book_device_other_get(data=None):
    forms = {'addTest'      : addSingleCellsForm(),
             'selectDevice' : selectOtherForm(),
             'addCampaign'  : addCampaignForm(),
             'addProject'   : addProjectForm(partners="No one")}
    forms['addTest'].type_1.choices      = [ (i, test_types[i]) for i in range(len(test_types)) ]
    forms['addTest'].type_2.choices      = [ (i, test_types[i]) for i in range(len(test_types)) ]
    forms['addTest'].campaign.choices    = [ (i, campaigns[i])  for i in range(len (campaigns)) ]
    forms['addTest'].chambers.choices    = [ (i, chambers[i])   for i in range(len (chambers))  ]
    forms['addCampaign'].project.choices = [ (i, projects[i])   for i in range(len (projects))  ]
    return render_template('book_channel.html', data = data, forms = forms, channelList=channelList,type='other')

@app.route('/booking/channel/<device>')
# @login_required
def get_channels(device):
    # channels =[ {'id':channel.id, 'name':channel.chan_number} for channel in Channel.query.filter_by(device_id=int(device)).all() ]
    channels_ = [ {'id':i, 'name': i+1} for i in range(channels[int(device)]) ]
    print(channels_)
    return jsonify({'channels':channels_})

@app.route('/measure/end')
@app.route('/measure/end/<id>')
def endMesure_get(id=None):
    return redirect(url_for(schedule_get()))

@app.route('/measure/cancel')
@app.route('/measure/cancel/<id>')
def cancel(id=None):
    return redirect(url_for(schedule_get()))