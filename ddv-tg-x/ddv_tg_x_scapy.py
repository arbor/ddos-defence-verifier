import sys, time
import pandas as pd
from scapy.all import *

tg_v_r_report_filename = 'ddv_tg_v_report.csv'
tg_a_r_report_filename = 'ddv_tg_a_report.csv'

def ddv_tg_v_report(action, uuid, eut, host, src_ip, dst_ip, dst_proto, dur, int, test_name, metric): # action=write|get
    if action == 'write':
            tg_v_r_list = []
            tg_v_r_list_entry = {	# populate results report csv
                                'tg_v_r_timestamp': datetime.now(),
                                'tg_v_r_task_id': uuid,			# ddv tg unique task id
                                'tg_v_r_eut': eut,			# Entity Under Test
                                'tg_v_r_host': host,			# TG-x host/agent
                                'tg_v_r_src_ip': src_ip,
                                'tg_v_r_dst_ip': dst_ip,
                                'tg_v_r_dst_proto': dst_proto,
                                'tg_v_r_p_cnt': dur,			# number of packets
                                'tg_v_r_p_int': int,			# interval between packets
                                'tg_v_r_test_name': test_name,
                                'tg_v_r_metric': metric,
                                }
            tg_v_r_list.append(tg_v_r_list_entry)
            tg_v_r_list_df = pd.DataFrame.from_dict(tg_v_r_list)
            tg_v_r_list_df.set_index('tg_v_r_timestamp', inplace=True)
            #print(tg_v_r_list_df)
            tg_v_r_list_df.to_csv(tg_v_r_report_filename, mode='a', header=False, columns=[
                                                                                        'tg_v_r_task_id',
                                                                                        'tg_v_r_eut',
                                                                                        'tg_v_r_host',
                                                                                        'tg_v_r_src_ip',
                                                                                        'tg_v_r_dst_ip',
                                                                                        'tg_v_r_dst_proto',
                                                                                        'tg_v_r_p_cnt',
                                                                                        'tg_v_r_p_int',
                                                                                        'tg_v_r_test_name',
                                                                                        'tg_v_r_metric'
                                                                                        ])
    elif action == 'get':
        tg_v_r_report_df = pd.read_csv(tg_v_r_report_filename, names=[
                                                                'tg_v_r_timestamp',
                                                                'tg_v_r_task_id',
                                                                'tg_v_r_eut',
                                                                'tg_v_r_host',
                                                                'tg_v_r_src_ip',
                                                                'tg_v_r_dst_ip',
                                                                'tg_v_r_dst_proto',
                                                                'tg_v_r_p_cnt',
                                                                'tg_v_r_p_int',
                                                                'tg_v_r_test_name',
                                                                'tg_v_r_metric'
                                                                ], dtype={'tg_v_host_id': str,'tg_v_p_cnt': str}, header=None)
        tg_v_r_report_df.set_index('tg_v_r_timestamp', inplace=True)
        try:
            if uuid > 0:
                return tg_v_r_report_df[tg_v_r_report_df['tg_v_r_task_id'] == uuid]
            else:
                return tg_v_r_report_df
        except:
            return tg_v_r_report_df



def ddv_tg_a_report(uuid, eut, host, src_ip, dst_ip, dst_proto, dur, int, test_name, metric):
            tg_a_r_list = []
            tg_a_r_list_entry = {                                       # populate results report csv
                                'tg_a_r_timestamp': datetime.now(),
                                'tg_a_r_task_id': uuid,                 # ddv tg unique task id
                                'tg_a_r_eut': eut,                      # Entity Under Test
                                'tg_a_r_host': host,                    # TG-x host/agent
                                'tg_a_r_src_ip': src_ip,
                                'tg_a_r_dst_ip': dst_ip,
                                'tg_a_r_dst_proto': dst_proto,
                                'tg_a_r_p_cnt': dur,                      # number of packets
                                'tg_a_r_p_int': int,                      # interval between packets
                                'tg_a_r_test_name': test_name,
                                'tg_a_r_metric': metric,
                                }
            tg_a_r_list.append(tg_a_r_list_entry)
            tg_a_r_list_df = pd.DataFrame.from_dict(tg_a_r_list)
            tg_a_r_list_df.set_index('tg_a_r_timestamp', inplace=True)
            #print(tg_a_r_list_df)
            tg_a_r_list_df.to_csv(tg_a_r_report_filename, mode='a', header=False, columns=[
                                                                                        'tg_a_r_task_id',
                                                                                        'tg_a_r_eut',
                                                                                        'tg_a_r_host',
                                                                                        'tg_a_r_src_ip',
                                                                                        'tg_a_r_dst_ip',
                                                                                        'tg_a_r_dst_proto',
                                                                                        'tg_a_r_p_cnt',
                                                                                        'tg_a_r_p_int',
                                                                                        'tg_a_r_test_name',
                                                                                        'tg_a_r_metric'
                                                                                        ])



