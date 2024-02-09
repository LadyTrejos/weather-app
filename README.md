# Prerrequisitos
Añadir al `export PYTHONPATH="${PYTHONPATH}:<path_to_weather_dict>"`

# Uso en dev
Para usarlo en desarrollo con Sawtooth en Ubuntu, se debe iniciar:
* El validador `sudo -u sawtooth sawtooth-validator -vv`
* El motor de consenso Devmode `sudo -u sawtooth devmode-engine-rust -vv --connect tcp://localhost:5050`
* La API REST `sudo -u sawtooth sawtooth-rest-api -v`
* El procesador de transacciones de configuración `sudo -u sawtooth settings-tp -v`
* Luego se ejecuta el archivo **main** para iniciar el procesador de transacciones para la aplicación `python3 main.py`  

### Opciones disponibles:
* **set:** guardar en la Blockchain un valor registrado por un sensor

```python3 cli.py set <parameter> <value> <sensor> <timestamp> --username <username>```

  > *\<parameter>* es el tipo de dato registrado por el sensor. Ejemplo: temperatura, humedad.  
  > *\<value>* es el valor registrado para ese parámetro.  
  *\<sensor>* es el nombre/identificador del sensor que registró el dato.  
  *\<timestamp>* es la fecha y hora en que se tomó la medida (formato: "DD/MM/AAAA HH:MM:SS")  
  *\<username>* (opcional) es el nombre que tiene la llave privada del usuario (por defecto toma el nombre de la sesión actual del pc)  
  Ejemplo: `python3 cli.py set temperatura 26.7 sensor1 "11/03/2021 14:07:34" --username my_key`
  
* **show:** mostrar el valor registrado por un sensor para un parámetro en un momento específico.  
```python3 cli.py show <parameter> <sensor> <timestamp>```

* **list:** mostrar todos los datos registrados en la cadena de bloques.
```python3 cli.py list```
