# Install Mac Dependancies
# python3 -m pip install flask
# python3 -m pip install pandas
# python3 -m pip install networkx
# python3 -m pip install plotly
# python3 -m pip install paramiko
# python3 -m pip install scp

# sudo pip3 install -r requirements.txt

#!/usr/bin/env python3

from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, render_template, flash, make_response, Markup, Response, stream_with_context
from datetime import datetime
import pandas as pd
import time, sys, json, requests, pprint, ast, ddv_c_sl_api, random, paramiko, math, difflib, ddv_c_cfg
import networkx as nx
import numpy as np
import matplotlib as plt
import plotly.graph_objects as go
import vtpy as vps
from decimal import Decimal
from scp import SCPClient
from collections import deque, OrderedDict
from ddv_c_cfg import out_list_filename, eut_list_filename, agents_list_filename, tg_v_tasks_list_filename, tg_a_tasks_list_filename # required due to globals() breaking with cfg import

plt.use('agg') # needed to allow flask to keep running while producing images
pp = pprint.PrettyPrinter(indent=5)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='development key', USERNAME='admin', PASSWORD='ddv'))

if ddv_c_cfg.vps_apikey != 'NONE':
    vps.s.headers.update({"API-Key": ddv_c_cfg.vps_apikey})
else:
    print(
        'VULTRAPI environment variable not set. Some functions will not work and return error 403.'
    )

tg_a_vectors = [
                'icmp-flood',
                'udp-flood-dst-port-80',
                'udp-flood-dst-port-53',
                'tcp-syn-flood-dst-port-80',
                'ipv4-proto-0',
                'chargen-ra-flood-dst-port-80',
                'dns-ra-flood-dst-port-80'
                ]


tg_v_protos = [
                'icmp',
                'http',
                'https',
                'dns'
                ]


@app.route('/ddv_c_settings', methods=['GET', 'POST'])
def ddv_c_settings():
    try:
        import ddv_c_cfg
        if request.method == 'GET':
            f_current = open('ddv_c_cfg.py', 'r') # read in config file
            f_old = open('ddv_c_cfg_old.py', 'w+')
            cfgDict = OrderedDict() # normal dict does not preserve order
            for line in f_current:
                f_old.write(line) # Create a backup of cfg file
                listedline = line.strip().split(' = ') # split around the = sign for Key and Value
                if len(listedline) > 1: # we have the = sign in there
                    commentline = listedline[1].strip().split(' # ') # split around the # sign for Detail (Comments)
                    cfgDict[listedline[0]] = [commentline[0], commentline[1]] # add Key, Value and Comments to Dict
            f_current.close()
            f_old.close()
        if request.method == 'POST':
            cfgDict = OrderedDict() # normal dict does not preserve order
            newDict = request.form.to_dict(flat=False) # change from ImmutableMultiDict to Dict
            #print(newDict)
            for n in range(len(newDict['Key'])): #The POST returns each Table Data Column at a time, need to join them back into Dict again
                cfgDict[newDict['Key'][n]] = [newDict['Value'][n], newDict['Description'][n]]  # add Key, Value and Comments back to Dict
            f_new = open('ddv_c_cfg_new.py', 'w') # write out new config file
            for k, v in cfgDict.items():
                f_new.write(str(k) + ' = '+ str(v[0]) + ' # ' + str(v[1]) + '\n')
            f_new.close()
            # record all config setting changes to ddv_c_cfg_changes.txt
            diff = difflib.ndiff(open('ddv_c_cfg_new.py').readlines(),open('ddv_c_cfg_old.py').readlines())
            f_changes = open('ddv_c_cfg_changes.txt', 'a+')
            f_changes.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n' + ''.join(diff))
            #print ''.join(diff),
            f_changes.close()
            try: # do error checks on the ddv_c_cfg_new file
                import ddv_c_cfg_new # check if there are syntax issues with new ddv_c_cfg_new file, before writing it out to ddv_c_cfg.py
                f_new = open('ddv_c_cfg_new.py', 'r') # read in config file
                f_current = open('ddv_c_cfg.py', 'w+')
                for line in f_new:
                    f_current.write(line)
            except:
                flash('There is a syntax error with your updates to the ddv_c_cfg file, recent changes to ddv_c_cfg has NOT been saved', 'flash_red')
                return render_template(
                                        "ddv_c_settings.html",
                                        data = {}
                                        )
        return render_template(
                                "ddv_c_settings.html",
                                data = cfgDict.items()
                                )
    except:
        flash('There is a syntax error with the ddv_c_cfg file, please remediate', 'flash_red')
        return render_template(
                                "ddv_c_settings.html",
                                data = {}
                                )



@app.route('/ddv_tg_settings', methods=['GET', 'POST'])
def ddv_tg_settings():
    try:
        my_public_ip = requests.get("https://api.ipify.org/?format=json").json()['ip']
    except:
        my_public_ip = '255.255.255.255'
    try:
        if request.method == 'GET':
            f_current = open('./ddv-tg-x/ddv_tg_cfg.py', 'r') # read in config file
            f_old = open('./ddv-tg-x/ddv_tg_cfg_old.py', 'w+')
            cfgDict = OrderedDict() # normal dict does not preserve order
            for line in f_current:
                f_old.write(line) # Create a backup of cfg file
                listedline = line.strip().split(' = ') # split around the = sign for Key and Value
                if len(listedline) > 1: # we have the = sign in there
                    commentline = listedline[1].strip().split(' # ') # split around the # sign for Detail (Comments)
                    cfgDict[listedline[0]] = [commentline[0], commentline[1]] # add Key, Value and Comments to Dict
            f_current.close()
            f_old.close()
        if request.method == 'POST':
            cfgDict = OrderedDict() # normal dict does not preserve order
            newDict = request.form.to_dict(flat=False) # change from ImmutableMultiDict to Dict
            #print(newDict)
            for n in range(len(newDict['Key'])): #The POST returns each Table Data Column at a time, need to join them back into Dict again
                cfgDict[newDict['Key'][n]] = [newDict['Value'][n], newDict['Description'][n]]  # add Key, Value and Comments back to Dict
            f_new = open('./ddv-tg-x/ddv_tg_cfg_new.py', 'w') # write out new config file
            for k, v in cfgDict.items():
                f_new.write(str(k) + ' = '+ str(v[0]) + ' # ' + str(v[1]) + '\n')
            f_new.close()
            # record all config setting changes to ddv_tg_cfg_changes.txt
            diff = difflib.ndiff(open('./ddv-tg-x/ddv_tg_cfg_new.py').readlines(),open('./ddv-tg-x/ddv_tg_cfg_old.py').readlines())
            f_changes = open('./ddv-tg-x/ddv_tg_cfg_changes.txt', 'a+')
            f_changes.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n' + ''.join(diff))
            #print ''.join(diff),
            f_changes.close()
            try: # do error checks on the ddv_tg_cfg_new file
                f_new = open('./ddv-tg-x/ddv_tg_cfg_new.py', 'r') # read in config file
                f_current = open('./ddv-tg-x/ddv_tg_cfg.py', 'w+')
                for line in f_new:
                    f_current.write(line)
            except:
                flash('There is a syntax error with your updates to the ddv_tg_cfg file, recent changes to ddv_tg_cfg has NOT been saved', 'flash_red')
                return render_template(
                                        "ddv_tg_settings.html",
                                        data = {}
                                        )
        return render_template(
                                "ddv_tg_settings.html",
                                data = cfgDict.items(),
                                my_public_ip = my_public_ip
                                )
    except:
        flash('There is a syntax error with the ddv_tg_cfg file, please remediate', 'flash_red')
        return render_template(
                                "ddv_tg_settings.html",
                                data = {}
                                )


def get_out():
    try:
        out_list_df = pd.read_csv(ddv_c_cfg.out_list_filename, names=[
                                                                'out_enrollment_id',
                                                                'out_companyname',
                                                                'out_contactname',
                                                                'out_contactemail',
                                                                'out_contactnumber',
                                                                'out_industry',
                                                                'out_sl_ip',
                                                                'out_sl_api',
                                                                'out_enrollment_date'
                                                                ], dtype={'out_contactnumber': str}, header=None)
        out_list_df.set_index('out_enrollment_id', inplace=True)
        return out_list_df
    except:
        out_list_df = pd.DataFrame([['empty']], index=['error'], columns=['out_companyname'])
        return out_list_df
        

def get_eut():
    try:
        eut_list_df = pd.read_csv(ddv_c_cfg.eut_list_filename, names=[
                                                                'eut_enrollment_id',
                                                                'eut_shortname',
                                                                'eut_dst_ip',
                                                                'eut_companyname',
                                                                'eut_companyname_id',
                                                                'eut_enrollment_date'
                                                                ], dtype={'eut_companyname_id': str}, header=None)
        eut_list_df.set_index('eut_enrollment_id', inplace=True)
        return eut_list_df
    except:
        eut_list_df = pd.DataFrame([['empty']], index=['error'], columns=['eut_shortname'])
        return eut_list_df

def get_agents():
    try:
        agent_list_df = pd.read_csv(ddv_c_cfg.agents_list_filename, names=[
                                                                'agent_enrollment_id',
                                                                'agent_hostname',
                                                                'agent_ip',
                                                                'agent_port',
                                                                'agent_location',
                                                                'agent_description',
                                                                'agent_role',
                                                                'agent_local_api_key',
                                                                'agent_remote_api_key',
                                                                'agent_enrollment_date'
                                                                ], dtype={'agent_local_api_key': str,'agent_remote_api_key': str}, header=None)
        agent_list_df.set_index('agent_enrollment_id', inplace=True)
        return agent_list_df
    except:
        agent_list_df = pd.DataFrame([['empty']], index=['error'], columns=['agent_role'])
        return agent_list_df

def get_tg_v_tasks():
    try:
        tg_v_list_df = pd.read_csv(ddv_c_cfg.tg_v_tasks_list_filename, names=[
                                                                'tg_v_enrollment_id',
                                                                'tg_v_eut',
                                                                'tg_v_eut_id',
                                                                'tg_v_host',
                                                                'tg_v_host_id',
                                                                'tg_v_src_ip',
                                                                'tg_v_dst_ip',
                                                                'tg_v_dst_proto',
                                                                'tg_v_pps',
                                                                'tg_v_dur',
                                                                'tg_v_p_cnt',
                                                                'tg_v_p_int',
                                                                'tg_v_description',
                                                                'tg_v_enrollment_date',
                                                                'tg_v_status'
                                                                ], dtype={'tg_v_host_id': str,'tg_v_p_cnt': str}, header=None)
        tg_v_list_df.set_index('tg_v_enrollment_id', inplace=True)
        return tg_v_list_df
    except:
        tg_v_list_df = pd.DataFrame([['empty']], index=['error'], columns=['error'])
        return tg_v_list_df
        

def get_tg_a_tasks():
    try:
        tg_a_list_df = pd.read_csv(ddv_c_cfg.tg_a_tasks_list_filename, names=[
                                                                'tg_a_enrollment_id',
                                                                'tg_a_eut',
                                                                'tg_a_eut_id',
                                                                'tg_a_host',
                                                                'tg_a_host_id',
                                                                'tg_a_src_ip',
                                                                'tg_a_dst_ip',
                                                                'tg_a_dst_vector',
                                                                'tg_a_pps',
                                                                'tg_a_dur',
                                                                'tg_a_p_cnt',
                                                                'tg_a_p_int',
                                                                'tg_a_description',
                                                                'tg_a_enrollment_date',
                                                                'tg_a_status'
                                                                ], dtype={'tg_a_host_id': str,'tg_a_p_cnt': str}, header=None)
        tg_a_list_df.set_index('tg_a_enrollment_id', inplace=True)
        return tg_a_list_df
    except:
        tg_a_list_df = pd.DataFrame([['empty']], index=['error'], columns=['error'])
        return tg_a_list_df
        
        
        
def get_alert_mit_details():
    try:
        amd_list_df = pd.read_csv(ddv_c_sl_api.sl_ddv_mo_alert_list_filename, names=[
                                                                                    'alert_gid',
                                                                                    'mo_gid',
                                                                                    'mo_name',
                                                                                    'alert_class',
                                                                                    'alert_type',
                                                                                    'alert_importance',
                                                                                    'alert_ongoing',
                                                                                    'start_time',
                                                                                    'host_address',
                                                                                    'impact_bps',
                                                                                    'impact_pps',
                                                                                    'misuse_types',
                                                                                    'mitigation_data',
                                                                                    'source_prefixes'
                                                                ], header=None)
        amd_list_df.set_index('alert_gid', inplace=True)
        return amd_list_df
    except:
        amd_list_df = pd.DataFrame([['empty']], index=['error'], columns=['out_companyname'])
        return amd_list_df
        

        
def edit_df(ddv_df, row_indexer, col_indexer, new_value):
    # ddv_df can be out, eut, agents, tg_v_tasks, tg_a_tasks
    df = globals()['get_' + ddv_df]() # construct the function to run from var input, and get df
    df.loc[row_indexer, col_indexer] = new_value # change value in df
    df.to_csv(globals()[ddv_df + '_list_filename'], mode='w', header=False) # overwrite new df to old csv


        
@app.route('/', methods=['GET'])
def ddv_landing_page():
    return render_template('index.html')


@app.route('/alert_lookup/<mo_gid>', methods=['GET'])
def alert_lookup(mo_gid):
    ddv_c_sl_api.sl_dos_alert_search(mo_gid)


@app.route('/agents_status', methods=['GET'])
def agents_status():
    try:
        agent_list_df = get_agents()
        agents_status = []
        for uuid in agent_list_df.index:
            agent_enrollment_id = uuid
            agent_hostname = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_hostname'].values[0])
            agent_ip = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_ip'].values[0])
            agent_port = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_port'].values[0])
            agent_location = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_location'].values[0])
            agent_description = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_description'].values[0])
            agent_role = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_role'].values[0])
            agent_enrollment_date = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_enrollment_date'].values[0])
            url = 'https://' + str(agent_ip) + ':' + str(agent_port)+ '/ddv_tg_x_keepalive'
            #print url
            try:
                task_resp = requests.get(url, verify=False, timeout=ddv_c_cfg.agent_timeout)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('action') == 'success':
                        agent_health_response = task_resp.json().get('health')
                        agent_tasks_response = task_resp.json().get('tasks')
                        try:
                            if agent_tasks_response[0]['index'] == 'error':
                                agent_tasks_response = []
                            else:
                                pass
                        except:
                            pass
                        session['remote_agent_alive'] = True
                        #flash('DDV-C: ' + str(agent_hostname) + ': ' + str(task_resp.json().get('health')), 'flash_green') # success message from remote agent
                    else:
                        pass
                else:
                    agent_health_response = 'offline'
                    agent_tasks_response = []
            except:
                flash('DDV-C: There was a problem connecting to the Remote Agent: ' + str(agent_hostname), 'flash_red')
                session['remote_agent_alive'] = False
                agent_health_response = 'offline'
                agent_tasks_response = []
            agents_status_entry = {
                            #'agent_enrollment_id': agent_enrollment_id,
                            'agent_hostname': agent_hostname,
                            'agent_ip': agent_ip,
                            'agent_port': agent_port,
                            'agent_location': agent_location,
                            'agent_description': agent_description,
                            'agent_role': agent_role,
                            'agent_enrollment_date': agent_enrollment_date,
                            'agent_health': str(agent_health_response) + ' (' + str(len(agent_tasks_response)) + ' tasks)',
                            'edit': agent_enrollment_id,
                            'delete': agent_enrollment_id,
                            'push': agent_enrollment_id
                           }
            agents_status.append(agents_status_entry)
        #print agents_status
        agents_status_df = pd.DataFrame.from_dict(agents_status)
        # Reorder columns back to original ordering
        agents_status_df = agents_status_df[[
                                            #'agent_enrollment_id',
                                            'agent_hostname',
                                            'agent_ip',
                                            'agent_port',
                                            'agent_location',
                                            'agent_description',
                                            'agent_role',
                                            'agent_enrollment_date',
                                            'agent_health',
                                            'edit',
                                            'delete',
                                            'push'
                                            ]]
        return render_template(
                                "list_agents_status.html",
                                column_names=agents_status_df.columns.values,
                                row_data=list(agents_status_df.values.tolist()),
                                edit_link_column="edit",
                                delete_link_column="delete",
                                push_link_column="push",
                                zip=zip
                                )
    except:
        flash('No DDV-TG-x Agents Configured as yet.  Please Configure Agents...', 'flash_red')
        return redirect(url_for('enroll_agents'))

