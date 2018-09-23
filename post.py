from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
from time import time
import os
import requests
import signal
import sqlite3
import time
import sets
bd = '/home/pi/Documents/scripts/registro.db'
server = 'http://192.168.0.13:1337'
hostname = "google.com" #example

archivo = '/home/pi/Documents/scripts/clases.txt'
def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    
response = os.system("ping -c 1 " + hostname)

#and then check the response...
if response == 0:
	print hostname, 'is up!'  
	aux = 0
	lineas = len(open(archivo).readlines())
	with open(archivo) as f:
		content = f.readlines()
		f.close()
		#si hay conexion, enviar y reemplazar
		while aux < lineas:
			var1 = content[aux]
			var = var1
			clase = var[:15]
			var = clase+':ENVIADO\n'
			#si var y var1 son distintos significa que la clase no ha sido enviada, se procede a enviar y cambiar estado
			if var !=var1:
				conn = sqlite3.connect(bd)
				c = conn.cursor()
				c.execute("SELECT * FROM  CLASES WHERE CLA_ID=?",(clase,))
				a = c.fetchall()
				clase=str(clase)
				for row in a:
					a1 = '"id":'+'"'+clase+'"'+','#idestu
					a1 = a1+'"fecha":'+'"'+str(row[1])+'"'+','#fecha
					a1 = a1+'"runAcademico":'+'"'+row[2]+'"'+','#run academico
					a1 = a1+'"horaInicio":'+'"'+row[3]+'"'+','#hora inicio
					a1 = '{'+a1+'"horaTermino":'+'"'+row[4]+'"'+'}'#hora termino
					#datosjson = json.loads(a1)
					print a1
					r = requests.post(server+'/clases', data=a1)
					print(r.status_code, r.reason)

				c.execute("SELECT * FROM  ASISTENCIAS WHERE ASI_CLASE=?",(clase,))
				a = c.fetchall()
				for row in a:
					a1 = '"id":'+str(row[0])+','#id
					a1 = a1+'"clase":'+'"'+clase+'"'+','#clase
					a1 = a1+'"fecha":'+'"'+row[2]+'"'+','#fecha
					a1 = '{'+a1+'"runEstudiante":'+'"'+row[3]+'"'+'}'#runestudiante
					#datosjson = json.loads(a1)
					print a1
					r = requests.post(server+'/asistencias', data=a1)
					print(r.status_code, r.reason)
				replace(archivo, var1, var)
			aux = aux+1
else:
	print "se sigue esperando, no hay conexion"


