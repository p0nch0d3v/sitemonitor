#!/usr/bin/python3

import sqlite3
import ast
from datetime import datetime

db_file_name = 'site_monitor.db'
db_table_name = 'SiteStatus'
datetime_format = '%Y-%m-%d %H:%M:%S.%f'
table_info_cache = {}

def db_check_status(site_name, new_status):
    need_notify = False
    current_status = db_get_status(site_name)
    previous_status = None
    if current_status == None:
        if new_status['host']['result'] == False or new_status['page']['result'] == False:
            need_notify = True
        db_set_status(site_name, new_status)
    else:
        host_result = current_status['host']['result'] != new_status['host']['result']
        page_result = current_status['page']['result'] != new_status['page']['result']
        host_ip = get_dict_value(current_status['host'], 'ip') != get_dict_value(new_status['host'], 'ip')
        host_fqdn = get_dict_value(current_status['host'], 'FQDN') != get_dict_value(new_status['host'], 'FQDN')
        page_code = get_dict_value(current_status['page'], 'code') != get_dict_value(new_status['page'], 'code')
        if host_result == True or page_result == True or host_ip == True or host_fqdn == True or page_code == True:
             need_notify = True
             new_status['EventNumber'] = current_status['EventNumber'] + 1
             previous_status = current_status
             db_update_status(site_name, new_status)
    current_status = db_get_status(site_name)
    return {'notify': need_notify, 'current_status': current_status, 'previous_status': previous_status}

def db_get_status(site_name):
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    p = (site_name,)
    c.execute('SELECT HostResult, HostIp, HostFQDN, PageResult, PageCode, PageMsg, LastUpdate, EventNumber FROM {tn} WHERE Name="{n}"'.format(tn= db_table_name,n= site_name))
    current_status = c.fetchone()
    conn.close()
    if current_status != None:
        current_status = {'host': {'result': bool(current_status[0]), 'ip': current_status[1], 'FQDN': current_status[2]}, 'page': {'result': bool(current_status[3]), 'code': current_status[4], 'msg': str(current_status[5])}, 'LastUpdate': datetime.strptime(current_status[6], datetime_format).strftime(datetime_format), 'EventNumber': int(current_status[7])}
    return current_status

def db_set_status(site_name, new_status):
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    values = (site_name,
        new_status['host']['result'],
        get_dict_value(new_status['host'], 'ip'),
        get_dict_value(new_status['host'], 'FQDN'),
        new_status['page']['result'],
        get_dict_value(new_status['page'], 'code'),
        str(get_dict_value(new_status['page'], 'msg')),
        datetime.now().strftime(datetime_format), )
    c.execute('INSERT INTO %s (Name, HostResult, HostIp, HostFQDN, PageResult, PageCode, PageMsg, LastUpdate, EventNumber) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)' % db_table_name, values)
    conn.commit()
    conn.close()

def db_update_status(site_name, new_status):
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    values = (new_status['host']['result'],
        get_dict_value(new_status['host'], 'ip'),
        get_dict_value(new_status['host'], 'FQDN'),
        new_status['page']['result'],
        get_dict_value(new_status['page'], 'code'),
        str(get_dict_value(new_status['page'], 'msg')),
        datetime.now().strftime(datetime_format),
        new_status['EventNumber'],
        site_name, )
    c.execute('UPDATE %s SET HostResult = ?, HostIp = ?, HostFQDN = ?, PageResult = ?, PageCode = ?, PageMsg = ?, LastUpdate = ?, EventNumber = ? WHERE Name = ?' % db_table_name, values)
    conn.commit()
    conn.close()

def get_dict_value(dict, key, default=None):
    if key in dict:
        return dict[key]
    else:
        if type(default) != type(None):
            return default
        else:
            return None

def db_init():
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {tn} (Name TEXT, HostResult BOOLEAN, PageResult BOOLEAN)'.format(tn= db_table_name))
    conn.commit()
    if table_has_column(db_table_name, 'HostIp') is False:
        c.execute('ALTER TABLE {tn} ADD COLUMN HostIp TEXT NULL'.format(tn=db_table_name))
        conn.commit()
    if table_has_column(db_table_name, 'HostFQDN') is False:
        c.execute('ALTER TABLE {tn} ADD COLUMN HostFQDN TEXT NULL'.format(tn=db_table_name))
        conn.commit()
    if table_has_column(db_table_name, 'PageCode') is False:
        c.execute('ALTER TABLE {tn} ADD COLUMN PageCode TEXT NULL'.format(tn=db_table_name))
        conn.commit()
    if table_has_column(db_table_name, 'PageMsg') is False:
        c.execute('ALTER TABLE {tn} ADD COLUMN PageMsg TEXT NULL'.format(tn=db_table_name))
        conn.commit()
    if table_has_column(db_table_name, 'LastUpdate') is False:
        c.execute('ALTER TABLE {tn} ADD COLUMN LastUpdate TEXT NULL'.format(tn=db_table_name))
        conn.commit()
    if table_has_column(db_table_name, 'LastUpdate') is False:
        c.execute('ALTER TABLE {tn} ADD COLUMN EventNumber INT NULL'.format(tn=db_table_name))
        conn.commit()
    conn.commit()
    conn.close()
    print(get_table_info(db_table_name, True))

def table_has_column(table_name, column_name):
    table_info = get_table_info(table_name)
    for col in table_info:
        if col[1] == column_name:
            return True
    return False

def get_table_info(table_name, force=False):
    if get_dict_value(table_info_cache, table_name) is None or force is True:
        conn = sqlite3.connect(db_file_name)
        with conn:
            cur = conn.cursor()
            cur.execute('PRAGMA table_info({tn})'.format(tn=table_name))
            info = cur.fetchall()
            for d in info:
                print(d[0], d[1], d[2])
        conn.close()
        table_info_cache[table_name] = info
    else:
        info = table_info_cache[table_name]
    return info
