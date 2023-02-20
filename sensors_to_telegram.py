# alarms send me a message in a telegram channel
# works with i5 Chinese mini pc 
 
import psutil
import os
import requests
import time
import subprocess

def send_telegram(text: str):
    token = "5751913776:YOUR_TOKEN_MUST_BE_HERE"
    url = "https://api.telegram.org/bot"
    
    # who gets the channel id
    #https://api.telegram.org/bot5751913776:YOUR_TOKEN_MUST_BE_HERE/getUpdates
    channel_id = "-1001numbers7202"
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
         "chat_id": channel_id,
         "text": text
          })

    if r.status_code != 200:
        raise Exception("post_text error")

def print_or_send_to_telegram(warning, values_for_print):
    #print(warning + values_for_print)
    send_telegram(warning + values_for_print)

def get_names_and_values(gotten_name):
    names_and_values = ''
    if hasattr(psutil, "sensors_temperatures"):
        sensors_temperatures = psutil.sensors_temperatures()
        for name, entries in sensors_temperatures.items():
            for entry in entries:
                if name == gotten_name:
                    names_and_values += str(name) + str(entry.label) + " = " + str(entry.current) + "\n"
    return names_and_values
    
def get_motherboard_temperature(host_name, last_status, motherboard_alarm_value):

    names_and_values = get_names_and_values('acpitz')
    motherboard_current_value = psutil.sensors_temperatures().get('acpitz')[1][1]
    motherboard_high_str = 'Motherboard alarm temperature = ' + str(motherboard_alarm_value)
    values_for_print = "\n" + names_and_values + motherboard_high_str + "\n"
    
    if motherboard_current_value >= motherboard_alarm_value and last_status == 'NORMAL':
        warning = host_name + 'The motherboard is High'
        print_or_send_to_telegram(warning, values_for_print)
        return 'ALARM'
    elif motherboard_current_value < motherboard_alarm_value and last_status == 'ALARM':
        warning = host_name + 'The motherboard is Normal'
        print_or_send_to_telegram(warning, values_for_print)
        return 'NORMAL'    
    else:
        return last_status
        
        
def get_cpu_temperature(host_name, last_status, CPU_alarm_value):

    names_and_values = get_names_and_values('coretemp')

    CPU_current_value = psutil.sensors_temperatures().get('coretemp')[0][1]
    high_str = 'CPU alarm temperature = ' + str(CPU_alarm_value)
    values_for_print = "\n" + names_and_values + high_str + "\n"
               
    if CPU_current_value >= CPU_alarm_value and last_status == 'NORMAL':
        warning = host_name + 'Temperature of CPU is High'
        print_or_send_to_telegram(warning, values_for_print)
        return 'ALARM'
    elif CPU_current_value < CPU_alarm_value and last_status == 'ALARM':
        warning = host_name + 'Temperature of CPU is Normal'
        print_or_send_to_telegram(warning, values_for_print)
        return 'NORMAL'
    else:
        return last_status

def get_hdd_temperature(host_name, name_hdd_sda, last_status, alarm_value_hdd):
    # There is another way to use it
    
    # hddtemp needs sudo (root)
    # chmod a+s /usr/sbin/hddtemp
    # and change hddtemp to /usr/sbin/hddtemp 
    
    output = subprocess.check_output(['/usr/sbin/hddtemp', name_hdd_sda])
    output = output.decode('UTF-8')
    output = output.split(' ')
    text = output[0] + " " + output[1] + " " + output[2]
    current_value_hdd = int(output[3][:-3])
    end_text = output[3][-3:] # + "\n"
    high_str = 'HDD alarm temperature = ' + str(alarm_value_hdd)
    values_for_print = "\n" + text + str(current_value_hdd) + "\n" + high_str + end_text

    if current_value_hdd >= alarm_value_hdd and last_status == 'NORMAL': 
        warning = host_name + 'Temperature ' + name_hdd_sda + ' is High'
        print_or_send_to_telegram(warning, values_for_print)
        return 'ALARM'
    elif current_value_hdd < alarm_value_hdd and last_status == 'ALARM': 
        warning = host_name + 'Temperature ' + name_hdd_sda + ' is Normal'
        print_or_send_to_telegram(warning, values_for_print)
        return 'NORMAL'
    else:
        return last_status
        
def get_disk_space(host_name, disk_space_name, last_status, disk_alarm_value):
    hdd = psutil.disk_usage(disk_space_name)
    hdd_total = "Status '/' \nTotal: " + str(round(int(hdd.total) /  (2**30),2)) + " GB\n"
    hdd_used = "Used: " + str(round(int(hdd.used) /  (2**30),2)) + " GB\n"
    hdd_free = "Free: " + str(round(int(hdd.free) /  (2**30),2)) + " GB\n"
    hdd_percent = "Percent: " + str(hdd.percent)
    
    values_for_print = "\n" + hdd_total + hdd_used + hdd_free + hdd_percent + "\ndisk alarm value: " + str(disk_alarm_value)
    
    if hdd.percent >=  disk_alarm_value and last_status == 'NORMAL': 
        warning = host_name + 'Space of ' + disk_space_name + ' is High'
        print_or_send_to_telegram(warning, values_for_print)
        return 'ALARM'
    elif hdd.percent <  disk_alarm_value and last_status == 'ALARM':
        warning = host_name + 'Space of ' + disk_space_name + ' is Normal'
        print_or_send_to_telegram(warning, values_for_print)
        return 'NORMAL'
    else:
        return last_status  

def main():

    host_name = 'CITADELDEVELOP' + ": "
    
    motherboard_status = 'ALARM'
    motherboard_alarm_value = 60 #60  30 =  testing values 
    
    status_cpu = 'ALARM' #'NORMAL' =  testing values 
    CPU_alarm_value = 80 #80 55 =  testing values 
    
    status_hdd_sda = 'ALARM'
    name_hdd_sda = '/dev/sda'    
    high_value_hdd = 50 #50 42 =  testing values 
        
    disk_space_status = 'ALARM' #'NORMAL' =  testing values 
    disk_space_name = '/'
    disk_space_alarm_value = 80

    while 1:
        motherboard_status = get_motherboard_temperature(host_name, motherboard_status, motherboard_alarm_value)
        status_cpu = get_cpu_temperature(host_name, status_cpu, CPU_alarm_value)      
        status_hdd_sda = get_hdd_temperature(host_name, name_hdd_sda, status_hdd_sda, high_value_hdd)
        disk_space_status = get_disk_space(host_name, disk_space_name,  disk_space_status, disk_space_alarm_value)
        time.sleep(300) #6 600  =  testing values 
main()
