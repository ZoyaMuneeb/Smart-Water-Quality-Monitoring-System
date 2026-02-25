import RPi.GPIO as GPIO
import time
import serial
import LCD1602 as LCD
import PCF8591 as ADC
import urllib.request

from keypadfunc import keypad
from RFIDTest import validate_rfid
from flask import Flask
from flask import send_file
from datetime import datetime
from picamera import PiCamera

SERIAL_PORT = '/dev/ttyS0'
read_API = "9X2M014Y2K71SN49"
write_API = "9T01JGNUJ7L5KKFR"
CH_ID = 2741076 #Channel ID from Thingspeak
myapp = Flask(__name__)
MyCamera=PiCamera()

def authenticator():
    print("Please enter the password: ")
    key1n,key1s = keypad() #ones position
    time.sleep(0.5) #sleep so it waits a while until we input again
    key1f = shift(key1n,key1s)
    key2n,key2s = keypad() #tens position
    time.sleep(0.5) #sleep so it waits a while :)
    key2f = shift(key2n,key2s)
    keyf = str(key1f) + str(key2f) #converting to string
    print (keyf);
    if(keyf==password):
        print("Your password is correct. Please scan your ID for access")
        ser.flushInput()
        ser.flushOutput()
        data=ser.read(12)
        code = validate_rfid(data)
        if code:
            print ("RFID tag: {}".format(code))
        time.sleep(1)
        if(code =="5300C7F4D2"):
            print("Access granted")
            time.sleep(1)
            return True
        else:
            print("Wrong RFID! Access not granted! Please try again!")
    else:
        print("Wrong Password! Try again!")
    return False

def shift(keyxn, keyxs):
    if(GPIO.input(BUTTON) == 1):
        keyxf=keyxs
    else:
        keyxf=keyxn
    return keyxf

def getTurbidity(): #AN0
    ADC0_units= ADC.read(0)
    ADC0_Turbidity=(ADC0_units*40)/256 
    return ADC0_Turbidity

def getORP(): #AN1
    ADC1_units= ADC.read(1)
    ADC1_ORP=(ADC1_units*2000)/256 
    ADC1_ORP-=1000
    return ADC1_ORP

def getpH(): #AN2
    ADC2_units= ADC.read(2)
    ADC2_pH=(ADC2_units*14)/256 #since 14 is max value
    return ADC2_pH

def getTDS(): #AN3
    ADC3_units= ADC.read(3)
    ADC3_TDS=(ADC3_units*2000)/256
    return ADC3_TDS

def distance():
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)
    while GPIO.input(ECHO)==0:
        a = 0
    time1 = time.time()
    while GPIO.input(ECHO)==1:
        a = 0
    time2 = time.time()
    duration = time2 - time1
    return duration*1000000/58

def action(self):
    LCD.clear()
    flash(BLED)

