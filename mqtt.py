import machine
import time
import paho.mqtt.client as mqtt #define mqtt broker
import esp
import gc
import webrepl
import network

#start the web REPL
webrepl.start()

#collect garbage
gc.collect()

#Wi-Fi configuration
ssid =  "abcdef" #wifi ssid
password = "xyz" #wifi password

# Function to connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi")
        wlan.connect(ssid, password)
          

        while not wlan.isconnected():
            time.sleep(1)
            
print("Connected to Wi-Fi")

# Connect to Wi-Fi
connect_wifi()

#define mqtt broker and topic
broker_address= 000.000.00.00 # IP address of the device running the mosquitto server
topic = "bot"

#callback when a connection is established.
def on_connect(client,userdata, flags, rc):
    print ("connected with result code" + str(rc))
    client.subscribe(topic) #subscribe to the topic when connected

#callback when a message is recieved.
def on_message(client, userdata, msg):
    command = msg.payload.decode('utf-8')
    print("Recieved command:", command)
    
    #define GPIO pins to control the bot
    left_forward_pin = 13
    left_reverse_pin = 12
    right_forward_pin = 11
    right_reverse_pin = 10

    #Set up GPIO pins
    left_forward = machine.Pin(13, machine.Pin.OUT)
    left_reverse = machine.Pin(12, machine.Pin.OUT)
    right_forward = machine.Pin(11, machine.Pin.OUT)
    right_reverse = machine.Pin(10, machine.Pin.OUT)

    if command == 'F':
        # Move forward (all motors rotate in forward direction)
        left_forward.on()
        right_forward.on()
    
    elif command == 'B':
        # Move reverse (all motors rotate in reverse direction)
        left_reverse.on()
        right_reverse.on()
    
    elif command == 'L':
        # Turn right (left side motors rotate in forward direction, right side motors don't rotate)
        left_forward.on()
        right_reverse.on()
                
    elif command == 'R':
        # Turn left (right side motors rotate in forward direction, left side motors don't rotate)
        right_forward.on()
        left_reverse.on()
                
    elif command == 'S':
        # STOP (all motors stop)
        left_forward.off()
        left_reverse.off()
        right_forward.off()
        right_reverse.off()
    
#initialise mqtt client
client = mqtt.client()
client.on_connect = on_connect
client.on_message = on_message

#connect to the mqtt broker
client.connect(broker_address, 1883, 60)

# Loop to keep the script running and handle MQTT messages
try:
    client.loop_start()
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    # Clean up GPIO
    left_forward.off()
    left_reverse.off()
    right_forward.off()
    right_reverse.off()

    # Disconnect from MQTT broker
    client.loop_stop()
    client.disconnect()
    