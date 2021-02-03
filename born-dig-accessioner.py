#/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import logging.config
import yaml
import functools
import time
from decorator import decorator
import csv
import datetime
import html as html_core
import inspect
import traceback
import signal
import json
from ast import literal_eval
from collections import deque
import sys

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table
import plotly.graph_objs as go
import dash.exceptions

import dill as pickle

import os
from pathlib import Path
import requests


'''
TO-DO - progress bar instead of log printing.

'''

#FIX
#EXE_PATH = os.getcwd()
EXE_PATH = sys.executable.replace('/born-dig-accessioner', '')

def serve_layout(EXE_PATH=EXE_PATH):
    #eventually move these into an external config file
    archivesspace_instances = [{'label': 'PROD', 'value': 'https://archivesspace.library.yale.edu/api'},
            {'label': 'TEST', 'value': 'https://testarchivesspace.library.yale.edu/api'},
            {'label': 'DEV', 'value': 'https://devarchivesspace.library.yale.edu/api'},
            {'label': 'LOCAL', 'value': 'http://localhost:8089'}]
    return html.Div(children=[html.Div(children=[html.H1(children=['Born Digital Accessioning Tools'], className='header-label'),
        html.Div(children=[dcc.Tabs(
            id='all-tabs',
            className='tab_container',
            value='bulk_tab',
            children=[dcc.Tab(
                    #label='Bulk Updates',
                    value='bulk_tab',
                    className='custom-tab',
                    selected_className='custom-tab--selected',
                    children=[html.Div(children=[html.Div(children=[html.P('Create or update archival object records and create event records for DASS workflows.')], className='directions'),
                                                 html.Div(children=dcc.RadioItems(id="api_instance_checklist",
                                                                        options=archivesspace_instances,
                                                                        labelStyle={'display': 'inline-block', 'padding-left': '5px', 'padding-right': '20px'}), className='api_checklist'),
                                                  html.Div(children=[
                                                                    html.Div(children=[dcc.Dropdown(id="input_file_dropdown",
                                                                                           multi=False,
                                                                                           placeholder='Select an input file',
                                                                                           options=[{"label": i, "value": 'data/api_inputs/' + i} for i in os.listdir(f'{EXE_PATH}/data/api_inputs') if i != '.DS_Store' and i != 'excel_sheets' and '.~lock' not in i], className='drop')], className='dropdown'),
                                                                    html.Div(children=[dcc.Dropdown(id="backup_folder_dropdown",
                                                                                           multi=False,
                                                                                           placeholder='Select a backup directory',
                                                                                           options=[{"label": i, "value": 'data/json_backups/' + i} for i in next(os.walk(f'{EXE_PATH}/data/json_backups'))[1]], className='drop')], className='dropdown')], className='dropdown_container'),
                                                 html.Div(children=dcc.RadioItems(id="create_update_selection",
                                                                        options=[{"label": "Create records", "value": "create"}, {"label": "Update records", "value": "update"}],
                                                                        labelStyle={'display': 'inline-block', 'padding-left': '5px', 'padding-right': '20px'}), className='api_checklist'),
                                                 html.Div(children=[dcc.ConfirmDialogProvider(
                                                                        children=[html.Button('Go', id='go_time', n_clicks=0, className='api-button')],
                                                                        id='are_you_surrre',
                                                                        message='With great power comes great responsibility! Are you sure you want to do this?'),
                                                                   #html.Div(className='divider'),
                                                                    html.Button('Stop', id='stop_time',
                                                                                       n_clicks=0,
                                                                    className='api-button')], className='button-div'),
                                                 html.Div(children=[html.H5(id='operation-docs', className='query-desc'),
                                                                   html.Pre(id='api_table', className='doc-table')]),
                                                 dcc.Store(id='selected_0', storage_type="memory"),
                                                 dcc.Store(id='selected_1', storage_type="memory"),
                                                 dcc.Store(id='selected_2', storage_type="memory"),
                                                 dcc.Store(id='selected_3', storage_type="memory"),
                                                 dcc.Store(id='selected_4', storage_type="memory"),
                                                 dcc.Store(id='selected_5', storage_type="memory"),
                                                 dcc.Store(id='selected_6', storage_type="memory"),
                                                 dcc.Store(id='selected_7', storage_type="memory"),
                                                 dcc.Store(id='output-storage', storage_type="memory"),
                                                 dcc.Store(id='object_store', storage_type='memory'),
                                                 html.Div(id='display_log', className='display-log'),
                                                 dcc.Interval(id='log-update', interval=20000000, n_intervals=0)], className='body_div')])])], className='tab_div_container'),
         html.Footer(children=[html.Div(children=[html.A('Yale', href='https://archives.yale.edu', target='_blank', className='yale_footer'),
                                                  html.A('Contact', href='mailto:alicia.detelich@yale.edu', target='_blank', className='footer_links'),
                                                  html.A('Help', href='https://github.com/ucancallmealicia/born-digital-accessioner', target='_blank', className='footer_links')],
                                        className='footer_div_style')], className='footer_style')], className='app_container')])

