#/usr/bin/python3
#~/anaconda3/bin/python
# -*- coding: utf-8 -*-

from tkinter import StringVar, Tk, Text, Toplevel, Menu, Label, DISABLED, RAISED, RIDGE, SUNKEN, GROOVE, LEFT, LabelFrame, WORD, INSERT, Button, Entry, W, E, N, S, NW, HORIZONTAL, VERTICAL, Frame, messagebox, filedialog, ttk, scrolledtext, Scrollbar, Canvas
from tkinter.filedialog import askopenfilename
import json, requests, csv, os, sys, subprocess, time, logging, re, cgi, datetime, traceback, webbrowser
from itertools import islice
from pathlib import Path

class BornDigitalGUI(Frame):
    def __init__(self, master):
        ##### Configure Canvas #####
        Frame.__init__(self, master)
        self.master = master
        self.canvas = Canvas(master, borderwidth=0)
        self.frame = Frame(self.canvas)
        self.canvas.create_window((4,4), window=self.frame, anchor='nw', tags='self.frame')
        self.master.title('Born Digital Accessioner 1.0')
        self.initmenu()
        self.frame.config(bg='gainsboro', highlightthickness=0)
        self.canvas.config(bg='gainsboro', highlightthickness=0)
        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.frame.grid(row=0, column=0, sticky="nsew")

        ##### Execute login process by pressing Enter ####
        self.master.bind('<Return>', self.asloginprocess)
        
        ########### Step 1: Login to ArchivesSpace API ###########
        
        ## Set Step 1 Variable Inputs ##
        self.authenticate = StringVar()
        self.api_url = StringVar()
        self.username = StringVar()
        self.password = StringVar()
   #     self.agent_name = StringVar()
        self.login_confirmed = StringVar()
        
        ## Create Step 1 Widgets ##
        
        self.login_labelframe = LabelFrame(self.frame, text='Step 1: Connect to ArchivesSpace', font=('Arial', 14), bg='gainsboro', padx=1, pady=1)
        self.api_url_label = Label(self.login_labelframe, text='ArchivesSpace URL: ', font=('Arial', 13), bg='gainsboro')
        self.username_label = Label(self.login_labelframe, text='ArchivesSpace Username: ', font=('Arial', 13), bg='gainsboro')
        self.password_label = Label(self.login_labelframe, text='ArchivesSpace Password: ', font=('Arial', 13), bg='gainsboro')
        self.alternate_agent_label = Label(self.login_labelframe, text='Agent Authorizer (Optional):', font=('Arial', 13), bg='gainsboro')
        self.api_url_entry = Entry(self.login_labelframe, width=32, textvariable=self.api_url, highlightthickness=0)
        self.username_entry = Entry(self.login_labelframe, width=32, textvariable=self.username, highlightthickness=0)
        self.password_entry =Entry(self.login_labelframe, width=32, textvariable=self.password, show='*', highlightthickness=0)