@app.route('/agent_lookup/<uuid>', methods=['GET'])
def agent_lookup(uuid):
    try:
        agent_list_df = get_agents()
        agent_enrollment_id = uuid
        agent_hostname = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_hostname'].values[0])
        agent_ip = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_ip'].values[0])
        agent_port = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_port'].values[0])
        agent_location = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_location'].values[0])
        agent_description = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_description'].values[0])
        agent_role = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_role'].values[0])
        agent_enrollment_date = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_enrollment_date'].values[0])
        return {
                        'agent_enrollment_id': agent_enrollment_id,
                        'agent_hostname': agent_hostname,
                        'agent_ip': agent_ip,
                        'agent_port': agent_port,
                        'agent_location': agent_location,
                        'agent_description': agent_description,
                        'agent_role': agent_role,
                        'agent_enrollment_date': agent_enrollment_date
                }
    except:
        return {
                        'error': 'invalid uuid',
                        'agent_enrollment_id': 0
                }

@app.route('/remote_agent_enroll_push', methods=['GET', 'POST'])
def remote_agent_enroll_push():
    agent_list_df = get_agents()
    error = None
    try:
        agent_names = agent_list_df.agent_hostname
    except:
        return redirect(url_for('enroll_agents'))
    if request.method == 'POST':
        uuid = agent_list_df[agent_list_df['agent_hostname'] == request.form['agent_hostname']].index.values[0]
    if request.method == 'GET':
        try: #Landing directly in push page, with GET, results in no uuid, hence needs exception
            uuid = int(request.args.get('push_agent_uuid'))
        except:
            pass
    try:
        agent_enrollment_id = uuid
        agent_hostname = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_hostname'].values[0])
        agent_ip = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_ip'].values[0])
        agent_port = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_port'].values[0])
        agent_location = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_location'].values[0])
        agent_description = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_description'].values[0])
        agent_role = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_role'].values[0])
        agent_local_api_key = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_local_api_key'].values[0])
        agent_remote_api_key = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_remote_api_key'].values[0])
        agent_enrollment_date = str(agent_list_df[agent_list_df.index == int(uuid)]['agent_enrollment_date'].values[0])
        enroll_data =   {
                        'agent_enrollment_id': agent_enrollment_id,
                        'agent_hostname': agent_hostname,
                        'agent_ip': agent_ip,
                        'agent_port': agent_port,
                        'agent_location': agent_location,
                        'agent_description': agent_description,
                        'agent_role': agent_role,
                        'agent_local_api_key': agent_local_api_key,
                        'agent_remote_api_key': agent_remote_api_key,
                        'agent_enrollment_date': agent_enrollment_date
                        }
        enroll_agent_entry(enroll_data)
    except:
        pass
    agent_list_df = get_agents()
    agent_names = agent_list_df.agent_hostname
    return render_template('remote_agent_enroll_push.html', error=error, agent_names=agent_names, data=agent_list_df.to_html())

@app.route('/remote_tg_v_task_push', methods=['GET', 'POST'])
def remote_tg_v_task_push():
    tg_v_tasks_entries = get_tg_v_tasks()
    tg_v_names = tg_v_tasks_entries.reset_index().to_dict('records') # pass whole dataframe as 'list of dicts' to render template select list
    agent_entries = get_agents()
    error = None
    if request.method == 'POST':
        try:
            uuid = int(request.form['tg_v_enrollment_id'])
        except:
            return redirect(url_for('enroll_tg_v_tasks'))
    if request.method == 'GET':
        try: #Landing directly in push page, with GET, results in no uuid, hence needs exception
            uuid = int(request.args.get('push_tg_v_task_uuid'))
        except:
            pass
    try:
        tg_v_enrollment_id = uuid
        tg_v_eut = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_eut'].values[0])
        tg_v_eut_id = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_eut_id'].values[0])
        tg_v_host = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_host'].values[0])
        tg_v_host_id = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_host_id'].values[0])
        tg_v_host_ip = str(agent_entries[agent_entries.index == int(tg_v_host_id)]['agent_ip'].values[0])
        tg_v_host_port = str(agent_entries[agent_entries.index == int(tg_v_host_id)]['agent_port'].values[0])
        tg_v_src_ip = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_src_ip'].values[0])
        tg_v_dst_ip = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_dst_ip'].values[0])
        tg_v_dst_proto = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_dst_proto'].values[0])
        tg_v_pps = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_pps'].values[0])
        tg_v_dur = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_dur'].values[0])
        tg_v_p_cnt = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_p_cnt'].values[0])
        tg_v_p_int = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_p_int'].values[0])
        tg_v_description = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_description'].values[0])
        tg_v_enrollment_date = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_enrollment_date'].values[0])
        tg_v_status = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_status'].values[0])
        task_data =   {
                        'tg_v_enrollment_id': tg_v_enrollment_id,
                        'tg_v_eut': tg_v_eut,
                        'tg_v_eut_id': tg_v_eut_id,
                        'tg_v_host': tg_v_host,
                        'tg_v_host_id': tg_v_host_id,
                        'tg_v_host_ip': tg_v_host_ip,
                        'tg_v_src_ip': tg_v_src_ip,
                        'tg_v_dst_ip': tg_v_dst_ip,
                        'tg_v_dst_proto': tg_v_dst_proto,
                        'tg_v_pps': tg_v_pps,
                        'tg_v_dur': tg_v_dur,
                        'tg_v_p_cnt': tg_v_p_cnt,
                        'tg_v_p_int': tg_v_p_int,
                        'tg_v_description': tg_v_description,
                        'tg_v_enrollment_date': tg_v_enrollment_date,
                        'tg_v_status': tg_v_status
                        }
        #task_data = json.dumps(task_data)
        #header = {
        #    "X-DDV-APIToken":tg_v_local_api_key,
        #    "Content-Type": "application/json"
        #}
        #print task_data
        url = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port)+ '/remote_tg_v_task_push/' + str(tg_v_enrollment_id)
        #print url
        try:
            task_resp = requests.post(url, verify=False, json=task_data)
            if task_resp.ok:
                #return task_resp.json()
                #print task_resp.json()
                if task_resp.json().get('enrollment') == 'failed':
                    flash(task_resp.json().get('error'), 'flash_red')
                    session['remote_task_enrolled'] = False
                elif task_resp.json().get('enrollment') == 'success':
                    session['remote_task_enrolled'] = True
                    flash(task_resp.json().get('message'), 'flash_green')
                else:
                    pass
            else:
                pass
        except:
            flash('DDV-C: There was a problem connecting to the Remote Agent', 'flash_red')
        tg_v_tasks_entries = get_tg_v_tasks()
        tg_v_names = tg_v_tasks_entries.reset_index().to_dict('records')
    except:
        pass
    return render_template('remote_tg_v_task_push.html',
                            error=error,
                            tg_v_names=tg_v_names,
                            data=tg_v_tasks_entries.to_html())


@app.route('/remote_tg_a_task_push', methods=['GET', 'POST'])
def remote_tg_a_task_push():
    tg_a_tasks_entries = get_tg_a_tasks()
    tg_a_names = tg_a_tasks_entries.reset_index().to_dict('records') # pass whole dataframe as 'list of dicts' to render template select list
    agent_entries = get_agents()
    error = None
    if request.method == 'POST':
        try:
            uuid = int(request.form['tg_a_enrollment_id'])
        except:
            return redirect(url_for('enroll_tg_a_tasks'))
    if request.method == 'GET':
        try: #Landing directly in push page, with GET, results in no uuid, hence needs exception
            uuid = int(request.args.get('push_tg_a_task_uuid'))
        except:
            pass
    try:
        tg_a_enrollment_id = uuid
        tg_a_eut = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_eut'].values[0])
        tg_a_eut_id = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_eut_id'].values[0])
        tg_a_host = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_host'].values[0])
        tg_a_host_id = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_host_id'].values[0])
        try:
            tg_a_host_ip = str(agent_entries[agent_entries.index == int(tg_a_host_id)]['agent_ip'].values[0])
            tg_a_host_port = str(agent_entries[agent_entries.index == int(tg_a_host_id)]['agent_port'].values[0])
        except:
            error = 'DDV-C: Remote Agent, ' + str(tg_a_host) + ', no longer exists'
            return render_template('remote_tg_a_task_push.html',
                        error=error,
                        tg_a_names=tg_a_names,
                        data=tg_a_tasks_entries.to_html())
        tg_a_src_ip = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_src_ip'].values[0])
        tg_a_dst_ip = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_dst_ip'].values[0])
        tg_a_dst_vector = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_dst_vector'].values[0])
        tg_a_pps = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_pps'].values[0])
        tg_a_dur = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_dur'].values[0])
        tg_a_p_cnt = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_p_cnt'].values[0])
        tg_a_p_int = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_p_int'].values[0])
        tg_a_description = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_description'].values[0])
        tg_a_enrollment_date = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_enrollment_date'].values[0])
        tg_a_status = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_status'].values[0])
        task_data =   {
                        'tg_a_enrollment_id': tg_a_enrollment_id,
                        'tg_a_eut': tg_a_eut,
                        'tg_a_eut_id': tg_a_eut_id,
                        'tg_a_host': tg_a_host,
                        'tg_a_host_id': tg_a_host_id,
                        'tg_a_host_ip': tg_a_host_ip,
                        'tg_a_src_ip': tg_a_src_ip,
                        'tg_a_dst_ip': tg_a_dst_ip,
                        'tg_a_dst_vector': tg_a_dst_vector,
                        'tg_a_pps': tg_a_pps,
                        'tg_a_dur': tg_a_dur,
                        'tg_a_p_cnt': tg_a_p_cnt,
                        'tg_a_p_int': tg_a_p_int,
                        'tg_a_description': tg_a_description,
                        'tg_a_enrollment_date': tg_a_enrollment_date,
                        'tg_a_status': tg_a_status
                        }
        #task_data = json.dumps(task_data)
        #header = {
        #    "X-DDV-APIToken":tg_a_local_api_key,
        #    "Content-Type": "application/json"
        #}
        #print task_data
        url = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port)+ '/remote_tg_a_task_push/' + str(tg_a_enrollment_id)
        #print url
        try:
            task_resp = requests.post(url, verify=False, json=task_data)
            if task_resp.ok:
                #return task_resp.json()
                #print task_resp.json()
                if task_resp.json().get('enrollment') == 'failed':
                    flash(task_resp.json().get('error'), 'flash_red')
                    session['remote_task_enrolled'] = False
                elif task_resp.json().get('enrollment') == 'success':
                    session['remote_task_enrolled'] = True
                    flash(task_resp.json().get('message'), 'flash_green')
                else:
                    pass
            else:
                pass
        except:
            flash('DDV-C: There was a problem connecting to the Remote Agent, ' + str(tg_a_host), 'flash_red')
        tg_a_tasks_entries = get_tg_a_tasks()
        tg_a_names = tg_a_tasks_entries.reset_index().to_dict('records')
    except:
        pass
    return render_template('remote_tg_a_task_push.html',
                            error=error,
                            tg_a_names=tg_a_names,
                            data=tg_a_tasks_entries.to_html())


@app.route('/device_keepalive', methods=['POST'])
def device_keepalive():
    try:
        content = request.json
        ka_uuid = content['unique_id']
        ka_enroll_id = content['enroll_id']
        device_list_df = pd.read_csv(device_list_filename, names=['enroll_id', 'uuid', 'device_info', 'first_seen', 'last_seen'], header=None)
        device_list_df.set_index('enroll_id', inplace=True)
        device_list_df.ix[device_list_df[device_list_df['uuid'] == ka_uuid].index[0], 'last_seen'] = datetime.now()
        #print device_list_df
        device_list_df.to_csv(device_list_filename, mode='w', header=False, columns=['uuid', 'device_info', 'first_seen', 'last_seen'])
        return jsonify(
                       {'ka_enroll_id': ka_enroll_id,
                       'ka_uuid': ka_uuid
                       }
                       )
    except:
        return 0


@app.route('/stream_content')
def stream_content():
    def file_reader(filename):
        previous_file = 0
        while True:
            try:
                time.sleep(1)
                current_file = len(open(filename).readlines(  ))
                #print(previous_file, current_file, (int(current_file) - int(previous_file)))
                for entry in deque(open(filename), (int(current_file) - int(previous_file))):
                    yield str(entry) + '<br/>\n'
                previous_file = current_file
            except:
                pass
    return Response(stream_with_context(file_reader('scroller_log')), mimetype='text/html')

@app.route('/stream')
def stream():
    return render_template('scroller.html')

def stream_logger(line):
    f = open('scroller_log', 'a+')
    f.write(line + '\n')
    f.close()
    
def stream_logger_clear():
    f = open('scroller_log', 'w+')
    f.close()
    

@app.route('/stream_test')
def stream_test():
    f = open('scroller_log', 'w+')
    f.close()
    for i in range(10):
        j = math.sqrt(i)
        time.sleep(1)
        # this value should be inserted into file
        stream_logger(str(i))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in', 'flash_blue')
            return redirect(url_for('out_status'))
    return render_template('login.html', error=error)


@app.route('/manage_vps_agents', methods=['GET', 'POST'])
def manage_vps_agents():
    error = None
    try:
        vps_servers = dict(vps.serverlist())
    except:
        error = 'DDV-C: VPS API or Connection not configured'
        vps_servers = {}
    if request.method == 'POST':
        try:
            if int(request.form['vps_qty']) > 0:
                #print(request.form['vps_qty'])
                new_vps_list = vps_tg_x_provision(int(request.form['vps_qty']))
                vps_tg_x_configure(new_vps_list)
                vps_servers = dict(vps.serverlist()) # get fresh list of servers after provisioning
        except:
            pass
        try:
            if request.form['vps_destroy'] == 'Yes':
                #print(request.form['vps_destroy'])
                vps_tg_x_kill_all()
                vps_servers = dict(vps.serverlist()) # get fresh list of servers after deletion
            else:
                #print(request.form['vps_destroy'])
                pass
        except:
            pass
    if request.method == 'GET':
        try:
            vps_servers = dict(vps.serverlist())
        except:
            error = 'DDV-C: VULTR VPS API not configured correctly.  Generate API Key from www.vultr.com'
    return render_template('manage_vps_agents.html', error=error, data=vps_servers.values())

@app.route('/list_agents', methods=['GET'])
def list_agents():
        agent_entries = get_agents()
        return render_template('list_agents.html', data=agent_entries.to_html())
#        return render_template('list_agents.html', tables=[agent_entries.to_html(classes='agents')],
#                               titles = ['Configured Agents'])
                               
                               
@app.route('/enroll_agents', methods=['GET', 'POST'])
def enroll_agents():
    port_role_map = { 'V' : ddv_c_cfg.ddv_tg_v_port, 'A' : ddv_c_cfg.ddv_tg_a_port}
    agent_entries = get_agents()
    error = None
    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
            agent_list_entry = {
                                'agent_enrollment_id': int(time.time()),
                                'agent_hostname': request.form['agent_hostname'],
                                'agent_ip': request.form['agent_ip'],
                                'agent_port': port_role_map[request.form['agent_role']],
                                'agent_location': request.form['agent_location'],
                                'agent_description': request.form['agent_description'],
                                'agent_role': request.form['agent_role'],
                                'agent_local_api_key': request.form['agent_local_api_key'],
                                'agent_remote_api_key': request.form['agent_remote_api_key'],
                                'agent_enrollment_date': str(datetime.now())
                                }
            #print agent_list_entry
            enroll_agent_entry(agent_list_entry)
            agent_entries = get_agents()
    return render_template('enroll_agents.html', error=error, data=agent_entries.to_html())


def enroll_vps_agents(vps_list):
    port_role_map = { 'V' : ddv_c_cfg.ddv_tg_v_port, 'A' : ddv_c_cfg.ddv_tg_a_port}
    for vps_server in vps_list:
        agent_list_entry_a = {
                            'agent_enrollment_id': '99' + str(vps_server['SUBID']) + '99',  # if int(uuid) starts and ends with 99, it's an A
                            'agent_hostname': str('VPS-' + str(vps_server['location']) + '-' + str(vps_server['SUBID']) + '-A'),
                            'agent_ip': str(vps_server['main_ip']),
                            'agent_port': port_role_map['A'],
                            'agent_location': str(vps_server['location']),
                            'agent_description': str(vps_server['tag']),
                            'agent_role': 'A',
                            'agent_local_api_key': '',
                            'agent_remote_api_key': '',
                            'agent_enrollment_date': str(datetime.now())
                            }
        agent_list_entry_v = {
                            'agent_enrollment_id': '88' + str(vps_server['SUBID']) + '88',  # if int(uuid) starts and ends with 88, it's a V
                            'agent_hostname': str('VPS-' + str(vps_server['location']) + '-' + str(vps_server['SUBID']) + '-V'),
                            'agent_ip': str(vps_server['main_ip']),
                            'agent_port': port_role_map['V'],
                            'agent_location': str(vps_server['location']),
                            'agent_description': str(vps_server['tag']),
                            'agent_role': 'V',
                            'agent_local_api_key': '',
                            'agent_remote_api_key': '',
                            'agent_enrollment_date': str(datetime.now())
                            }
        # Add new VPS server as Attacker Role
        enroll_agent_entry(agent_list_entry_a)
        # Add new VPS server as Verifier Role
        enroll_agent_entry(agent_list_entry_v)


