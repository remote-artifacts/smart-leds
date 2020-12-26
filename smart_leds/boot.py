from smart_leds import SmartLeds
import async_http_server
import json

with open("config.json") as f:
    config = json.load(f)

# starting web server
sl = SmartLeds(config)
sl.connect()
loop = async_http_server.asyncio.get_event_loop()
sl.create_tasks(loop)
loop.run_forever()
