from __future__ import print_function
from flask import flash, Markup
import requests, json, time, random, os, sys, pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
import pandas as pd
pp = pprint.PrettyPrinter(indent=5)

## Settings ##
ddv_mit_template_name = 'ddv_tg_mit_template'           # DDV TMS Mitigation Template name
ddv_shds_name = 'ddv_tg_shds'                           # DDV Shared Host Detection Settings name
sl_ddv_mo_list_filename = 'sl_ddv_mo_list.csv'
sl_ddv_mo_alert_list_filename = 'sl_ddv_mo_alert_list.csv'
sl_config_auto_commit = True
enabled_misuse_types = ['dns', 'icmp', 'dns_amp', 'tcpsyn', 'chargen_amp', 'ipnull', 'snmp_amp', 'ntp_amp', 'ssdp_amp', 'l2tp_amp', 'udp']

# make sure the system cert bundle has the root
# CA that signed the certificate Sightline is using or use verify=False (Insecure) and suppress:
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

misuse_types = {
    "0-1": ["ICMP", "icmp"],
    "1-1": ["IP Fragmentation", "ipfrag"],
    "2-1": ["IPv4 Protocol 0", "ipnull"],
    "3-1": ["IP Private", "ippriv"],
    "4-1": ["TCP NULL", "tcpnull"],
    "5-1": ["TCP SYN", "tcpsyn"],
    "6-1": ["TCP RST", "tcprst"],
    "7-1": ["Total Traffic", "total"],
    "8-1": ["DNS", "dns"],
    "9-1": ["UDP", "udp"],
    "10-1": ["NTP AAmplification", "ntp_amp"],
    "11-1": ["DNS Amplification", "dns_amp"],
    "12-1": ["SNMP Amplification", "snmp_amp"],
    "13-1": ["chargen Amplification", "chargen_amp"],
    "14-1": ["SSDP Amplification", "ssdp_amp"],
    "15-1": ["MS SQL RS Amplification", "mssql_amp"],
    "16-1": ["TCP ACK", "tcpack"],
    "17-1": ["TCP SYN/ACK Amplification", "tcpsynack"],
    "18-1": ["L2TP Amplification", "l2tp_amp"],
    "19-1": ["mDNS Amplification", "mdns_amp"],
    "20-1": ["NetBIOS Amplification", "netbios_amp"],
    "21-1": ["RIPv1 Amplification", "ripv1_amp"],
    "22-1": ["rpcbind Amplification", "rpcbind_amp"],
    "23-1": ["memcached Amplification", "memcached_amp"],
    "24-1": ["CLDAP Amplification", "cldap_amp"]
    }


def stream_logger(line):
    f = open('scroller_log', 'a+')
    f.write(line + '\n')
    f.close()

def sl_dos_mit_search(mit_gid):
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url_1 = str(base_url) + 'mitigations/' + str(mit_gid)
    url_2 = str(base_url) + 'mitigations/' + str(mit_gid) + '/rates_all_devices'
    mitigations_response = requests.get(url_1,
                                        verify=False,
                                        headers=header)
    mitigation_rates_all_devices_response = requests.get(url_2,
                                        verify=False,
                                        headers=header)
    #pp.pprint(mitigations_response.json())
    #pp.pprint(mitigation_rates_all_devices_response.json())
    mitigations_response = mitigations_response.json()
    mitigation_rates_all_devices_response = mitigation_rates_all_devices_response.json()
    # Sort through mitigation details and get all active countermeasures and stats
    mitigation_rates_all_devices_cm = []
    for entry in mitigation_rates_all_devices_response['data']['attributes']:
        #if  (entry == 'timeseries_start') or (entry == 'total') or (entry == 'step'): # ignore non TMS CMs
        if  (entry == 'timeseries_start') or (entry == 'step'): # ignore non TMS CMs
            pass
        else:
            #print(mitigation_rates_all_devices_response['data']['attributes'][entry])
            mitigation_rates_all_devices_cm.append({entry: mitigation_rates_all_devices_response['data']['attributes'][entry]})
    sl_ddv_dos_mitigation = {
                            'mit_gid': mitigations_response['data']['id'],
                            'mit_name': mitigations_response['data']['attributes']['name'],
                            'mit_tms_group': mitigations_response['data']['relationships']['tms_group']['data']['id'],
                            'mit_cm': mitigation_rates_all_devices_cm
                            }
    #pp.pprint(mitigations_response)
    #pp.pprint(mitigation_rates_all_devices_response)
    #pp.pprint(sl_ddv_dos_mitigation)
    return sl_ddv_dos_mitigation
    