def enroll_agent_entry(agent_list_entry):
    agent_list = []
    agent_list.append(agent_list_entry)
    agent_list_df = pd.DataFrame.from_dict(agent_list)
    agent_list_df.set_index('agent_enrollment_id', inplace=True)
    #print agent_lookup(agent_list_entry['agent_enrollment_id'])
    try: # if the entry exists already, don't append a new entry (which will result in duplicates)
        if int(agent_lookup(agent_list_entry['agent_enrollment_id'])['agent_enrollment_id']) == 0:
            agent_list_df.to_csv(ddv_c_cfg.agents_list_filename, mode='a', header=False, columns=[
                                                                                #'agent_enrollment_id',
                                                                                'agent_hostname',
                                                                                'agent_ip',
                                                                                'agent_port',
                                                                                'agent_location',
                                                                                'agent_description',
                                                                                'agent_role',
                                                                                'agent_local_api_key',
                                                                                'agent_remote_api_key',
                                                                                'agent_enrollment_date'
                                                                                ])
        else:
            pass
    except:
        pass
    session['new_agent_enrolled'] = True
    flash('DDV-C: New Agent Enrolled', 'flash_green')
    # Once new Agent is Enrolled, try and enroll remote agent
    header = {
        "X-DDV-APIToken": agent_list_df['agent_local_api_key'],
        "Content-Type": "application/json"
    }
    # Connect to Remote Agent and Configure it
    url = 'https://' + str(agent_list_entry['agent_ip']) + ':' + str(agent_list_entry['agent_port'])+ '/remote_agent_enroll/' + str(agent_list_entry['agent_enrollment_id'])
    #print url
    try:
        enroll_resp = requests.post(url, verify=False, json=agent_list_entry, timeout=ddv_c_cfg.agent_timeout)
        if enroll_resp.ok:
            #return enroll_resp.json()
            #print enroll_resp.json()
            if enroll_resp.json().get('enrollment') == 'failed':
                flash(enroll_resp.json().get('error'), 'flash_red')
                session['remote_agent_enrolled'] = False
            elif enroll_resp.json().get('enrollment') == 'success':
                session['remote_agent_enrolled'] = True
                flash('DDV-C: ' + str(enroll_resp.json().get('agent_hostname')) + ' successfully enrolled', 'flash_green')
            else:
                pass
        else:
            pass
    except:
        flash('DDV-C: Connection to Remote Agent Timed-Out', 'flash_red')

def delete_vps_agents(vps_uuids):
    for vps_id in vps_uuids:
        # Delete both the Attacker and Verifier roles in one go
        try:
            agent_entries = get_agents()
            del_agent_ip = agent_entries[agent_entries.index == vps_id]['agent_ip'].values[0]
            del_agent_port = agent_entries[agent_entries.index == vps_id]['agent_port'].values[0]
            delete_agent_entry(agent_entries, vps_id, del_agent_ip, del_agent_port)
        except:
            pass


@app.route('/delete_agents', methods=['GET', 'POST'])
def delete_agents():
    error = None
    agent_entries = get_agents()
    try:
        agent_names = agent_entries.agent_hostname
    except:
        return redirect(url_for('enroll_agents'))
    if request.method == 'GET':
        try:
            uuid = int(request.args.get('delete_agent_uuid')) # https://127.0.0.1:2020/delete_agents?delete_agent_uuid=1594133309
            if (int(str(uuid)[:2]) and int(str(uuid)[-2:]) == 99 or int(str(uuid)[:2]) and int(str(uuid)[-2:]) == 88): #VPS Specific tasks
                vps_subid = int(str(uuid)[2:][:-2]) # find id between the 99 or 88 identifiers
                vps_uuids = [int('99' + str(vps_subid) + '99'), int('88' + str(vps_subid) + '88')]
                delete_vps_agents(vps_uuids)
                # Destroy VPS next
                vps.kill([str(vps_subid)])
                flash('DDV-C: VPS server, ' + str(vps_subid) + ' destroyed', 'flash_green')
                agent_entries = get_agents()
                agent_names = agent_entries.agent_hostname
            else:
                del_agent_ip = agent_entries[agent_entries.index == uuid]['agent_ip'].values[0]
                del_agent_port = agent_entries[agent_entries.index == uuid]['agent_port'].values[0]
                delete_agent_entry(agent_entries, uuid, del_agent_ip, del_agent_port)
                agent_entries = get_agents()
                agent_names = agent_entries.agent_hostname
            return render_template('delete_agents.html', error=error, agent_names=agent_names, data=agent_entries.to_html())
        except:
            pass
    if request.method == 'POST':
        uuid = agent_entries[agent_entries['agent_hostname'] == request.form['agent_hostname']].index.values[0]
        if (int(str(uuid)[:2]) and int(str(uuid)[-2:]) == 99 or int(str(uuid)[:2]) and int(str(uuid)[-2:]) == 88): #VPS Specific tasks
            vps_subid = int(str(uuid)[2:][:-2]) # find id between the 99 or 88 identifiers
            vps_uuids = [int('99' + str(vps_subid) + '99'), int('88' + str(vps_subid) + '88')]
            delete_vps_agents(vps_uuids)
            # Destroy VPS next
            vps.kill([str(vps_subid)])
            flash('DDV-C: VPS server, ' + str(vps_subid) + ' destroyed', 'flash_green')
            agent_entries = get_agents()
            agent_names = agent_entries.agent_hostname
        else:
            del_agent_ip = agent_entries[agent_entries.index == uuid]['agent_ip'].values[0]
            del_agent_port = agent_entries[agent_entries.index == uuid]['agent_port'].values[0]
            delete_agent_entry(agent_entries, uuid, del_agent_ip, del_agent_port)
            agent_entries = get_agents()
            agent_names = agent_entries.agent_hostname
    return render_template('delete_agents.html', error=error, agent_names=agent_names, data=agent_entries.to_html())
    
def delete_agent_entry(agent_entries, uuid, del_agent_ip, del_agent_port):
    # 1. Before removing the agent, find and delete all associated agent tasks
    # 1a. Find and delete all Attack Tasks
    tg_a_task_entries = get_tg_a_tasks()
    for task_entry in tg_a_task_entries[tg_a_task_entries['tg_a_host_id'] == str(uuid)].index.values:
        try:
            tg_a_task_entries = get_tg_a_tasks() # get fresh task list after each recursive deletion of task
            if delete_tg_a_task_entry(task_entry) == 'success':
                pass
            else:
                pass
                #flash('DDV-C: ' + str(uuid) + ' task could not be deleted', 'flash_red')
        except:
            flash('DDV-C: No more tasks to be deleted', 'flash_red')
    # 1b. Find and delete all Verifier Tasks
    tg_v_task_entries = get_tg_v_tasks()
    for task_entry in tg_v_task_entries[tg_v_task_entries['tg_v_host_id'] == str(uuid)].index.values:
        try:
            tg_v_task_entries = get_tg_v_tasks() # get fresh task list after each recursive deletion of task
            if delete_tg_v_task_entry(task_entry) == 'success':
                pass
            else:
                pass
                #flash('DDV-C: ' + str(uuid) + ' task could not be deleted', 'flash_red')
        except:
            flash('DDV-C: No more tasks to be deleted', 'flash_red')
    # 2. Delete agent after deleting all associated tasks
    agent_entries.drop(index=int(uuid)).to_csv(ddv_c_cfg.agents_list_filename, mode='w', header=False, columns=[
                                                                                          #'agent_enrollment_id',
                                                                                          'agent_hostname',
                                                                                          'agent_ip',
                                                                                          'agent_port',
                                                                                          'agent_location',
                                                                                          'agent_description',
                                                                                          'agent_role',
                                                                                          'agent_local_api_key',
                                                                                          'agent_remote_api_key',
                                                                                          'agent_enrollment_date'
                                                                                          ])
    session['agent_deleted'] = True
    flash('DDV-C: Remote Agent deleted', 'flash_green')
    # Wipe all data from remote agent
    url = 'https://' + str(del_agent_ip) + ':' + str(del_agent_port)+ '/ddv_tg_x_config_flush'
    #print url
    try:
        task_resp = requests.get(url, verify=False, timeout=ddv_c_cfg.agent_timeout)
        if task_resp.ok:
            #return task_resp.json()
            #print task_resp.json()
            if task_resp.json().get('action') == 'failed':
                flash(task_resp.json().get('message'), 'flash_red')
                session['remote_agent_deleted'] = False
            elif task_resp.json().get('action') == 'success':
                session['remote_agent_deleted'] = True
                flash('DDV-C: Remote Agent ' + str(task_resp.json().get('message')), 'flash_green') # success message from remote agent
            else:
                pass
    except:
        flash('DDV-C: There was a problem connecting to the Remote Agent', 'flash_red')

    
@app.route('/edit_agents', methods=['GET', 'POST'])
def edit_agents():
    port_role_map = { 'V' : ddv_c_cfg.ddv_tg_v_port, 'A' : ddv_c_cfg.ddv_tg_a_port}
    error = None
    if request.method == 'GET':
        uuid = int(request.args.get('edit_agent_uuid')) # https://127.0.0.1:2020/edit_agents?agent_uuid=1600095410
        #print uuid
        agent_entries = get_agents()
        #agent_entry = agent_entries[agent_entries.index == uuid]
        agent_entry = agent_entries[agent_entries.index == uuid].reset_index().to_dict('records')
        return render_template('edit_agents.html', error=error, data=agent_entries.to_html(), agent=agent_entry)
    if request.method == 'POST':
        # 1. get desired edits from form POST
        data = {
                'agent_hostname': request.form['agent_hostname'],
                'agent_ip': request.form['agent_ip'],
                'agent_port': port_role_map[request.form['agent_role']],
                'agent_location': request.form['agent_location'],
                'agent_description': request.form['agent_description'],
                'agent_role': request.form['agent_role'],
                'agent_local_api_key': request.form['agent_local_api_key'],
                'agent_remote_api_key': request.form['agent_remote_api_key']
                }
        # 2. update df with new data
        for key in data:
            edit_df('agents', int(request.form['agent_enrollment_id']), key, data[key])
        return redirect(url_for('agents_status'))



@app.route('/enroll_tg_v_tasks', methods=['GET', 'POST'])
def enroll_tg_v_tasks():
    error = None
    tg_v_tasks_entries = get_tg_v_tasks()
    eut_entries = get_eut()
    #eut_names = eut_entries.eut_shortname
    eut_names = eut_entries.reset_index().to_dict('records')
    agent_entries = get_agents()
    #tg_v_hosts = agent_entries[agent_entries.agent_role == 'V'].agent_hostname
    tg_v_hosts = agent_entries[agent_entries.agent_role == 'V'].reset_index().to_dict('records')
    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
            tg_v_list_entry = {
                                'tg_v_enrollment_id': int(time.time()),
                                'tg_v_eut': next((item for item in eut_names if item['eut_enrollment_id'] == int(request.form['eut_name_id'])), None)['eut_shortname'],
                                'tg_v_eut_id': int(request.form['eut_name_id']),
                                'tg_v_host': next((item for item in tg_v_hosts if item['agent_enrollment_id'] == int(request.form['tg_v_host_id'])), None)['agent_hostname'],
                                'tg_v_host_id': request.form['tg_v_host_id'],
                                'tg_v_src_ip': '',
                                'tg_v_dst_ip': next((item for item in eut_names if item['eut_enrollment_id'] == int(request.form['eut_name_id'])), None)['eut_dst_ip'],
                                'tg_v_dst_proto': request.form['tg_v_dst_proto'],
                                'tg_v_pps': int(request.form['tg_v_pps']),
                                'tg_v_dur': int(request.form['tg_v_dur']),
                                'tg_v_p_cnt': (int(request.form['tg_v_pps'])*int(request.form['tg_v_dur'])),
                                'tg_v_p_int': float(1)/int(request.form['tg_v_pps']),
                                'tg_v_description': request.form['tg_v_description'],
                                'tg_v_enrollment_date': str(datetime.now()),
                                'tg_v_status': request.form['tg_v_status']
                                }
            # Once new Task is Enrolled, try and push to remote agent
            tg_v_host_id = int(request.form['tg_v_host_id'])
            tg_v_host_ip = agent_entries[agent_entries.index == tg_v_host_id]['agent_ip'].values[0]
            tg_v_host_port = agent_entries[agent_entries.index == tg_v_host_id]['agent_port'].values[0]
            tg_v_list_entry['tg_v_host_ip'] = tg_v_host_ip  # have to add this key in in addition to tg_v_list_entry for push to remote to work
            enroll_tg_v_task_entry(tg_v_list_entry, tg_v_host_ip, tg_v_host_port)
            # Refresh task entries for page refresh
            tg_v_tasks_entries = get_tg_v_tasks()
    return render_template('enroll_tg_v_tasks.html',
                            error=error,
                            tg_v_hosts=tg_v_hosts,
                            eut_names=eut_names,
                            tg_v_protos=tg_v_protos,
                            data=tg_v_tasks_entries.to_html())

def enroll_tg_v_task_entry(tg_v_list_entry, tg_v_host_ip, tg_v_host_port):
            # 1. update the local csv with the task entry
            tg_v_list = []
            tg_v_list.append(tg_v_list_entry)
            tg_v_list_df = pd.DataFrame.from_dict(tg_v_list)
            tg_v_list_df.set_index('tg_v_enrollment_id', inplace=True)
            #print tg_v_list_df
            tg_v_list_df.to_csv(ddv_c_cfg.tg_v_tasks_list_filename, mode='a', header=False, columns=[
                                                                                        #'tg_v_enrollment_id',
                                                                                        'tg_v_eut',
                                                                                        'tg_v_eut_id',
                                                                                        'tg_v_host',
                                                                                        'tg_v_host_id',
                                                                                        'tg_v_src_ip',
                                                                                        'tg_v_dst_ip',
                                                                                        'tg_v_dst_proto',
                                                                                        'tg_v_pps',
                                                                                        'tg_v_dur',
                                                                                        'tg_v_p_cnt',
                                                                                        'tg_v_p_int',
                                                                                        'tg_v_description',
                                                                                        'tg_v_enrollment_date',
                                                                                        'tg_v_status'
                                                                                        ])
            session['new_tg_v_enrolled'] = True
            flash('DDV-C: New Verifier Task Enrolled', 'flash_green')
            # 2. push task entry to the remote host
            url = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port)+ '/remote_tg_v_task_push/' + str(tg_v_list_entry['tg_v_enrollment_id'])
            #print url
            try:
                task_resp = requests.post(url, verify=False, json=tg_v_list_entry)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('enrollment') == 'failed':
                        flash(task_resp.json().get('error'), 'flash_red')
                        session['remote_task_enrolled'] = False
                    elif task_resp.json().get('enrollment') == 'success':
                        session['remote_task_enrolled'] = True
                        flash(task_resp.json().get('message'), 'flash_green')
                    else:
                        pass
                else:
                    pass
            except:
                flash('DDV-C: There was a problem connecting to the Remote Agent', 'flash_red')
                       
@app.route('/delete_tg_v_task', methods=['GET', 'POST'])
def delete_tg_v_task():
    tg_v_task_entries = get_tg_v_tasks()
    agent_entries = get_agents()
    error = None
    #tg_v_names = tg_v_task_entries.tg_v_eut
    tg_v_names = tg_v_task_entries.reset_index().to_dict('records') # pass whole dataframe as 'list of dicts' to render template select list
    if request.method == 'GET':
        try:
            uuid = int(request.args.get('delete_tg_v_task_uuid'))
            delete_tg_v_task_entry(uuid)
            # get fresh task list after the delete
            tg_v_task_entries = get_tg_v_tasks()
            #tg_v_names = tg_v_task_entries.tg_v_eut
            tg_v_names = tg_v_task_entries.reset_index().to_dict('records')
            return render_template('delete_tg_v_task.html',
                                error=error,
                                tg_v_names=tg_v_names,
                                data=tg_v_task_entries.to_html())
        except:
            return render_template('delete_tg_v_task.html',
                    error=error,
                    tg_v_names=tg_v_names,
                    data=tg_v_task_entries.to_html())
    if request.method == 'POST':
        #uuid = tg_v_task_entries[tg_v_task_entries['tg_v_eut'] == request.form['tg_v_eut']].index.values[0]
        try:
            uuid = int(request.form['tg_v_enrollment_id'])
        except:
            return redirect(url_for('enroll_tg_v_tasks'))
        delete_tg_v_task_entry(uuid)
        # get fresh task list after the delete
        tg_v_task_entries = get_tg_v_tasks()
        #tg_v_names = tg_v_task_entries.tg_v_eut
        tg_v_names = tg_v_task_entries.reset_index().to_dict('records')
        return render_template('delete_tg_v_task.html',
                            error=error,
                            tg_v_names=tg_v_names,
                            data=tg_v_task_entries.to_html())
                            

