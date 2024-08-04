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

#///////////////////////////////////ACCESS MYSQL/////////////////////////////
db = mysql.connector.connect(
  host="192.168.31.10",
  user="ruse",
  passwd="123",
  database="rumahsensor"
  )
print("ok konek")
cursor = db.cursor()
db.ping(reconnect=True)
#///////////////////////////////////ACCESS MYSQL/////////////////////////////

serGPS = serial.Serial(
            port='/dev/ttyUSB0',\
            baudrate=115200,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=100)
        
ser = serial.Serial(
    port='/dev/ttyUSB1',\
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
            suhuair = dataSensor[0]
            suhu = dataSensor[1]
            hum  = dataSensor[2]
            Vaki = dataSensor[3]
            Aaki = dataSensor[4]
            

            
            
            data = serGPS.readline()
            a= a+1
            
            print(str(a))
                        
            stringData = data.decode('utf-8')
            #print(stringData)
            print("lewat string data")

            header = stringData[:2]
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
        

                lat = dataGPS[0]
                long = dataGPS[1]
                course = dataGPS[2]
                dataSVS = dataGPS[3]
                d = date.today()

                
                serGPS.write(kirimWhere)
        
                

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
        
 
                lat = dataGPS[0]
                long = dataGPS[1]
                course = dataGPS[2]
                dataSVS = dataGPS[3]
                d = date.today()

                
                serGPS.write(kirimWhere)
                serGPS.write(kirimStatus)

        
            else:
                print("else")
                lat='0'
                long='0'
                course='0'
                dataSVS='0'
                d = date.today()

                serGPS.write(kirimWhere)
                serGPS.write(kirimStatus)
                
            print (freqstring,';',powerstring,';',suhuair,';', suhu,';', hum, ';',Vaki,';',Aaki,';',lat,';',long,';',course,';',dataSVS)
            sql = "INSERT INTO datars (Frequensi, amplitude, Vaki, Aaki, Suhuair, Suhu, Humiditas, latitude, longitude, course, satelit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (freqstring, powerstring, Vaki, Aaki,suhuair, suhu, hum, lat, long, course, dataSVS)
            cursor.execute(sql, val)
            db.commit()
            print(cursor.rowcount, "ok masuk")
            sleep(5)

s_Sensor.close()
s_GPS.close()
sdr.close()
