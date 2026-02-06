from fastapi import FastAPI, WebSocket
import random

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("Cliente conectado")

    while True:
        state = await ws.receive_json()

        lateral = state.get("lateralOffset", 0)
        curvature = state.get("curvatureAhead", 0)
        front_dist = state.get("frontDist", 0)
        speed = state.get("speed", 0)

        track_width = 120

        # --- Política lateral ---
        # Lateral target dinámico con algo de ruido
        lateral_target = -lateral + random.uniform(-20, 20)
        lateral_target = max(-track_width/2, min(track_width/2, lateral_target))

        # --- Política velocidad ---
        throttle = 0.6 + random.uniform(-0.1, 0.1)
        if abs(curvature) > 0.1 or front_dist < 15:
            throttle = 0.3
        elif front_dist > 50:
            throttle = 0.8

        # Enviar acción al cliente
        action = {
            "lateralTarget": lateral_target,
            "throttle": throttle
        }

        await ws.send_json(action)