def delete_tg_v_task_entry(uuid):
    try:
        tg_v_task_entries = get_tg_v_tasks()
        agent_entries = get_agents()
        agent_uuid = int(tg_v_task_entries[tg_v_task_entries.index == uuid]['tg_v_host_id'].values[0])
        tg_v_host_ip = agent_entries[agent_entries.index == agent_uuid]['agent_ip'].values[0]
        tg_v_host_port = agent_entries[agent_entries.index == agent_uuid]['agent_port'].values[0]
        tg_v_task_entries.drop(index=int(uuid)).to_csv(ddv_c_cfg.tg_v_tasks_list_filename, mode='w', header=False, columns=[
                                                                                          #'tg_v_enrollment_id',
                                                                                          'tg_v_eut',
                                                                                          'tg_v_eut_id',
                                                                                          'tg_v_host',
                                                                                          'tg_v_host_id',
                                                                                          'tg_v_src_ip',
                                                                                          'tg_v_dst_ip',
                                                                                          'tg_v_dst_proto',
                                                                                          'tg_v_pps',
                                                                                          'tg_v_dur',
                                                                                          'tg_v_p_cnt',
                                                                                          'tg_v_p_int',
                                                                                          'tg_v_description',
                                                                                          'tg_v_enrollment_date',
                                                                                          'tg_v_status'
                                                                                           ])
        session['tg_v_task_deleted'] = True
        flash('DDV-C: ddv-tg-v task deleted', 'flash_green')
        # Delete task from remote ddv-tg-v agents as well
        try:
            url = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port)+ '/remote_tg_v_task_delete/' + str(uuid)
            #print url
            try:
                task_resp = requests.get(url, verify=False, timeout=ddv_c_cfg.agent_timeout)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('action') == 'failed':
                        flash(task_resp.json().get('error'), 'flash_red')
                        session['remote_task_deleted'] = False
                    elif task_resp.json().get('action') == 'success':
                        session['remote_task_deleted'] = True
                        flash(str(task_resp.json().get('message')), 'flash_green') # success message from remote agent
                    else:
                        pass
                else:
                    pass
            except:
                flash('DDV-C: There was a problem connecting to the Remote Agent', 'flash_red')
        except:
            pass
    except:
        pass
            
                            
@app.route('/edit_tg_v_task', methods=['GET', 'POST'])
def edit_tg_v_task():
    error = None
    eut_entries = get_eut()
    tg_v_task_entries = get_tg_v_tasks()
    eut_names = eut_entries.reset_index().to_dict('records')
    agent_entries = get_agents()
    tg_v_hosts = agent_entries[agent_entries.agent_role == 'A'].reset_index().to_dict('records')
    if request.method == 'GET':
        uuid = int(request.args.get('edit_tg_v_task_uuid')) # https://127.0.0.1:2020/edit_tg_v_task?edit_tg_v_task_uuid=1600788172
        #print uuid
        tg_v_task_entry = tg_v_task_entries[tg_v_task_entries.index == uuid].reset_index().to_dict('records')
        return render_template('edit_tg_v_task.html',
                                error=error,
                                tg_v_protos=tg_v_protos,
                                data=tg_v_task_entries.to_html(),
                                task=tg_v_task_entry)
    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
            # 1. get desired edits from form POST
            uuid = int(request.form['tg_v_enrollment_id'])
            tg_v_task_list = []
            tg_v_task_list_entry = {
                                'tg_v_enrollment_id': request.form['tg_v_enrollment_id'],
                                'tg_v_eut': request.form['tg_v_eut'],
                                'tg_v_eut_id': request.form['tg_v_eut_id'],
                                'tg_v_host': request.form['tg_v_host'],
                                'tg_v_host_id': request.form['tg_v_host_id'],
                                'tg_v_src_ip': '',
                                'tg_v_dst_ip': request.form['tg_v_dst_ip'],
                                'tg_v_dst_proto': request.form['tg_v_dst_proto'],
                                'tg_v_pps': int(request.form['tg_v_pps']),
                                'tg_v_dur': int(request.form['tg_v_dur']),
                                'tg_v_p_cnt': (int(request.form['tg_v_pps'])*int(request.form['tg_v_dur'])),
                                'tg_v_p_int': float(1)/int(request.form['tg_v_pps']),
                                'tg_v_description': request.form['tg_v_description'],
                                'tg_v_enrollment_date': request.form['tg_v_enrollment_date'],
                                'tg_v_status': request.form['tg_v_status']
                                }
            tg_v_task_list.append(tg_v_task_list_entry)
            tg_v_task_list_df = pd.DataFrame.from_dict(tg_v_task_list)
            tg_v_task_list_df.set_index('tg_v_enrollment_id', inplace=True)
            #print tg_v_task_list_df
            # 2. drop modified task from csv and wipe from remote agent
            delete_tg_v_task_entry(int(request.form['tg_v_enrollment_id']))
            # 3. add modified agent back to csv
            #print tg_v_task_list_entry, tg_v_host_ip, tg_v_host_port
            agent_uuid = int(tg_v_task_entries[tg_v_task_entries.index == uuid]['tg_v_host_id'].values[0])
            tg_v_host_ip = agent_entries[agent_entries.index == agent_uuid]['agent_ip'].values[0]
            tg_v_host_port = agent_entries[agent_entries.index == agent_uuid]['agent_port'].values[0]
            tg_v_task_list_entry['tg_v_host_ip'] = tg_v_host_ip  # have to add this key in in addition to tg_v_task_list_entry for push to remote to work
            enroll_tg_v_task_entry(tg_v_task_list_entry, tg_v_host_ip, tg_v_host_port)
            # get fresh task list after delete/enroll steps
            tg_v_task_entries = get_tg_v_tasks()
            return redirect(url_for('tg_v_tasks_status'))
          
@app.route('/tg_v_tasks_status', methods=['GET'])
def tg_v_tasks_status():
    try:
        agent_entries = get_agents()
        tg_v_tasks_entries = get_tg_v_tasks()
        tg_v_tasks_status = []
        for uuid in tg_v_tasks_entries.index:
            tg_v_enrollment_id = uuid
            tg_v_eut = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_eut'].values[0])
            tg_v_eut_id = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_eut_id'].values[0])
            tg_v_host = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_host'].values[0])
            tg_v_host_id = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_host_id'].values[0])
            tg_v_host_ip = str(agent_entries[agent_entries.index == int(tg_v_host_id)]['agent_ip'].values[0])
            tg_v_host_port = str(agent_entries[agent_entries.index == int(tg_v_host_id)]['agent_port'].values[0])
            tg_v_src_ip = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_src_ip'].values[0])
            tg_v_dst_ip = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_dst_ip'].values[0])
            tg_v_dst_proto = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_dst_proto'].values[0])
            tg_v_pps = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_pps'].values[0])
            tg_v_dur = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_dur'].values[0])
            tg_v_p_cnt = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_p_cnt'].values[0])
            tg_v_p_int = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_p_int'].values[0])
            tg_v_description = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_description'].values[0])
            tg_v_enrollment_date = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_enrollment_date'].values[0])
            tg_v_status = str(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)]['tg_v_status'].values[0])
            # URL for getting keepalive and health status from TG-x:
            url_ka = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port)+ '/ddv_tg_x_keepalive'
            # URL for getting state of each task, running/idle/failed
            url_state = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port)+ '/ddv_tg_v_task_run/' + str(uuid) + '/status'
            #print url
            try:
                task_resp = requests.get(url_ka, verify=False, timeout=ddv_c_cfg.agent_timeout)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('action') == 'success':
                        tg_v_task_health_response = task_resp.json().get('health')
                        tg_v_task_tasks_response = task_resp.json().get('tasks')
                        for task in tg_v_task_tasks_response:
                            #print task['tg_v_enrollment_id'], uuid
                            if int(task['tg_v_enrollment_id']) == int(uuid):
                                task_state = requests.get(url_state, verify=False, timeout=ddv_c_cfg.agent_timeout)
                                if task_state.ok:
                                    task_current_state = task_state.json().get('state')
                                else: # the Verifier tasks are blocking, waiting for test result output, so timeout probably means it's still running
                                    task_current_state = 'unknown'
                                tg_v_task_tasks_response = 'in-sync' + ', ' + str(task_current_state)
                                break # once there's a match, stop the 'for' loop
                            else:
                                tg_v_task_tasks_response = 'not in-sync'
                        session['remote_tg_v_task_alive'] = True
                        #flash('DDV-C: ' + str(tg_v_host) + ': ' + str(task_resp.json().get('health')), 'flash_green') # success message from remote tg_v_task
                    else:
                        pass
                else:
                    tg_v_task_health_response = 'offline'
                    tg_v_task_tasks_response = 'unknown'
            except:
                flash('DDV-C: There was a problem connecting to the Remote tg_v_task: ' + str(tg_v_host), 'flash_red')
                session['remote_tg_v_task_alive'] = False
                tg_v_task_health_response = 'offline'
                tg_v_task_tasks_response = 'unknown'
            tg_v_tasks_status_entry = {
                            #'tg_v_task_enrollment_id': tg_v_enrollment_id,
                            'tg_v_task_eut': tg_v_eut,
                            #'tg_v_task_eut_id': tg_v_eut_id,
                            'tg_v_task_host': tg_v_host,
                            #'tg_v_task_host_id': tg_v_host_id,
                            'tg_v_task_host_ip': tg_v_host_ip,
                            #'tg_v_task_src_ip': tg_v_src_ip,
                            'tg_v_task_dst_ip': tg_v_dst_ip,
                            'tg_v_task_dst_proto': tg_v_dst_proto,
                            'tg_v_task_pps': tg_v_pps,
                            'tg_v_task_dur': tg_v_dur,
                            #'tg_v_task_p_cnt': tg_v_p_cnt,
                            #'tg_v_task_p_int': tg_v_p_int,
                            'tg_v_task_description': tg_v_description,
                            'tg_v_task_enrollment_date': tg_v_enrollment_date,
                            'tg_v_task_status': tg_v_status,
                            'tg_v_task_health': str(tg_v_task_health_response) + ' (task ' + str((tg_v_task_tasks_response)) + ')',
                            'edit': tg_v_enrollment_id,
                            'delete': tg_v_enrollment_id,
                            'push': tg_v_enrollment_id
                           }
            tg_v_tasks_status.append(tg_v_tasks_status_entry)
        #print tg_v_tasks_status
        tg_v_tasks_status_df = pd.DataFrame.from_dict(tg_v_tasks_status)
        # Reorder columns back to original ordering
        tg_v_tasks_status_df = tg_v_tasks_status_df[[
                                            #'tg_v_task_enrollment_id',
                                            'tg_v_task_eut',
                                            #'tg_v_task_eut_id',
                                            'tg_v_task_host',
                                            #'tg_v_task_host_id',
                                            'tg_v_task_host_ip',
                                            #'tg_v_task_src_ip',
                                            'tg_v_task_dst_ip',
                                            'tg_v_task_dst_proto',
                                            'tg_v_task_pps',
                                            'tg_v_task_dur',
                                            #'tg_v_task_p_cnt',
                                            #'tg_v_task_p_int',
                                            'tg_v_task_description',
                                            'tg_v_task_enrollment_date',
                                            'tg_v_task_status',
                                            'tg_v_task_health',
                                            'edit',
                                            'delete',
                                            'push'
                                            ]]
        return render_template(
                                "list_tg_v_tasks_status.html",
                                column_names=tg_v_tasks_status_df.columns.values,
                                row_data=list(tg_v_tasks_status_df.values.tolist()),
                                edit_link_column="edit",
                                delete_link_column="delete",
                                push_link_column="push",
                                zip=zip
                                )
    except:
        flash('No DDV-TG-V Tasks Configured as yet.  Please Configure Verifier Tasks...', 'flash_red')
        return redirect(url_for('enroll_tg_v_tasks'))

    

@app.route('/enroll_tg_a_tasks', methods=['GET', 'POST'])
def enroll_tg_a_tasks():
    error = None
    tg_a_tasks_entries = get_tg_a_tasks()
    eut_entries = get_eut()
    #eut_names = eut_entries.eut_shortname
    eut_names = eut_entries.reset_index().to_dict('records')
    agent_entries = get_agents()
    #tg_a_hosts = agent_entries[agent_entries.agent_role == 'A'].agent_hostname
    tg_a_hosts = agent_entries[agent_entries.agent_role == 'A'].reset_index().to_dict('records')
    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
            tg_a_list_entry = {
                                'tg_a_enrollment_id': int(time.time()),
                                'tg_a_eut': next((item for item in eut_names if item['eut_enrollment_id'] == int(request.form['eut_name_id'])), None)['eut_shortname'],
                                'tg_a_eut_id': int(request.form['eut_name_id']),
                                'tg_a_host': next((item for item in tg_a_hosts if item['agent_enrollment_id'] == int(request.form['tg_a_host_id'])), None)['agent_hostname'],
                                'tg_a_host_id': request.form['tg_a_host_id'],
                                'tg_a_src_ip': '',
                                'tg_a_dst_ip': next((item for item in eut_names if item['eut_enrollment_id'] == int(request.form['eut_name_id'])), None)['eut_dst_ip'],
                                'tg_a_dst_vector': request.form['tg_a_dst_vector'],
                                'tg_a_pps': int(request.form['tg_a_pps']),
                                'tg_a_dur': int(request.form['tg_a_dur']),
                                'tg_a_p_cnt': (int(request.form['tg_a_pps'])*int(request.form['tg_a_dur'])),
                                'tg_a_p_int': float(1)/int(request.form['tg_a_pps']),
                                'tg_a_description': request.form['tg_a_description'],
                                'tg_a_enrollment_date': str(datetime.now()),
                                'tg_a_status': request.form['tg_a_status']
                                }
            # Once new Task is Enrolled on DDV, try and push task to remote agent
            tg_a_host_id = int(request.form['tg_a_host_id'])
            tg_a_host_ip = agent_entries[agent_entries.index == tg_a_host_id]['agent_ip'].values[0]
            tg_a_host_port = agent_entries[agent_entries.index == tg_a_host_id]['agent_port'].values[0]
            tg_a_list_entry['tg_a_host_ip'] = tg_a_host_ip  # have to add this key in in addition to tg_a_list_entry for push to remote to work
            enroll_tg_a_task_entry(tg_a_list_entry, tg_a_host_ip, tg_a_host_port)
            # Refresh task entries for page refresh
            tg_a_tasks_entries = get_tg_a_tasks()
    return render_template('enroll_tg_a_tasks.html',
                            error=error,
                            tg_a_hosts=tg_a_hosts,
                            eut_names=eut_names,
                            tg_a_vectors=tg_a_vectors,
                            data=tg_a_tasks_entries.to_html())


def enroll_tg_a_task_entry(tg_a_list_entry, tg_a_host_ip, tg_a_host_port):
            # 1. update the local csv with the task entry
            tg_a_list = []
            tg_a_list.append(tg_a_list_entry)
            tg_a_list_df = pd.DataFrame.from_dict(tg_a_list)
            tg_a_list_df.set_index('tg_a_enrollment_id', inplace=True)
            tg_a_list_df.to_csv(ddv_c_cfg.tg_a_tasks_list_filename, mode='a', header=False, columns=[
                                                                                        #'tg_a_enrollment_id',
                                                                                        'tg_a_eut',
                                                                                        'tg_a_eut_id',
                                                                                        'tg_a_host',
                                                                                        'tg_a_host_id',
                                                                                        'tg_a_src_ip',
                                                                                        'tg_a_dst_ip',
                                                                                        'tg_a_dst_vector',
                                                                                        'tg_a_pps',
                                                                                        'tg_a_dur',
                                                                                        'tg_a_p_cnt',
                                                                                        'tg_a_p_int',
                                                                                        'tg_a_description',
                                                                                        'tg_a_enrollment_date',
                                                                                        'tg_a_status'
                                                                                        ])
            session['new_tg_a_enrolled'] = True
            flash('DDV-C: New Attack Task Enrolled', 'flash_green')
            # 2. push task entry to the remote host
            url = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port)+ '/remote_tg_a_task_push/' + str(tg_a_list_entry['tg_a_enrollment_id'])
            #print url
            try:
                task_resp = requests.post(url, verify=False, json=tg_a_list_entry, timeout=ddv_c_cfg.agent_timeout)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('enrollment') == 'failed':
                        flash(task_resp.json().get('error'), 'flash_red')
                        session['remote_task_enrolled'] = False
                    elif task_resp.json().get('enrollment') == 'success':
                        session['remote_task_enrolled'] = True
                        flash(task_resp.json().get('message'), 'flash_green')
                    else:
                        pass
                else:
                    pass
            except:
                flash('DDV-C: There was a problem connecting to the Remote Agent', 'flash_red')

                            