#        self.alternate_agent = Entry(self.login_labelframe, width=32, textvariable=self.agent_name, highlightthickness=0)
        self.login_confirmed_variable = Label(self.login_labelframe, textvariable=self.login_confirmed, width=25, font=('Arial', 13), bg='gainsboro', highlightthickness=0, anchor='e')
        self.connect_button = Button(self.login_labelframe, text='Connect!',command=self.asloginprocess, width=10, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")

        ## Set Set Step 1 Widget Layout ##
        self.login_labelframe.grid(column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.login_labelframe.grid_rowconfigure(0, weight=1)
        self.login_labelframe.grid_columnconfigure(0, weight=1)
        self.api_url_label.grid(column=0, row=2, sticky="nw")
        self.api_url_entry.grid(column=0, row=3, sticky="nw")
        self.username_label.grid(column=0, row=4, sticky="nw")
        self.username_entry.grid(column=0, row=5, sticky="nw")
        self.password_label.grid(column=0, row=6, sticky="nw")
        self.password_entry.grid(column=0, row=7, sticky="nw")
        self.login_confirmed_variable.grid(column=1, row=6, sticky="ns")
        self.connect_button.grid(column=1, row=7, sticky="ne")
 #       self.alternate_agent_label.grid(column=0, row=8, sticky="nw")
 #       self.alternate_agent.grid(column=0, row=9, sticky="nw")

        ########### Step 2: Select Input CSV ###########

        ## Set Step 2 Variable Inputs ##
        self.csv_filename = StringVar()
        
        ## Create Step 2 Widgets ##
        self.fileselect_labelframe = LabelFrame(self.frame, text='Step 2: Select Input CSV', font=('Arial', 14), bg='gainsboro', highlightthickness=0, padx=1, pady=1)
        self.file_selected_label = Label(self.fileselect_labelframe, text='Selection: ', font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.selected_csv_variable = Label(self.fileselect_labelframe, textvariable=self.csv_filename, width=65, font=('Arial', 11), anchor='w', bg='gainsboro', highlightthickness=0)
        self.input_csv_button = Button(self.fileselect_labelframe, text='Select File', command=self.csvbutton, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")
        
        ## Set Step 2 Layout ##
        self.fileselect_labelframe.grid(column=0, columnspan=2, sticky="nsew", padx=5, pady=5)  
        self.fileselect_labelframe.grid_rowconfigure(0, weight=1)
        self.fileselect_labelframe.grid_columnconfigure(0, weight=1)
        self.input_csv_button.grid(column=1, row=10, sticky='se')
        self.file_selected_label.grid(column=0, columnspan=1, row=11, sticky='w')
        self.selected_csv_variable.grid(column=0, row=12, columnspan=2, sticky='w')

        ## Set Step _ Variable Inputs ##
        self.csv_output = StringVar()

        ########### Step 3: Choose an Action ###########
        
        ## Create Step 3 Widgets ##
        self.action_labelframe = LabelFrame(self.frame, text='Step 3: Choose Action', font=('Arial', 14), bg='gainsboro', highlightthickness=0, padx=1, pady=1)
        self.create_components_button = Button(self.action_labelframe, text='Create records', width=30, command=self.run_create_script, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")
        self.update_components_button =  Button(self.action_labelframe, text='Update records', width=30, command=self.run_update_script, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")
        
        ## Set Step 3 Layout ##
        self.action_labelframe.grid(column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.action_labelframe.grid_rowconfigure(0, weight=1)
        self.action_labelframe.grid_columnconfigure(0, weight=1)
        self.create_components_button.grid(row=13,columnspan=2)
        self.update_components_button.grid(row=14, columnspan=2)

        ########### Step 4: Review Output ###########

        ## Set Step 4 Variable Inputs ##
        self.update_attempts = StringVar()
        self.updates_success = StringVar()
        self.elapsed_time = StringVar()
        self.log_file = StringVar()
        self.error_dialog = StringVar()
        self.script_status = StringVar()
        self.parent_id = StringVar()
        self.resource_id = StringVar()
        self.repo_id_no = StringVar()

        ## Create Step 4 Widgets ##
        self.output_labelframe = LabelFrame(self.frame, text='Step 4: Review Output', font=('Arial', 14), bg='gainsboro', highlightthickness=0, padx=1, pady=1)
        self.script_status_variable = Label(self.output_labelframe, textvariable=self.script_status, font=('Arial', 13), anchor='e', bg='gainsboro', highlightthickness=0)
        self.record_updates_attempted_label = Label(self.output_labelframe, text='Record updates attempted: ', width=30, font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.record_updates_attempted_variable = Label(self.output_labelframe, textvariable=self.update_attempts, width=30, font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.records_updated_successsfully_label = Label(self.output_labelframe, text='Records updated successfully: ', width=30, font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.records_updated_successsfully_variable = Label(self.output_labelframe, textvariable=self.updates_success, width=30, font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.elapsed_time_label = Label(self.output_labelframe, text='Elapsed time: ', width=30, font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.elapsed_time_variable = Label(self.output_labelframe, textvariable=self.elapsed_time, width=30, font=('Arial', 13), anchor='w', bg='gainsboro', highlightthickness=0)
        self.view_output_file_button = Button(self.output_labelframe, text='Open Output File', command=self.opencsvoutput, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")
        self.view_error_log_button = Button(self.output_labelframe, text='Open Log', command=self.openerrorlog, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")
        self.view_url_button = Button(self.output_labelframe, text='Open in ArchivesSpace', command=self.openparent_record, relief=RAISED, bd=1, padx=3, pady=3, highlightthickness=0, cursor="hand1")

        ## Set Step 5 Layout ##    
        self.output_labelframe.grid(column=0, columnspan=2, sticky="nsew", padx=5, pady=5)   
        self.output_labelframe.grid_rowconfigure(0, weight=1)
        self.output_labelframe.grid_columnconfigure(0, weight=1)
        self.script_status_variable.grid(column=1, row=15, sticky='e')
        self.record_updates_attempted_label.grid(column=0, row=16)
        self.records_updated_successsfully_label.grid(column=0, row=17)
        self.elapsed_time_label.grid(column=0, row=18)
        self.record_updates_attempted_variable.grid(column=1, row=16, sticky='w')
        self.records_updated_successsfully_variable.grid(column=1, row=17, sticky='w')
        self.elapsed_time_variable.grid(column=1, row=18, sticky='w')     
        self.view_output_file_button.grid(column=1, row=19, sticky="ne")
        self.view_error_log_button.grid(column=1, row=20, sticky="ne")
        self.view_url_button.grid(column=1, row=21, sticky="ne")
        
        ## Clear Inputs, Help Buttons
        
        self.clear_labelframe = LabelFrame(self.frame, text=None, bg='gainsboro', highlightthickness=0, padx=1, pady=1)
        self.clear_labelframe.grid(column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.clear_labelframe.grid_rowconfigure(0, weight=1)
        self.clear_labelframe.grid_columnconfigure(0, weight=1)
        self.clear_all_inputs_button = Button(self.clear_labelframe, text='Clear Inputs', command=self.clear_inputs, relief=RAISED, bd=1, padx=5, pady=5, highlightthickness=0, cursor="hand1")
        self.clear_all_inputs_button.grid(column=0, row=22)
        
        #Initiates error logging
        self.error_log()
   
    ####### Functions #########
    
    #initializes file menu - see https://stackoverflow.com/questions/34442626/why-is-the-menu-not-showing-on-my-tkinter-gui/34442773
    def initmenu(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        filemenu = Menu(menubar)
        filemenu.add_command(label='Help', command=self.new_window)
        filemenu.add_command(label='Template', command=self.open_template)
        filemenu.add_command(label="Exit", command=self.client_exit)
        menubar.add_cascade(label="File", menu=filemenu)
    
    #Opens the help file in a new window
    def new_window(self):
        self.newwindow = Toplevel(self.master)
        self.newwindow.title('Born-Digital Accessioner Help')
        f = open('./files/bd_accessioner_help.txt', 'r', encoding='utf-8')
        self.textbox = Text(self.newwindow, width=115)
        self.textbox.pack(side='top', fill='both', expand=True)
        self.textbox.insert(0.0, f.read())
        self.textbox.config(state=DISABLED, wrap=WORD)
        self.textbox.grid_rowconfigure(0, weight=1)
        self.textbox.grid_columnconfigure(0, weight=1)
        
    #exits program
    def client_exit(self):
        self.quit()
    
    #opens the born-dig-accessioner template in the system's default program
    def open_template(self):
        #Open template file
        if sys.platform == "win32":
            os.startfile('./files/Template_Digital_Accessioning_Service_Metadata_102017.xlsx')
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, './files/Template_Digital_Accessioning_Service_Metadata_102017.xlsx'])
        
    #logs in to ArchivesSpace API
    def asloginprocess(self, event=None):
        try:
            #basic/imperfect check for improperly formatted URLs
            urlcheck = re.compile(
                r'^https?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            #if URL field is empty; missing field error checks may be obsolete now but I'm leaving it in because the URL checks may not be perfect
            if self.api_url.get() == '':
                self.login_confirmed.set('Missing value, try again')
            #empty username field
            if self.username.get() == '':
                self.login_confirmed.set('Missing value, try again')
            #empty password field
            if self.password.get() == '':
                self.login_confirmed.set('Missing value, try again')
            #uses reg ex above to check formulation of URL; may not be perfect but anything it misses gets caught later 
            if not re.match(urlcheck, self.api_url.get()):
                self.login_confirmed.set('Invalid URL, try again')
            else:
                if self.api_url.get().endswith('/'):
                    self.api_url.set(self.api_url.get() + 'api')
                else:
                    self.api_url.set(self.api_url.get() + '/api')
                #self.api_url.set(self.api_url.get())
                auth = requests.post(self.api_url.get()+'/users/'+self.username.get()+'/login?password='+self.password.get()).json()
                if 'error' in auth.keys():
                    self.login_confirmed.set('Login failed, try again')
                elif 'session' in auth.keys():
                    session = auth["session"]
                    h = {'X-ArchivesSpace-Session':session, 'Content_Type': 'application/json'}
                    self.login_confirmed.set('Login successful!')
                    self.authenticate.set(h)
                    return h
        #this captures a URL that is valid but not correct, plus any other errors
        except Exception:
            self.login_confirmed.set('Error, check login info and try again') 
    
    #gets headers without logging in to API again - a bit of a hack with the JSON loads (bc the StringVar doesn't return key/value pair), but it works for now
    def get_headers(self):
        headers_string = self.authenticate.get()
        if self.authenticate.get() == '':
            messagebox.showerror('Error!', 'Please log in to the ArchivesSpace API')
            return
        else:
            valid_json = headers_string.replace("'", "\"")
            headers_json = json.loads(valid_json)
            return headers_json
    
    #opens CSV
    def opencsv(self):
        filename = self.csv_filename.get()
        if self.csv_filename.get() == '':
            messagebox.showinfo('Error!', 'Please choose an input CSV')
            return
        else:
            try:
                file = open(filename, 'r', encoding='utf-8', errors='replace')
                csvin = csv.reader(file)
                #Skips first two rows
                next(csvin, None)
                next(csvin, None)
                return csvin
            except:
                problem = messagebox.showerror('Error', 'Could not open CSV file.') 
                logging.exception('Error: ')
                return
    
    def outputcsv(self):
        filename = self.csv_filename.get()
        newname = filename.rsplit(".", 1)[0]
        if self.csv_filename.get() == '':
            messagebox.showinfo('Error!', 'Please choose an input CSV')
            return
        else:
            c = open(newname + '_outfile.csv', 'a', encoding='utf-8', newline='')
            csvoutputfile = newname + '_outfile.csv'
            self.csv_output.set(str(csvoutputfile))
            writer = csv.writer(c)
            return (c, writer)
        
    def timer(self, start):
        elapsedTime = time.time() - start
        m, s = divmod(elapsedTime, 60)
        h, m = divmod(m, 60)
        self.elapsed_time.set('%d:%02d:%02d' % (h, m, s))

    #gets a list of repositories
    def repos(self, header_value):
        repo_list = requests.get(self.api_url.get() + '/repositories', headers=header_value).json()
        repo_d = {}
        for repo in repo_list:
            if repo['repo_code'] not in repo_d:
                repo_d[repo['repo_code']] = repo['uri'][14:]
        return repo_d 
    
    #the ao_id here is the parent archival object ID       
    def create_child_component(self, header_value, repo_num, ao_id, unit_id, extent_type, ao_title, container):
        ''''This function creates a new archival component, based on the data in the born-digtial accessioning worksheet'''
        #First, check if there is a value in the top container field. There won't always be one.
        if container != '':
            try:
                #form a new child component using data from the DAS spreadsheet
                child_component = {"publish": True, "title": ao_title, "level": "item",
                         "component_id": unit_id, "jsonmodel_type": "archival_object","linked_events": [],
                         "extents": [{"number": '1',
                                      "portion": "whole",
                                      "extent_type": extent_type,
                                      "jsonmodel_type": "extent"}],
                         "instances": [{"instance_type": 'mixed_materials',
                                        "jsonmodel_type": 'instance',
                                        "sub_container": {"jsonmodel_type": 'sub_container',
                                                          "top_container": {"ref": container}
                                                          }
                                        }
                                       ],
                        "resource": {"ref": '/repositories/'+repo_num+'+/resources/'+self.resource_id.get()},
                        "parent": {"ref": '/repositories/'+repo_num+'/archival_objects/'+ao_id}}                      
            except Exception as exc:
                logging.exception('Error: ')
                #Do I want this here or do I want to continue when something goes wrong?
                messagebox.showerror('Error!', 'Something went wrong. Please check error log.')
                return
        #if there is no value in the top container field of the DAS spreadsheet, create a child component without a top container
        else:
            child_component = {"publish": True, "title": ao_title, "level": "item",
                     "component_id": unit_id, "jsonmodel_type": "archival_object","linked_events": [],
                     "extents": [{ "number": '1', "portion": "whole", "extent_type": extent_type, "jsonmodel_type": "extent"}],
                     "resource": {"ref": '/repositories/'+repo_num+'+/resources/'+self.resource_id.get()},
                     "parent": {"ref": '/repositories/'+repo_num+'/archival_objects/'+ao_id}}
        #Post the child archival object
        child_post = requests.post(self.api_url.get()+'/repositories/'+repo_num+'/archival_objects',headers=header_value,json=child_component).json()
        return child_post
    
    #Don't use all of those arguments,but need them to make action() work - can I use ***kwargs in the action part?); or default arguments
    def update_child_component(self, header_value, repo_num, ao_id, unit_id, extent_type, ao_title=None, container=None):
        #as of right now this function leaves the ArchivesSpace title intact, but could be modified to take title from spreadsheet
        component_json = requests.get(self.api_url.get()+'/repositories/'+repo_num+'/archival_objects/'+ao_id,headers=header_value).json()
        #updates component ID
        component_json['component_id'] = unit_id
        #updates extent
        component_json['extents']= [{ "number": '1', "portion": "whole", "extent_type": extent_type, "jsonmodel_type": "extent"}]
        component_post = requests.post(self.api_url.get()+'/repositories/'+repo_num+'/archival_objects/'+ao_id,headers=header_value,json=component_json).json()
        return component_post
    
    def create_event (self, header_value, user, ao_id, repo_num, event_type, outcome_value, date_value, note_value):
        '''This function creates an event in ASpace, based on the four possible parameters provided in the born-digital accessioning worksheet'''
        # Get the event type
        event_type = event_type.lower()
        # Get the event outcome
        outcome_value = outcome_value.lower()
        # Get the event date - add a check so that if there's only 2 digits for YY make it YYYY
        if date_value != '':
            if '-' in date_value:
                date_value = date_value.replace('-', '/')
            if date_value[-4:].isdigit():
                date_value = datetime.datetime.strptime(date_value, '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                date_value = datetime.datetime.strptime(date_value, '%m/%d/%y').strftime('%Y-%m-%d')
        event = {"event_type": event_type, "jsonmodel_type": "event",
                 "outcome": outcome_value,
                 "outcome_note": note_value,
                 "linked_agents": [{ "role": "authorizer", "ref": user}],
                 "linked_records": [{ "role": "source", "ref": '/repositories/'+repo_num+'/archival_objects/'+ao_id }],
                 "date": { "begin": date_value, "date_type": "single", "label": "event", "jsonmodel_type": "date" }}    
        # Post that event
        event_post = requests.post(self.api_url.get()+'/repositories/'+repo_num+'/events',headers=header_value,json=event).json()
        #logging.debug(str(event_post))
        return event_post

    def get_top_containers(self, csv_var, repo_dictionary, header_value):
        logging.debug('Setting parent ID')
        #takes the first parent URL and sets it as the parent
        self.parent_id.set(csv_var[0][2].rpartition("_")[2])
        logging.debug(self.parent_id.get())
        #this gets a list of top containers for the parent component - assumes there will only be one parent...is this true??
        parent_component = requests.get(self.api_url.get()+'/repositories/'+repo_dictionary.get(csv_var[0][0])+'/archival_objects/'+self.parent_id.get(),headers=header_value).json()
        tc_list = [instance['sub_container']['top_container']['ref'] for instance in parent_component['instances']]        
        tuplelist = []
        for tc_uri in tc_list:
            top_container = requests.get(self.api_url.get() + tc_uri, headers=header_value).json()
            tuplelist.append((top_container['uri'], top_container['indicator']))
        return tuplelist

    def search_agent(self, user_name, headervalue):
        if user_name == '':
            cur_user = requests.get(self.api_url.get() + '/users/current-user', headers=headervalue).json()
            agent_uri = cur_user['agent_record']['ref']
            return agent_uri
        else:
            search_agent = requests.get(self.api_url.get() + '/search?page=1&type[]=agent_person&q=title:' + user_name, headers=headervalue).json()
            if search_agent['total_hits'] == 1:
                logging.debug('Search agent: result found for ' + user_name)
                agent_uri = search_agent['results'][0]['uri']
                return agent_uri
            if search_agent['total_hits'] == 0:
                logging.debug('Search agent error: no results found')
                messagebox.showerror('Error!'       'No agent authorizer found.')
                return
            if search_agent['total_hits'] > 1:
                messagebox.showerror('Error!'       'Multiple agent authorizer matches. Please refine search.')
                logging.debug('Search agent error: multiple results found')
                return

    #this function runs when either the create or update button is pushed. When the create button is pressed, the action variable takes
    #on the value of the create function, and when the update button is pressed the action variable takes the value of the update function
    def process_file(self, action):
        #Initiates the confirmation dialog
        go = self.areyousure()
        #just if go?
        if go == True:
            #captures start time
            starttime = time.time()
            headers = self.get_headers()
            if headers != None:
                repo_dict = self.repos(headers)
                csvfile = self.opencsv()
                csvlist = [row for row in csvfile]
                logging.debug('Setting user')
                current_username = csvlist[0][8]
                current_user = self.search_agent(current_username, headers)
                #takes the resource id and sets it as a StringVar       
                logging.debug('Setting resource ID')
                if '/#' in str(csvlist[0][2]):
                    self.resource_id.set(csvlist[0][2].partition('/#')[0].rpartition('/')[2])
                else:
                    self.resource_id.set(csvlist[0][2].partition('#')[0].rpartition('/')[2])
                logging.debug(self.resource_id.get())
                #see if this works - and see what happens when you set Open in ArchivesSpace URL
                if action == self.create_child_component:
                    tc_indicator_list = self.get_top_containers(csvlist, repo_dict, headers)
                if csvlist != None:
                    x = 0
                    fileobject, csvoutfile = self.outputcsv()
                    try:
                        for i, row in enumerate(csvlist, 1):
                            logging.debug('Working on row ' + str(i))
                            #check to see if current user is still the same
                            username_field = row[8]
                            #make sure this works; only resets the user when it's someone new
                            if username_field != '' and username_field != current_username:
                                logging.debug('New user search')
                                current_user = self.search_agent(username_field, headers)
                                current_username = username_field
                                logging.debug('New user results: ' + str(current_user))
                            #should be a better way to skip empty/invalid rows, but i've added this for now - CHANGE THIS!!!!
                            if row[0] in repo_dict:
                                # save the original row length - used to get event data later on
                                original_row_length = len(row)
                                # Getting data from CSV file
                                repo = repo_dict.get(row[0])
                                parent_ao_id = str(row[2]).rpartition("_")[2]
                                #if calling the update component script, will set the URL as the most recently updated record - 
                                #this is for the Open in ArchivesSpace button
                                if action == self.update_child_component:
                                    self.parent_id.set(parent_ao_id)
                                #gets the title of the ao, accounting for any HTML that might be present
                                title = cgi.escape(row[3])
                                component_id = row[4]
                                extent = row[5]       
                                top_container = row[6]
                                if top_container != '':
                                    logging.debug('Matching top_containers')
                                    for uri, indicator in tc_indicator_list:
                                        if uri != None:
                                            if indicator == top_container:
                                                top_container = uri
                                        else:
                                            #should continue with script or no??
                                            logging.debug('uri None')
                                #this runs either the create archival objects or update archival objects script, and returns the result
                                logging.debug('Calling action function')
                                updated_component = action(headers, repo, parent_ao_id, component_id, extent, title, top_container)
                                logging.debug('Finishing action function')
                                if updated_component != None:
                                    if 'uri' in updated_component: 
                                        updated_component_uri = updated_component['uri']
                                        row.append(updated_component_uri)
                                        #creating events based on the rows in the spreadsheet - CHANGE TO CSVDICT
                                        if original_row_length > 10 and row[9] != '':
                                            new_event = self.create_event(headers, current_user, updated_component_uri, repo, row[9], row[10], row[11], cgi.escape(row[12]))
                                            row.append(new_event['uri'])
                                        if original_row_length > 14 and row[15] != '':
                                            new_event = self.create_event(headers, current_user, updated_component_uri, repo, row[13], row[14], row[15], cgi.escape(row[16]))
                                            row.append(new_event['uri'])
                                        if original_row_length > 18 and row[17] != '':
                                            new_event = self.create_event(headers, current_user, updated_component_uri, repo, row[17], row[18], row[19], cgi.escape(row[20]))
                                            row.append(new_event['uri'])
                                        if original_row_length > 22 and row[21] != '':
                                            new_event = self.create_event(headers, current_user, updated_component_uri, repo, row[21], row[22], row[23], cgi.escape(row[24]))
                                            row.append(new_event['uri'])
                                        x = self.process_results(updated_component, x)
                                        csvoutfile.writerow(row)
                                    #this catches most errors related to failed posts.
                                    else:
                                        logging.debug('Error: ' + str(updated_component))
                                        csvoutfile.writerow(row)
                                elif updated_component == None:
                                    logging.debug('Component did not create/update')
                                    csvoutfile.writerow(row)
                    except:
                        logging.exception('Error: ')
                        csvoutfile.writerow(row)
                        #this will stop the script - should I have it continue instead??
                        #messagebox.showerror('Error!', 'Something went wrong! Check logs!')
                        #return
                    self.update_attempts.set(str(i))
                    self.updates_success.set(str(x))
                    self.timer(starttime)
                    #add logging here
                    logging.debug('Update attempts: ' + str(i))
                    logging.debug('Updated successfully: ' + str(x))
                    logging.debug('Elapsed time: ' + self.elapsed_time.get())
                    #change this so that it's inside the loop
                    done = self.script_finished()
                    fileobject.close()
                else:
                    return
            else:
                return
        else:
            return
    
    #connected to "create child component" button
    def run_create_script(self):
        self.process_file(self.create_child_component)
    
    #connected to "update child component" button
    def run_update_script(self):
        self.process_file(self.update_child_component)
  
  #Initiate logging - is this all I need? See logging cookbook in Python docs  
    def error_log(self):
        #make sure this works on all systems...add another temp folder for pre-Windows 10?
        if sys.platform == "win32":
            self.log_file.set('\\Windows\\Temp\\error_log.log')
        else:
            self.log_file.set('/tmp/error_log.log')
        #Basic logging config
        logging.basicConfig(filename=self.log_file.get(), level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')

    def process_results(self, jsonname, counter):
        if 'status' in jsonname:
            counter +=1
            return counter
        if 'error' in jsonname:       
            logging.debug(str(datetime.datetime.now()))
            logging.debug(str(jsonname.get('error')))

### WIDGET FILE HANDLING ###

    #File open dialog for input CSV button widget
    def csvbutton(self):
        filename = filedialog.askopenfilename(parent=self.frame)
        self.csv_filename.set(str(filename))
        return filename
    
    #opens csv output file via button widget
    def opencsvoutput(self):
        filename = self.csv_output.get()
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
    
    #opens program log via button widget - will this work if there is no log?
    def openerrorlog(self):
        #filename = self.log_file.get()
        if sys.platform == "win32":
            try:
                os.startfile('\\Windows\\Temp\\error_log.log')
            except:
                messagebox.showerror('Error!', 'Error log does not exist')
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            try:
                subprocess.call([opener, '/tmp/error_log.log'])
            except:
                messagebox.showerror('Error!', 'Error log does not exist')
    
    #Opens the parent record in ArchivesSpace staff interface via button widget
    def openparent_record(self):
        #this is where I could use the resource ID
        url_end = self.parent_id.get()
        resource = self.resource_id.get()
        get_api = self.api_url.get()
        base_url = get_api[:-3]
        #add something here to make sure there are enough/not to many forward slashes...still works but doesn't look right
        full_url = base_url + '/resources/' + resource + '#tree::archival_object_' + url_end
        if full_url[-1].isdigit() :
            try:
                webbrowser.open(full_url, new=2)
            except:
                messagebox.showerror('Error!', '\n                     Invalid URL')
        else:
            if 'https' in base_url:
                webbrowser.open(base_url, new=2)
            else:
                messagebox.showerror('Error!', '\n                     Invalid URL')
  
    #message box confirming actions, that script is about run
    def areyousure(self):
        result = messagebox.askyesno('Are you sure?', '\n      Click YES to proceed, NO to cancel')
        if result == True:
            self.script_status.set('...Updates in progress...')
            self.script_status.get()
        if result == False:
            false = messagebox.showinfo('Updates Canceled', '\n\n      Press OK to return to menu')
        return result
        
    #Show script finished message on frame
    def script_finished(self):
    #    box = messagebox.showinfo('Done!', 'Script finished. Check outfile for details')
        self.script_status.set('Updates finished!')
        self.script_status.get()
    
    #Clear all GUI inputs - start fresh
    def clear_inputs(self):
        r = messagebox.askyesno('Are you sure?', '\nClick YES to clear inputs, NO to cancel')
        if r == True:
            self.api_url.set('')
            self.username.set('')
            self.password.set('')
            self.login_confirmed.set('')
            self.csv_filename.set('')
            self.update_attempts.set('')
            self.updates_success.set('')
            self.elapsed_time.set('')
            self.script_status.set('')
            self.parent_id.set('')
        else:
            return    
        
root = Tk()
gui = BornDigitalGUI(root)
root.mainloop()