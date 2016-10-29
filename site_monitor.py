#!/usr/bin/python3

import http.client
import socket
import sys
import urllib
import urllib.request
import urllib.response
import urllib.error
import threading
import json
import os
import getopt
from datetime import datetime
from datetime import date
from smtplib import SMTP

import site_monitor_config
from site_monitor_db import *

log = {
    'directory': 'log',
    'global_filename': 'site_monitor',
    'mail_filename': 'site_monitor_mail'
}

def is_host_online(host, timeout= 10):
    try:
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(host)
        fqdn = socket.getfqdn(host)
        return {'result': True, 'ip': str(ip), 'FQDN': str(fqdn), 'msg': None}
    except:
        exception = str((sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
        write_log(log['global_filename'], exception)
        return {'result': False, 'ip': None, 'FQDN': None, 'msg': sys.exc_info()[1]}

def is_page_available(page):
    try:
        response = urllib.request.urlopen(page)
        html = response.read()
        return {'result': True, 'code': str(response.code), 'msg': str(response.msg)}
    except urllib.error.HTTPError as e:
        write_log(log['global_filename'], (e, (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
        return {'result' : False, 'code' : str(e.code), 'msg' : e.read()}
    except urllib.error.URLError as e:
        write_log(log['global_filename'], (e, (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
        return {'result': False, 'code': '500', 'msg': e.reason}
    except:
        write_log(log['global_filename'], (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
        return {'result': False, 'code': '500', 'msg': sys.exc_info()[1]}

def get_page_status(name, host, page, notify_address, timeout=10):
    if name is None or len(name) == 0:
        raise Error("No name defined")
    if host is None or len(host) == 0:
        raise Error("No host defined")
    global_notify_address = site_monitor_config.config['global']['notify']
    all_notify_address = notify_address + list(set(global_notify_address) - set(notify_address))
    if all_notify_address is None or len(all_notify_address) == 0:
        raise Error("No notification address defined")

    host_status = is_host_online(host, timeout)
    page_status = is_page_available(page)
    result = {'host': host_status, 'page': page_status }
    filename = name
    need_notify = db_check_status(name, result)
    write_log(filename, need_notify)
    if (need_notify['notify'] == True):
        normalize_page_msg(need_notify['previous_status'])
        normalize_page_msg(need_notify['current_status'])
        previous_status_str = str(json.dumps(need_notify['previous_status'], sort_keys=True, indent=4))
        current_status_str = str(json.dumps(need_notify['current_status'], sort_keys=True, indent=4))
        body = 'Previous: ' + previous_status_str + '\r\n\r\n' + 'Current: ' + current_status_str
        send_notification_email(to_address=all_notify_address, subject='[{name}] - Site status changed #{eventNumber}'.format(name=name, eventNumber=need_notify['current_status']['EventNumber']), body=body)

def normalize_page_msg(status):
    if type(status) != type(None) and type(status['page']) != type(None) and type(status['page']['msg']) != type(None):
        msg = status['page']['msg']
        if(len(msg) > 100):
            msg = msg[:49] + str("...") + msg[-49:]
        status['page']['msg'] = msg

def write_log(filename, message):
    if not os.path.exists(log['directory']):
        os.makedirs(log['directory'])
    now = datetime.now()
    filename = os.path.join(log['directory'], (filename + ("_" + now.strftime("%Y%m%d")) + ".log"))
    with open(filename, 'a') as out:
        message = str(now) + ' - '+ str(message) + '\n'
        out.write(message)

def send_notification_email(to_address, subject, body):
    from_address = site_monitor_config.config['smtp']['from_address']

    server_address = site_monitor_config.config['smtp']['server']
    port = site_monitor_config.config['smtp']['port']
    server = SMTP('{server}:{port}'.format(server=server_address, port=port))
    server.starttls()

    user = site_monitor_config.config['smtp']['login']['user']
    password = site_monitor_config.config['smtp']['login']['password']
    server.login(user, password)

    body = '\r\n'.join(['To: %s' % to_address, 'From: %s' % from_address, 'Subject: %s' % subject, '', body])

    server.sendmail(from_address, to_address, body)
    server.quit()

    write_log(log['mail_filename'], body)

def check_internet(host, page):
    host_status = is_host_online(host)
    page_status = is_page_available(page)
    return (host_status['result'] and page_status['result'])

def parse_arguments(argv):
    options = {'dbupdate': False}
    opts, args = getopt.getopt(argv,"d", ['db-update'])
    for opt, arg in opts:
        if opt in ("-d", "--db-update"):
            options['dbupdate'] = True
    return options

def main(argv):
    try:
        options = parse_arguments(argv)
        print(options)
        if get_dict_value(options, 'dbupdate', False) is True:
            db_init()
        else:
            internet_site = [s for s in site_monitor_config.config['sites'] if get_dict_value(s, 'reference', False) == True]
            if(internet_site is not None and len(internet_site) > 0):
                internet_site = internet_site[0]
                if check_internet(internet_site['host'], internet_site['url']):
                    sites = [s for s in site_monitor_config.config['sites'] if (get_dict_value(s, 'reference', False) == False and get_dict_value(s, 'enabled', False) == True)]
                    for site in sites:
                        if get_dict_value(site, 'reference', False) == False:
                            t = threading.Thread(target=get_page_status, args=(site['name'], site['host'], site['url'], site['notify'], site['timeout']))
                            t.start()
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    except:
        str(sys.exc_info()[0]) + ' | ' + str(sys.exc_info()[1]) + ' | ' + str(sys.exc_info()[2])
        write_log(log['global_filename'], text)

if __name__ == "__main__":
    main(sys.argv[1:])