@app.route('/delete_tg_a_task', methods=['GET', 'POST'])
def delete_tg_a_task():
    tg_a_task_entries = get_tg_a_tasks()
    agent_entries = get_agents()
    error = None
    tg_a_names = tg_a_task_entries.reset_index().to_dict('records') # pass whole dataframe as 'list of dicts' to render template select list
    if request.method == 'GET':
        try:
            uuid = int(request.args.get('delete_tg_a_task_uuid'))
            delete_tg_a_task_entry(uuid)
            # get fresh task list after the delete
            tg_a_task_entries = get_tg_a_tasks()
            tg_a_names = tg_a_task_entries.reset_index().to_dict('records')
            return render_template('delete_tg_a_task.html',
                                error=error,
                                tg_a_names=tg_a_names,
                                data=tg_a_task_entries.to_html())
        except:
            return render_template('delete_tg_a_task.html',
                                error=error,
                                tg_a_names=tg_a_names,
                                data=tg_a_task_entries.to_html())
    if request.method == 'POST':
        try:
            uuid = int(request.form['tg_a_enrollment_id'])
        except:
            return redirect(url_for('enroll_tg_a_tasks'))
        delete_tg_a_task_entry(uuid)
        # get fresh task list after the delete
        tg_a_task_entries = get_tg_a_tasks()
        tg_a_names = tg_a_task_entries.reset_index().to_dict('records')
        return render_template('delete_tg_a_task.html',
                            error=error,
                            tg_a_names=tg_a_names,
                            data=tg_a_task_entries.to_html())


def delete_tg_a_task_entry(uuid):
    try:
        tg_a_task_entries = get_tg_a_tasks()
        agent_entries = get_agents()
        agent_uuid = int(tg_a_task_entries[tg_a_task_entries.index == uuid]['tg_a_host_id'].values[0])
        tg_a_host_ip = agent_entries[agent_entries.index == agent_uuid]['agent_ip'].values[0]
        tg_a_host_port = agent_entries[agent_entries.index == agent_uuid]['agent_port'].values[0]
        tg_a_task_entries.drop(index=int(uuid)).to_csv(ddv_c_cfg.tg_a_tasks_list_filename, mode='w', header=False, columns=[
                                                                                          #'tg_a_enrollment_id',
                                                                                          'tg_a_eut',
                                                                                          'tg_a_eut_id',
                                                                                          'tg_a_host',
                                                                                          'tg_a_host_id',
                                                                                          'tg_a_src_ip',
                                                                                          'tg_a_dst_ip',
                                                                                          'tg_a_dst_vector',
                                                                                          'tg_a_pps',
                                                                                          'tg_a_dur',
                                                                                          'tg_a_p_cnt',
                                                                                          'tg_a_p_int',
                                                                                          'tg_a_description',
                                                                                          'tg_a_enrollment_date',
                                                                                          'tg_a_status'
                                                                                           ])
        session['tg_a_task_deleted'] = True
        flash('DDV-C: ddv-tg-a task deleted', 'flash_green')
        # Delete task from remote ddv-tg-a agents as well
        try:
            url = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port)+ '/remote_tg_a_task_delete/' + str(uuid)
            #print url
            try:
                task_resp = requests.get(url, verify=False, timeout=ddv_c_cfg.agent_timeout)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('action') == 'failed':
                        flash(task_resp.json().get('error'), 'flash_red')
                        session['remote_task_deleted'] = False
                        return 'failed'
                    elif task_resp.json().get('action') == 'success':
                        session['remote_task_deleted'] = True
                        flash(str(task_resp.json().get('message')), 'flash_green') # success message from remote agent
                        return 'success'
                    else:
                        pass
                else:
                    pass
            except:
                flash('DDV-C: There was a problem connecting to the Remote Agent', 'flash_red')
        except:
            pass
    except:
        pass

@app.route('/edit_tg_a_task', methods=['GET', 'POST'])
def edit_tg_a_task():
    error = None
    eut_entries = get_eut()
    tg_a_task_entries = get_tg_a_tasks()
    eut_names = eut_entries.reset_index().to_dict('records')
    agent_entries = get_agents()
    tg_a_hosts = agent_entries[agent_entries.agent_role == 'A'].reset_index().to_dict('records')
    if request.method == 'GET':
        uuid = int(request.args.get('edit_tg_a_task_uuid')) # https://127.0.0.1:2020/edit_tg_a_task?edit_tg_a_task_uuid=1600788172
        #print uuid
        tg_a_task_entry = tg_a_task_entries[tg_a_task_entries.index == uuid].reset_index().to_dict('records')
        return render_template('edit_tg_a_task.html',
                                error=error,
                                tg_a_vectors=tg_a_vectors,
                                data=tg_a_task_entries.to_html(),
                                task=tg_a_task_entry)
    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
            # 1. get desired edits from form POST
            uuid = int(request.form['tg_a_enrollment_id'])
            tg_a_task_list = []
            tg_a_task_list_entry = {
                                'tg_a_enrollment_id': request.form['tg_a_enrollment_id'],
                                'tg_a_eut': request.form['tg_a_eut'],
                                'tg_a_eut_id': request.form['tg_a_eut_id'],
                                'tg_a_host': request.form['tg_a_host'],
                                'tg_a_host_id': request.form['tg_a_host_id'],
                                'tg_a_src_ip': '',
                                'tg_a_dst_ip': request.form['tg_a_dst_ip'],
                                'tg_a_dst_vector': request.form['tg_a_dst_vector'],
                                'tg_a_pps': int(request.form['tg_a_pps']),
                                'tg_a_dur': int(request.form['tg_a_dur']),
                                'tg_a_p_cnt': (int(request.form['tg_a_pps'])*int(request.form['tg_a_dur'])),
                                'tg_a_p_int': float(1)/int(request.form['tg_a_pps']),
                                'tg_a_description': request.form['tg_a_description'],
                                'tg_a_enrollment_date': request.form['tg_a_enrollment_date'],
                                'tg_a_status': request.form['tg_a_status']
                                }
            tg_a_task_list.append(tg_a_task_list_entry)
            tg_a_task_list_df = pd.DataFrame.from_dict(tg_a_task_list)
            tg_a_task_list_df.set_index('tg_a_enrollment_id', inplace=True)
            #print tg_a_task_list_df
            # 2. drop modified task from csv and wipe from remote agent
            delete_tg_a_task_entry(int(request.form['tg_a_enrollment_id']))
            # 3. add modified agent back to csv
            #print tg_a_task_list_entry, tg_a_host_ip, tg_a_host_port
            agent_uuid = int(tg_a_task_entries[tg_a_task_entries.index == uuid]['tg_a_host_id'].values[0])
            tg_a_host_ip = agent_entries[agent_entries.index == agent_uuid]['agent_ip'].values[0]
            tg_a_host_port = agent_entries[agent_entries.index == agent_uuid]['agent_port'].values[0]
            tg_a_task_list_entry['tg_a_host_ip'] = tg_a_host_ip  # have to add this key in in addition to tg_a_task_list_entry for push to remote to work
            enroll_tg_a_task_entry(tg_a_task_list_entry, tg_a_host_ip, tg_a_host_port)
            # get fresh task list after delete/enroll steps
            tg_a_task_entries = get_tg_a_tasks()
            return redirect(url_for('tg_a_tasks_status'))


@app.route('/tg_a_tasks_status', methods=['GET'])
def tg_a_tasks_status():
    try:
        agent_entries = get_agents()
        tg_a_tasks_entries = get_tg_a_tasks()
        tg_a_tasks_status = []
        for uuid in tg_a_tasks_entries.index:
            tg_a_enrollment_id = uuid
            tg_a_eut = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_eut'].values[0])
            tg_a_eut_id = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_eut_id'].values[0])
            tg_a_host = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_host'].values[0])
            tg_a_host_id = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_host_id'].values[0])
            tg_a_host_ip = str(agent_entries[agent_entries.index == int(tg_a_host_id)]['agent_ip'].values[0])
            tg_a_host_port = str(agent_entries[agent_entries.index == int(tg_a_host_id)]['agent_port'].values[0])
            tg_a_src_ip = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_src_ip'].values[0])
            tg_a_dst_ip = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_dst_ip'].values[0])
            tg_a_dst_vector = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_dst_vector'].values[0])
            tg_a_pps = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_pps'].values[0])
            tg_a_dur = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_dur'].values[0])
            tg_a_p_cnt = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_p_cnt'].values[0])
            tg_a_p_int = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_p_int'].values[0])
            tg_a_description = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_description'].values[0])
            tg_a_enrollment_date = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_enrollment_date'].values[0])
            tg_a_status = str(tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)]['tg_a_status'].values[0])
            # URL for getting keepalive and health status from TG-x:
            url_ka = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port)+ '/ddv_tg_x_keepalive'
            # URL for getting state of each task, running/idle/failed
            url_state = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port)+ '/ddv_tg_a_task_run/' + str(uuid) + '/status'
            #print url
            try:
                task_resp = requests.get(url_ka, verify=False, timeout=ddv_c_cfg.agent_timeout)
                if task_resp.ok:
                    #return task_resp.json()
                    #print task_resp.json()
                    if task_resp.json().get('action') == 'success':
                        tg_a_task_health_response = task_resp.json().get('health')
                        tg_a_task_tasks_response = task_resp.json().get('tasks')
                        for task in tg_a_task_tasks_response:
                            #print task['tg_a_enrollment_id'], uuid
                            if int(task['tg_a_enrollment_id']) == int(uuid):
                                task_state = requests.get(url_state, verify=False, timeout=ddv_c_cfg.agent_timeout)
                                if task_state.ok:
                                    task_current_state = task_state.json().get('state')
                                else:
                                    task_current_state = 'unknown'
                                tg_a_task_tasks_response = 'in-sync' + ', ' + str(task_current_state)
                                break # once there's a match, stop the 'for' loop
                            else:
                                tg_a_task_tasks_response = 'not in-sync'
                        session['remote_tg_a_task_alive'] = True
                        #flash('DDV-C: ' + str(tg_a_host) + ': ' + str(task_resp.json().get('health')), 'flash_green') # success message from remote tg_a_task
                    else:
                        pass
                else:
                    tg_a_task_health_response = 'offline'
                    tg_a_task_tasks_response = 'unknown'
            except:
                flash('DDV-C: There was a problem connecting to the Remote tg_a_task: ' + str(tg_a_host), 'flash_red')
                session['remote_tg_a_task_alive'] = False
                tg_a_task_health_response = 'offline'
                tg_a_task_tasks_response = 'unknown'
            tg_a_tasks_status_entry = {
                            #'tg_a_task_enrollment_id': tg_a_enrollment_id,
                            'tg_a_task_eut': tg_a_eut,
                            #'tg_a_task_eut_id': tg_a_eut_id,
                            'tg_a_task_host': tg_a_host,
                            #'tg_a_task_host_id': tg_a_host_id,
                            'tg_a_task_host_ip': tg_a_host_ip,
                            #'tg_a_task_src_ip': tg_a_src_ip,
                            'tg_a_task_dst_ip': tg_a_dst_ip,
                            'tg_a_task_dst_vector': tg_a_dst_vector,
                            'tg_a_task_pps': tg_a_pps,
                            'tg_a_task_dur': tg_a_dur,
                            #'tg_a_task_p_cnt': tg_a_p_cnt,
                            #'tg_a_task_p_int': tg_a_p_int,
                            'tg_a_task_description': tg_a_description,
                            'tg_a_task_enrollment_date': tg_a_enrollment_date,
                            'tg_a_task_status': tg_a_status,
                            'tg_a_task_health': str(tg_a_task_health_response) + ' (task ' + str((tg_a_task_tasks_response)) + ')',
                            'edit': tg_a_enrollment_id,
                            'delete': tg_a_enrollment_id,
                            'push': tg_a_enrollment_id
                           }
            tg_a_tasks_status.append(tg_a_tasks_status_entry)
        #print tg_a_tasks_status
        tg_a_tasks_status_df = pd.DataFrame.from_dict(tg_a_tasks_status)
        # Reorder columns back to original ordering
        tg_a_tasks_status_df = tg_a_tasks_status_df[[
                                            #'tg_a_task_enrollment_id',
                                            'tg_a_task_eut',
                                            #'tg_a_task_eut_id',
                                            'tg_a_task_host',
                                            #'tg_a_task_host_id',
                                            'tg_a_task_host_ip',
                                            #'tg_a_task_src_ip',
                                            'tg_a_task_dst_ip',
                                            'tg_a_task_dst_vector',
                                            'tg_a_task_pps',
                                            'tg_a_task_dur',
                                            #'tg_a_task_p_cnt',
                                            #'tg_a_task_p_int',
                                            'tg_a_task_description',
                                            'tg_a_task_enrollment_date',
                                            'tg_a_task_status',
                                            'tg_a_task_health',
                                            'edit',
                                            'delete',
                                            'push'
                                            ]]
        return render_template(
                                "list_tg_a_tasks_status.html",
                                column_names=tg_a_tasks_status_df.columns.values,
                                row_data=list(tg_a_tasks_status_df.values.tolist()),
                                edit_link_column="edit",
                                delete_link_column="delete",
                                push_link_column="push",
                                zip=zip
                                )
    except:
        flash('No DDV-TG-A Tasks Configured as yet.  Please Configure Attack Tasks...', 'flash_red')
        return redirect(url_for('enroll_tg_a_tasks'))

        

@app.route('/enroll_eut', methods=['GET', 'POST'])
def enroll_eut():
    eut_entries = get_eut()
    out_entries = get_out()
    #out_companynames = out_entries.out_companyname
    out_companynames = out_entries.reset_index().to_dict('records')
    error = None
    if request.method == 'POST':
            eut_list_entry = {
                                'eut_enrollment_id': int(time.time()),
                                'eut_shortname': request.form['eut_shortname'],
                                'eut_dst_ip': request.form['eut_dst_ip'],
                                'eut_companyname': next((item for item in out_companynames if item['out_enrollment_id'] == int(request.form['out_companyname_id'])), None)['out_companyname'],
                                'eut_companyname_id': request.form['out_companyname_id'],
                                'eut_enrollment_date': datetime.now()
                                }
            enroll_eut_entry(eut_list_entry)
            eut_entries = get_eut()
    return render_template('enroll_eut.html',
                            error=error,
                            out_companynames=out_companynames,
                            data=eut_entries.to_html())


def enroll_eut_entry(eut_list_entry):
        eut_list = []
        eut_list.append(eut_list_entry)
        eut_list_df = pd.DataFrame.from_dict(eut_list)
        eut_list_df.set_index('eut_enrollment_id', inplace=True)
        #print eut_list_df
        eut_list_df.to_csv(ddv_c_cfg.eut_list_filename, mode='a', header=False, columns=[
                                                                                    #'eut_enrollment_id',
                                                                                    'eut_shortname',
                                                                                    'eut_dst_ip',
                                                                                    'eut_companyname',
                                                                                    'eut_companyname_id',
                                                                                    'eut_enrollment_date'
                                                                                    ])
        session['new_eut_enrolled'] = True
        flash('DDV-C: New Entity Enrolled', 'flash_green')


@app.route('/delete_eut', methods=['GET', 'POST'])
def delete_eut():
    error = None
    eut_entries = get_eut()
    eut_names = eut_entries.reset_index().to_dict('records')
    if request.method == 'GET':
        try:
            uuid = int(request.args.get('delete_eut_uuid'))
            delete_eut_entry(uuid)
        except:
            pass
    if request.method == 'POST':
        try:
            uuid = int(request.form['eut_shortname']) # Get uuid of EUT from form POST
            delete_eut_entry(uuid)
        except:
            return redirect(url_for('enroll_eut'))
    eut_entries = get_eut()
    eut_names = eut_entries.reset_index().to_dict('records')
    return render_template('delete_eut.html', error=error, eut_names=eut_names, data=eut_entries.to_html())


