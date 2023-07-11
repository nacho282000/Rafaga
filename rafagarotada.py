import http.client
import json
import os
import time
import subprocess

# configurar la dirección IP y la clave de API de deCONZ
deconz_ip = "192.168.0.117"
api_key = "D782C80C89"

# ID del sensor de puerta
sensor_id = "00:15:8d:00:08:c9:6b:8b-01-0006"

# establecer la carpeta de destino de las imágenes
folder_path = "/home/nacho/fotos"

# contar el número de imágenes tomadas
image_counter = 1

# crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# configurar la conexión HTTP
conn = http.client.HTTPConnection(deconz_ip, port=8080)

# establecer el estado anterior del sensor como desconocido
last_sensor_state = None

# tiempo límite para tomar fotos después de que la puerta esté abierta (30 segundos)
time_limit = 30

# tiempo de espera entre cada foto (1 segundo por defecto)
wait_time = 1

# bucle infinito para comprobar el estado del sensor
while True:
    # obtener el estado del sensor
    url = "/api/" + api_key + "/sensors/" + sensor_id
    conn.request("GET", url)
    response = conn.getresponse()

    # analizar la respuesta JSON
    if response.status == 200:
        response_json = json.loads(response.read().decode('utf-8'))
        sensor_state = response_json["state"]["open"]
        if last_sensor_state is None:
            # si el estado anterior es desconocido, establecerlo como el estado actual
            last_sensor_state = sensor_state
        elif sensor_state != last_sensor_state:
            # si el estado actual es diferente al estado anterior, tomar una foto y guardarla
            if sensor_state:
                print("Puerta abierta, tomando fotos...")
                time_elapsed = 0
                while sensor_state and time_elapsed < time_limit:
                    time.sleep(wait_time)  # esperar antes de tomar otra foto
                    image_name = "imagen" + str(image_counter) + ".jpg"
                    image_path = folder_path + "/" + image_name
                    # Captura la imagen con fswebcam y la rota 270 grados
                    subprocess.run(["fswebcam", "-r", "1280x720", "-S", "3", "--jpeg", "95", "--rotate", "270", "--save", image_path])
                    print("Imagen guardada como:", image_path)
                    image_counter += 1
                    time_elapsed += wait_time
                    # obtener el estado actual del sensor después de tomar una foto
                    conn.request("GET", url)
                    response = conn.getresponse()
                    if response.status == 200:
                        response_json = json.loads(response.read().decode('utf-8'))
                        sensor_state = response_json["state"]["open"]
                    else:
                        print("Error al obtener el estado del sensor.")
                print("Se detuvo la toma de fotos.")
            # actualizar el estado anterior del sensor
            last_sensor_state = sensor_state
    else:
        print("Error al obtener el estado del sensor.")

    # esperar un segundo antes de volver a comprobar el estado del sensor
    time.sleep(1)

# cerrar la conexión
conn.close()
