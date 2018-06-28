import RPi.GPIO as GPIO                    #Import GPIO library
import time                                #Import time library
from pubnub import Pubnub
import Adafruit_DHT as dht

GPIO.setmode(GPIO.BOARD)                   #Set GPIO pin numbering 

pubnub = Pubnub(publish_key='pub-c-e621b8e2-bdcb-4d07-afca-f7f477cc05fc',subscribe_key='sub-c-643cb84e-af34-11e6-936d-02ee2ddab7fe');
channel = 'rangefinder'
channel1 = 'home'
LED = 13
Motor1A = 33
Motor1B = 35
Motor1E = 37
TRIG = 29                                  #Associate pin 33 to TRIG
ECHO = 31                                  #Associate pin 35 to ECHO
PIR_PIN = 15

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in
GPIO.setup(LED,GPIO.OUT)
GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)

pwm=GPIO.PWM(11,50)
pwm.start(7.5)

def callback(m, channel1):
	if m['sw'] == 2:
		GPIO.output(Motor1A,GPIO.HIGH)
		GPIO.output(Motor1B,GPIO.LOW)
		GPIO.output(Motor1E,GPIO.HIGH)
	if m['sw'] == 3:
		GPIO.output(Motor1E,GPIO.LOW)
	if m['sw'] == 0:
		GPIO.output(LED,1)
	if m['sw'] == 1:
		GPIO.output(LED,0)
	if m['sw'] == 4:
		pwm.ChangeDutyCycle(2.5)
	if m['sw'] == 5:
		pwm.ChangeDutyCycle(7.5)
		
pubnub.subscribe(channels=channel1, callback=callback, error=callback)

def callback(message):
    print(message)

#published in this fashion to comply with Eon
m = 0;
while True:
	if m==0:
		GPIO.output(Motor1A,GPIO.HIGH)
                GPIO.output(Motor1B,GPIO.LOW)
                GPIO.output(Motor1E,GPIO.HIGH)
		GPIO.output(LED,1)
		pwm.ChangeDutyCycle(2.5)
		m=1
	else:
		GPIO.output(Motor1E,GPIO.LOW)
		GPIO.output(LED,0)
		pwm.ChangeDutyCycle(7.5)
		m=0
	h,t = dht.read_retry(dht.DHT22, 4)
	i = GPIO.input(PIR_PIN)

	GPIO.output(TRIG, True)                  #Set TRIG as HIGH
	time.sleep(0.00001)                      #Delay of 0.00001 seconds
	GPIO.output(TRIG, False)                 #Set TRIG as LOW

	while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
		pulse_start = time.time()              #Saves the last known time of LOW pulse

	while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
		pulse_end = time.time()                #Saves the last known time of HIGH pulse 

	pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

	distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
	distance = round(distance, 2)            #Round to two decimal points
	
	
	message = {
		'motion': i,
		'read': 'Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(t, h),
		'distance': distance - 0.5
	}
	pubnub.publish(channel, message)
