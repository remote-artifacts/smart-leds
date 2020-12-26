# Smart Leds
This is a led controller meant to be cheap, energy efficient but easy to use and powerful.

# Installing
* Upload micropython into your device
* Upload the files or use upip
* Configure `config.json`

# Configuring
First you need to know which pins of your device are PWM and then, assign them to a color. Check `config.json.dist`
to see an example.

The next thing to configure is your wifi. Just put your `bssid` and `password`. You can also specify more network
parameters like the ip address, gateway... or use the default values.

Once you have everything configure, you will see your leds fading until wifi connection is done. At this moment you will
see a flash and then all leds off. Now you can access to the ip address of the device using your browser (from a pc, phone...).

The server uses a json rest api so feel free to build your own tools to interact with the led controller!

# Tested devices
I have tested this leds program on these devices:
* ESP32
* ESP8266

# TODO
* Configuration done using a wizzard using the AP wifi inteface
* Add some kind of authentication/security (currently all wifi devices can control the leds)
* Full mqtt support: Only ESP32 is able to use mqtt because ESP8266 does not have enough memory
* Better led control interface
