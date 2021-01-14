# Python version 2:
# sudo pip install flask (or apt-get install python-flask)
# sudo pip install pandas (or apt-get install python-pandas)
# sudo pip install requests (or apt-get install python-requests)
# sudo pip install --pre scapy[basic]
# sudo pip install pyopenssl
# Python version 3:
# sudo pip3 install flask (or apt-get install python3-flask)
# sudo pip3 install pandas (or apt-get install python3-pandas)
# sudo pip3 install requests (or apt-get install python3-requests)
# sudo pip3 install --pre scapy[basic]
# sudo pip3 install pyopenssl
#
from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, render_template, flash
from datetime import datetime
from multiprocessing import Process, Value, current_process
import pandas as pd
import time, sys, json, requests, os, argparse, ddv_tg_x_scapy, ddv_tg_cfg
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='development key', USERNAME='admin', PASSWORD='ddv'))


def get_tg_v_tasks():
    try:
        tg_v_list_df = pd.read_csv(ddv_tg_cfg.ddv_tg_v_task_filename, names=[
                                                                'tg_v_enrollment_id',
                                                                'tg_v_eut',
                                                                'tg_v_eut_id',
                                                                'tg_v_host',
                                                                'tg_v_host_id',
                                                                'tg_v_host_ip',
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
        tg_a_list_df = pd.read_csv(ddv_tg_cfg.ddv_tg_a_task_filename, names=[
                                                                'tg_a_enrollment_id',
                                                                'tg_a_eut',
                                                                'tg_a_eut_id',
                                                                'tg_a_host',
                                                                'tg_a_host_id',
                                                                'tg_a_host_ip',
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

        
        
        
def tg_a_task_pid(action, uuid, pid): #get_pid|put_uuid|del_uuid, uuid, pid
    try:
        if action == 'get_pid':
            tg_a_task_pid_df = pd.read_csv(ddv_tg_cfg.ddv_tg_a_task_pid_filename, names=[
                                                                    'uuid',
                                                                    'pid'
                                                                    ], header=None)
            return tg_a_task_pid_df[tg_a_task_pid_df['uuid'] == uuid]['pid'].values[0]
        elif action == 'put_uuid':
            uuid_pid_list = []
            uuid_pid_list_entry = {
                                    'uuid': uuid,
                                    'pid': pid
                                }
            uuid_pid_list.append(uuid_pid_list_entry)
            uuid_pid_list_df = pd.DataFrame.from_dict(uuid_pid_list)
            uuid_pid_list_df.to_csv(ddv_tg_cfg.ddv_tg_a_task_pid_filename, mode='a', header=False, columns=[
                                                                                                'uuid',
                                                                                                'pid'
                                                                                                ])
            return 1
        elif action == 'del_uuid':
            tg_a_task_pid_df = pd.read_csv(ddv_tg_cfg.ddv_tg_a_task_pid_filename, names=[
                                                                    'uuid',
                                                                    'pid'
                                                                    ], header=None)
            tg_a_task_pid_df[tg_a_task_pid_df.uuid != uuid].to_csv(ddv_tg_cfg.ddv_tg_a_task_pid_filename, mode='w', header=False, columns=[
                                                                                                                       'uuid',
                                                                                                                       'pid'
                                                                                                                       ])
            return 1
    except:
        return -1
        #pass
        
        

def tg_v_task_pid(action, uuid, pid): #get_pid|put_uuid|del_uuid, uuid, pid
    try:
        if action == 'get_pid':
            tg_v_task_pid_df = pd.read_csv(ddv_tg_cfg.ddv_tg_v_task_pid_filename, names=[
                                                                    'uuid',
                                                                    'pid'
                                                                    ], header=None)
            return tg_v_task_pid_df[tg_v_task_pid_df['uuid'] == uuid]['pid'].values[0]
        elif action == 'put_uuid':
            uuid_pid_list = []
            uuid_pid_list_entry = {
                                    'uuid': uuid,
                                    'pid': pid
                                }
            uuid_pid_list.append(uuid_pid_list_entry)
            uuid_pid_list_df = pd.DataFrame.from_dict(uuid_pid_list)
            uuid_pid_list_df.to_csv(ddv_tg_cfg.ddv_tg_v_task_pid_filename, mode='a', header=False, columns=[
                                                                                                'uuid',
                                                                                                'pid'
                                                                                                ])
            return 1
        elif action == 'del_uuid':
            tg_v_task_pid_df = pd.read_csv(ddv_tg_cfg.ddv_tg_v_task_pid_filename, names=[
                                                                    'uuid',
                                                                    'pid'
                                                                    ], header=None)
            tg_v_task_pid_df[tg_v_task_pid_df.uuid != uuid].to_csv(ddv_tg_cfg.ddv_tg_v_task_pid_filename, mode='w', header=False, columns=[
                                                                                                                       'uuid',
                                                                                                                       'pid'
                                                                                                                       ])
            return 1
    except:
        return -1
        #pass


def get_tg_v_enroll_data():
    try:
        tg_v_enroll_data_df = pd.read_csv(ddv_tg_cfg.ddv_v_enrollment_filename, names=[
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
                                                                            ], header=None)
        tg_v_enroll_data_df.set_index('agent_enrollment_id', inplace=True)
        return tg_v_enroll_data_df
    except:
        tg_v_enroll_data_df = pd.DataFrame([['empty']], index=['error'], columns=['error'])
        return tg_v_enroll_data_df


def get_tg_a_enroll_data():
    try:
        tg_a_enroll_data_df = pd.read_csv(ddv_tg_cfg.ddv_a_enrollment_filename, names=[
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
                                                                            ], header=None)
        tg_a_enroll_data_df.set_index('agent_enrollment_id', inplace=True)
        return tg_a_enroll_data_df
    except:
        tg_a_enroll_data_df = pd.DataFrame([['empty']], index=['error'], columns=['error'])
        return tg_a_enroll_data_df


def get_tg_x_hostname():
    try:
        if args.role == 'V':
            return get_tg_v_enroll_data()['agent_hostname'].values[0]
        elif args.role == 'A':
            return get_tg_a_enroll_data()['agent_hostname'].values[0]
    except:
        return 'unset'

@app.route('/remote_agent_enroll/<uuid>', methods=['POST'])
def remote_agent_enroll(uuid):
    if (os.path.exists(ddv_tg_cfg.ddv_v_enrollment_filename) and args.role == 'V'):
        return jsonify(
        {'enrollment': 'failed',
         'error': str(get_tg_x_hostname()) + ': ddv-tg-v agent already enrolled'
        }
        )
    elif (os.path.exists(ddv_tg_cfg.ddv_a_enrollment_filename) and args.role == 'A'):
        return jsonify(
        {'enrollment': 'failed',
         'error': str(get_tg_x_hostname()) + ': ddv-tg-a agent already enrolled'
        }
        )
    else:
        try:
            if args.role == 'V':
                ddv_x_enrollment_filename = ddv_tg_cfg.ddv_v_enrollment_filename
            if args.role == 'A':
                ddv_x_enrollment_filename = ddv_tg_cfg.ddv_a_enrollment_filename
            content = request.json
            agent_enrollment_id = content['agent_enrollment_id']
            agent_hostname = content['agent_hostname']
            agent_ip = content['agent_ip']
            agent_port = content['agent_port']
            agent_location = content['agent_location']
            agent_description = content['agent_description']
            agent_role = content['agent_role']
            agent_local_api_key = content['agent_local_api_key']
            agent_remote_api_key = content['agent_remote_api_key']
            agent_enrollment_date = content['agent_enrollment_date']
            enrollment_history = []
            agent_list = []
            agent_list_entry = {
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
            agent_list.append(agent_list_entry)
            agent_list_df = pd.DataFrame.from_dict(agent_list)
            agent_list_df.set_index('agent_enrollment_id', inplace=True)
            #print(agent_list_df)
            agent_list_df.to_csv(ddv_x_enrollment_filename, mode='w', header=False, columns=[
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
            return jsonify(
                           {'enrollment': 'success',
                            'agent_hostname': agent_hostname,
                            'enrollment_id': agent_enrollment_id
                           }
                           )
        except:
            return jsonify(
                           {'enrollment': 'failed',
                            'enrollment_id': uuid
                           }
                           )

@app.route('/remote_tg_v_task_push/<uuid>', methods=['POST'])
def remote_tg_v_task_push(uuid):
    content = request.json
    try:
        tg_v_tasks_entries = get_tg_v_tasks()
        if ((tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)].index.values[0] == int(uuid)) and (args.role == 'V')):
            tg_v_task_delete(uuid) # delete and overwrite the existing task
            result = tg_v_task_write(content)
            return result
    except:
        #e = sys.exc_info()[0]
        #print('Error: ' + str(e))
        pass
        result = tg_v_task_write(content)
        return result
        
def tg_v_task_write(content):
        try:
            tg_v_enrollment_id = content['tg_v_enrollment_id']
            tg_v_eut = content['tg_v_eut']
            tg_v_eut_id = content['tg_v_eut_id']
            tg_v_host = content['tg_v_host']
            tg_v_host_id = content['tg_v_host_id']
            tg_v_host_ip = content['tg_v_host_ip']
            tg_v_src_ip = content['tg_v_src_ip']
            tg_v_dst_ip = content['tg_v_dst_ip']
            tg_v_dst_proto = content['tg_v_dst_proto']
            tg_v_pps = content['tg_v_pps']
            tg_v_dur = content['tg_v_dur']
            tg_v_p_cnt = content['tg_v_p_cnt']
            tg_v_p_int = content['tg_v_p_int']
            tg_v_description = content['tg_v_description']
            tg_v_enrollment_date = content['tg_v_enrollment_date']
            tg_v_status = content['tg_v_status']
            tg_v_list = []
            tg_v_list_entry = {
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
            tg_v_list.append(tg_v_list_entry)
            tg_v_list_df = pd.DataFrame.from_dict(tg_v_list)
            tg_v_list_df.set_index('tg_v_enrollment_id', inplace=True)
            #print(tg_v_list_df)
            tg_v_list_df.to_csv(ddv_tg_cfg.ddv_tg_v_task_filename, mode='a', header=False, columns=[
                                                                                        #'tg_v_enrollment_id',
                                                                                        'tg_v_eut',
                                                                                        'tg_v_eut_id',
                                                                                        'tg_v_host',
                                                                                        'tg_v_host_id',
                                                                                        'tg_v_host_ip',
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
            return jsonify(
                           {'enrollment': 'success',
                            'tg_v_eut': tg_v_eut,
                            'enrollment_id': tg_v_enrollment_id,
                            'message': str(tg_v_host) + ': ' + str(tg_v_eut) + ' ddv-tg-v task successfully updated'
                           }
                           )
        except:
            return jsonify(
                           {'enrollment': 'failed',
                            'enrollment_id': tg_v_enrollment_id
                           }
                           )
                           
@app.route('/remote_tg_v_task_delete/<uuid>', methods=['GET'])
def remote_tg_v_task_delete(uuid):
    try:
        # Check if we have an entry for this uuid in task list
        tg_v_tasks_entries = get_tg_v_tasks()
        if ((int(tg_v_tasks_entries[tg_v_tasks_entries.index == int(uuid)].index.values[0]) == int(uuid)) and (args.role == 'V')):
            tg_v_task_delete(uuid)
            return jsonify(
                {'action': 'success',
                'message': str(get_tg_x_hostname()) + ': ddv-tg-v task ' + str(uuid) + ' successfully deleted'
                }
                )
        else:
            return jsonify(
            {'action': 'failed',
             'error': str(get_tg_x_hostname()) + ': ddv-tg-v task does not exist'
            }
            )
    except:
        #e = sys.exc_info()[0]
        #return 'Error: ' + str(e)
        return jsonify(
        {'action': 'failed',
         'error': str(get_tg_x_hostname()) + ': ddv-tg-v task does not exist'
        }
        )

def tg_v_task_delete(uuid):
    tg_v_tasks_entries = get_tg_v_tasks()
    tg_v_tasks_entries.drop(index=int(uuid)).to_csv(ddv_tg_cfg.ddv_tg_v_task_filename, mode='w', header=False, columns=[
                                                                                  #'tg_v_enrollment_id',
                                                                                  'tg_v_eut',
                                                                                  'tg_v_eut_id',
                                                                                  'tg_v_host',
                                                                                  'tg_v_host_id',
                                                                                  'tg_v_host_ip',
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

@app.route('/ddv_tg_v_tasks_action/<action>', methods=['GET']) # action = start|stop
def ddv_tg_v_tasks_action(action):
    global ddv_v_tasks_loop_p
    try:
        if ((action == 'start') and (ddv_v_tasks_loop_p.is_alive() == False)):
            ddv_v_tasks_loop_p.start()
            return jsonify(
                            {'action': 'started',
                             'message': str(get_tg_x_hostname()) + ': all ddv-tg-v tasks are now running'
                            }
                            )
        elif ((action == 'start') and (ddv_v_tasks_loop_p.is_alive() == True)):
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': all ddv-tg-v tasks already running'
                            }
                            )
        elif action == 'status':
            status = str(ddv_v_tasks_loop_p.is_alive())
            return jsonify(
                            {'running': str(status),
                            'message': str(get_tg_x_hostname()) + ': all ddv-tg-v tasks is running'
                            }
                            )
        elif ((action == 'stop') and (ddv_v_tasks_loop_p.is_alive() == True)):
            ddv_v_tasks_loop_p.terminate()
            return jsonify(
                            {'action': 'stopped',
                             'message': str(get_tg_x_hostname()) + ': all ddv-tg-v tasks are now stopped'
                            }
                            )
        elif ((action == 'stop') and (ddv_v_tasks_loop_p.is_alive() == False)):
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': all ddv-tg-v tasks already stopped'
                            }
                            )
        else:
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': General Error in Action'
                            }
                            )
    except AssertionError as error:
        if action == 'start':
            #global ddv_v_tasks_loop_p
            ddv_v_tasks_loop_p = Process(target=ddv_v_tasks_loop, args=(looping_on,))
            ddv_v_tasks_loop_p.start()
            return jsonify(
                            {'action': 'started',
                             'message': str(get_tg_x_hostname()) + ': all ddv-tg-v tasks are now running'
                            }
                            )
        else:
            return "AssertionError"

def ddv_v_tasks_loop(loop_on):
    #try:
        #while action == 'start':
    while True:
        if loop_on.value == True:
            #print(loop_on.value)
            print("DDV-TG-V: Running Verifier Tasks")
            tg_v_tasks_entries = get_tg_v_tasks()
            tg_v_active_tasks = tg_v_tasks_entries[tg_v_tasks_entries['tg_v_status'] == 'A'] # Only run Active Tasks
            for index in tg_v_active_tasks.index:
                uuid = index
                tg_v_eut = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_eut'].values[0])
                tg_v_eut_id = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_eut_id'].values[0])
                tg_v_host = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_host'].values[0])
                tg_v_src_ip = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_src_ip'].values[0])
                tg_v_dst_ip = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_dst_ip'].values[0])
                tg_v_dst_proto = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_dst_proto'].values[0])
                tg_v_p_cnt = int(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_p_cnt'].values[0])
                tg_v_p_int = float(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_p_int'].values[0])
                if tg_v_dst_proto == 'icmp':
                    ddv_tg_x_scapy.icmp_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                elif tg_v_dst_proto == 'http':
                    tg_v_dst_proto = 80
                    #print(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                    ddv_tg_x_scapy.tcp_syn_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                elif tg_v_dst_proto == 'https':
                    tg_v_dst_proto = 443
                    #print(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                    ddv_tg_x_scapy.tcp_syn_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                elif tg_v_dst_proto == 'dns':
                    tg_v_dst_proto = 53
                    #print(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                    ddv_tg_x_scapy.udp_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                else:
                    return "DDV-TG-V: No Tasks to run"
                    pass
            time.sleep(ddv_tg_cfg.ddv_tg_v_tasks_run_int)
    #except:
    #    e = sys.exc_info()[0]
    #    return 'Error: ' + str(e)
    #return "DDV-TG-V: All Verifier Tasks Stopped"
    
    
@app.route('/ddv_tg_v_task_run/<uuid>/<action>', methods=['GET']) # action is start|status|stop
def ddv_tg_v_task_run(uuid, action):
    global ddv_tg_v_task_spawn_p
    uuid = int(uuid)
    tg_v_tasks_entries = get_tg_v_tasks()
    try:
        tg_v_eut = str(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_eut'].values[0])
        tg_v_eut_id = str(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_eut_id'].values[0])
        tg_v_host = str(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_host'].values[0])
        tg_v_src_ip = str(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_src_ip'].values[0])
        tg_v_dst_ip = str(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_dst_ip'].values[0])
        tg_v_dst_proto = str(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_dst_proto'].values[0])
        tg_v_p_cnt = int(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_p_cnt'].values[0])
        tg_v_p_int = float(tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_p_int'].values[0])
    except:
        return jsonify(
        {'action': 'invalid',
         'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', does not exist'
        }
        )
    uid = 'ddv_tg_v_task_' + str(uuid)
    try:
        try:
            # need to ensure we only set Process once
            type(ddv_tg_v_task_spawn_p)
        except NameError:
            #global ddv_tg_v_task_spawn_p
            ddv_tg_v_task_spawn_p = Process(name=uid, target=ddv_tg_v_task_run_spawn, args=(uuid,))
        status = tg_v_task_pid('get_pid', int(uuid), 0) # check if running pid exists for task uuid
        if ((action == 'start') and (status < 0)): # no pid found
            ddv_tg_v_task_spawn_p.start()
            tg_v_task_pid('del_uuid', int(uuid), 0)
            tg_v_task_pid('put_uuid', int(uuid), int(ddv_tg_v_task_spawn_p.pid))
            return jsonify(
                            {'action': 'started',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', started',
                             'detail': str(tg_v_host) + ': ddv-tg-v task, ' + str(uuid) + ', sending ' + str(tg_v_dst_proto) + ' to ' + str(tg_v_eut) + ', ' + str(tg_v_dst_ip),
                             'state': 'running'
                            }
                            )
        elif ((action == 'start') and (status > 0)):
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', already running',
                             'state': 'running'
                            }
                            )
        elif action == 'result':
                ddv_tg_v_task_spawn_p.join()
                return jsonify(
                                {'running_pid': str(status),
                                'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', completed',
                                'metric': str(ddv_tg_v_task_spawn_p.exitcode), # using exitcode to get success metric from spawn
                                'state': 'idle'
                                }
                                )
        elif action == 'status':
            if status > 0:
                return jsonify(
                                {'running_pid': str(status),
                                'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', is running',
                                'state': 'running'
                                }
                                )
            elif status < 0:
                return jsonify(
                                {'running_pid': str(status),
                                'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', not running',
                                'state': 'idle'
                                }
                                )
        elif ((action == 'stop') and (status > 0)):
            ddv_tg_v_task_spawn_p.terminate()
            tg_v_task_pid('del_uuid', int(uuid), 0)
            return jsonify(
                            {'action': 'stopped',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', stopped',
                             'state': 'idle'
                            }
                            )
        elif ((action == 'stop') and (status < 0)):
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', not running',
                             'state': 'idle'
                            }
                            )
        else:
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': General Error in Action',
                             'state': 'failed'
                            }
                            )
    except AssertionError as error:
        if action == 'start':
            #global ddv_tg_v_task_spawn_p
            ddv_tg_v_task_spawn_p = Process(name=uid, target=ddv_tg_v_task_run_spawn, args=(uuid,))
            ddv_tg_v_task_spawn_p.start()
            tg_v_task_pid('del_uuid', int(uuid), 0)
            tg_v_task_pid('put_uuid', int(uuid), int(ddv_tg_v_task_spawn_p.pid))
            return jsonify(
                            {'action': 'started',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-v task, ' + str(uuid) + ', started',
                             'detail': str(tg_v_host) + ': ddv-tg-v task, ' + str(uuid) + ', sending ' + str(tg_v_dst_proto) + ' to ' + str(tg_v_eut) + ', ' + str(tg_v_dst_ip),
                             'state': 'running'
                            }
                            )
        else:
            return "AssertionError"
    
def ddv_tg_v_task_run_spawn(uuid): # multiprocessor worker
    name = current_process().name
    print(name, 'Starting')
    tg_v_tasks_entries = get_tg_v_tasks()
    #tg_v_active_tasks = tg_v_tasks_entries[tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]['tg_v_status'] == 'V'] # Only run Active Tasks
    tg_v_active_tasks = tg_v_tasks_entries[tg_v_tasks_entries.index == uuid]
    try:
        for index in tg_v_active_tasks.index:
            tg_v_eut = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_eut'].values[0])
            tg_v_eut_id = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_eut_id'].values[0])
            tg_v_host = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_host'].values[0])
            tg_v_src_ip = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_src_ip'].values[0])
            tg_v_dst_ip = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_dst_ip'].values[0])
            tg_v_dst_proto = str(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_dst_proto'].values[0])
            tg_v_p_cnt = int(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_p_cnt'].values[0])
            tg_v_p_int = float(tg_v_active_tasks[tg_v_active_tasks.index == uuid]['tg_v_p_int'].values[0])
            if tg_v_dst_proto == 'icmp':
                tg_v_result = ddv_tg_x_scapy.icmp_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
            elif tg_v_dst_proto == 'http':
                tg_v_dst_proto = 80
                #print(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                tg_v_result = ddv_tg_x_scapy.tcp_syn_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
            elif tg_v_dst_proto == 'https':
                tg_v_dst_proto = 443
                #print(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                tg_v_result = ddv_tg_x_scapy.tcp_syn_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
            elif tg_v_dst_proto == 'dns':
                tg_v_dst_proto = 53
                #print(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
                tg_v_result = ddv_tg_x_scapy.udp_v(uuid, tg_v_eut, tg_v_host, tg_v_src_ip, tg_v_dst_ip, tg_v_dst_proto, tg_v_p_cnt, tg_v_p_int)
            else:
                return "DDV-TG-V: No Tasks to run"
                pass
    except:
        e = sys.exc_info()[0]
        return 'Error: ' + str(e)
    print(name, 'Exiting')
    tg_v_task_pid('del_uuid', int(uuid), 0)
    exit(tg_v_result) # changeing exitcode from 0 to metric value
    return tg_v_result



@app.route('/ddv_tg_a_tasks_run', methods=['GET'])
def ddv_tg_a_tasks_run():
    tg_a_tasks_entries = get_tg_a_tasks()
    tg_a_active_tasks = tg_a_tasks_entries[tg_a_tasks_entries['tg_a_status'] == 'A'] # Only run Active Tasks
    try:
        for index in tg_a_active_tasks.index:
            uuid = index
            tg_a_eut = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_eut'].values[0])
            tg_a_eut_id = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_eut_id'].values[0])
            tg_a_host = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_host'].values[0])
            tg_a_src_ip = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_src_ip'].values[0])
            tg_a_dst_ip = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_dst_ip'].values[0])
            tg_a_dst_vector = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_dst_vector'].values[0])
            tg_a_p_cnt = int(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_p_cnt'].values[0])
            tg_a_p_int = float(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_p_int'].values[0])
            if tg_a_dst_vector == 'icmp-flood':
                ddv_tg_x_scapy.icmp_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'chargen-ra-flood-dst-port-80':
                tg_a_dst_vector = 80
                tg_a_src_port = 19
                ddv_tg_x_scapy.ra_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_src_port, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'tcp-syn-flood-dst-port-80':
                tg_a_dst_vector = 80
                ddv_tg_x_scapy.tcp_syn_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'udp-flood-dst-port-80':
                tg_a_dst_vector = 80
                ddv_tg_x_scapy.udp_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'udp-flood-dst-port-53':
                tg_a_dst_vector = 53
                ddv_tg_x_scapy.udp_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'ipv4-proto-0':
                ddv_tg_x_scapy.ipv4_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            else:
                return "DDV-TG-A: No Tasks to run"
                pass
    except:
        e = sys.exc_info()[0]
        return 'Error: ' + str(e)
    return "DDV-TG-A: All Attack Tasks Completed"


@app.route('/ddv_tg_a_task_run/<uuid>/<action>', methods=['GET']) # action is start|status|stop
def ddv_tg_a_task_run(uuid, action):
    global ddv_tg_a_task_spawn_p
    uuid = int(uuid)
    tg_a_tasks_entries = get_tg_a_tasks()
    tg_a_eut = str(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_eut'].values[0])
    tg_a_host = str(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_host'].values[0])
    tg_a_src_ip = str(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_src_ip'].values[0])
    tg_a_dst_ip = str(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_dst_ip'].values[0])
    tg_a_dst_vector = str(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_dst_vector'].values[0])
    tg_a_p_cnt = int(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_p_cnt'].values[0])
    tg_a_p_int = float(tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_p_int'].values[0])
    uid = 'ddv_tg_a_task_' + str(uuid)
    try:
        try:
            # need to ensure we only set Process once
            type(ddv_tg_a_task_spawn_p)
        except NameError:
            #global ddv_tg_a_task_spawn_p
            ddv_tg_a_task_spawn_p = Process(name=uid, target=ddv_tg_a_task_run_spawn, args=(uuid,))
        #if ((action == 'start') and (ddv_tg_a_task_spawn_p.is_alive() == False)):
        status = tg_a_task_pid('get_pid', int(uuid), 0) # check if running pid exists for task uuid
        if ((action == 'start') and (status < 0)): # no pid found
            ddv_tg_a_task_spawn_p.start()
            tg_a_task_pid('del_uuid', int(uuid), 0)
            tg_a_task_pid('put_uuid', int(uuid), int(ddv_tg_a_task_spawn_p.pid))
            return jsonify(
                            {'action': 'started',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', started',
                             'detail': str(tg_a_host) + ': ddv-tg-a task, ' + str(uuid) + ', sending ' + str(tg_a_dst_vector) + ' to ' + str(tg_a_eut) + ', ' + str(tg_a_dst_ip),
                             'state': 'running'
                            }
                            )
        elif ((action == 'start') and (status > 0)):
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', already running',
                             'state': 'running'
                            }
                            )
        elif action == 'status':
            if status > 0:
                return jsonify(
                                {'running_pid': str(status),
                                'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', is running',
                                'state': 'running'
                                }
                                )
            elif status < 0:
                return jsonify(
                                {'running_pid': str(status),
                                'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', not running',
                                'state': 'idle'
                                }
                                )
        elif ((action == 'stop') and (status > 0)):
            ddv_tg_a_task_spawn_p.terminate()
            tg_a_task_pid('del_uuid', int(uuid), 0)
            return jsonify(
                            {'action': 'stopped',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', stopped',
                             'state': 'idle'
                            }
                            )
        elif ((action == 'stop') and (status < 0)):
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', not running',
                             'state': 'idle'
                            }
                            )
        else:
            return jsonify(
                            {'action': 'failed',
                             'message': str(get_tg_x_hostname()) + ': General Error in Action',
                             'state': 'failed'
                            }
                            )
    except AssertionError as error:
        if action == 'start':
            #global ddv_tg_a_task_spawn_p
            ddv_tg_a_task_spawn_p = Process(name=uid, target=ddv_tg_a_task_run_spawn, args=(uuid,))
            ddv_tg_a_task_spawn_p.start()
            tg_a_task_pid('del_uuid', int(uuid), 0)
            tg_a_task_pid('put_uuid', int(uuid), int(ddv_tg_a_task_spawn_p.pid))
            return jsonify(
                            {'action': 'started',
                             'message': str(get_tg_x_hostname()) + ': ddv-tg-a task, ' + str(uuid) + ', started',
                             'detail': str(tg_a_host) + ': ddv-tg-a task, ' + str(uuid) + ', sending ' + str(tg_a_dst_vector) + ' to ' + str(tg_a_eut) + ', ' + str(tg_a_dst_ip),
                             'state': 'running'
                            }
                            )
        else:
            return "AssertionError"
    
def ddv_tg_a_task_run_spawn(uuid): # multiprocessor worker
    name = current_process().name
    print(name, 'Starting')
    tg_a_tasks_entries = get_tg_a_tasks()
    #tg_a_active_tasks = tg_a_tasks_entries[tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]['tg_a_status'] == 'A'] # Only run Active Tasks
    tg_a_active_tasks = tg_a_tasks_entries[tg_a_tasks_entries.index == uuid]
    try:
        for index in tg_a_active_tasks.index:
            tg_a_eut = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_eut'].values[0])
            tg_a_eut_id = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_eut_id'].values[0])
            tg_a_host = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_host'].values[0])
            tg_a_src_ip = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_src_ip'].values[0])
            tg_a_dst_ip = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_dst_ip'].values[0])
            tg_a_dst_vector = str(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_dst_vector'].values[0])
            tg_a_p_cnt = int(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_p_cnt'].values[0])
            tg_a_p_int = float(tg_a_active_tasks[tg_a_active_tasks.index == uuid]['tg_a_p_int'].values[0])
            if tg_a_dst_vector == 'icmp-flood':
                ddv_tg_x_scapy.icmp_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'chargen-ra-flood-dst-port-80':
                tg_a_dst_vector = 80
                tg_a_src_port = 19
                ddv_tg_x_scapy.ra_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_src_port, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'dns-ra-flood-dst-port-80':
                tg_a_dst_vector = 80
                tg_a_src_port = 53
                ddv_tg_x_scapy.ra_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_src_port, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'tcp-syn-flood-dst-port-80':
                tg_a_dst_vector = 80
                ddv_tg_x_scapy.tcp_syn_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'udp-flood-dst-port-80':
                tg_a_dst_vector = 80
                ddv_tg_x_scapy.udp_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'udp-flood-dst-port-53':
                tg_a_dst_vector = 53
                ddv_tg_x_scapy.udp_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            elif tg_a_dst_vector == 'ipv4-proto-0':
                ddv_tg_x_scapy.ipv4_flood_a(uuid, tg_a_eut, tg_a_host, tg_a_src_ip, tg_a_dst_ip, tg_a_dst_vector, tg_a_p_cnt, tg_a_p_int)
            else:
                return "DDV-TG-A: No Tasks to run"
                pass
    except:
        e = sys.exc_info()[0]
        return 'Error: ' + str(e)
    print(name, 'Exiting')
    tg_a_task_pid('del_uuid', int(uuid), 0)
    return tg_a_host, tg_a_dst_vector, tg_a_dst_ip
    return "DDV-TG-A: All Attack Tasks Completed"


@app.route('/remote_tg_a_task_push/<uuid>', methods=['POST'])
def remote_tg_a_task_push(uuid):
    content = request.json
    try:
        tg_a_tasks_entries = get_tg_a_tasks()
        if ((tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)].index.values[0] == int(uuid)) and (args.role == 'A')):
            tg_a_task_delete(uuid) # delete and overwrite the existing task
            result = tg_a_task_write(content)
            return result
    except:
        #e = sys.exc_info()[0]
        #print('Error: ' + str(e))
        pass
        result = tg_a_task_write(content)
        return result
        
def tg_a_task_write(content):
        try:
            tg_a_enrollment_id = content['tg_a_enrollment_id']
            tg_a_eut = content['tg_a_eut']
            tg_a_eut_id = content['tg_a_eut_id']
            tg_a_host = content['tg_a_host']
            tg_a_host_id = content['tg_a_host_id']
            tg_a_host_ip = content['tg_a_host_ip']
            tg_a_src_ip = content['tg_a_src_ip']
            tg_a_dst_ip = content['tg_a_dst_ip']
            tg_a_dst_vector = content['tg_a_dst_vector']
            tg_a_pps = content['tg_a_pps']
            tg_a_dur = content['tg_a_dur']
            tg_a_p_cnt = content['tg_a_p_cnt']
            tg_a_p_int = content['tg_a_p_int']
            tg_a_description = content['tg_a_description']
            tg_a_enrollment_date = content['tg_a_enrollment_date']
            tg_a_status = content['tg_a_status']
            tg_a_list = []
            tg_a_list_entry = {
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
            tg_a_list.append(tg_a_list_entry)
            tg_a_list_df = pd.DataFrame.from_dict(tg_a_list)
            tg_a_list_df.set_index('tg_a_enrollment_id', inplace=True)
            #print(tg_a_list_df)
            tg_a_list_df.to_csv(ddv_tg_cfg.ddv_tg_a_task_filename, mode='a', header=False, columns=[
                                                                                        #'tg_a_enrollment_id',
                                                                                        'tg_a_eut',
                                                                                        'tg_a_eut_id',
                                                                                        'tg_a_host',
                                                                                        'tg_a_host_id',
                                                                                        'tg_a_host_ip',
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
            return jsonify(
                           {'enrollment': 'success',
                            'tg_a_eut': tg_a_eut,
                            'enrollment_id': tg_a_enrollment_id,
                            'message': str(tg_a_host) + ': ' + str(tg_a_eut) + ' ddv-tg-a task successfully updated'
                           }
                           )
        except:
            return jsonify(
                           {'enrollment': 'failed',
                            'enrollment_id': uuid
                           }
                           )

@app.route('/remote_tg_a_task_delete/<uuid>', methods=['GET'])
def remote_tg_a_task_delete(uuid):
    try:
        # Check if we have an entry for this uuid in task list
        tg_a_tasks_entries = get_tg_a_tasks()
        if ((tg_a_tasks_entries[tg_a_tasks_entries.index == int(uuid)].index.values[0] == int(uuid)) and (args.role == 'A')):
            tg_a_task_delete(uuid)
            return jsonify(
                {'action': 'success',
                'message': str(get_tg_x_hostname()) + ': ddv-tg-a task ' + str(uuid) + ' successfully deleted'
                }
                )
        else:
            return jsonify(
            {'action': 'failed',
             'error': str(get_tg_x_hostname()) + ': ddv-tg-a task does not exist'
            }
            )
    except:
        #e = sys.exc_info()[0]
        #return 'Error: ' + str(e)
        return jsonify(
        {'action': 'failed',
         'error': str(get_tg_x_hostname()) + ': ddv-tg-a task does not exist'
        }
        )
        
def tg_a_task_delete(uuid):
    tg_a_tasks_entries = get_tg_a_tasks()
    tg_a_tasks_entries.drop(index=int(uuid)).to_csv(ddv_tg_cfg.ddv_tg_a_task_filename, mode='w', header=False, columns=[
                                                                                  #'tg_a_enrollment_id',
                                                                                  'tg_a_eut',
                                                                                  'tg_a_eut_id',
                                                                                  'tg_a_host',
                                                                                  'tg_a_host_id',
                                                                                  'tg_a_host_ip',
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


@app.route('/ddv_tg_x_config_flush', methods=['GET'])
def ddv_tg_x_config_flush():
    try:
        if (os.path.exists(ddv_tg_cfg.ddv_v_enrollment_filename)) and (args.role == 'V'):
            os.remove(ddv_tg_cfg.ddv_v_enrollment_filename)
        if (os.path.exists(ddv_tg_cfg.ddv_a_enrollment_filename)) and (args.role == 'A'):
            os.remove(ddv_tg_cfg.ddv_a_enrollment_filename)
        if (os.path.exists(ddv_tg_cfg.ddv_tg_v_task_filename)) and (args.role == 'V'):
            os.remove(ddv_tg_cfg.ddv_tg_v_task_filename)
        if (os.path.exists(ddv_tg_cfg.ddv_tg_a_task_filename)) and (args.role == 'A'):
            os.remove(ddv_tg_cfg.ddv_tg_a_task_filename)
        if (os.path.exists(ddv_tg_x_scapy.tg_v_r_report_filename)) and (args.role == 'V'):
            os.remove(ddv_tg_x_scapy.tg_v_r_report_filename)
        if (os.path.exists(ddv_tg_x_scapy.tg_a_r_report_filename)) and (args.role == 'A'):
            os.remove(ddv_tg_x_scapy.tg_a_r_report_filename)
        return jsonify(
            {'action': 'success',
             'message': 'restored to factory default'
            }
            )
    except:
        return jsonify(
            {'action': 'success',
             'message': str(get_tg_x_hostname()) + ': restored to factory default'
            }
            )


@app.route('/ddv_tg_x_keepalive', methods=['GET'])
def ddv_tg_x_keepalive():
    if args.role == 'A':
        return jsonify(
        {'action': 'success',
         'health': 'OK',
         'role': 'A',
         'enrolled': os.path.exists(ddv_tg_cfg.ddv_a_enrollment_filename),
         'tasks': get_tg_a_tasks().reset_index().to_dict('records')
        }
        )
    elif args.role == 'V':
        return jsonify(
        {'action': 'success',
         'health': 'OK',
         'role': 'V',
         'enrolled': os.path.exists(ddv_tg_cfg.ddv_v_enrollment_filename),
         'tasks': get_tg_v_tasks().reset_index().to_dict('records')
        }
        )
    else:
        pass

@app.before_request
def limit_remote_addr():
    if request.remote_addr != ddv_tg_cfg.ddv_c_ip:
        abort(403)  # Forbidden

def main():
    global args
    parser = argparse.ArgumentParser(description='ddv-tg-x v0.1')
    parser.add_argument('-r','--role', help='DDV TG Role (V or R, Default is V, Verifier)',required=True, nargs='?', const="none", type=str, default="V")
    args = parser.parse_args()
    try:
      if args.role == 'V':
        print("ddv-tg-v: Running in Verifier role")
        global ddv_v_tasks_loop_p, looping_on
        looping_on = Value('b', True)
        ddv_v_tasks_loop_p = Process(target=ddv_v_tasks_loop, args=(looping_on,))
        #ddv_v_tasks_loop_p.start()
        app.run(host=ddv_tg_cfg.my_ip, port=ddv_tg_cfg.ddv_tg_v_port, debug=True, use_reloader=True, ssl_context='adhoc')
      elif args.role == 'A':
        print("ddv-tg-a: Running in Attacker role")
        app.run(host=ddv_tg_cfg.my_ip, port=ddv_tg_cfg.ddv_tg_a_port, debug=True, use_reloader=True, ssl_context='adhoc')
      else:
        print("Check required CLI arguments and try again")
    except KeyboardInterrupt:
        print('closing script through ctrl-c')
    
main()
