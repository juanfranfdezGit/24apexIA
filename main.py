from fastapi import FastAPI, WebSocket
import random

app = FastAPI()

TRACK_WIDTH = 120

current_bias = 0
timer = 0

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global current_bias, timer

    await ws.accept()
    print("Agent connected")

    while True:
        state = await ws.receive_json()

        lateral = state["lateralOffset"]
        front_dist = state["frontDist"]
        speed = state["speed"]

        timer -= 1
        if timer <= 0:
            current_bias = random.uniform(-TRACK_WIDTH/3, TRACK_WIDTH/3)
            timer = random.randint(30, 120)

        lateral_target = current_bias - lateral * 0.3

        throttle = 0.7
        if front_dist < 20:
            throttle = 0.2
        elif speed > 60:
            throttle = 0.9

        action = {
            "lateralTarget": lateral_target,
            "throttle": throttle
        }

        await ws.send_json(action)