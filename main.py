from fastapi import FastAPI, WebSocket
import random

app = FastAPI()

TRACK_WIDTH = 120
bestLapTime = float("inf")
best_bias = 0
current_bias = 0
target_bias = 0
prev_lap = 0
prev_t = 0
bias_timer = 0

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global bestLapTime, best_bias, current_bias, target_bias, prev_lap, prev_t, bias_timer

    await ws.accept()
    print("Agent connected")

    while True:
        state = await ws.receive_json()
        t = state["t"]
        lap = state["lap"]
        lastLapTime = state["lastLapTime"]

        # --- Reward simple: progreso ---
        reward = (t - prev_t) % 1
        prev_t = t

        # --- Comprobar vuelta ---
        if lap > prev_lap:
            prev_lap = lap
            if lastLapTime < bestLapTime:
                bestLapTime = lastLapTime
                best_bias = current_bias
                print(f"New best lap: {bestLapTime:.2f}s, best_bias={best_bias:.2f}")

        # --- Actualiza el target_bias periódicamente ---
        bias_timer -= 1
        if bias_timer <= 0:
            # Nuevo objetivo aleatorio cerca de la mejor trazada
            target_bias = best_bias + random.uniform(-TRACK_WIDTH * 0.1, TRACK_WIDTH * 0.1)
            target_bias = max(-TRACK_WIDTH/2, min(TRACK_WIDTH/2, target_bias))
            bias_timer = random.randint(30, 60)  # cambiar cada 0.5-1s aprox

        # --- Mueve suavemente current_bias hacia target_bias ---
        smoothing = 0.05  # porcentaje de interpolación por tick
        current_bias += (target_bias - current_bias) * smoothing

        # --- Acción final ---
        lateralTarget = current_bias
        throttle = 0.7  # fijo por ahora

        action = {
            "lateralTarget": lateralTarget,
            "throttle": throttle
        }

        await ws.send_json(action)