#external_stylesheets=[dbc.themes.BOOTSTRAP]
print(f"{EXE_PATH}/assets")
app = dash.Dash(__name__, assets_folder=f"{EXE_PATH}/assets")
#app.config.suppress_callback_exceptions = True
app.layout = serve_layout


def setup_logging(default_path=f'{EXE_PATH}/data/logs/logging_config.yml', default_level=logging.DEBUG, EXE_PATH=EXE_PATH):
    '''Sets up logging configuration'''
    print(f'Setting up logging in {__name__}')
    fp = default_path
    if os.path.exists(fp):
        with open(fp, 'r') as file_path:
            config = yaml.safe_load(file_path.read())
            config['handlers']['debug_file_handler']['filename'] = f'{EXE_PATH}/data/logs/debug.log'
            config['handlers']['error_file_handler']['filename'] = f'{EXE_PATH}/data/logs/errors.log'
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def bd_logger(logger_object):
    '''This is a decorator function which takes a logger object as an argument
    and logs the start and end/runtime of each function called during program
    execution. This decorator is applied to almost every function in the
    aspace-tools package. Could potentially remove the decorator from all of the
    json_data.py functions (already not in the queries.py functions), since all
    they do is take strings and put them into dictionaries, which takes no time at all
    Would be nice to know when the function runs, though, so maybe have a second
    decorator for the queries.py and json_data functions??'''
    #def decorator_as_tools_logger(func):
    @decorator
    def wrapper_as_tools_logger(func, *args, **kwargs):
        logger_object.debug(f'Starting {func.__name__!r}')
        start_time = time.perf_counter()
        try:
            #logging.debug(f'args: {args}')
            #logging.debug(f'kwargs: {kwargs}')
            value = func(*args, **kwargs)
            end_time = time.perf_counter()
            run_time = end_time - start_time
            logger_object.debug(f'{func.__name__!r} run time: {run_time:.4f} secs')
            return value
        except Exception:
            logger_object.exception('Error: ')
    return wrapper_as_tools_logger
    #return decorator_as_tools_logger

#Open a CSV in reader mode
def opencsv(input_csv=None):
    """Opens a CSV in reader mode."""
    try:
        if input_csv is None:
            input_csv = input('Please enter path to CSV: ')
        if input_csv == 'quit':
            quit()
        file = open(input_csv, 'r', encoding='utf-8')
        csvin = csv.reader(file)
        headline = next(csvin, None)
        return headline, csvin
    except:
        logging.exception('Error: ')
        logging.debug('Trying again...')
        logging.debug('CSV not found. Please try again. Enter "quit" to exit')
        h, c = opencsv()
        return h, c

def config_file_helper(value, config_type, EXE_PATH=EXE_PATH):
    with open(f'{EXE_PATH}/data/config.json', 'r', encoding='utf-8') as config_file:
        cfg = json.load(config_file)
    cfg[config_type] = value
    with open(f'{EXE_PATH}/data/config.json', 'w', encoding='utf-8') as config_file:
        json.dump(cfg, config_file)
    return value

def save_session(session, api_url, EXE_PATH=EXE_PATH):
    if 'archivesspace' in api_url:
        fpname = api_url[8:-21]
    elif 'local' in api_url:
        fpname = 'local'
    with open(f'{EXE_PATH}/data/sessions/{fpname}.pkl', 'wb') as out_strm:
        pickle.dump(session, out_strm)
        return f'{EXE_PATH}/data/sessions/{fpname}.pkl'