def delete_eut_entry(uuid):
    eut_entries = get_eut()
    agent_entries = get_agents()
    tg_a_task_entries = get_tg_a_tasks()
    tg_v_task_entries = get_tg_v_tasks()
    try:
        # 1. Before removing the agent, find and delete all associated agent tasks
        # 1a. Find and delete all Attack Tasks for this EUT UUID
        for task_entry in tg_a_task_entries[tg_a_task_entries['tg_a_eut_id'] == uuid].index.values:
            try:
                tg_a_task_entries = get_tg_a_tasks() # get fresh task list after each recursive deletion of task
                if delete_tg_a_task_entry(task_entry) == 'success':
                    pass
                else:
                    pass
                    #flash('DDV-C: ' + str(uuid) + ' task could not be deleted', 'flash_red')
            except:
                flash('DDV-C: Remote tasks could not be deleted', 'flash_red')
        # 1b. Find and delete all Verifier Tasks for this EUT
        for task_entry in tg_v_task_entries[tg_v_task_entries['tg_v_eut_id'] == uuid].index.values:
            try:
                tg_v_task_entries = get_tg_v_tasks() # get fresh task list after each recursive deletion of task
                if delete_tg_v_task_entry(task_entry) == 'success':
                    pass
                else:
                    pass
                    #flash('DDV-C: ' + str(uuid) + ' task could not be deleted', 'flash_red')
            except:
                flash('DDV-C: Remote tasks could not be deleted', 'flash_red')
        # 2. Delete EUT after deleting all associated tasks
        eut_entries.drop(index=int(uuid)).to_csv(ddv_c_cfg.eut_list_filename, mode='w', header=False, columns=[
                                                                                                    #'eut_enrollment_id',
                                                                                                    'eut_shortname',
                                                                                                    'eut_dst_ip',
                                                                                                    'eut_companyname',
                                                                                                    'eut_companyname_id',
                                                                                                    'eut_enrollment_date'
                                                                                                    ])
        session['eut_deleted'] = True
        flash('DDV-C: Entity Under Test successfully deleted', 'flash_green')
    except:
        pass


@app.route('/eut_status', methods=['GET'])
def eut_status():
    try:
        tg_a_task_entries = get_tg_a_tasks()
        tg_v_task_entries = get_tg_v_tasks()
        agent_entries = get_agents()
        eut_entries = get_eut()
        eut_status = []
        for uuid in eut_entries.index:
            # 1. List current EUT entries
            eut_enrollment_id = uuid
            eut_shortname = str(eut_entries[eut_entries.index == int(uuid)]['eut_shortname'].values[0])
            eut_dst_ip = str(eut_entries[eut_entries.index == int(uuid)]['eut_dst_ip'].values[0])
            eut_companyname = str(eut_entries[eut_entries.index == int(uuid)]['eut_companyname'].values[0])
            eut_companyname_id = str(eut_entries[eut_entries.index == int(uuid)]['eut_companyname_id'].values[0])
            eut_enrollment_date = str(eut_entries[eut_entries.index == int(uuid)]['eut_enrollment_date'].values[0])
            try:
                eut_a_tasks_cnt = len(tg_a_task_entries[tg_a_task_entries['tg_a_eut_id'] == uuid].index.values)
            except:
                eut_a_tasks_cnt = 0
            try:
                eut_v_tasks_cnt = len(tg_v_task_entries[tg_v_task_entries['tg_v_eut_id'] == uuid].index.values)
            except:
                eut_v_tasks_cnt = 0
            eut_status_entry = {
                            #'eut_enrollment_id': eut_enrollment_id,
                            'eut_shortname': eut_shortname,
                            'eut_dst_ip': eut_dst_ip,
                            'eut_companyname': eut_companyname,
                            'eut_companyname_id': eut_companyname_id,
                            'eut_enrollment_date': eut_enrollment_date,
                            'eut_a_tasks': eut_a_tasks_cnt,
                            'eut_v_tasks': eut_v_tasks_cnt,
                            'edit': eut_enrollment_id,
                            'delete': eut_enrollment_id
                           }
            eut_status.append(eut_status_entry)
        #print eut_status
        eut_status_df = pd.DataFrame.from_dict(eut_status)
        # Reorder columns back to original ordering
        eut_status_df = eut_status_df[[
                                            #'eut_enrollment_id',
                                            'eut_shortname',
                                            'eut_dst_ip',
                                            'eut_companyname',
                                            'eut_companyname_id',
                                            'eut_enrollment_date',
                                            'eut_a_tasks',
                                            'eut_v_tasks',
                                            'edit',
                                            'delete'
                                            ]]
        return render_template(
                                "list_eut_status.html",
                                column_names=eut_status_df.columns.values,
                                row_data=list(eut_status_df.values.tolist()),
                                edit_link_column="edit",
                                delete_link_column="delete",
                                zip=zip
                                )
    except:
        flash('No EUT Configured as yet.  Please Configure EUT...', 'flash_red')
        return redirect(url_for('enroll_eut'))



@app.route('/edit_eut', methods=['GET', 'POST'])
def edit_eut():
    error = None
    if request.method == 'GET':
        uuid = int(request.args.get('edit_eut_uuid')) # https://127.0.0.1:2020/edit_eut?eut_uuid=1600095410
        eut_entries = get_eut()
        eut_entry = eut_entries[eut_entries.index == uuid].reset_index().to_dict('records')
        return render_template('edit_eut.html', error=error, data=eut_entries.to_html(), eut=eut_entry)
    if request.method == 'POST':
        # 1. get desired edits from form POST
        data = {
                            'eut_shortname': request.form['eut_shortname'],
                            'eut_dst_ip': request.form['eut_dst_ip'],
                            'eut_companyname': request.form['eut_companyname'],
                            'eut_companyname_id': request.form['eut_companyname_id']
                }
        # 2. update df with new data
        for key in data:
            edit_df('eut', int(request.form['eut_enrollment_id']), key, data[key])
        return redirect(url_for('eut_status'))


@app.route('/enroll_out', methods=['GET', 'POST'])
def enroll_out():
    out_entries = get_out()
    error = None
    if request.method == 'POST':
            out_list_entry = {
                                'out_enrollment_id': int(time.time()),
                                'out_companyname': request.form['out_companyname'],
                                'out_contactname': request.form['out_contactname'],
                                'out_contactemail': request.form['out_contactemail'],
                                'out_contactnumber': request.form['out_contactnumber'],
                                'out_industry': request.form['out_industry'],
                                'out_sl_ip': request.form['out_sl_ip'],
                                'out_sl_api': request.form['out_sl_api'],
                                'out_enrollment_date': datetime.now()
                                }
            enroll_out_entry(out_list_entry)
            out_entries = get_out()
    return render_template('enroll_out.html', error=error, data=out_entries.to_html())
    
    
def enroll_out_entry(out_list_entry):
        out_list = []
        out_list.append(out_list_entry)
        out_list_df = pd.DataFrame.from_dict(out_list)
        out_list_df.set_index('out_enrollment_id', inplace=True)
        #print out_list_df
        out_list_df.to_csv(ddv_c_cfg.out_list_filename, mode='a', header=False, columns=[
                                                                                    'out_companyname',
                                                                                    'out_contactname',
                                                                                    'out_contactemail',
                                                                                    'out_contactnumber',
                                                                                    'out_industry',
                                                                                    'out_sl_ip',
                                                                                    'out_sl_api',
                                                                                    'out_enrollment_date'
                                                                                    ])
        session['new_out_enrolled'] = True
        flash('New Organisation Added', 'flash_green')


@app.route('/delete_out', methods=['GET', 'POST'])
def delete_out():
    out_entries = get_out()
    error = None
    out_names = out_entries.reset_index().to_dict('records')
    if request.method == 'GET':
        try:
            uuid = int(request.args.get('delete_out_uuid'))
            delete_out_entry(uuid)
        except:
            pass
    if request.method == 'POST':
        #uuid = out_entries[out_entries['out_companyname'] == request.form['out_companyname']].index.values[0]
        uuid = request.form['out_companyname']
        delete_out_entry(uuid)
    out_entries = get_out()
    out_names = out_entries.reset_index().to_dict('records')
    return render_template('delete_out.html', error=error, out_names=out_names, data=out_entries.to_html())
    
def delete_out_entry(uuid):
    out_entries = get_out()
    eut_entries = get_eut()
    try:
        # 1. Find all EUT linked to OUT, and delete these first (Tasks associated with EUT should also be deleted)
        try:
            for eut_entry in eut_entries[eut_entries['eut_companyname_id'] == str(uuid)].index.values:
                delete_eut_entry(eut_entry)
        except KeyError:
            pass
        # 2. Remote OUT entry
        out_entries.drop(index=int(uuid)).to_csv(ddv_c_cfg.out_list_filename, mode='w', header=False, columns=[
                                                                                                    'out_companyname',
                                                                                                    'out_contactname',
                                                                                                    'out_contactemail',
                                                                                                    'out_contactnumber',
                                                                                                    'out_industry',
                                                                                                    'out_sl_ip',
                                                                                                    'out_sl_api',
                                                                                                    'out_enrollment_date'
                                                                                                    ])
        session['out_deleted'] = True
        flash('DDV-C: Organisation Under Test successfully deleted', 'flash_green')
    except:
        pass


@app.route('/out_status', methods=['GET'])
def out_status():
    try:
        tg_a_task_entries = get_tg_a_tasks()
        tg_v_task_entries = get_tg_v_tasks()
        eut_entries = get_eut()
        out_entries = get_out()
        out_status = []
        for uuid in out_entries.index:
            # 1. List current out entries
            out_enrollment_id = uuid
            out_companyname = str(out_entries[out_entries.index == int(uuid)]['out_companyname'].values[0])
            out_contactname = str(out_entries[out_entries.index == int(uuid)]['out_contactname'].values[0])
            out_contactemail = str(out_entries[out_entries.index == int(uuid)]['out_contactemail'].values[0])
            out_contactnumber = str(out_entries[out_entries.index == int(uuid)]['out_contactnumber'].values[0])
            out_industry = str(out_entries[out_entries.index == int(uuid)]['out_industry'].values[0])
            out_sl_ip = str(out_entries[out_entries.index == int(uuid)]['out_sl_ip'].values[0])
            out_sl_api = str(out_entries[out_entries.index == int(uuid)]['out_sl_api'].values[0])
            out_enrollment_date = str(out_entries[out_entries.index == int(uuid)]['out_enrollment_date'].values[0])
            # Calculate total attack and verifier tasks associated with this OUT
            a_tasks_cnt = 0
            v_tasks_cnt = 0
            try:
                for eut_uuid in eut_entries[eut_entries['eut_companyname_id'] == str(uuid)].index.values:
                    a_tasks_cnt = a_tasks_cnt + len(tg_a_task_entries[tg_a_task_entries['tg_a_eut_id'] == eut_uuid])
                    v_tasks_cnt = v_tasks_cnt + len(tg_v_task_entries[tg_v_task_entries['tg_v_eut_id'] == eut_uuid])
            except KeyError:
                pass
            # Calculate total EuT associated with this OuT
            out_eut_cnt = 0
            try:
                out_eut = eut_entries[eut_entries['eut_companyname_id'] == str(uuid)]['eut_shortname'].values
                out_eut_cnt = out_eut_cnt + len(out_eut)
            except KeyError:
                 pass
            #print(out_companyname, out_eut)
            out_status_entry = {
                            #'out_enrollment_id': out_enrollment_id,
                            'out_companyname': out_companyname,
                            'out_contactname': out_contactname,
                            'out_contactemail': out_contactemail,
                            'out_contactnumber': out_contactnumber,
                            'out_industry': out_industry,
                            'out_sl_ip': out_sl_ip,
                            'out_sl_api': out_sl_api,
                            'out_enrollment_date': out_enrollment_date,
                            'out_eut_cnt': out_eut_cnt,
                            #'out_eut': out_eut,
                            'out_a_tasks': a_tasks_cnt,
                            'out_v_tasks': v_tasks_cnt,
                            'edit': out_enrollment_id,
                            'delete': out_enrollment_id,
                            'verify': out_enrollment_id,
                            'run': out_enrollment_id,
                            'draw': out_enrollment_id
                           }
            out_status.append(out_status_entry)
        #print(out_status)
        out_status_df = pd.DataFrame.from_dict(out_status)
        # Reorder columns back to original ordering
        out_status_df = out_status_df[[
                                            #'out_enrollment_id',
                                            'out_companyname',
                                            'out_contactname',
                                            'out_contactemail',
                                            'out_contactnumber',
                                            'out_industry',
                                            'out_sl_ip',
                                            #'out_sl_api',
                                            'out_enrollment_date',
                                            'out_eut_cnt',
                                            #'out_eut',
                                            'out_a_tasks',
                                            'out_v_tasks',
                                            'edit',
                                            'delete',
                                            'verify',
                                            'run',
                                            'draw'
                                            ]]
        return render_template(
                                "list_out_status.html",
                                column_names=out_status_df.columns.values,
                                row_data=list(out_status_df.values.tolist()),
                                edit_link_column="edit",
                                delete_link_column="delete",
                                verify_link_column="verify",
                                run_link_column="run",
                                draw_link_column="draw",
                                zip=zip
                                )
    except:
        flash('No OUT Configured as yet.  Please Configure OUT...', 'flash_red')
        return redirect(url_for('enroll_out'))


@app.route('/edit_out', methods=['GET', 'POST'])
def edit_out():
    error = None
    if request.method == 'GET':
        uuid = int(request.args.get('edit_out_uuid')) # https://127.0.0.1:2020/edit_out?out_uuid=1600095410
        out_entries = get_out()
        out_entry = out_entries[out_entries.index == uuid].reset_index().to_dict('records')
        return render_template('edit_out.html', error=error, data=out_entries.to_html(), out=out_entry)
    if request.method == 'POST':
        # 1. get desired edits from form POST
        data = {
                'out_companyname': request.form['out_companyname'],
                'out_contactname': request.form['out_contactname'],
                'out_contactemail': request.form['out_contactemail'],
                'out_contactnumber': request.form['out_contactnumber'],
                'out_industry': request.form['out_industry'],
                'out_sl_ip': request.form['out_sl_ip'],
                'out_sl_api': request.form['out_sl_api']
                }
        # 2. update df with new data
        for key in data:
            edit_df('out', int(request.form['out_enrollment_id']), key, data[key])
        return redirect(url_for('out_status'))


def run_ddv_tg_a_tasks(uuid, euts_of_out):
    tg_a_task_entries = get_tg_a_tasks()
    agent_entries = get_agents()
    message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C: Starting DDV-TG-A Attack tasks...'
    flash(message, 'flash_blue')
    stream_logger(message)
    for index in euts_of_out.index: #for each eut, get attack tasks associated with them
        for entry in tg_a_task_entries[tg_a_task_entries['tg_a_eut_id'] == index].index:
            tg_a_task_id = entry
            tg_a_host = tg_a_task_entries[tg_a_task_entries.index == entry]['tg_a_host'].values[0]
            tg_a_host_id = int(tg_a_task_entries[tg_a_task_entries.index == entry]['tg_a_host_id'].values[0])
            tg_a_host_ip = agent_entries[agent_entries.index == tg_a_host_id]['agent_ip'].values[0]
            tg_a_host_port = agent_entries[agent_entries.index == tg_a_host_id]['agent_port'].values[0]
            #print tg_a_task_id, tg_a_host_id, tg_a_host_ip, tg_a_host_port
            url = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port) + '/ddv_tg_a_task_run/' + str(tg_a_task_id) + '/status'
            #print url
            try:
                task_resp = requests.get(url, verify=False, timeout=ddv_c_cfg.agent_timeout)
                #pp.pprint(task_resp)
                if task_resp.ok:
                    #print task_resp.json()
                    if int(task_resp.json().get('running_pid')) < 0: # ddv-tg-a tasks not running, so start them
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_orange')
                        stream_logger(message)
                        url = 'https://' + str(tg_a_host_ip) + ':' + str(tg_a_host_port) + '/ddv_tg_a_task_run/' + str(tg_a_task_id) + '/start'
                        #print url
                        task_resp = requests.get(url, verify=False, timeout=ddv_c_cfg.agent_timeout)
                        #print(str(tg_a_host_ip) + ' - ' + str(tg_a_task_id) + ': ' + str(task_resp.json()))
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_green')
                        stream_logger(message)
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + str(task_resp.json().get('detail'))
                        flash(message, 'flash_green')
                        stream_logger(message)
                    elif int(task_resp.json().get('running_pid')) > 0:
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_green')
                        stream_logger()
                        #print(str(tg_a_host_ip) + ' - ' + str(tg_a_task_id) + ': ' + str(task_resp.json().get('message')))
                    else:
                        pass
            except requests.ConnectionError as e:
                message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C: ' + str(tg_a_host) + ': ' + str(e)
                flash(message, 'flash_red')
                stream_logger(message)
                pass


