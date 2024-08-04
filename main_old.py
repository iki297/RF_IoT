import serial
import socket
import pymysql
from datetime import date
from datetime import time
from datetime import datetime
from time import sleep
import mysql.connector
from pylab import *
from rtlsdr import *
import numpy as np
import paho.mqtt.client as paho             #mqtt library
import os
import json
from datetime import datetime

#/////////////////////////////////////Access Thingsboard/////////////////////////////////
ACCESS_TOKEN='tkrs'                 #Token of your device
broker="202.46.7.33"                #host name
port=1883                       #data listening port

def on_publish(client,userdata,result):             #create function for

    print("data published to thingsboard \n")
    pass

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client1= paho.Client("control1")                    #create client object
client1.on_publish = on_publish                     #assign function to
client1.on_connect = on_connect

client1.username_pw_set(ACCESS_TOKEN)               #access token from

client1.connect(broker,port,keepalive=60) 
#////////////////////////////////////THINGSBOARD ACCESS//////////////////////////////////////////////

#///////////////////////////////////ACCESS MYSQL/////////////////////////////
db = mysql.connector.connect(
  host="192.168.31.10",
  user="root",
  passwd="",
  database="rumahsensor"
  )
print("ok konek")
cursor = db.cursor()
db.ping(reconnect=True)
#///////////////////////////////////ACCESS MYSQL/////////////////////////////

serGPS = serial.Serial(
            port='/dev/ttyUSB1',\
            baudrate=115200,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=100)
        
ser = serial.Serial(
    port='/dev/ttyUSB0',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=100)
        
print('connected to: ' + serGPS.portstr + ser.portstr )
        
comWhere = 'AT^GT_CM=WHERE\r\n'
kirimWhere = comWhere.encode('utf-8')
comStatus = 'AT^GT_CM=STATUS\r\n'
kirimStatus = comStatus.encode('utf-8')
serGPS.write(kirimWhere)
a=0
print (str(a))
sdr = RtlSdr()

# configure device
sdr.sample_rate = 2.4e6
sdr.center_freq = 16e8
sdr.gain = 'auto'

samples = sdr.read_samples(256*1024)


while True:
            power, freq = psd(samples, NFFT=1024, Fs=sdr.sample_rate/1.45e3, Fc=sdr.center_freq/1e6)
            xlabel('Frequency (MHz)')
            ylabel('Relative power (dB)')
            powerstring=""
            freqstring=""
            for i in range(1,1024):
                powerstring= powerstring +","+ str ('{:.5}'.format(power[i]))
                freqstring= freqstring+","+ str ('{:.7}'.format(freq[i]))
            
            ser.flush()
            msg = ser.readline()
            strMsg = msg.decode('utf-8')
            msgRep = strMsg.replace('\r\n','')
            print(msgRep)
            dataSensor = msgRep.split(',')
            suhu = dataSensor[0]
            hum  = dataSensor[1]
            Vaki = dataSensor[2]
            Aaki = dataSensor[3]
            
#////////////////////Send data to THINGSBOARD//////////////////////////
            payload = "{"
            payload+="\"Suhu\":suhu,";
            payload += "\"Kelembaban\":hum,";
            payload += "\"Voltage\":Vaki,";
            payload += "\"Current\":Aaki";
            payload += "}"

            ret = client1.publish("simple", payload)  # topic-

            print("Please check LATEST TELEMETRY field of your device")
            print(payload)

            time.sleep(1)
#////////////////////Send data to THINGSBOARD//////////////////////////
            
            
            data = serGPS.readline()
            a= a+1
            
            print(str(a))
                        
            stringData = data.decode('utf-8')
            #print(stringData)
            print("lewat string data")

            header = stringData[:4]
            if (header == 'Last'):
                print('masuk last')
                delData1 = stringData.replace('Last position! Lat:S','')
                delData2 = delData1.replace('Lon:E','')
                delData3 = delData2.replace('Course:','')
                delData4 = delData3.replace('Speed:','')
                delData5 = delData4.replace('Km/h','')
                delData6 = delData5.replace('DateTime:','')
                delData7 = delData6.replace('\r\n','')
                dataGPS = delData7.split(',')
        
                #Value
                lat = dataGPS[0]
                long = dataGPS[1]
                course = dataGPS[2]
                dataSVS = dataGPS[3]
                d = date.today()
#                 t = datetime.time(datetime.today())
                #dt= dateTime

                print (freqstring,';',powerstring,';', suhu,';', hum, ';',Vaki,';',Aaki,';',lat,';',long,';',course,';',dataSVS)
                sql = "INSERT INTO datars (Frequensi, amplitude, Vaki, Aaki, Suhu, Humiditas, latitude, longitude, course, satelit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (freqstring, powerstring, Vaki, Aaki, suhu, hum, lat, long, course, dataSVS)
                cursor.execute(sql, val)
                db.commit()
                print(cursor.rowcount, "ok masuk")
                
                serGPS.write(kirimWhere)
        
                
                sleep(1)
                serGPS.write(kirimStatus)

            elif (header == 'Curr'):
                print('masuk curr')
                delData1 = stringData.replace('Current position! Lat:S','')
                delData2 = delData1.replace('Lon:E','')
                delData3 = delData2.replace('Course:','')
                delData4 = delData3.replace('Speed:','')
                delData5 = delData4.replace('Km/h','')
                delData6 = delData5.replace('DateTime:','')
                delData7 = delData6.replace('\r\n','')
                dataGPS = delData7.split(',')
        
                #Value
                lat = dataGPS[0]
                long = dataGPS[1]
                course = dataGPS[2]
                dataSVS = dataGPS[3]
                d = date.today()
#                 t = datetime.time(datetime.today())
                print (freqstring,';',powerstring,';', suhu,';', hum, ';',Vaki,';',Aaki,';',lat,';',long,';',course,';',dataSVS)
                sql = "INSERT INTO datars (Frequensi, amplitude, Vaki, Aaki, Suhu, Humiditas, latitude, longitude, course, satelit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (freqstring, powerstring, Vaki, Aaki, suhu, hum, lat, long, course, dataSVS)
                cursor.execute(sql, val)
                db.commit()
                print(cursor.rowcount, "ok masuk")
                
                serGPS.write(kirimWhere)
        
#                 print(d,';',t,';',pesanGPSaja)
                sleep(1)
                serGPS.write(kirimStatus)
#                 print('test1')
        
            else:
                print("else")
                lat='0'
                long='0'
                course='0'
                dataSVS='0'
                d = date.today()
#                 t = datetime.time(datetime.today())
                
                print (freqstring,';',powerstring,';', suhu,';', hum, ';',Vaki,';',Aaki,';',lat,';',long,';',course,';',dataSVS)
                sql = "INSERT INTO datars (Frequensi, amplitude, Vaki, Aaki, Suhu, Humiditas, latitude, longitude, course, satelit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (freqstring, powerstring, Vaki, Aaki, suhu, hum, lat, long, course, dataSVS)
                cursor.execute(sql, val)
                db.commit()
                print(cursor.rowcount, "ok masuk")
                
                sleep(1)
                serGPS.write(kirimWhere)
                

            
        #print('test3')
s_Sensor.close()
s_GPS.close()
sdr.close()