def load_session(api_url, session_list, EXE_PATH=EXE_PATH, session=None, session_file=None):
    if ('local' in api_url and 'local.pkg' in session_list):
        session_file = f'{EXE_PATH}/data/sessions/local.pkl'
        session = pickle.load(open(session_file, 'rb'))
    else:
        sessions = [(pickle.load(open(f'{EXE_PATH}/data/sessions/{sesh}', 'rb')), f'{EXE_PATH}/data/sessions/{sesh}') for sesh in session_list if api_url[8:-21] == sesh[:-4]]
        if sessions:
            session = sessions[0][0]
            session_file = sessions[0][1]
    return session, session_file

def as_session(api_url, username, password, EXE_PATH=EXE_PATH, session=None):
    session_list = os.listdir(f'{EXE_PATH}/data/sessions')
    session, session_file = load_session(api_url, session_list)
    if (session == [] or session == None):
        try:
            session = requests.Session()
            session.headers.update({'Content_Type': 'application/json'})
            response = session.post(api_url + '/users/' + username + '/login',
                         params={"password": password, "expiring": False})
            if response.status_code != 200:
                logging.debug(f"Error could not connect: {response.status_code}")
            else:
                session_toke = json.loads(response.text)['session']
                session.headers['X-ArchivesSpace-Session'] = session_toke
                session_file = save_session(session, api_url)
        except Exception:
            logging.debug(traceback.format_exc())
    return session, session_file


#Open a CSV file in writer mode
def opencsvout(output_csv=None):
    """Opens a CSV in write mode."""
    try:
        if output_csv is None:
            output_csv = input('Please enter path to output CSV: ')
        if output_csv == 'quit':
            quit()
        fileob = open(output_csv, 'a', encoding='utf-8', newline='')
        csvout = csv.writer(fileob)
        logging.debug('Outfile opened: ' + output_csv)
        return (fileob, csvout)
    except Exception:
        logging.exception('Error: ')
        print('Error creating outfile. Please try again. Enter "quit" to exit')
        f, c = opencsvout()
        return (f, c)

def opencsvdictout(output_csv=None, col_names=None):
    """Opens a CSV in DictWriter mode."""
    try:
        if output_csv is None:
            output_csv = input('Please enter path to CSV: ')
        fileob = open(output_csv, 'a', newline='', encoding='utf-8')
        if col_names != None:
            csvin = csv.DictWriter(fileob, col_names)
            csvin.writeheader()
        else:
            csvin = csv.DictWriter(fileob)
        return fileob, csvin
    except:
        logging.exception('Error: ')
        logging.debug('Trying again...')
        print('CSV not found. Please try again.')
        return opencsvdictout()

#Open a CSV in dictreader mode
def opencsvdict(input_csv=None):
    """Opens a CSV in DictReader mode."""
    '''Fieldnames currently hardcoded because I need to fix the formatting of the CSV reader, since there are instructions embedded in the cells of the first row that get split into different rows when I try to parse the file before reading it into the CSV dict '''
    fieldnames = ['Repository Name', 'Security Tag', 'Parent Record', 'Title', 'Component Unique ID', 'Type_1', 'Type_2_Number', 'Type_2', 'Top Container', 'Collection Name', 'Event_Type_1', 'Outcome_1', 'Begin_1', 'Outcome_Note_1', 'Event_Type_2', 'Outcome_2', 'Begin_2', 'Outcome_Note_2', 'Event_Type_3', 'Outcome_3', 'Begin_3', 'Outcome_Note_3', 'Authorizer']
    try:
        if input_csv is None:
            input_csv = input('Please enter path to input CSV file: ')
        if input_csv in ('quit', 'Q', 'Quit'):
            raise SystemExit
        infile = open(input_csv, 'r', encoding='utf-8', newline='')
        csv_file = csv.DictReader(infile, fieldnames=fieldnames)
        #skips first two rows of CSV file
        for i in range(2):
            next(csv_file)
        return csv_file, fieldnames
    except FileNotFoundError:
        return opencsvdict()