def run_ddv_tg_v_tasks(uuid, euts_of_out): # uuid is out_uuid
    tg_v_task_entries = get_tg_v_tasks()
    agent_entries = get_agents()
    message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C: Starting DDV-TG-V Verifier tasks...'
    flash(message, 'flash_blue')
    stream_logger(message)
    for index in euts_of_out.index: #for each eut, get verifier tasks associated with them
        for entry in tg_v_task_entries[tg_v_task_entries['tg_v_eut_id'] == index].index:
            tg_v_task_id = entry
            tg_v_host = tg_v_task_entries[tg_v_task_entries.index == entry]['tg_v_host'].values[0]
            tg_v_host_id = int(tg_v_task_entries[tg_v_task_entries.index == entry]['tg_v_host_id'].values[0])
            tg_v_host_ip = agent_entries[agent_entries.index == tg_v_host_id]['agent_ip'].values[0]
            tg_v_host_port = agent_entries[agent_entries.index == tg_v_host_id]['agent_port'].values[0]
            #print tg_v_task_id, tg_v_host_id, tg_v_host_ip, tg_v_host_port
            url = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port) + '/ddv_tg_v_task_run/' + str(tg_v_task_id) + '/status'
            #print url
            try:
                task_resp = requests.get(url, verify=False)
                #pp.pprint(task_resp)
                if task_resp.ok:
                    #print task_resp.json()
                    if int(task_resp.json().get('running_pid')) < 0: # ddv-tg-v tasks not running, so start them
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_orange')
                        stream_logger(message)
                        url = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port) + '/ddv_tg_v_task_run/' + str(tg_v_task_id) + '/start'
                        #print url
                        task_resp = requests.get(url, verify=False)
                        #print(str(tg_v_haost_ip) + ' - ' + str(tg_v_task_id) + ': ' + str(task_resp.json()))
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_green')
                        stream_logger(message)
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + str(task_resp.json().get('detail'))
                        flash(message, 'flash_green')
                        stream_logger(message)
                        # get the metric result when the task has completed
                        result_url = 'https://' + str(tg_v_host_ip) + ':' + str(tg_v_host_port) + '/ddv_tg_v_task_run/' + str(tg_v_task_id) + '/result'
                        #print url
                        task_resp = requests.get(result_url, verify=False)
                        #print(str(tg_v_haost_ip) + ' - ' + str(tg_v_task_id) + ': ' + str(task_resp.json()))
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '........ ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_green')
                        stream_logger(message)
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.......... ' + str(task_resp.json().get('metric')) + '% Success Rate'
                        flash(message, 'flash_green')
                        stream_logger(message)
                    elif int(task_resp.json().get('running_pid')) > 0: # ddv-tg-v tasks already running
                        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + str(task_resp.json().get('message'))
                        flash(message, 'flash_green')
                        stream_logger(message)
                        #print(str(tg_v_host_ip) + ' - ' + str(tg_v_task_id) + ': ' + str(task_resp.json().get('message')))
                    else:
                        pass
            except requests.ConnectionError as e:
                message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C: ' + str(tg_v_host) + ': ' + str(e)
                flash(message, 'flash_red')
                stream_logger(message)
                pass


@app.route('/run_out', methods=['GET', 'POST'])
def run_out(): # run all attack and verifier tasks linked to organistation uuid
    error = None
    out_entries = get_out()
    eut_entries = get_eut()
    out_names = out_entries.reset_index().to_dict('records')
    if request.method == 'POST':
        stream_logger('DDV-C_SL: Please wait a few minutes while we run the DDoS Defense Verification Tests...')
        uuid = request.form['out_companyname']
        run_type = request.form['run_type']
        try:
            euts_of_out = eut_entries[eut_entries['eut_companyname_id'] == str(uuid)] #get all eut under out
        except:
            return redirect(url_for('enroll_out'))
        if run_type == 'F': # Run the full set of tests
            stream_logger_clear()
            run_ddv_tg_v_tasks(uuid, euts_of_out)
            run_ddv_tg_a_tasks(uuid, euts_of_out)
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C_SL: Waiting ' + str(ddv_c_cfg.ddv_run_sl_check_delay) + ' seconds before querying Sightline for data'
            flash(message, 'flash_blue')
            stream_logger(message)
            time.sleep(ddv_c_cfg.ddv_run_sl_check_delay)
            ddv_c_sl_api.sl_ddv_run(out_entries[out_entries.index == int(uuid)]['out_sl_ip'].values[0], out_entries[out_entries.index == int(uuid)]['out_sl_api'].values[0], euts_of_out)
            run_ddv_tg_v_tasks(uuid, euts_of_out)
            # Graph snapshot of DDV Full Test
            try:
                graph_data = amd_hierarchy()
                draw_sankey(graph_data)
            except:
                pass
        elif run_type == 'D': # Run only Sightline/AED Deployment Checks
            stream_logger_clear()
            ddv_c_sl_api.sl_ddv_run(out_entries[out_entries.index == int(uuid)]['out_sl_ip'].values[0], out_entries[out_entries.index == int(uuid)]['out_sl_api'].values[0], euts_of_out)
            # Graph snapshot of DDV Full Test
            try:
                graph_data = amd_hierarchy()
                draw_sankey(graph_data)
            except:
                pass
        elif run_type == 'V': # Run only Verifier Tasks
            stream_logger_clear()
            run_ddv_tg_v_tasks(uuid, euts_of_out)
        elif run_type == 'A': # Run only Attack Tasks
            stream_logger_clear()
            run_ddv_tg_a_tasks(uuid, euts_of_out)
        else:
            pass
        out_entries = get_out()
        out_names = out_entries.reset_index().to_dict('records')
    return render_template('run_out.html', error=error, out_names=out_names, data=out_entries.to_html())


@app.route('/sl_config_out', methods=['GET', 'POST'])
def sl_config_out(): # verify all attack and verifier tasks linked to organistation uuid
    stream_logger_clear()
    error = None
    eut_entries = get_eut()
    out_entries = get_out()
    out_names = out_entries.reset_index().to_dict('records')
    if request.method == 'POST':
        uuid = request.form['out_companyname']
        action = request.form['action']
        try:
            eut_list = eut_entries[eut_entries['eut_companyname_id'] == str(uuid)] #get all eut under out
        except:
            error = 'DDV-C: No EuT found.  Please create an EuT and try again.'
            return render_template('sl_config_out.html', error=error, out_names=out_names, data=out_entries.to_html())
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C_SL: Verifying if base configs are on ' + str(out_entries[out_entries.index == int(uuid)]['out_companyname'].values[0]) + ' Sightline'
        flash(message, 'flash_blue')
        stream_logger(message)
        try:
            ddv_c_sl_api.sl_ddv_base_config(action, out_entries[out_entries.index == int(uuid)]['out_sl_ip'].values[0], out_entries[out_entries.index == int(uuid)]['out_sl_api'].values[0], eut_list)
        except:
            error = 'DDV-C: No Sightline/AED IP and/or API details.  Add IP and API details to Organisation Under Test'
        out_entries = get_out()
        out_names = out_entries.reset_index().to_dict('records')
    return render_template('sl_config_out.html', error=error, out_names=out_names, data=out_entries.to_html())


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'flash_blue')
    return redirect(url_for('login'))


def ddv_hierarchy_search(dict_input, dict_key): # ddv_nodes list/dict and key to return values | ex. ddv_nodes, 'color'
    r_dict = {}
    for key in dict_input.keys():
        for i in range(len(dict_input.get(key))):
            if dict_input.get(key)[i].get(dict_key) == None:
                pass
            else:
                #print(key, dict_input.get(key)[i].get(dict_key))
                r_dict[key] = dict_input.get(key)[i].get(dict_key)
    #print(r_dict)
    return r_dict


def ddv_hierarchy():
    out_entries = get_out()
    eut_entries = get_eut()
    agent_entries = get_agents()
    tg_a_task_entries = get_tg_a_tasks()
    tg_v_task_entries = get_tg_v_tasks()
    ddv_nodes = []
    ddv_edges = []
    #1. find all parent OuT
    for out_uuid in out_entries.index:
        out_uuid_name = out_entries[out_entries.index == out_uuid]['out_companyname'].values[0]
        print(out_uuid, out_uuid_name)
        ddv_nodes.append(
                        (int(out_uuid),
                        {
                        'name' : out_uuid_name,
                        'color' : 'paleturquoise',
                        'fixed' : 'fixed',
                        'size' : 10
                        })
                        )
        eut_entries_x_out = eut_entries[eut_entries['eut_companyname_id'] == str(out_uuid)]
        #2. find all child EuT linked to OuT
        for eut_uuid in eut_entries_x_out.index:
            eut_uuid_name = eut_entries[eut_entries.index == eut_uuid]['eut_shortname'].values[0]
            print("  " + str(eut_uuid), str(eut_uuid_name))
            ddv_nodes.append(
                            (int(eut_uuid),
                            {
                            'name' : eut_uuid_name,
                            'color' : 'paleturquoise',
                            'fixed' : None,
                            'size' : 50
                             })
                             )
            ddv_edges.append(
                            (
                            int(eut_uuid),
                            int(out_uuid),
                            {
                            'color' : 'skyblue',
                            'weight' : 2,
                            'label' : 'OuT<>EuT',
                            'pps' : 1
                             })
                             )
            #3a. find all attack tasks (grandchildren) linked to each EuT
            for tg_a_task_entry in tg_a_task_entries[tg_a_task_entries['tg_a_eut_id'] == eut_uuid].index.values:
                tg_a_task_entry_vector = tg_a_task_entries[tg_a_task_entries.index == tg_a_task_entry]['tg_a_dst_vector'].values[0]
                tg_a_task_entry_pps = tg_a_task_entries[tg_a_task_entries.index == tg_a_task_entry]['tg_a_pps'].values[0]
                print("    " + str(tg_a_task_entry), str(tg_a_task_entry_vector), str(tg_a_task_entry_pps))
                #ddv_nodes.append((int(tg_a_task_entry) , {'name' : '', 'color' : 'red', 'fixed' : None, 'size': 200}))
                #ddv_edges.append((int(eut_uuid) , int(tg_a_task_entry), {'color': 'red', 'weight': 8, 'label': str(tg_a_task_entry_vector), 'length' : 10}))
                #4a. find TG-A Agents linked to each attack (great-grandchildren)
                tg_a_task_host_uuid = tg_a_task_entries[tg_a_task_entries.index == tg_a_task_entry]['tg_a_host_id'].values[0]
                tg_a_task_host_name = tg_a_task_entries[tg_a_task_entries.index == tg_a_task_entry]['tg_a_host'].values[0]
                print("      " + str(tg_a_task_host_uuid), str(tg_a_task_host_name))
                ddv_nodes.append(
                                (
                                int(tg_a_task_host_uuid),
                                {
                                'name' : tg_a_task_host_name,
                                'color' : 'red',
                                'fixed' : None,
                                'size' : 20
                                 })
                                 )
                #ddv_edges.append((int(tg_a_task_entry) , int(tg_a_task_host_uuid), {'color': 'red', 'weight': 8}))
                # or
                ddv_edges.append(
                                (
                                int(tg_a_task_host_uuid),
                                int(eut_uuid),
                                {
                                'color' : 'salmon',
                                'weight' : 8,
                                'label' : str(tg_a_task_entry_vector),
                                'pps' : str(tg_a_task_entry_pps)
                                 })
                                 )
            #3b. find all verifier tasks (grandchildren) linked to each EuT
            for tg_v_task_entry in tg_v_task_entries[tg_v_task_entries['tg_v_eut_id'] == eut_uuid].index.values:
                tg_v_task_entry_proto = tg_v_task_entries[tg_v_task_entries.index == tg_v_task_entry]['tg_v_dst_proto'].values[0]
                tg_v_task_entry_pps = tg_v_task_entries[tg_v_task_entries.index == tg_v_task_entry]['tg_v_pps'].values[0]
                print("    " + str(tg_v_task_entry), str(tg_v_task_entry_proto), str(tg_v_task_entry_pps))
                #ddv_nodes.append((int(tg_v_task_entry) , {'name' : '', 'color': 'green', 'fixed' : None, 'size': 200}))
                #ddv_edges.append((int(eut_uuid) , int(tg_v_task_entry), {'color': 'green', 'weight': 4, 'label': str(tg_v_task_entry_proto), 'length' : 10}))
                #4b. find TG-V Agents linked to each attack (great-grandchildren)
                tg_v_task_host_uuid = tg_v_task_entries[tg_v_task_entries.index == tg_v_task_entry]['tg_v_host_id'].values[0]
                tg_v_task_host_name = tg_v_task_entries[tg_v_task_entries.index == tg_v_task_entry]['tg_v_host'].values[0]
                print("      " + str(tg_v_task_host_uuid), str(tg_v_task_host_name))
                ddv_nodes.append(
                                (
                                int(tg_v_task_host_uuid),
                                {
                                'name' : tg_v_task_host_name,
                                'color' : 'green',
                                'fixed' : None,
                                'size' : 20
                                 })
                                 )
                #ddv_edges.append((int(tg_v_task_entry) , int(tg_v_task_host_uuid), {'color': 'green', 'weight': 4}))
                # or
                ddv_edges.append(
                                (
                                int(tg_v_task_host_uuid),
                                int(eut_uuid),
                                {
                                'color' : 'palegreen',
                                'weight' : 4,
                                'label' : str(tg_v_task_entry_proto),
                                'pps' : str(tg_v_task_entry_pps)
                                 })
                                 )
    return ddv_nodes, ddv_edges