# Verifier Traffic Generator scripts: These should allow legit responses from targets, in order to verify proper comms

def icmp_v(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval):
	ans, unans = srloop(IP(dst=dst_ip)/ICMP(), count=p_count, inter=interval)
	ddv_tg_v_report('write', uuid, eut, host, src_ip, dst_ip, proto, p_count, interval, 'icmp_v', int(pct_calc(int(len(ans)), int(p_count))))
	print(int(pct_calc(int(len(ans)), int(p_count))))
	return int(pct_calc(int(len(ans)), int(p_count)))

def tcp_syn_v(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval):
	dst_port = proto
	ans, unans = srloop(IP(dst=dst_ip)/TCP(sport=RandShort(), dport=dst_port,flags='S'), count=p_count, inter=interval)
	ddv_tg_v_report('write', uuid, eut, host, src_ip, dst_ip, proto, p_count, interval, 'tcp_syn_v', int(pct_calc(int(len(ans)), int(p_count))))
	print(int(pct_calc(int(len(ans)), int(p_count))))
	return int(pct_calc(int(len(ans)), int(p_count)))

def udp_v(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval):
        dst_port = proto
        ans, unans = srloop(IP(dst=dst_ip)/UDP(sport=RandShort(), dport=dst_port), count=p_count, inter=interval)
        ddv_tg_v_report('write', uuid, eut, host, src_ip, dst_ip, proto, p_count, interval, 'udp_v', int(pct_calc(int(len(ans)), int(p_count))))
        print(int(pct_calc(int(len(ans)), int(p_count))))
        return int(pct_calc(int(len(ans)), int(p_count)))

def dns_v(uuid, eut, host, src_ip, dst_ip, proto, dns_q_name, dns_q_type):
	ans = sr1(IP(dst=dst_ip)/UDP(sport=RandShort(), dport=53)/DNS(rd=1,qd=DNSQR(qname=dns_q_name,qtype=dns_q_type)), timeout=2)
	try:
		print(int(pct_calc(int(len(ans)), int(len(ans)))))
		ddv_tg_v_report('write', uuid, eut, host, src_ip, dst_ip, proto, 1, 0, 'dns_v', int(pct_calc(int(len(ans)), int(len(ans)))))
		return int(pct_calc(int(len(ans)), int(len(ans))))
	except:
		print(0)
		return 0

def traceroute_v(uuid, host):
	result, unans = traceroute([host],maxttl=20)
	return result.show()

def pct_calc(part, whole):
	return 100 * float(part)/float(whole)


# Attack Traffic Generator scripts: These could allow responses from targets, in order to verify proper comms, but isn't a prerequisite

def icmp_flood_a(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval):  # p_count = 0?, inter=0.00001 for flooding
        send(IP(dst=dst_ip)/ICMP()/("DDV-A"*1000), count=p_count, inter=interval)
        ddv_tg_a_report(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval, 'icmp_flood_a', 0)
        return 0
        
def udp_flood_a(uuid, eut, host, src_ip, dst_ip, dst_vector, p_count, interval):
        send(IP(dst=dst_ip)/UDP(sport=RandShort(), dport=dst_vector), count=p_count, inter=interval)
        ddv_tg_a_report(uuid, eut, host, src_ip, dst_ip, dst_vector, p_count, interval, 'udp_flood_a', 0)
        return 0
        
def tcp_syn_flood_a(uuid, eut, host, src_ip, dst_ip, dst_vector, p_count, interval):
        dst_port = dst_vector
        send(IP(dst=dst_ip)/TCP(sport=RandShort(), dport=dst_port), count=p_count, inter=interval)
        ddv_tg_a_report(uuid, eut, host, src_ip, dst_ip, dst_port, p_count, interval, 'tcp_syn_flood_a', 0)
        return 0
        
def ipv4_flood_a(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval):  # p_count = 0?, inter=0.00001 for flooding
        send(IP(dst=dst_ip), count=p_count, inter=interval)
        ddv_tg_a_report(uuid, eut, host, src_ip, dst_ip, proto, p_count, interval, 'ipv4_flood_a', 0)
        return 0
        
def ra_flood_a(uuid, eut, host, src_ip, src_port, dst_ip, dst_port, p_count, interval):
        send(IP(dst=dst_ip)/UDP(sport=src_port, dport=dst_port), count=p_count, inter=interval)
        ddv_tg_a_report(uuid, eut, host, src_ip, dst_ip, dst_port, p_count, interval, 'ra_flood_a', 0)
        return 0

#uuid = 1591112673

#def main():
#	icmp_v(uuid, '192.168.88.25', 5, 0.5)
#	tcp_syn_v(uuid, '8.8.8.8', 53, 5, 2)
#	udp_v(uuid, '8.8.8.8', 53, 5, 1)
#	dns_v(uuid, '8.8.8.8', 'google.com', 'A')
#	#traceroute_v(uuid, 'www.cnn.com')
#	time.sleep(20)
#	main()

#main()