@app.callback([Output('selected_0', 'data')
    , Output('object_store', 'data')],
    [Input('api_instance_checklist', 'value')])
def select_api_instance(value, EXE_PATH=EXE_PATH):
    '''Modifies the config file to a user-selected ArchivesSpace instance'''
    if value:
        config_file_helper(value, 'api_url')
        with open(f'{EXE_PATH}/data/config.json') as cfg_file:
            config_file = json.load(cfg_file)
            sesh, sesh_file = as_session(config_file['api_url'], config_file['api_username'], config_file['api_password'])
            #logging.debug(sesh_file)
            #logging.debug(sesh)
            return value, sesh_file
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(
    Output('selected_1', 'data'),
    [Input('input_file_dropdown', 'value')])
def select_input_file(value):
    '''Modifies the config file to a user-selected input file'''
    if value:
        return config_file_helper(value, 'input_csv')
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(
    Output('selected_2', 'data'),
    [Input('backup_folder_dropdown', 'value')])
def select_backup_directory(value):
    '''Modifies the config file to a user-selected backup directory.'''
    if value:
        return config_file_helper(value, 'backup_directory')
    else:
        raise dash.exceptions.PreventUpdate()

#WHEN SHOULD THIS RUN?? Right now it runs when the API instance checklist is selected. Which I think makes sense.
@app.callback(Output('selected_7', 'data'),
    [Input('input_file_dropdown', 'value')],
    [State('selected_0', 'data'),
     State('object_store', 'data')])
def set_agent(input_file, api_url, session_file_path, EXE_PATH=EXE_PATH):
    if input_file:
        if session_file_path:
            with open(session_file_path, 'rb') as session_file_p:
                session_data = pickle.load(session_file_p)
                #logging.debug(session_data)
            if api_url:
                with open(f'{EXE_PATH}/data/config.json') as cnfg_file:
                    config_file = json.load(cnfg_file)
                    '''Alternatively this can be set within the CSV file itself - that's how Mary has her spreadsheet set up'''
                    agent_authorizer = config_file['agent_authorizer']
                    #logging.debug(f"agent_authorizer: {agent_authorizer}")
                    if (agent_authorizer != "" and agent_authorizer != config_file['api_username']):
                        #logging.debug('SEARCHING AGENTS')
                        search_agent = session_data.get(api_url + '/search?page=1&type[]=agent_person&q=title:' + agent_authorizer).json()
                        #logging.debug(search_agent)
                        if search_agent['total_hits'] == 1:
                            logging.debug(f'Search agent: result found for {agent_authorizer}')
                            agent_uri = search_agent['results'][0]['uri']
                            return agent_uri
                        if search_agent['total_hits'] == 0:
                            cur_user = session_data.get(api_url + '/users/current-user').json()
                            agent_uri = cur_user['agent_record']['ref']
                            logging.debug('Search agent error: no results found. Assigning current user as authorizer')
                            return agent_uri
                            #raise dash.exceptions.PreventUpdate()
                        if search_agent['total_hits'] > 1:
                            logging.debug('Search agent error: multiple results found')
                            #add some kind of message here?
                            raise dash.exceptions.PreventUpdate()
                        # else:
                        #     logging.debug('SOME OTHER THING')
                    else:
                        cur_user = session_data.get(api_url + '/users/current-user').json()
                        agent_uri = cur_user['agent_record']['ref']
                        return agent_uri
            else:
                raise dash.exceptions.PreventUpdate()
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('selected_4', 'data'),
    [Input('input_file_dropdown', 'value')])
def set_resource_id(value):
    '''Sets the resource ID'''
    if value:
        header_row, csvfile = opencsv(value)
        for i in range(2):
            next(csvfile)
        csvlist = next(csvfile)
        if '/#' in str(csvlist[2]):
            resource_id = (csvlist[2].partition('/#')[0].rpartition('/')[2])
        else:
            resource_id = (csvlist[2].partition('#')[0].rpartition('/')[2])
        return resource_id
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('selected_5', 'data'),
    [Input('input_file_dropdown', 'value')],
    [State('selected_0', 'data'),
     State('object_store', 'data')])