def sl_dos_alert_search(mo_gid, mo_name):
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = str(base_url) + 'alerts/?filter=/data/relationships/managed_object/data/id=' + str(mo_gid) + '+AND+/data/attributes/alert_type=dos_host_detection+AND+/data/attributes/ongoing=true'
    response = requests.get(url,
                            verify=False,
                            headers=header)
    #return response.json()
    #return str(response.json()['data']['attributes'][attribute])
    #print(json.dumps(response.json()['data'], indent=4, sort_keys=True))
    sl_ddv_mo_alert_list = []
    entries = response.json()
    for entry in entries['data']:
        try:
            mitigation_id = entry['relationships']['mitigation']['data']
            for mit_entry in mitigation_id:
                mitigation_id = str(((mit_entry)['id']))
                #time.sleep(20) # wait a few seconds for auto-mitigation details to build
                sl_ddv_dos_mitigation = sl_dos_mit_search(mitigation_id)
        except:
            mitigation_id = 'tms-none'
        #print(entry)
        sl_ddv_mo_alert_list_entry = {
                                    'alert_gid': entry['id'],
                                    'mo_gid': mo_gid,
                                    'mo_name': mo_name,
                                    'alert_class': entry['attributes']['alert_class'],
                                    'alert_type':   entry['attributes']['alert_type'],
                                    'alert_importance': entry['attributes']['importance'],
                                    'alert_ongoing': entry['attributes']['ongoing'],
                                    'start_time': entry['attributes']['start_time'],
                                    'host_address': entry['attributes']['subobject']['host_address'],
                                    'impact_bps': entry['attributes']['subobject']['impact_bps'],
                                    'impact_pps': entry['attributes']['subobject']['impact_pps'],
                                    'misuse_types': entry['attributes']['subobject']['misuse_types'],
                                    'mitigation_data': sl_ddv_dos_mitigation,
                                    'source_prefixes': sl_dos_alert_src_prefix_search(entry['relationships']['traffic']['links']['related'])
                                    }
        sl_ddv_mo_alert_list.append(sl_ddv_mo_alert_list_entry)
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: DoS Alert#' + str(entry['id']) + ': ' + str(entry['attributes']['alert_type']) + ', Target: ' + str(entry['attributes']['subobject']['host_address']) + ', Type: ' + str(entry['attributes']['subobject']['misuse_types'])
        flash(message, 'flash_green')
        stream_logger(message)
        if mitigation_id == 'tms-none':
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: TMS Mitigations: None'
            flash(message, 'flash_orange')
            stream_logger(message)
        else:
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: TMS Mitigation#' + str(sl_ddv_dos_mitigation['mit_gid']) + ': ' + str(sl_ddv_dos_mitigation['mit_name'])
            flash(message, 'flash_green')
            stream_logger(message)
            for entry in sl_ddv_dos_mitigation['mit_cm']:
                message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.......... ' + 'DDV-C_SL: TMS CM: ' + str(list(entry.keys())[0]) + ' [ dropping: ' + str(entry[list(entry.keys())[0]]['drop']['pps']['current']) + ' pps | ' + str(entry[list(entry.keys())[0]]['drop']['bps']['current']) + ' bps ] & ' + ' [ passing: ' + str(entry[list(entry.keys())[0]]['pass']['pps']) + ' pps | ' + str(entry[list(entry.keys())[0]]['pass']['bps']) + ' bps ]'
                flash(message, 'flash_green')
                stream_logger(message)
    sl_ddv_mo_alert_list_df = pd.DataFrame.from_dict(sl_ddv_mo_alert_list)
    sl_ddv_mo_alert_list_df.set_index('alert_gid', inplace=True)
    #print sl_ddv_mo_alert_list_df
    sl_ddv_mo_alert_list_df.to_csv(sl_ddv_mo_alert_list_filename, mode='a', header=False, columns=[
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
                                                                                    ])

