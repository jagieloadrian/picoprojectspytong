import time

import urequests

from modules.ISSState import ISSState


# ========== POBIERANIE ISS ==========
def get_iss_position():
    try:
        response = urequests.get("http://api.open-notify.org/iss-now.json")
        data = response.json()
        response.close()

        lat = float(data["iss_position"]["latitude"])
        lon = float(data["iss_position"]["longitude"])
        print(f"Current position is: lat: {lat} lon: {lon} responsed at: {data["timestamp"]}")
        return lat, lon

    except:
        return None, None

def maybe_fetch_iss(state: ISSState):
    now = time.time()
    if now - state.last_api_time >= 5:
        lat, lon = get_iss_position()
        if lat is not None:
            state.target_lat = lat
            state.target_lon = lon
            state.last_api_time = now

def interpolate_position(state: ISSState):
    dt = time.time() - state.last_api_time
    t = dt / 5
    if t > 1:
        t = 1
    state.current_lat += (state.target_lat - state.current_lat) * t
    state.current_lon += (state.target_lon - state.current_lon) * t