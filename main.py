#!/usr/bin/env python
# -*- coding: utf8 -*-


import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import sqlite3

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# mensajes iniciales
print "Permanezca tarjeta hasta que se apague la luz verde."
print "Presione Ctrl-C para detener."
key = [0xA0,0xA1,0xA2,0xA3,0xA4,0xA5]
GPIO.setwarnings(False)
#id capturador -> asociado a facultad y sala
id_capturador="ING301"
#bucle para leer tarjetas
#el primero en pasar la tarjeta debe ser el docente
docente=False
docente_id=None
terminar_clase=False
#base de datos
bd = '/home/pi/Documents/scripts/registro.db'
while continue_reading:
	
	#declaracion de variables e inicializacion de GPIO 
	condicion=None
	rut=None
	nombre=None
	paterno=None
	materno=None
	led_verde=32
	led_rojo=37
	#buzzer mute 31
	#buzzer on 29
	buzzer=31
	control = True
	ciclo = 0
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(led_verde,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(led_rojo,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.LOW)

	#obtener condicion (academico/estudiante)
	while continue_reading:
		# Scan for cards    
		(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
		# If a card is found
		#if status == MIFAREReader.MI_OK:
		# Get the UID of the card
		(status,uid) = MIFAREReader.MFRC522_Anticoll()
		# If we have the UID, continue
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(led_verde,GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(led_rojo,GPIO.OUT, initial=GPIO.LOW)
		if status == MIFAREReader.MI_OK:
			# This is the default key for authentication
			# Select the scanned tag
			MIFAREReader.MFRC522_SelectTag(uid)
			numero = 80

			# Authenticate
			status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, numero, key, uid)
			# Check if authenticated
			if status == MIFAREReader.MI_OK:
				GPIO.output(led_verde,GPIO.HIGH)
				#GPIO.output(buzzer,GPIO.HIGH)
				condicion = MIFAREReader.MFRC522_Read(numero)
				#print condicion+"."
				if condicion!="error":
					GPIO.output(led_verde,GPIO.HIGH)
					ciclo = ciclo+1
				MIFAREReader.MFRC522_StopCrypto1()
			else:
				print "Authentication error"
				GPIO.output(led_rojo,GPIO.HIGH)
				control = False
				break
			break
		#si condicion es ACADEMICO, continuar el ciclo, caso contrario esperar otra tarjeta
		else:
			if(docente):
				GPIO.setmode(GPIO.BOARD)
				GPIO.setup(led_verde,GPIO.OUT, initial=GPIO.HIGH)
				time.sleep(.3)
				GPIO.setmode(GPIO.BOARD)
				GPIO.output(led_verde, GPIO.LOW)
				time.sleep(1.2)
			if(docente!=True):
				GPIO.setmode(GPIO.BOARD)
				GPIO.setup(led_verde,GPIO.OUT, initial=GPIO.HIGH)
				time.sleep(1)

	#obtener nombre
	cont = 0
	while continue_reading and control and ciclo == 1:  
		(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
		(status,uid) = MIFAREReader.MFRC522_Anticoll()
		if status == MIFAREReader.MI_OK:
			MIFAREReader.MFRC522_SelectTag(uid)
			numero = 72
			status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, numero, key, uid)
			if status == MIFAREReader.MI_OK:
				nombre = MIFAREReader.MFRC522_Read(numero)
				if nombre != "error":
					ciclo = ciclo+1
				MIFAREReader.MFRC522_StopCrypto1()
			else:
				print "Authentication error"
				control = False
				break
			break
		else:
			cont = cont+1
			if cont == 2:
				print "error al retirar tarjeta"
				control = False
			
	#obtener apellido paterno
	cont = 0
	while continue_reading and control and ciclo == 2:   
		(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
		(status,uid) = MIFAREReader.MFRC522_Anticoll()
		if status == MIFAREReader.MI_OK:
			MIFAREReader.MFRC522_SelectTag(uid)
			numero = 73
			status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, numero, key, uid)
			if status == MIFAREReader.MI_OK:
				paterno = MIFAREReader.MFRC522_Read(numero)
				if paterno!="error":
					ciclo = ciclo+1
				MIFAREReader.MFRC522_StopCrypto1()
			else:
				print "Authentication error"
				control = False
				break
			break
		else:
			cont = cont+1
			if cont == 2:
				print "error al retirar tarjeta"
				control = False
			
			
	#obtener apellido materno
	cont=0
	while continue_reading and control and ciclo == 3:  
		(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
		(status,uid) = MIFAREReader.MFRC522_Anticoll()
		if status == MIFAREReader.MI_OK:
			MIFAREReader.MFRC522_SelectTag(uid)
			numero = 74
			status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, numero, key, uid)
			if status == MIFAREReader.MI_OK:
				materno = MIFAREReader.MFRC522_Read(numero)
				if materno!="error":
					ciclo=ciclo+1
				MIFAREReader.MFRC522_StopCrypto1()
			else:
				print "Authentication error"
				control = False
				break
			break
		else:
			cont = cont+1
			if cont == 2:
				print "error al retirar tarjeta"
				control = False
			
			
	#obtener rut
	cont = 0
	while continue_reading and control and ciclo ==4: 
		(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
		(status,uid) = MIFAREReader.MFRC522_Anticoll()
		if status == MIFAREReader.MI_OK:
			MIFAREReader.MFRC522_SelectTag(uid)
			numero = 68
			status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, numero, key, uid)
			if status == MIFAREReader.MI_OK:
				rut = MIFAREReader.MFRC522_Read(numero)
				if rut != "error":
					ciclo == 5
				MIFAREReader.MFRC522_StopCrypto1()
			else:
				print "Authentication error"
				control = False
				break
			break
		else:
			cont = cont+1
			if cont == 2:
				print "error al retirar tarjeta"
				control = False
			
			
	#guardar si datos NO son None (null)
	#primeros datos a guardar->Datos docente
	#cambiar condicion por "ACADEMICO "
	if(rut=="18760504-0"):
		condicion = "ACADEMICO "
	if (rut!=None and nombre!=None and paterno!=None and materno!=None and control and condicion=="ACADEMICO " and docente==False):
		docente=True
		docente_id=rut
		#conexion y cursor a la BD sqlite

		conn = sqlite3.connect(bd)
		c = conn.cursor()
		#insertar en tabla clase
		fecha = time.strftime("%y/%m/%d")
		print "fecha "+fecha 
		hora_inicio = time.strftime("%H:%M")
		#c.execute("INSERT INTO clase (id_capturador, fecha, hora_inicio) VALUES (?,?,?)",(id_capturador, fecha, hora_inicio))
		#insertar en tabla CLASES
		id_clase = time.strftime("%m")
		id_clase = id_clase+time.strftime("%d")
		id_clase = id_clase+time.strftime("%H")
		id_clase = id_clase+time.strftime("%M")
		id_clase = id_clase+time.strftime("%S")
		id_clase = id_clase+rut[:5]
		print "id "+ id_clase
		print "fecha "+fecha
		print rut
		print hora_inicio
		c.execute("INSERT INTO CLASES (CLA_ID, CLA_FECHA, CLA_RUN_ACADEMICO, CLA_HORA_INICIO) VALUES (?,?,?,?)", (id_clase, fecha, rut, hora_inicio))
		#INSERT INTO CLASES (CLA_ID, CLA_FECHA, CLA_RUN_ACADEMICO, CLA_HORA_INICIO) VALUES (1,01/01/01,18760504-0,21:56)
		#alerta buzzer y leds
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.HIGH)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.LOW)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.HIGH)
		#enviar y guardar en DB local
	  	conn.commit()
		conn.close()
		#imprimir datos de tarjeta por pantalla
		print "docente inicia clase"
		print (condicion+ " RUT: "+rut+" Nombre: "+nombre+paterno+materno)
		#Dejar rut como None para que no entre al proximo ciclo
		rut=None
		
	
	#guardar datos alumnos
	#guardar si datos NO son None (null)
	
	if (rut!=None and nombre!=None and paterno!=None and materno!=None and control and condicion=="ESTUDIANTE" and docente):
		#conexion y cursor a la BD sqlite
		#conn = sqlite3.connect('prueba.db')
		conn = sqlite3.connect(bd)
		c = conn.cursor()
		#consulta para verificar que no existe estudiante en la db
		c.execute("select ASI_RUN_ESTUDIANTE from ASISTENCIAS where ASI_CLASE=? and ASI_RUN_ESTUDIANTE=?",(id_clase, rut))
		busqueda = c.fetchall()
		fecha = time.strftime("%y/%m/%d")
		#guardar estudiante si no existe en la db
		if (busqueda==[]):
			c.execute("INSERT INTO ASISTENCIAS (ASI_CLASE, ASI_FECHA, ASI_RUN_ESTUDIANTE) VALUES (?,?, ?)", (id_clase, fecha, rut))
		#alerta buzzer y leds
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.HIGH)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.LOW)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.HIGH)
		#enviar y guardar en DB local
		conn.commit()
		conn.close()
		#imprimir datos de tarjeta por pantalla
		print "estudiante se registra en asistencia clase"
		print (condicion+ " RUT: "+rut+" Nombre: "+nombre+paterno+materno)
	
	#tarjeta no valida, retirada antes de tiempo o no es el docente quien inicia primero la clase
	if (control == False or docente == False):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(led_verde,GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.HIGH)
		GPIO.setup(led_rojo,GPIO.OUT, initial=GPIO.HIGH)
		time.sleep(.4)
	
	#dejar de guardar asistencia si docente vuelve a pasar tarjeta 
	if(docente and rut==docente_id):
		#docente en iniciar clase vuelve a pasar tarjeta->terminar clase 
		docente=False
		docente_id=None
		#conn = sqlite3.connect('prueba.db')
		conn = sqlite3.connect(bd)
		c = conn.cursor()
		hora_termino = time.strftime("%H:%M")
		c.execute("UPDATE CLASES SET CLA_HORA_TERMINO=? WHERE CLA_ID=?", (hora_termino, id_clase))
	  	conn.commit()
		conn.close()
		#crear archivo para enviar via post
		f = open('clases.txt','a')
		f.write(id_clase+':PENDIENTE\n')
		f.close()
		#alerta buzzer y leds
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.HIGH)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.LOW)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.HIGH)
		print "docente termina clase"
	#si docente 2 (otro docente) pasa la TUI
	##cambiar a "ACADEMICO "
	if(docente and rut!=None and rut!=docente_id and condicion!="ESTUDIANTE"):
		#docente 2 pasa la tarjeta->terminar clase, iniciar clase 
		docente_id=rut
		conn = sqlite3.connect(bd)
		c = conn.cursor()
		hora_termino = time.strftime("%H:%M")
		c.execute("UPDATE CLASES SET CLA_HORA_TERMINO=? WHERE CLA_ID=?", (hora_termino, id_clase))
		f = open('clases.txt','a')
		f.write(id_clase+':PENDIENTE\n')
		f.close()
	  	conn.commit()
		id_clase = time.strftime("%Y %B %D")[12:14]
		id_clase = id_clase+time.strftime("%Y %B %D")[15:17]
		id_clase = id_clase+time.strftime("%H")
		id_clase = id_clase+time.strftime("%M")
		id_clase = id_clase+time.strftime("%S")[:2]
		id_clase = id_clase+rut[:6]
		hora_inicio = time.strftime("%H:%M")
		c.execute("INSERT INTO CLASES (CLA_ID, CLA_FECHA, CLA_RUN_ACADEMICO, CLA_HORA_INICIO) VALUES (?,?,?,?)",(id_clase, fecha, rut, hora_inicio))
		conn.close()
		#crear archivo para enviar via post
		
		
		#alerta buzzer y leds
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.HIGH)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.LOW)
		time.sleep(.15)
		GPIO.output(buzzer,GPIO.HIGH)
		print "docente termina clase"
		print "docente inicia clase"
		print (condicion+ " RUT: "+rut+" Nombre: "+nombre+paterno+materno)
	
	#esperar un tiempo y apagar pines
	time.sleep(.2)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(led_verde,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(led_rojo,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.LOW)
	GPIO.cleanup()
	time.sleep(.65)