def sl_mo_search(operator, name):   # operator = cn|eq
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = str(base_url) + 'managed_objects/?filter[]=a/name.' + str(operator) + '.' + str(name)
    response = requests.get(url,
                            verify=False,
                            headers=header)
    #return str(response.json()['data']['attributes'][attribute])
    return response.json()
    

def sl_dos_alert_history_search(mo_gid): # search for all alerts for given MO (GID)
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = str(base_url) + 'alerts/?filter=/data/relationships/managed_object/data/id=' + str(mo_gid) + '+AND+/data/attributes/alert_type=dos_host_detection+AND+/data/attributes/importance=2'
    response = requests.get(url,
                            verify=False,
                            headers=header)
    #return str(response.json()['data']['attributes'][attribute])
    #print(json.dumps(response.json()['data'], indent=4, sort_keys=True))
    return response.json()['data']


def sl_dos_alert_src_ip_search(alert_src_ip_url): # search for all source_ip's listed under specific alert url
    print(alert_src_ip_url)
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    response = requests.get(alert_src_ip_url,
                            verify=False,
                            headers=header)
    #return str(response.json()['data']['attributes'][attribute])
    #print(json.dumps(response.json()['data'], indent=4, sort_keys=True))
    pp.pprint(response.json())
    return response.json()['data']['attributes']['source_ips']
    
    

def sl_dos_alert_src_prefix_search(alert_src_traffic_url): # search for all source_ip's listed under specific alert url
    query_unit = 'pps'
    alert_src_prefix_url = alert_src_traffic_url + '/src_prefixes/?query_unit=' + query_unit
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    response = requests.get(alert_src_prefix_url,
                            verify=False,
                            headers=header)
    #return str(response.json()['data']['attributes'][attribute])
    #print(json.dumps(response.json()['data'], indent=4, sort_keys=True))
    prefix_entries = []
    for prefix_entry in response.json()['data']:
        prefix_entries.append(prefix_entry['attributes']['view']['network']['unit'][query_unit])
    #pp.pprint(response.json())
    #print(prefix_entries)
    return prefix_entries



def sl_dos_alert_details_x_mo(sl_ip, sl_token, mo_gid):
    global base_url, token
    base_url = 'https://' + str(sl_ip) + '/api/sp/'
    token = sl_token
    mo_alerts = sl_dos_alert_history_search(mo_gid)
    sl_ddv_mo_alerts_detail_list = []
    for entry in mo_alerts:
        try:
            mitigation_id = entry['relationships']['mitigation']['data']['id']
        except:
            mitigation_id = 'tms-none'
        sl_ddv_mo_alerts_detail_list_entry =     {
            'mo_gid': entry['relationships']['managed_object']['data']['id'],
            'mo_name': get_mo_attribute(entry['relationships']['managed_object']['data']['id'], 'name'),
            'alert_gid': entry['id'],
            'alert_class': entry['attributes']['alert_class'],
            'alert_type':   entry['attributes']['alert_type'],
            'alert_importance': entry['attributes']['importance'],
            'alert_ongoing': entry['attributes']['ongoing'],
            'start_time': entry['attributes']['start_time'],
            'host_address': entry['attributes']['subobject']['host_address'],
            'impact_bps': entry['attributes']['subobject']['impact_bps'],
            'impact_pps': entry['attributes']['subobject']['impact_pps'],
            'misuse_types': entry['attributes']['subobject']['misuse_types'],
            'mitigation_gid': mitigation_id,
            #'source_ip_addresses_url': entry['relationships']['source_ip_addresses']['links']['related'],
            'source_ip_addresses': sl_dos_alert_src_ip_search(entry['relationships']['source_ip_addresses']['links']['related'])
                        }
        sl_ddv_mo_alerts_detail_list.append(sl_ddv_mo_alerts_detail_list_entry)
    return sl_ddv_mo_alerts_detail_list


def sl_mit_template_search(name):
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = str(base_url) + 'mitigation_templates/'
    response = requests.get(url,
                            verify=False,
                            headers=header)
    for entry in response.json()['data']:
        if str(entry['attributes']['name']) == str(name):
            return entry['id'] # return gid for mitigation id
        else:
            pass
    return 0
        