def amd_hierarchy():
    amd_entries = get_alert_mit_details()
    ddv_nodes = []
    ddv_edges = []
    #1. find all unique MOs and misuse_types within the active alerts
    for mo_gid in amd_entries['mo_gid']:
        mo_name = amd_entries[amd_entries['mo_gid'] == mo_gid]['mo_name'].values[0]
        misuse_types = amd_entries[amd_entries['mo_gid'] == mo_gid]['misuse_types'].values[0]
        print(mo_gid, mo_name)
        ddv_nodes.append(
                        (int(mo_gid),
                        {
                        'name' : mo_name,
                        'color' : 'paleturquoise',
                        'size': 10
                         })
                        )
        ddv_nodes.append(
                        (str(misuse_types),
                        {
                        'name' : misuse_types,
                        'color' : 'orange',
                        'size': 10
                         })
                        )
    #2. find all hosts under attack for MO for active alert
        host_address = amd_entries[amd_entries['mo_gid'] == mo_gid]['host_address'].values[0]
        impact_pps = amd_entries[amd_entries['mo_gid'] == mo_gid]['impact_pps'].values[0]
        print('  ' + str(host_address))
        ddv_nodes.append(
                        (str(host_address),
                        {'name' : host_address,
                        'color' : 'green',
                        'size': 50
                         })
                        )
        #ddv_edges.append(
        #                (str(host_address), int(mo_gid),
        #                {'color': 'skyblue',
        #                'weight': 2,
        #                'pps': 10
        #                 })
        #                )
    #3. find mitigations linked to MO for active alert
        for alert_gid in list(dict(amd_entries[amd_entries['mo_gid'] == mo_gid]['mitigation_data']).keys()):
            mit_gid = ast.literal_eval(dict(amd_entries[amd_entries['mo_gid'] == mo_gid]['mitigation_data'])[alert_gid])['mit_gid']
            mit_name = ast.literal_eval(dict(amd_entries[amd_entries['mo_gid'] == mo_gid]['mitigation_data'])[alert_gid])['mit_name']
            print('    ' + str(mit_gid), str(mit_name))
            ddv_nodes.append(
                            (str(mit_gid),
                            {'name' : mit_name,
                            'color' : 'paleturquoise',
                            'size': 50
                             })
                            )
    #4. find all countermeasures in use under each mitigation
            mit_cm = ast.literal_eval(dict(amd_entries[amd_entries['mo_gid'] == mo_gid]['mitigation_data'])[alert_gid])['mit_cm']
            if len(mit_cm) != 0: # look for active countermeasures first
                for mit_entry in mit_cm:
                    mit_cm_name = list(mit_entry.keys())[0]
                    if mit_cm_name != 'total': #Don't plot the total stats, which is seen as a CM
                        mit_cm_gid = mit_gid + '_' + mit_cm_name
                        mit_cm_drop_pps = mit_entry[mit_cm_name]['drop']['pps']['current'] #'average'|'current'|'max'|'pct95'
                        mit_cm_drop_bps = mit_entry[mit_cm_name]['drop']['bps']['current']
                        mit_cm_pass_pps = mit_entry[mit_cm_name]['pass']['pps']
                        if type(mit_cm_pass_pps) == dict: # an empty dict {} is returned if nothing is passed to host
                            mit_cm_pass_pps = 1
                        else:
                            pass
                        mit_cm_pass_bps = mit_entry[mit_cm_name]['pass']['bps']
                        if type(mit_cm_pass_bps) == dict:
                            mit_cm_pass_bps = 1
                        else:
                            pass
                        print('      ' + str(mit_cm_gid), str(mit_cm_name), str(mit_cm_drop_pps), str(mit_cm_pass_pps))
                        ddv_nodes.append(
                                        (str(mit_cm_gid),
                                        {
                                        'name' : mit_cm_name,
                                        'color' : 'black',
                                        'size': 50
                                         })
                                        )
                        ddv_edges.append(
                                        (int(mo_gid), str(mit_cm_gid),
                                        {
                                        'color': 'palegreen',
                                        'weight': 2,
                                        'label' : 'allowed_traffic',
                                        'pps': mit_cm_pass_pps
                                         })
                                         )
                        ddv_edges.append(
                                        (str(mit_cm_gid), str(mit_gid),
                                        {
                                        'color': 'salmon',
                                        'weight': 2,
                                        'label' : 'attack_traffic',
                                        'pps': mit_cm_drop_pps + 1 # adding 1 just in case drop is 0
                                         })
                                         )
                    else: # get total stats from "total" cm
                        mit_total_pass_pps = mit_entry[mit_cm_name]['pass']['pps']['current']
                        mit_total_drop_pps = mit_entry[mit_cm_name]['drop']['pps']['current']
                        mit_cm_gid = mit_gid + '_' + mit_cm_name
                        ddv_nodes.append(
                                        (str(mit_cm_gid),
                                        {
                                        'name' : 'total_passed',
                                        'color' : 'green',
                                        'size': 50
                                         })
                                        )
                        ddv_edges.append(
                                        (str(mit_cm_gid), str(mit_gid),
                                        {'color': 'palegreen',
                                        'weight': 2,
                                        'label' : 'allowed_traffic',
                                        'pps': mit_total_pass_pps
                                         })
                                        )
                        ddv_edges.append(
                                        (int(mo_gid), str(mit_cm_gid),
                                        {'color': 'palegreen',
                                        'weight': 2,
                                        'label' : 'allowed_traffic',
                                        'pps': mit_total_pass_pps
                                         })
                                        )
                        ddv_edges.append(
                                        (str(host_address), int(mo_gid),
                                        {'color': 'palegreen',
                                        'weight': 2,
                                        'label' : 'allowed_traffic',
                                        'pps': mit_total_pass_pps
                                         })
                                        )
        #5. find all source prefixes and rates within active alert
                for source_prefix_entry in ast.literal_eval(dict(amd_entries[amd_entries['mo_gid'] == mo_gid]['source_prefixes'])[alert_gid]):
                    src_pfx = source_prefix_entry['name']
                    src_pfx_gid = mit_gid + '_' + src_pfx
                    src_pfx_pps = source_prefix_entry['current_value']
                    print('      ' + str(src_pfx_gid), str(src_pfx), str(src_pfx_pps))
                    ddv_nodes.append(
                                    (str(src_pfx_gid),
                                    {
                                    'name' : src_pfx,
                                    'color' : 'red',
                                    'size': 50
                                     })
                                    )
                    ddv_edges.append(
                                    (str(mit_gid), str(misuse_types),
                                    {
                                    'color': 'salmon',
                                    'weight': 2,
                                    'label' : 'attack_traffic',
                                    'pps': src_pfx_pps
                                     })
                                    )
                    ddv_edges.append(
                                    (str(misuse_types), str(src_pfx_gid),
                                    {
                                    'color': 'salmon',
                                    'weight': 2,
                                    'label' : 'attack_traffic',
                                    'pps': src_pfx_pps
                                     })
                                    )
            else:
                pass
    #5. find all source prefixes and rates within active alert, where there are no active countermeasures on tms mitigation
                for source_prefix_entry in ast.literal_eval(dict(amd_entries[amd_entries['mo_gid'] == mo_gid]['source_prefixes'])[alert_gid]):
                    src_pfx = source_prefix_entry['name']
                    src_pfx_gid = mit_gid + '_' + src_pfx
                    src_pfx_pps = source_prefix_entry['current_value']
                    print('      ' + str(src_pfx_gid), str(src_pfx), str(src_pfx_pps))
                    ddv_nodes.append(
                                    (str(src_pfx_gid),
                                    {
                                    'name' : src_pfx,
                                    'color' : 'red',
                                    'size': 50
                                     })
                                    )
                    ddv_edges.append(
                                    (int(mo_gid), str(mit_gid),
                                    {
                                    'color': 'salmon',
                                    'weight': 2,
                                    'label' : 'attack_traffic',
                                    'pps': 1
                                     })
                                     )
                    ddv_edges.append(
                                    (str(mit_gid), str(misuse_types),
                                    {
                                    'color': 'salmon',
                                    'weight': 2,
                                    'label' : 'attack_traffic',
                                    'pps': src_pfx_pps
                                     })
                                    )
                    ddv_edges.append(
                                    (str(misuse_types), str(src_pfx_gid),
                                    {
                                    'color': 'salmon',
                                    'weight': 2,
                                    'label' : 'attack_traffic',
                                    'pps': src_pfx_pps
                                     })
                                    )
    return ddv_nodes, ddv_edges
    


@app.route('/hierarchy_draw_network')
def ddv_hierarchy_draw_network():
    #G = nx.Graph()
    G = nx.MultiDiGraph()
    graph_data = ddv_hierarchy()
    ddv_nodes = graph_data[0] #get only nodes
    ddv_edges = graph_data[1] #get only edges
    # Generate Graphs
    #1. Add nodes
    G.add_nodes_from(ddv_nodes)
    #2. Add Edges
    G.add_edges_from(ddv_edges)
    #3. draw Graph
    #pos = nx.spring_layout(
    #                        G,
                            #fixed=ddv_nodes_fixed
                            #scale = 2,
                            #seed = 84,
    #                        k = 0.3,
    #                        iterations = 20
    #                        )
    pos = nx.circular_layout(G)
    #pos = nx.random_layout(G)
    #pos[1604578336] = np.array([0, 0])
    nx.draw(
                    G,
                    pos,
                    labels = nx.get_node_attributes(G,'name'),
                    node_color = list(nx.get_node_attributes(G,'color').values()),
                    node_size = list(nx.get_node_attributes(G,'size').values()),
                    node_shape = 'o',
                    edge_color = nx.get_edge_attributes(G,'color').values(),
                    #width = list(nx.get_edge_attributes(G,'weight').values()),
                    font_size = 8,
                    connectionstyle='arc3, rad = 0.2'
                    )
    nx.draw_networkx_edge_labels(
                                G,
                                pos,
                                #edge_labels=nx.get_edge_attributes(G,'label'),
                                font_size = 6
                                )
    #nx.draw_networkx_edges(
    #                        G,
    #                        pos,
    #                        connectionstyle='arc3, rad = 0.2'
    #                        )
    dyn_file = './static/images/ddv-hierarchy' + str(int(time.time())) + '.png'
    plt.pyplot.axis('off')
    plt.pyplot.savefig(dyn_file)
    plt.pyplot.clf() # clear plt data, otherwise it keeps on adding over previous data
    G.clear()
    return render_template('draw_hierarchy.html', name = 'ddv-hierarchy', file = dyn_file)


@app.route('/draw_out')
def ddv_hierarchy_draw_out_sankey():
    graph_data = ddv_hierarchy()
    draw_sankey(graph_data)
    draw_network(graph_data)
    return redirect(url_for('out_status'))

@app.route('/draw_sankey')
def draw_sankey(graph_data):
    G = nx.MultiDiGraph() #'MultiDi' is required to stop edge pairs from being order low to high, and draw more than one edge per node pair
    the_nodes = graph_data[0] #get only nodes
    the_edges = graph_data[1] #get only edges
    #1. Add nodes
    G.add_nodes_from(the_nodes)
    #2. Add Edges
    G.add_edges_from(the_edges)
    #3. sort edges/link into seperate lists for source and target nodes, based in nodes indices
    source_list = []
    target_list = []
    for edge in list(G.edges()):
        source = list(G.nodes()).index((edge)[0])
        source_list.append(source)
        target = list(G.nodes()).index((edge)[1])
        target_list.append(target)
    #4. build sankey diagram
    #print(list(nx.get_node_attributes(G,'name').values()))
    #print(source_list)
    #print(list(nx.get_edge_attributes(G,'label').values()))
    #print(target_list)
    fig = go.Figure(data=[go.Sankey(
        #arrangement = "snap",
        node = dict(
          pad = 15,
          thickness = 15,
          line = dict(color = "black", width = 0.5),
          label = list(nx.get_node_attributes(G,'name').values()),
          color = list(nx.get_node_attributes(G,'color').values()),
          customdata = list(nx.get_node_attributes(G,'name').values()),
          hovertemplate='Node %{customdata} has total value %{value} pps<extra></extra>',
        ),
        link = dict(
          source = source_list, # indices correspond to labels
          target = target_list,
          color = list(nx.get_edge_attributes(G,'color').values()),
          #label = list(nx.get_edge_attributes(G,'label').values()),
          value = list(nx.get_edge_attributes(G,'pps').values()),
          customdata = list(nx.get_edge_attributes(G,'label').values()),
          hovertemplate='%{source.customdata}<br />'+
            'sending %{value} pps of %{customdata} to<br />'+
            '%{target.customdata}<br />'+
            '<extra></extra>',
      ))])
    fig.update_layout(title_text="DDV Hierarchy View", font_size=12)
    fig.show()
    
    
@app.route('/draw_network')
def draw_network(graph_data):
    G = nx.MultiDiGraph()
    #graph_data = ddv_hierarchy()
    ddv_nodes = graph_data[0] #get only nodes
    ddv_edges = graph_data[1] #get only edges
    #1. Add nodes
    G.add_nodes_from(ddv_nodes)
    #2. Add Edges
    G.add_edges_from(ddv_edges)
    #Layout
    pos = nx.shell_layout(G)
    #pos = nx.spring_layout(G)
    #pos = nx.random_layout(G)
    #pos = nx.circular_layout(G)
    #Create Edges
    edge_x = []
    edge_y = []
    xtext = [] #text position on pos
    ytext = [] #text position on pos
    edge_trace = [] #needed to append colors and weights
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        xtext.append((x0+x1)/2) #get halfway point between
        ytext.append((y0+y1)/2) #get halfway point between
        edge_x.append(list((x0, x1, None)))
        edge_y.append(list((y0, y1, None)))
        edge_trace.append(go.Scatter(
            x=list((x0, x1, None)), y=list((y0, y1, None)),
            #line=dict(width=0.5, color='#888'),
            line=dict(
                width=nx.get_edge_attributes(G,'weight')[(edge[0], edge[1], 0)],
                color=nx.get_edge_attributes(G,'color')[(edge[0], edge[1], 0)]
                ),
            hoverinfo='none',
            mode='lines'))
    elabels_trace = go.Scatter(
        x=xtext, y=ytext,
        mode='text',
        marker_size=0.5,
        text=list(nx.get_edge_attributes(G,'label').values()),
        textposition='top center',
        hovertemplate='%{text}<extra></extra>')
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            #showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Greens',
            #reversescale=True,
            size=list(nx.get_node_attributes(G,'size').values()),
            #color=list(nx.get_node_attributes(G,'color').values()),
            #colorbar=dict(
            #    thickness=15,
            #    title='Node Connections',
            #    xanchor='left',
            #    titleside='right'
            #),
            line_width=2
                )
            )
    #print(node_trace)
    nlabels_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='text',
        marker_size=0.5,
        text=list(nx.get_node_attributes(G,'name').values()),
        # textposition='top center',
        hovertemplate='node: %{text}<extra></extra>')
    #Color Node Points
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    #Create Network Graph
    #fig = go.Figure(data=[edge_trace, elabels_trace, node_trace, nlabels_trace],
    fig = go.Figure(data = edge_trace + [elabels_trace, node_trace, nlabels_trace],
                 layout=go.Layout(
                    title='<br>DDV Network graph',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()



def vps_tg_x_provision(n_servers): #number of desired vps servers
    # Clear stream logger file first
    stream_logger_clear()
    # Do we have any VPS servers running?
    if len(vps.serverlist()) != 0:
        stream_logger(str(len(vps.serverlist())) + ' active VPS servers under your profile')
    else:
        stream_logger(str(len(vps.serverlist())) + ' active VPS servers under your profile')
    # Which Plans are available and in which Regions
    #print(vps.planlist())
    # Choose cheapest plan, and get a list of regions
    plans = vps.planlist()
    plan_dict = {}
    for plan in plans:
        plans[plan]['VPSPLANID'], plans[plan]['price_per_month']
        plan_dict[plans[plan]['VPSPLANID']] = Decimal(plans[plan]['price_per_month'])
    cheapest_plan = plans[min(plan_dict, key=plan_dict.get)]
    stream_logger('Cheapest Plan: ' + str(cheapest_plan))
    # get list of availble locations for the cheapest plan
    regions = vps.regionlist()
    for region_id in cheapest_plan['available_locations']:
        print(regions[str(region_id)])
    # Create desired number of VPS servers across a random selection of regions
    subid_list = []
    if len(cheapest_plan['available_locations']) < n_servers:
        n_servers = len(cheapest_plan['available_locations']) # Can't request more servers than there are avaialble
    for r_region_id in random.sample(cheapest_plan['available_locations'], n_servers):
        vps_id = vps.create([r_region_id, cheapest_plan['VPSPLANID'], '413', '0', '', '', str(regions[str(r_region_id)]['regioncode']) + '-DDV-TG-x', 'DDV-TG-x node in ' + str(regions[str(r_region_id)]['regioncode'])])
        subid_list.append(vps_id) # Each create request results in a unique ID per VPS
    #print(subid_list)
    vps_list = []
    for subid in subid_list: #check on provisioning state of each vps before provisioning via SSH/SCP
        #print(vps.getstatus([subid]))
        while vps.getstatus([subid])['server_state'] != 'ok':
            time.sleep(15)
            line = 'VPS Server ID: ' + str(subid) + ' provisioning status: ' + str(vps.getstatus([subid])['server_state']) + ', please wait to complete...'
            #print(line)
            stream_logger(line)
        stream_logger('VPS with ID: ' + str(subid) + ' fully provisioned and ready for further configuration...')
        vps_list.append(vps.getstatus([subid]))
    #print(vps_list)
    return vps_list


def vps_tg_x_configure(vps_list): #SSH and SCP to VPSs and get them up and running as DDV-TG-x (Attackers and Verifiers)
    for vps_server in vps_list:
        # install all required packages
        stream_logger('VPS Server: installing required packages and DDV-TG-x scripts. This may take a while, check TG-Agents > Status')
        commands = [
            'apt-get update -y',
            'apt install python3-pip -y',
            'pip3 install flask pandas requests pyopenssl',
            'pip3 install --pre scapy[basic]',
            ]
        for cmd in commands:
            ssh_client(vps_server['main_ip'], 'root', vps_server['default_password'], cmd)
        # transfer scripts
        ssh_scp_files(vps_server['main_ip'], 'root', vps_server['default_password'], 22, 'ddv-tg-x', '/root')
        # start ddv-tg-x scripts as A and V
        ddv_commands = [
                "cd /root/ddv-tg-x; screen -dmS DDV-TG-A; screen -S DDV-TG-A -p 0 -X stuff 'python3 /root/./ddv-tg-x/ddv-tg-x.py -r A\n'",
                "cd /root/ddv-tg-x; screen -dmS DDV-TG-V; screen -S DDV-TG-V -p 0 -X stuff 'python3 /root/./ddv-tg-x/ddv-tg-x.py -r V\n'",
                ]
        for ddv_cmd in ddv_commands:
            ssh_client(vps_server['main_ip'], 'root', vps_server['default_password'], ddv_cmd)
    # Auto Enroll new VPS agents into DDV-Console as both Attackers and Verifiers, remotely as well as into DDV-C
    stream_logger_clear()
    enroll_vps_agents(vps_list)

def vps_tg_x_kill_all():
    stream_logger_clear()
    vps_list = list(vps.serverlist().keys()) # fetch a list of all active VPSs
    # delete DDV-C Agents and associated tasks
    for vps_subid in vps_list:
        try:
            vps_uuids = [int('99' + str(vps_subid) + '99'), int('88' + str(vps_subid) + '88')]
            delete_vps_agents(vps_uuids)
        except:
            pass
    # list all VPSs and destroy
    vps.kill(vps_list)


def ssh_client(server, username, password, cmd_to_execute):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    #ssh_stdin.write('lol\n')
    #stdin.flush()
    #print(ssh_stdout.read())
    data = ssh_stdout.read().splitlines()
    for line in data:
        print(line)
        #stream_logger(line)
    ssh.close()


def ssh_scp_files(ssh_host, ssh_user, ssh_password, ssh_port, source_volume, destination_volume): # SSH/SCP Directory Recursively
    ssh = paramiko.SSHClient()
    #ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, password=ssh_password, look_for_keys=False)
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(source_volume, recursive=True, remote_path=destination_volume)



if __name__ == '__main__':
    app.run(host=ddv_c_cfg.my_ip, port=ddv_c_cfg.ddv_c_web_port, debug=True, ssl_context='adhoc')
