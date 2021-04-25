from A9G import A9G
import time

a9g = A9G("COM4")

while True:
	time.sleep(1)
	print(
"""1-IsOk
2-Llamar
3-Enviar mensaje
4-Contestar
5-Colgar
6-Conectar a broker MQTT
7-Publicar mensaje a topico
8-Suscribirse a topico
9-Desconectar MQTT 
10-Conectar GPS
11-Apagar el GPS
12-Obtener Posicion
""")
	x = input("\nIngrese opcion: ")
	if(x=="1"):
		a9g.isOk()
	if(x=="2"):
		phoneNumber = input("\nIngrese número ej(+549XXXXXXXXXX): ")
		a9g.callTo(phoneNumber=phoneNumber)
	if(x=="3"):
		phoneNumber = input("\nIngrese número ej(+549XXXXXXXXXX): ")
		text = input("\nIngrese mensaje: ")
		a9g.sendText(phoneNumber=phoneNumber,text=text)
	if(x=="4"):
		a9g.answerPhone()
	if(x=="5"):
		a9g.ringOff()
	if(x=="6"):
		host = input("\nIngrese Host: ")
		port = input("\nIngrese Puerto: ")
		user = input("\nIngrese Usuario: ")
		password = input("\nIngrese Password: ")
		a9g.mqttConnect(host=host,port=port,user=user,password=password)
	if(x=="7"):
		topic = input("\nIngrese Topico: ")
		mensaje = input("\nIngrese mensaje: ")
		a9g.mqttPublish(topic=topic,msj=mensaje)
	if(x=="8"):
		topic = input("\nIngrese Topico: ")
		a9g.mqttSuscribe(topic=topic)
	if(x=="9"):
		a9g.mqttDisconnect()
	if(x=="10"):
		a9g.gpsConnectAGPS(activarRastreo=True)
	if(x=="11"):
		a9g.gpsDisconnect()
	if(x=="12"):
		lat, lng = a9g.gpsGetLocation()
		print("http://maps.google.com/maps?q={},{}&z=17".format(lat,lng))
		print("Lat > ",lat)
		print("Lng > ",lng)