def sl_shds_search(operator, name):   # operator = cn|eq
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = str(base_url) + 'shared_host_detection_settings/?filter[]=a/name.' + str(operator) + '.' + str(name)
    response = requests.get(url,
                            verify=False,
                            headers=header)
    #return str(response.json()['data']['attributes'][attribute])
    return response.json()

def get_sl_ddv_mo(eut_list): # Find all MOs that match EUT names
    if os.path.exists(sl_ddv_mo_alert_list_filename): # start with cleared alert file
        os.remove(sl_ddv_mo_alert_list_filename)
    sl_ddv_mo_list = []
    for index in eut_list.index:
        sl_mo_search_data = sl_mo_search('eq', eut_list[eut_list.index == index]['eut_shortname'].values[0])
        #pp.pprint(sl_mo_search_data)
        #print(sl_mo_search_data['data'][0]['id'], sl_mo_search_data['data'][0]['attributes']['name'], sl_mo_search_data['data'][0]['attributes']['match'])
        sl_ddv_mo_list_entry = {
                            'mo_gid': sl_mo_search_data['data'][0]['id'],
                            'mo_name': sl_mo_search_data['data'][0]['attributes']['name'],
                            'mo_match': sl_mo_search_data['data'][0]['attributes']['match']
                            }
        sl_ddv_mo_list.append(sl_ddv_mo_list_entry)
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + 'DDV-C_SL: Sightline has MO, Name: ' + str(sl_mo_search_data['data'][0]['attributes']['name']) + ', GID: ' + str(sl_mo_search_data['data'][0]['id']) + ', Matching: ' + str(sl_mo_search_data['data'][0]['attributes']['match'])
        flash(message, 'flash_green')
        stream_logger(message)
        try:
            sl_dos_alert_search(sl_mo_search_data['data'][0]['id'], sl_mo_search_data['data'][0]['attributes']['name']) # find all alerts related to these MOs
        except:
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: DoS Alert# None'
            flash(message, 'flash_orange')
            stream_logger(message)
            #e = sys.exc_info()[0]
            #print ('Error: ' + str(e))
    sl_ddv_mo_list_df = pd.DataFrame.from_dict(sl_ddv_mo_list)
    sl_ddv_mo_list_df.set_index('mo_gid', inplace=True)
    #print sl_ddv_mo_list_df
    sl_ddv_mo_list_df.to_csv(sl_ddv_mo_list_filename, mode='w', header=False, columns=[
                                                                                    'mo_name',
                                                                                    'mo_match'
                                                                                    ])



def get_mo_attribute(gid, attribute): # attribute can be 'name' etc.
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = base_url + 'managed_objects/' + str(gid)
    response = requests.get(url,
                            verify=False,
                            headers=header)
    return str(response.json()['data']['attributes'][attribute])


def get_mo_detection_settings(gid):
    header = {
        "X-Arbux-APIToken":token,
        "Accept": "*/*"
    }
    url = base_url + 'managed_objects/' + str(gid)
    response = requests.get(url,
                            verify=False,
                            headers=header)
    return str(response.json()['data']['relationships']['shared_host_detection_settings']['data']['id'])

def get_shared_host_detection_settings(gid):
    if int(gid) != 0:
        header = {
            "X-Arbux-APIToken":token,
            "Accept": "*/*"
        }
        url = base_url + 'shared_host_detection_settings/' + str(gid)
        response = requests.get(url,
                                verify=False,
                                headers=header)
        #print(json.dumps(response.json(), indent=4))
        #return str(response.json()['data']['relationships']['shared_host_detection_settings']['data']['id'])
        #print(len(response.json()['data']['attributes']['misuse_types']))
        #for entry in range((len(response.json()['data']['attributes']['misuse_types']))):
        #pp.pprint(response.json())
        return (response.json()['data']['attributes']['misuse_types'])
    else:
        print("Misuse detection is disabled for this MO")