def flash(LED):   
    for i in range(2):
        GPIO.output(LED,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(LED,GPIO.LOW)
        time.sleep(1)

def determine_water_quality(ph, tds, orp, turbidity):
    # pH Score
    if 6.5 <= ph <= 8.5:
        ph_score = 100
    elif (5.5 <= ph < 6.5) or (8.5 < ph <= 9.5):
        ph_score = 50
    else:
        ph_score = 0

    # TDS Score
    if tds <= 500:
        tds_score = 100
    elif 500 < tds <= 1000:
        tds_score = 50
    else:
        tds_score = 0

    # ORP Score
    if 200 <= orp <= 600:
        orp_score = 100
    elif (0 <= orp < 200) or (600 < orp <= 800):
        orp_score = 50
    else:
        orp_score = 0

    # Turbidity Score
    if turbidity <= 5:
        turbidity_score = 100
    elif 5 < turbidity <= 10:
        turbidity_score = 50
    else:
        turbidity_score = 0

    # Calculate overall drinkability percentage
    drinkability_percentage = (ph_score + tds_score + orp_score + turbidity_score) / 4

    # Interpret the result
    if 80 <= drinkability_percentage <= 100:
        quality = "Safe"
        buzzer.ChangeFrequency(1)
        LCD.clear()
        LCD.write(0,0,"Safe to drink!!!")
        LCD.write(0,1,"Safety%={:.2f}%".format(drinkability_percentage))
        
        GPIO.output(RLED,GPIO.LOW)
        GPIO.output(YLED,GPIO.LOW)

        GPIO.output(GLED,GPIO.HIGH)

    elif 50 <= drinkability_percentage < 80:
        quality = "Semi-safe"
        buzzer.ChangeFrequency(200)
        LCD.clear()
        LCD.write(0,0,"Unsafe to drink")
        LCD.write(0,1,"Safety%={:.2f}%".format(drinkability_percentage))
        
        GPIO.output(RLED,GPIO.LOW)
        GPIO.output(GLED,GPIO.LOW)

        GPIO.output(YLED,GPIO.HIGH)

    else:
        quality = "Dangerous"
        buzzer.ChangeFrequency(500)
        LCD.clear()
        LCD.write(0,0,"DANGEROUS!")
        LCD.write(0,1,"Safety%={:.2f}%".format(drinkability_percentage))
        
        GPIO.output(YLED,GPIO.LOW)
        GPIO.output(GLED,GPIO.LOW)
        
        GPIO.output(RLED,GPIO.HIGH)
    
    return drinkability_percentage, quality

def get_last_value(Field_No):
    Numberofreadings = 1 #Number of values to read
    x = urllib.request.urlopen("https://api.thingspeak.com/channels/{}/fields/{}.csv?results={}".format(CH_ID,Field_No,Numberofreadings))
    data = x.read().decode('ascii') #Decode the read values to ascii i.e. read the imported date and convert it to ASCII
    data=",".join(data.split("\n")) #Convert the imported data (ASCII) to a comma separated string join the table data into comma separated string

    element = float(data.split(",")[5])
    return(element)
    
@myapp.route('/') #index route
def index():
    return "Welcome to the Smart Water Quality Monitoring System" #print on the client's web browser

@myapp.route('/status') #show a picture of water
def status():
    timestamp=datetime.now().isoformat()
    photo_path="/home/pi/Flaskpic.jpg"
            
    MyCamera.annotate_text="Pic taken at time {}".format(timestamp)
    time.sleep(2)
    MyCamera.capture(photo_path)
    response = send_file(photo_path, mimetype = "image/jpg")
    return response

@myapp.route('/<turbidity>/<orp>/<ph>/<tds>')
def dynamic_route(turbidity, orp, ph, tds):
    drinkability, quality = determine_water_quality(float(ph), float(tds), float(orp), float(turbidity))
    return "The drinkability% is {}. The water is {}.".format(drinkability, quality)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
LCD.init(0x27,1) #1 ==> Turning on the background light. 0x27 is the address of the LCD.
ADC.setup(0x48)

RLED = 12
YLED = 13
BLED = 27 
GLED = 16
BUTTON = 17
BUZZ = 18
TRIG = 5
ECHO = 6
password ="2@"
ser = serial.Serial(baudrate = 2400,  bytesize = serial.EIGHTBITS,  parity = serial.PARITY_NONE,  port = SERIAL_PORT, stopbits = serial.STOPBITS_ONE,  timeout = 1)

GPIO.setup(RLED, GPIO.OUT)
GPIO.setup(YLED, GPIO.OUT)
GPIO.setup(BLED, GPIO.OUT)
GPIO.setup(GLED, GPIO.OUT)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZ, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback = action, bouncetime = 2000)

buzzer = GPIO.PWM(BUZZ,1)
buzzer.start(50)
auth_flag = False

while True:
    while not auth_flag:
        auth_flag = authenticator()
    
    dis = distance()

    while(dis<100):
        print("Welcome to the smart water quality monitoring system")
        turbidity = getTurbidity()
        print("Turbidity ={}" .format(turbidity))
        orp = getORP()
        print("ORP ={}" .format(orp))
        ph = getpH()
        print("pH ={}" .format(ph))
        tds = getTDS()
        print("TDS ={}" .format(tds))

        LCD.clear()
        drinkability, quality = determine_water_quality(ph, tds, orp, turbidity)

        x=urllib.request.urlopen("https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}&field4={}&field5={}".format(write_API,turbidity,orp,ph,tds,drinkability))

        if(quality=="Safe" or quality == "Semi-safe"):
            water = input("Would you like some water? (Y/N) ")
            while (water == 'Y'):
                print("Press the button to start dispensing water!")
                while(GPIO.input(BUTTON)==1):
                    if(quality=="Semi-safe"):
                        yesWater = input("Are you sure you want to dispense water (Water is semi-safe)? (Y/N)")
                        if(yesWater=="N"):
                            break
                    cup_size=input("Choose cup size (L/S): ")
                    if(cup_size=='L'):
                        LCD.clear()
                        LCD.write(0,0,"Water dispensing")
                        time.sleep(10)
                        LCD.clear()
                        LCD.write(0,0,"Done!")
                        time.sleep(2)
                        LCD.clear()
                    elif(cup_size=='S'):
                        LCD.clear()
                        LCD.write(0,0,"Water dispensing")
                        time.sleep(4)
                        LCD.clear()
                        LCD.write(0,0,"Done!")
                        time.sleep(2)
                        LCD.clear()
                    water = input("Do you want more water? (Y/N) ")
        elif (quality=="Dangerous"):
            ph_last_value = get_last_value(3)
            turbidity_last_value = get_last_value(1)
            tds_last_value = get_last_value(4)
            orp_last_value = get_last_value(2)
            drinkability_last_value = get_last_value(5)
            print("Water is dangerous because turbidity={}, ORP={}, pH ={}, TDS={},".format(turbidity_last_value, orp_last_value, ph_last_value, tds_last_value))
            print("The drinkability% is = {}".format(drinkability_last_value))

        fl = input("Do you want to run on Flask? (Y/N) ")
        if (fl=='Y'):
            if __name__=='__main__':
                myapp.run(host='0.0.0.0', port=5080)

    print("System is off")
    buzzer.ChangeFrequency(1)