def set_repository(value, api_url, obj_store):
    if obj_store:
        with open(obj_store, 'rb') as session_file_path:
            session_data = pickle.load(session_file_path)
        if value:
            repo_dict = get_repos(session_data, api_url)
            #logging.debug(repo_dict)
            header_row, csvfile = opencsv(value)
            #logging.debug(csvfile)
            for i in range(2):
                next(csvfile)
            csvlist = next(csvfile)
            return repo_dict[csvlist[0]]
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('selected_6', 'data'),
    [Input('input_file_dropdown', 'value')])
def set_parent(value):
    if value:
        header_row, csvfile = opencsv(value)
        #fix this
        for i in range(2):
            next(csvfile)
        csvlist = next(csvfile)
        return str(csvlist[2]).rpartition("_")[2]
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('output-storage', 'data'),
     [Input('create_update_selection', 'value'),
      Input('go_time', 'n_clicks'),
      Input('stop_time', 'n_clicks'),
      Input('are_you_surrre', 'submit_n_clicks')],
     [State('selected_0', 'data'),
      State('selected_6', 'data'),
      State('selected_5', 'data'),
      State('selected_4', 'data'),
      State('selected_7', 'data'),
      State('backup_folder_dropdown', 'value'),
      State('input_file_dropdown', 'value'),
      State('object_store', 'data')])
def start_process(func_selection, n_clicks, s_clicks, confirm, api_url, parent_id, repo_id, resource_id, agent_uri, backup_dir, input_file, obj_store):
    if obj_store:
        if not confirm:
            raise dash.exceptions.PreventUpdate()
        else:
            with open(obj_store, 'rb') as session_file_path:
                session_data = pickle.load(session_file_path)
            n_clicks += 1
            if n_clicks > 0 and s_clicks == 0:
                if backup_dir and input_file:
                    try:
                        csvfile, fieldnames = opencsvdict(input_file)
                        extra_fieldnames = ['New_Component_URI', 'Event_URI_1', 'Event_URI_2', 'Event_URI_3']
                        fileobject, csvoutfile = opencsvdictout(f"{input_file}_out.csv", fieldnames + extra_fieldnames)
                        top_container_list = get_top_containers(api_url, session_data, repo_id, parent_id)
                        #logging.debug(top_container_list)
                        while csvfile:
                            row = next(csvfile)
                            #titles
                            row['Title'] = html_core.escape(row['Title'])
                            row['Parent Record'] = str(row['Parent Record']).rpartition("_")[2]
                            if func_selection == 'update':
                                #logging.debug('This part is running now')
                                top_container_list = get_top_containers(api_url, session_data, repo_id, row['Parent Record'])
                                #logging.debug(top_container_list)
                                row['Top Container'] = match_containers(top_container_list, row['Top Container'])
                                #logging.debug(row['Top Container'])
                                component, endpoint = update_child_component(row, session_data, api_url, row['Parent Record'], repo_id)
                            elif func_selection == 'create':
                                row['Top Container'] = match_containers(top_container_list, row['Top Container'])
                                component, endpoint = create_child_component(row, repo_id, parent_id, resource_id)
                            record_post = session_data.post(f"{api_url}{endpoint}", json=component).json()
                            logging.debug(record_post)
                            row = process_event_rows(row, agent_uri, repo_id, record_post, api_url, session_data)
                            csvoutfile.writerow(row)
                            #then write the row to something...
                            if s_clicks > 0 and n_clicks > 0:
                                return "nothing"
                    except Exception:
                        logging.debug(traceback.format_exc())
                    finally:
                        fileobject.close
                else:
                    raise dash.exceptions.PreventUpdate()
            else:
                raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback([Output('display_log', 'children'), Output('log-update', 'interval')],
    [Input('are_you_surrre', 'submit_n_clicks'), Input('stop_time', 'n_clicks'), Input('log-update', 'n_intervals')],
    [State('log-update', 'interval')])
def display_log(n_clicks, s_clicks, n_intervals, the_interval, EXE_PATH=EXE_PATH):
    if n_clicks:
        with open(f'{EXE_PATH}/data/logs/debug.log', 'r', encoding='utf-8') as lfile:
            last_30 = deque(lfile, 30)
            if (s_clicks == 0 and n_clicks > 0):
                return html.Div(list(last_30)), 1000
            if (s_clicks == 0 and n_clicks == 0):
                return html.Div(''), 2147483647
            if (s_clicks > 0 and n_clicks > 0):
                return html.Div(list(last_30)), 2147483647
    else:
        raise dash.exceptions.PreventUpdate()