def set_shared_host_detection_settings(gid, misuse_type, det_type):
    if int(gid) != 0:
        header = {
            "X-Arbux-APIToken": token,
            "Content-Type": "application/vnd.api+json",
        }
        if str(misuse_type) in enabled_misuse_types: # enable only misuse types we want to simulate attacks for
            state = True
        else:
            state = False
        if det_type == 'bps_pps':
            data = {
                "data": {
                    "attributes": {
                        "misuse_type": misuse_type,
                        "threshold_pps": 20,
                        "high_pps": 40,
                        "threshold_bps": 200000,
                        "high_bps": 400000,
                        "enabled": state,
                        "shds_lids": [gid]
                    }
                }
            }
        elif det_type == 'pps':
            data = {
                "data": {
                    "attributes": {
                        "misuse_type": misuse_type,
                        "threshold_pps": 20,
                        "high_pps": 40,
                        "enabled": state,
                        "shds_lids": [gid]
                    }
                }
            }
        else:
            pass
        url = base_url + 'shared_host_detection_setting_requests/'
        response = requests.post(url,
                                verify=False,
                                headers=header,
                                data=json.dumps(data))
        #pp.pprint(response.json())
        return response.json()
    else:
        print("Error")
        
        
def create_shared_host_detection_settings(name):
    true = True
    false = False
    header = {
        "X-Arbux-APIToken": token,
        "Content-Type": "application/vnd.api+json",
    }
    data = {
        "data": {
            "attributes": {
                "name": name,
                "fast_flood_enabled": true
            }
        }
    }
    url = base_url + 'shared_host_detection_settings/'
    response = requests.post(url,
                            verify=False,
                            headers=header,
                            data=json.dumps(data))
    #pp.pprint(response.json())
    #print(response.json()['data']['id'])
    shds_gid = response.json()['data']['id']
    for misuse_type in response.json()['data']['attributes']['misuse_types']:
        #print(misuse_type)
        if '_amp' in misuse_type: # bps and pps detection for _amp
            set_shared_host_detection_settings(shds_gid, misuse_type, 'bps_pps')
        elif len(response.json()['data']['attributes']['misuse_types'][misuse_type]['high']) <= 1: # only pps detection
            set_shared_host_detection_settings(shds_gid, misuse_type, 'pps')
        elif len(response.json()['data']['attributes']['misuse_types'][misuse_type]['high']) == 2: # bps and pps detection
            set_shared_host_detection_settings(shds_gid, misuse_type, 'bps_pps')
        else:
            print("Error with len")
            pass
        #time.sleep(2)
    return response.json()
    

def delete_shared_host_detection_settings(gid):
    header = {
        "X-Arbux-APIToken": token
    }
    url = base_url + 'shared_host_detection_settings/' + str(gid)
    response = requests.delete(url,
                            verify=False,
                            headers=header)
    if response.status_code == 204:
        return response
    else:
        print('delete_shared_host_detection_settings error')
        return response


def create_ddv_mo(mo_name, ip_prefix, shds_gid, mit_template_gid):
    header = {
        "X-Arbux-APIToken": token,
        "Content-Type": "application/vnd.api+json",
    }
    true = True
    false = False
    data = {
        "data": {
            "attributes": {
                "automitigation_precise_protection_prefixes": false,
                "automitigation_precise_protection_prefixes_mit_on_query_failure": false,
                "detection_network_country_enabled": false,
                "detection_network_enabled": false,
                "detection_profiled_autorate": false,
                "detection_profiled_enabled": false,
                "family": "customer",
                "match": ip_prefix,
                "match_enabled": true,
                "match_type": "cidr_blocks",
                "mitigation_automitigation_tms_enabled": true,
                "mitigation_automitigation_stop_event": "after_alert_ends",
                "mitigation_automitigation_stop_minutes": 0,
                "mitigation_automitigation_tms_enabled": true,
                "mitigation_automitigation_tms_reuse": true,
                "mitigation_blackhole_auto_enabled": false,
                "mitigation_flowspec_auto_enabled": false,
                "mitigation_automitigation": true,
                "name": mo_name,
                "scrub_insight_mo_match": false
            },
            "relationships": {
                "mitigation_templates_auto_ipv4": {
                  "data": {
                    "id": str(mit_template_gid),
                    "type": "mitigation_template"
                  },
                  "links": {
                    "related": "https://cete.demo.netscout.com/api/sp/v7/mitigation_templates/" + str(mit_template_gid)
                  }
                },
                "mitigation_templates_manual_ipv4": {
                  "data": {
                    "id": str(mit_template_gid),
                    "type": "mitigation_template"
                  },
                  "links": {
                    "related": "https://cete.demo.netscout.com/api/sp/v7/mitigation_templates/" + str(mit_template_gid)
                  }
                },
                "shared_host_detection_settings": {
                  "data": {
                    "id": str(shds_gid),
                    "type": "shared_host_detection_settings"
                  },
                  "links": {
                    "related": "https://cete.demo.netscout.com/api/sp/v7/shared_host_detection_settings/" + str(shds_gid)
                  }
                }
            }
        }
    }
    #pp.pprint(data)
    url = base_url + 'managed_objects/'
    response = requests.post(url,
                            verify=False,
                            headers=header,
                            data=json.dumps(data))
    #pp.pprint(response.json())
    #print(response.json()['data']['id'])
    #mo_gid = response.json()['data']['id']
    #print(mo_gid)
    #return mo_gid
    return response.json()

