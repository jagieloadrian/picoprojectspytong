import gc
import time

from modules.ISSState import ISSState
from modules.drawObjects import draw_map_viewport, drawTexts, lon_to_map_x, draw_iss, update_track, draw_track, \
    generateShadeLUT
from modules.issPositionService import get_iss_position, maybe_fetch_iss, interpolate_position
from modules.screenConfig import getScreenConfig, SCREEN_W
from modules.wifi import connect_wifi, syncTime
from images.earthfull import getBitmap


#
# ========== MAIN ==========
def main():
    generateShadeLUT()
    connect_wifi()
    syncTime()
    screen = getScreenConfig()
    scroll = 0
    track = []
    earthMap = getBitmap()
    state = ISSState()
    lat, lon = get_iss_position()
    if lat is not None:
        state.current_lat = lat
        state.current_lon = lon
        state.target_lat = lat
        state.target_lon = lon
        state.last_api_time = time.time()

    while True:
        frame_start = time.ticks_ms()
        maybe_fetch_iss(state)
        interpolate_position(state)

        map_x = lon_to_map_x(state.current_lon)
        scroll = int(map_x - SCREEN_W // 2)

        draw_map_viewport(screen, earthMap, scroll)
        drawTexts(screen, state.current_lat, state.current_lon)
        draw_iss(state.current_lat, state.current_lon, screen, scroll)

        update_track(state.current_lon, state.current_lat, track)
        draw_track(track, scroll, screen)

        elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
        if elapsed < 40:
            time.sleep_ms(40 - elapsed)

if __name__ == "__main__":
    main()