def get_top_container_helper(parent_component, api_url, session_data):
    tc_list = [instance['sub_container']['top_container']['ref'] for instance in parent_component['instances']]
    tuplelist = []
    for tc_uri in tc_list:
        top_container = session_data.get(f"{api_url}{tc_uri}").json()
        tuplelist.append((top_container['uri'], top_container['indicator']))
    return tuplelist

def get_top_containers(api_url, session_data, repo_id, parent_id, tup_list=None):
    #this gets a list of top containers for the parent component - assumes there will only be one parent...is this true??
    #what happens if there are no top containers?
    parent_component = session_data.get(f"{api_url}/repositories/{repo_id}/archival_objects/{parent_id}").json()
    #logging.debug(parent_component)
    if parent_component.get('instances') is not None and 'digital_object' not in [instance.get('instance_type') for instance in parent_component.get('instances')]:
        tup_list = get_top_container_helper(parent_component, api_url, session_data)
    else:
        #so what do I do when there isn't a container???
        #This gets the immediate parent of the parent_component variable
        parent_of_parent = parent_component['ancestors'][0]['ref']
        parent_of_parent_json = session_data.get(f"{api_url}/{parent_of_parent}").json()
        #logging.debug(parent_of_parent)
        tup_list = get_top_container_helper(parent_of_parent_json, api_url, session_data)
        #logging.debug(parent_component)
        #logging.debug('No linked instances')
    return tup_list

def match_containers(tc_indicator_list, top_container):
    #logging.debug(tc_indicator_list)
    #logging.debug(top_container)
    container_list = [uri for uri, indicator in tc_indicator_list if (uri != None and indicator == top_container)]
    #logging.debug(f'container_list: {container_list}')
    return container_list[0]

def get_repos(session_data, api_url):
    repo_list = session_data.get(f"{api_url}/repositories").json()
    repo_d = {repo['repo_code']: str(repo['uri'][14:]) for repo in repo_list}
    #logging.debug(repo_d)
    return repo_d

def create_new_instance(tc_uri, component):
    new_instance = [{"instance_type": 'mixed_materials',
                                "jsonmodel_type": 'instance',
                                "sub_container": {"jsonmodel_type": 'sub_container',
                                                  "top_container": {"ref": tc_uri}}}]
    component['instances'] = new_instance
    return component

def update_child_component(row, session_data, api_url, ao_id, repo_id):
    #fix the ao_id - WHAT DOES THIS MEAN???????
    component_json = session_data.get(f"{api_url}/repositories/{repo_id}/archival_objects/{ao_id}").json()
    current_top_container_uris = [instance['sub_container']['top_container']['ref']
                                  for instance in component_json.get('instances')
                                  if component_json.get('instances') is not None
                                  and 'digital_object' not in [instance.get('instance_type') for instance in component_json.get('instances')]]
    #logging.debug(current_top_container_uris)
    component_json['component_id'] = row['Component Unique ID']
    # this overwrites whatever extent may already be there
    component_json['extents'] = [{ "number": '1', "portion": "whole", "extent_type": row['Type_1'], "jsonmodel_type": "extent"}]
    if row['Type_2_Number'] != '':
        component_json['extents'].append({ "number": row['Type_2_Number'], "portion": "whole", "extent_type": row['Type_2'], "jsonmodel_type": "extent"})
    #component_json['extents'].append({ "number": '1', "portion": "whole", "extent_type": row[5], "jsonmodel_type": "extent"})
    #I want to check against the instance list now before adding the top container data
    if row['Top Container'] not in current_top_container_uris:
        component_json = create_new_instance(row['Top Container'], component_json)
    endpoint = f"/repositories/{repo_id}/archival_objects/{ao_id}"
    return component_json, endpoint