def delete_ddv_mo(gid):
    header = {
        "X-Arbux-APIToken": token
    }
    url = base_url + 'managed_objects/' + str(gid)
    response = requests.delete(url,
                            verify=False,
                            headers=header)
    if response.status_code == 204:
        return response
    else:
        print('delete_ddv_mo error')
        return response

def create_ddv_mit_template(name):
    header = {
        "X-Arbux-APIToken": token,
        "Content-Type": "application/vnd.api+json",
    }
    true = True
    false = False
    data = {
          "data": {
            "attributes": {
              "description": "DDV TMS Mitigation Template - Link this template to the appropriate TMS Group",
              "ip_version": 4,
              "name": name,
              "subobject": {
                "aif_http_url_regexp": {
                  "aif_http_level": "low",
                  "regexp_locked": false,
                  "regexp_logical_and": false,
                  "regexp_pass": false,
                  "url_regexp_logical_and": false
                },
                "bgp_announce": false,
                "diversion_prefix_mode": "disabled",
                "diversion_prefixes": [
                  ""
                ],
                "dns_auth": {
                  "mode": "passive",
                  "timeout": 60
                },
                "dns_object_ratelimiting": {
                  "blacklist_enabled": false,
                  "limit": 100
                },
                "dns_ratelimiting": {
                  "limit": 100
                },
                "dns_regex": {
                  "blacklist_blocked": false,
                  "dns_regex_pass": false,
                  "logical_and": false,
                  "match_direction": "query",
                  "regexp_uri_locked": false
                },
                "dns_scoping": {
                  "apply_on_match": true
                },
                "http_malformed": {
                  "level": "low",
                  "locked": false
                },
                "http_scoping": {
                  "apply_on_match": true
                },
                "ip_location_filterlist": {
                  "drop_matched_or_unmatched": "matched"
                },
                "payload": {
                  "blacklist_hosts": true,
                  "locked": false,
                  "match_src_port": false,
                  "match_src_port_locked": false,
                  "other_ip_protocols_locked": false,
                  "regex_pass": false,
                  "regexp_uri_locked": false,
                  "tcp_ports_locked": false,
                  "udp_ports_locked": false
                },
                "per_connection_flood_protection": {
                  "enforcement": "block"
                },
                "protection_prefixes": [
                  ""
                ],
                "sip_malformed": {
                  "locked": false
                },
                "tcp_connection_limiting": {
                  "blacklist": true,
                  "idle_timeout": 60,
                  "ignore_idle": true,
                  "max_connections": 25
                },
                "tcp_syn_auth": {
                  "auto": true,
                  "spoofed_flood_protection_automation": true
                },
                "tls_negotiation": {
                  "clients_can_alert": true,
                  "max_cipher_suites": 100,
                  "max_early_close": 25,
                  "max_extensions": 25,
                  "max_pend_secs": 30,
                  "min_pend_secs": 15
                },
                "udp_reflection_amp": {
                  "auto_transfer_misuse": true,
                  "auto_transfer_misuse_dns": true,
                  "blacklist_enabled": false,
                  "enabled": true
                }
              },
              "subtype": "tms"
            },
            "type": "mitigation_template"
          }
        }
    #pp.pprint(data)
    url = base_url + 'mitigation_templates/'
    response = requests.post(url,
                            verify=False,
                            headers=header,
                            data=json.dumps(data))
    mit_template_gid = response.json()['data']['id']
    return response.json()


