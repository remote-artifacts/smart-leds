import connect
import time
import leds
import async_http_server
import json
# from mqtt_async import MQTTClient, config

class SmartLeds:

    def __init__(self, config):
        self.wifi_config = config["wifi"]
        self.station = None
        pin_mapping = config["pins"]
        self.leds = leds.Leds(pin_mapping)
        self.color = "#000000"
        self.routes = {
            "": SmartLeds.index,
            "/": SmartLeds.index,
            "/effects": SmartLeds.effects,
            "/leds": self.handle_leds,
            "/light": self.handle_light,
            "/pulse": self.handle_pulse,
        }
        self.tasks = {}
        self.pulse_config = {p: {} for p in pin_mapping.keys()}

    def connect(self):
        keys = list(self.leds.leds.keys())
        attempt = 0
        if self.station is None:
            sta_config = self.wifi_config["sta"]
            self.station = connect.connect(**sta_config)
        while not self.station.isconnected():
            color = keys[attempt % len(keys)]
            attempt += 1
            self.leds.fade(**{"color": color, "duration": 1100})
            self.leds.fade(**{"color": color, "start": 1000, "end": 0, "duration": 1100})
            time.sleep(0.5)
        self.leds.flash(duration=0.5)


    # Web handlers
    @staticmethod
    def index(params, body):
        with open("www/index.html", "r") as f:
            return f.read(), 200

    @staticmethod
    def effects(params, body):
        with open("www/effects.html", "r") as f:
            return f.read(), 200


    async def pulse(self, color, start, end, duration):
        run = True
        while run:
            try:
                await self.leds.afade(color, start=start, end=end, duration=duration)
                await self.leds.afade(color, start=end, end=start, duration=duration)
            except async_http_server.asyncio.CancelledError:
                self.leds.off(color)
                run = False


    def handle_pulse(self, params, body):
        print(body)
        if body:
            for color, options in body.items():
                current_task = self.tasks.get(color)
                if current_task:
                    current_task.cancel()
                    print("Task canceled")
                duration = options.get("duration", 0)
                if duration > 0:
                    start = options["start"]
                    end = options["end"]
                    self.pulse_config[color] = {
                        "start": start,
                        "end": end,
                        "duration": duration
                    }
                    self.tasks[color] = async_http_server.asyncio.get_event_loop().create_task(self.pulse(color=color, start=start, end=end, duration=duration))

            return {"status": "ok"}, 200
        else:
            return self.pulse_config, 200

    def handle_leds(self, params, body):
        print(body)
        if body:
            msg = body["status"]
            if msg.startswith("#"):
                color = msg
                msg = msg.lstrip('#')
                data = tuple(int(msg[i:i + 2], 16) for i in (0, 2, 4))
                d = {"red": data[0] * 4, "green": data[1] * 4, "blue": data[2] * 4}
                self.leds.set(**d)
            else:
                pass
                # red.duty(0)
                # green.duty(0)
                # blue.duty(0)
            return body, 200
        else:
            return {"status": self.color}, 200

    def handle_light(self, params, body):
        if body:
            value = 1000 if body["status"] == "on" else 0
            print("Set white", value)
            self.leds.set(white=value)
            # l = async_http_server.asyncio.get_event_loop()
            # l.create_task(self.publish())

        else:
            print("White value is", self.leds.get("white"))
            value = self.leds.get("white")
        return {"status": "on" if value > 0 else "off"}, 200

    async def publish(self):
        await self.client.publish("prueba", 'CAGAOOO', qos=1)

    def configure_web_server(self, loop):
        async_http_server.router.update(self.routes)
        loop = async_http_server.asyncio.get_event_loop()
        loop.create_task(async_http_server.asyncio.start_server(async_http_server.handle_client, '0.0.0.0', 80))
        print("Listening port: 80")


    def mqtt_callback(self, topic, msg, retained, qos, dup):
        if topic == b"prueba":
            print(topic, msg, retained, qos, dup)
        elif topic == b"leds":
            try:
                data = json.loads(msg.decode())
                print("New data update")
                self.leds.set(**data)
            except Exception as e:
                print(e)

    async def mqtt_on_connect(self, client):
        await client.subscribe("prueba", 1)
        await client.subscribe("leds", 1)


    async def run_mqtt(self, client):
        self.client = client
        await client.connect()
        n = 0
        while True:
            await client.publish("prueba", 'Hello World #{}!'.format(n), qos=1)
            await async_http_server.asyncio.sleep(5)
            n += 1

    def configure_mqtt_client(self, loop):
        # MQTT STUFF
        config["server"] = '192.168.1.136'  # can also be a hostname
        config["subs_cb"] = self.mqtt_callback
        config["connect_coro"] = self.mqtt_on_connect

        client = MQTTClient(config)

        loop.create_task(self.run_mqtt(client))
        print("MQTT ready")

    def create_tasks(self, loop):
        # self.configure_mqtt_client(loop)
        self.configure_web_server(loop)