#the ao_id here is the parent archival object ID
def create_child_component(row, repo_id, parent_id, resource_id):
    #First, check if there is a value in the top container field. There won't always be one.
    child_component = {"publish": True, "title": row['Title'], "level": "item",
             "component_id": row['Component Unique ID'], "jsonmodel_type": "archival_object",
             "extents": [{"number": '1',
                          "portion": "whole",
                          "extent_type": row['Type_1'],
                          "jsonmodel_type": "extent"}],
             "resource": {"ref": f"/repositories/{repo_id}/resources/{resource_id}"},
            "parent": {"ref": f"/repositories/{repo_id}/archival_objects/{parent_id}"}}
    if row['Type_2_Number'] != '':
        child_component['extents'].append({ "number": row['Type_2_Number'], "portion": "whole", "extent_type": row['Type_2'], "jsonmodel_type": "extent"})
    if row['Top Container'] != '':
        child_component = create_new_instance(row['Top Container'], child_component)
    endpoint = f"/repositories/{repo_id}/archival_objects"
    return child_component, endpoint

# this should have more of the csv processing stuff....
def create_event(user, ao_id, repo_num, event_type, outcome_value, date_value, note_value, api_url, session_data):
    '''This function creates an event in ASpace, based on the four possible parameters provided in the born-digital accessioning worksheet'''
    # if date_value != '':
    #     if '-' in date_value:
    #         date_value = date_value.replace('-', '/')
    #     date_value = datetime.datetime.strptime(date_value, '%m/%d/%Y').strftime('%Y-%m-%d')
    event = {"event_type": event_type.lower(), "jsonmodel_type": "event", "outcome": outcome_value.lower(),
            "outcome_note": note_value, "linked_agents": [{ "role": "authorizer", "ref": user}],
             "linked_records": [{ "role": "source", "ref": '/repositories/' + repo_num + '/archival_objects/' + ao_id }],
             "date": { "begin": date_value, "date_type": "single", "label": "event", "jsonmodel_type": "date" }}
    event_post = session_data.post(f"{api_url}/repositories/{repo_num}/events", json=event).json()
    logging.debug(event_post)
    return event_post

def process_event_rows(row, agent_uri, repo_id, updated_component, api_url, headers):
    component_uri = updated_component.get('uri')
    row['New_Component_URI'] = component_uri
    #creating events based on the rows in the spreadsheet - can't use the csvdict because the row names are the same...
    if row['Event_Type_1'] != '':
        new_event = create_event(agent_uri, component_uri, repo_id, row['Event_Type_1'], row['Outcome_1'], row['Begin_1'], html_core.escape(row[
            'Outcome_Note_1']), api_url, headers)
        row['Event_URI_1'] = new_event.get('uri')
    if row['Event_Type_2'] != '':
        new_event = create_event(agent_uri, component_uri, repo_id, row['Event_Type_2'], row['Outcome_2'], row['Begin_2'], html_core.escape(row['Outcome_Note_2']), api_url, headers)
        row['Event_URI_2'] = new_event.get('uri')
    if row['Event_Type_3'] != '':
        new_event = create_event(agent_uri, component_uri, repo_id, row['Event_Type_3'], row['Outcome_3'], row['Begin_3'], html_core.escape(row['Outcome_Note_3']), api_url, headers)
        row['Event_URI_3'] = new_event.get('uri')
    return row


if __name__ == '__main__':
    logger_ob = setup_logging()
    logger = bd_logger(logger_ob)
    app.run_server(debug=False)



#     #Opens the parent record in ArchivesSpace staff interface via button widget
#     def openparent_record(self):
#         #this is where I could use the resource ID
#         url_end = self.parent_id.get()
#         resource = self.resource_id.get()
#         get_api = self.api_url.get()
#         base_url = get_api[:-3]
#         #add something here to make sure there are enough/not to many forward slashes...still works but doesn't look right
#         full_url = base_url + '/resources/' + resource + '#tree::archival_object_' + url_end
#         if full_url[-1].isdigit() :
#             try:
#                 webbrowser.open(full_url, new=2)
#             except:
#                 messagebox.showerror('Error!', '\n                     Invalid URL')
#         else:
#             if 'https' in base_url:
#                 webbrowser.open(base_url, new=2)
#             else:
#                 messagebox.showerror('Error!', '\n                     Invalid URL')