def delete_ddv_mit_template(gid):
    header = {
        "X-Arbux-APIToken": token
    }
    url = base_url + 'mitigation_templates/' + str(gid)
    response = requests.delete(url,
                            verify=False,
                            headers=header)
    if response.status_code == 204:
        return response
    else:
        #print(response)
        print('delete_ddv_mit_template error')
        return response


def sl_config_commit(message):
    header = {
        "X-Arbux-APIToken": token,
        "Content-Type": "application/vnd.api+json",
    }
    true = True
    false = False
    data = {
        "data": {
            "attributes": {
                "commit_log_message": "DDV-C via API: " + str(message)
            }
        }
    }
    url = base_url + 'config/'
    if sl_config_auto_commit:
        response = requests.post(url,
                                verify=False,
                                headers=header,
                                data=json.dumps(data))
        #pp.pprint(response.json())
        return response
    else:
        pass


def sl_ddv_run(sl_ip, sl_token, eut_list):
    global base_url, token
    base_url = 'https://' + str(sl_ip) + '/api/sp/'
    token = sl_token
    #global base_url, token
    message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C_SL: Fetching MO Records from Sightline'
    flash(message, 'flash_blue')
    stream_logger(message)
    try:
        get_sl_ddv_mo(eut_list)
    except:
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + 'DDV-C_SL: DDV MO not configured on Sightline'
        flash(message, 'flash_red')
        stream_logger(message)
    
    
