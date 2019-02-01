from flask import Flask
from flask import render_template
# Import des utilitaires python
import os
import time
import RPi.GPIO as GPIO

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('hello.html')


# Temperature
# Initialisation des broches
def init_sonde():
    os.system('modprobe w1-gpio')  # Allume le module 1wire
    os.system('modprobe w1-therm')  # Allume le module Temperature


class TemperatureSensor:

    def __init__(self, code):
        self.address = code
        # Chemin du fichier contenant la température (remplacer par votre valeur trouvée précédemment)
        self.device_file = '/sys/bus/w1/devices/' + code + '/w1_slave'
        self.temperatureC = 0
        self.temperatureF = 0

    # Méthode qui lit dans le fichier température
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    #  Méthode qui lit la temperature en Celsius
    def read_temp(self):
        lines = self.read_temp_raw()
        # Tant que la première ligne ne vaut pas 'YES', on attend 0,2s
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        # On cherche le '=' dans la seconde ligne du fichier
        equals_pos = lines[1].find('t=')
        # Si le '=' est trouvé, on converti ce qu'il y a après le '=' en degrés Celsius
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            self.temperatureC = round(temp_c, 2)
            self.temperatureF = round(self.convertCtoF(temp_c), 2)
            return 0

    #  Méthode qui converti la temperature en Fahrenheit
    def convertCtoF(self, tc):
        return tc * 9 / 5 + 32


# Routes

@app.route('/temperature/')
def getsensor():
    sonde = TemperatureSensor('28-0213121a4aaa')
    sonde.read_temp()
    print('Température de la sonde :', sonde.temperatureC, '°C -', sonde.temperatureF, '°F')
    return render_template('temperature.html', tc=sonde.temperatureC, tf=sonde.temperatureF)


# Leds
def init_led(broche):
    # Utilisation d'une norme de nommage pour les broches
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # Initialisation de la broche en mode "sortie"
    # Le nombre passé en paramètre correspond au numéro de GPIO et non au numéro de la broche.
    GPIO.setup(broche, GPIO.OUT)
    return 0

@app.route('/led/')
def leds():
    return render_template('leds.html')

@app.route('/led/on')
@app.route('/led/on/<int:broche>')
def lightOn(broche=None):
    # Initialisation des leds
    init_led(14)
    init_led(15)
    # Si le numéro de broche n'est pas indiqué
    if broche == None:
        print("Leds On")
        GPIO.output(14, GPIO.HIGH)
        GPIO.output(15, GPIO.HIGH)
        return "leds on"
    elif broche in [14, 15]:
        print("Led", broche, "on")
        GPIO.output(broche, GPIO.HIGH)
        return "led " + str(broche) + " on"
    else:
        print("broche non affectee")
        return "broche non affectee"


@app.route('/led/off')
@app.route('/led/off/<int:broche>')
def lightOff(broche=None):
    # Initialisation des leds
    init_led(14)
    init_led(15)
    # Si le numéro de broche n'est pas indiqué
    if broche == None:
        print("Leds Off")
        GPIO.output(14, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        return "leds off"
    elif broche in [14, 15]:
        print("Led", broche, "off")
        GPIO.output(broche, GPIO.LOW)
        return "led " + str(broche) + " off"
    else:
        print("broche non affectée")
        return "broche non affectée"