def sl_ddv_base_config(action, sl_ip, sl_token, eut_list):
    global base_url, token
    base_url = 'https://' + str(sl_ip) + '/api/sp/'
    token = sl_token
    #global base_url, token
    # Step 1: Check if Mitigation Template exists
    message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + 'DDV-C_SL: Fetching Mitigation Template from Sightline'
    flash(message, 'flash_blue')
    stream_logger(message)
    sl_mit_template_gid = int(sl_mit_template_search(ddv_mit_template_name)) # return gid of template if found (no filtering option in API)
    #pp.pprint(sl_mit_template_data)
    if sl_mit_template_gid == 0:
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: Mitigation Template, Name: ' + str(ddv_mit_template_name) + ', not found on Sightline'
        flash(message, 'flash_red')
        stream_logger(message)
        if action == 'add':
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: Mitigation Template, Configuring: ' + str(ddv_mit_template_name) + ', on Sightline'
            flash(message, 'flash_orange')
            stream_logger(message)
            sl_mit_template_create_data = create_ddv_mit_template(ddv_mit_template_name)
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '........ ' + 'DDV-C_SL: Mitigation Template, Successfully Created: ' + str(ddv_mit_template_name) + ', on Sightline, with GID: ' + str(sl_mit_template_create_data['data']['id'])
            flash(message, 'flash_green')
            stream_logger(message)
            mit_template_gid = sl_mit_template_create_data['data']['id']
        else:
            pass
        #pp.pprint(sl_mit_template_create_data)
    elif sl_mit_template_gid > 0:
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: Mitigation Template, Name: ' + str(ddv_mit_template_name) + ', found on Sightline'
        flash(message, 'flash_green')
        stream_logger(message)
        mit_template_gid = sl_mit_template_gid
        if action == 'remove':
            delete_ddv_mit_template_response = delete_ddv_mit_template(mit_template_gid)
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: Mitigation Template, Removed: ' + str(ddv_mit_template_name) + ', from Sightline'
            flash(message, 'flash_orange')
            stream_logger(message)
        else:
            pass
    else:
        pass
    # Step 2: Check if Shared Host Detection Setting (SHDS) Exists
    message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + 'DDV-C_SL: Fetching SHDS from Sightline'
    flash(message, 'flash_blue')
    stream_logger(message)
    sl_shds_data = sl_shds_search('eq', ddv_shds_name)
    #pp.pprint(len(sl_shds_data['data']))
    if len(sl_shds_data['data']) == 0:
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: SHDS, Name: ' + str(ddv_shds_name) + ', not found on Sightline'
        flash(message, 'flash_red')
        stream_logger(message)
        if action == 'add':
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: SHDS, Configuring: ' + str(ddv_shds_name) + ', on Sightline'
            flash(message, 'flash_orange')
            stream_logger(message)
            sl_shds_create_data = create_shared_host_detection_settings(ddv_shds_name)
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '........ ' + 'DDV-C_SL: SHDS, Successfully Created: ' + str(ddv_shds_name) + ', on Sightline, with GID: ' + str(sl_shds_create_data['data']['id'])
            flash(message, 'flash_green')
            stream_logger(message)
            #pp.pprint(sl_shds_create_data)
            shds_gid = int(sl_shds_create_data['data']['id'])
        else:
            pass
    elif len(sl_shds_data['data']) > 0:
        message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: SHDS, Name: ' + str(ddv_shds_name) + ', found on Sightline'
        flash(message, 'flash_green')
        stream_logger(message)
        shds_gid = int(sl_shds_data['data'][0]['id'])
        if action == 'remove':
            delete_shared_host_detection_settings(shds_gid)
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: SHDS, Removed: ' + str(ddv_shds_name) + ', from Sightline'
            flash(message, 'flash_orange')
            stream_logger(message)
        else:
            pass
    else:
        pass
    # Step 3: Check if MOs exists, and if they map to the Mitigation and SHDS Templates
    message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.. ' + 'DDV-C_SL: Fetching MO Records from Sightline'
    flash(message, 'flash_blue')
    stream_logger(message)
    for index in eut_list.index:
        #print(eut_list[eut_list.index == index]['eut_shortname'].values[0], eut_list[eut_list.index == index]['eut_dst_ip'].values[0])
        sl_mo_data = sl_mo_search('eq', eut_list[eut_list.index == index]['eut_shortname'].values[0])
        #pp.pprint(sl_mo_data)
        if len(sl_mo_data['data']) == 0:
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: MO, Name: ' + str(eut_list[eut_list.index == index]['eut_shortname'].values[0]) + ', not found on Sightline'
            flash(message, 'flash_red')
            stream_logger(message)
            if action == 'add':
                message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: MO, Configuring: ' + str(eut_list[eut_list.index == index]['eut_shortname'].values[0]) + ', on Sightline'
                flash(message, 'flash_orange')
                stream_logger(message)
                sl_mo_create_data = create_ddv_mo(eut_list[eut_list.index == index]['eut_shortname'].values[0], str(eut_list[eut_list.index == index]['eut_dst_ip'].values[0]) + '/32', shds_gid, mit_template_gid)
                message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '........ ' + 'DDV-C_SL: MO, Successfully Created: ' + str(eut_list[eut_list.index == index]['eut_shortname'].values[0]) + ', on Sightline, with GID: ' + str(sl_mo_create_data['data']['id'])
                flash(message, 'flash_green')
                stream_logger(message)
            else:
                pass
        else:
            message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '.... ' + 'DDV-C_SL: MO, Name:' + str(eut_list[eut_list.index == index]['eut_shortname'].values[0]) + ', found on Sightline'
            flash(message, 'flash_green')
            stream_logger(message)
            if action == 'remove':
                delete_ddv_mo(int(sl_mo_data['data'][0]['id']))
                message = str(datetime.now().strftime("%H:%M:%S")) + ' ' + '...... ' + 'DDV-C_SL: MO, Removed: ' + str(eut_list[eut_list.index == index]['eut_shortname'].values[0]) + ', from Sightline'
                flash(message, 'flash_orange')
                stream_logger(message)
                # 3b: Mitigation template may not be deleted while linked to MO, so trying to delete after MO deletion step if required
                print(delete_ddv_mit_template_response)
                if delete_ddv_mit_template_response.status_code == 400:
                    print(mit_template_gid)
                    delete_ddv_mit_template(mit_template_gid)
                else:
                    pass
            else:
                pass
            pass
    # Step 4: Commit Config to Sightline if auto commit is enabled
    if action == 'add':
        sl_config_commit("Base configs have been added")
    elif action == 'remove':
        sl_config_commit("Base configs have been removed")
    else:
        pass

