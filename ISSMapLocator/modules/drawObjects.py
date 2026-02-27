import time

from modules.screenConfig import SCREEN_W, SCREEN_H
import images.earthfull as earth
from modules.st7789py import WHITE
import modules.vga2_16x16 as font
import images.death_star as issBitmap


# ========== DRAWING ==========
framebuffer = bytearray(SCREEN_W * SCREEN_H * 2)
shade_lut = bytearray(65536 * 2)

def draw_map_viewport(screen, file, scroll):

    day_offset = get_day_offset()
    while scroll < 0:
        scroll += earth.WIDTH
    while scroll >= earth.WIDTH:
        scroll -= earth.WIDTH

    fb_index = 0

    for row in range(SCREEN_H):

        map_row = row
        if map_row >= earth.HEIGHT:
            map_row -= earth.HEIGHT

        row_start = map_row * earth.WIDTH * 2
        src_x = scroll

        for col in range(SCREEN_W):
            idx = row_start + src_x * 2

            color_hi = file[idx]
            color_lo = file[idx+1]

            color = (color_hi << 8) | color_lo

            if src_x > day_offset:
                lut_i = color * 2
                framebuffer[fb_index]   = shade_lut[lut_i]
                framebuffer[fb_index+1] = shade_lut[lut_i+1]
            else:
                framebuffer[fb_index]   = color_hi
                framebuffer[fb_index+1] = color_lo

            framebuffer[fb_index] = color >> 8
            framebuffer[fb_index+1] = color & 0xFF
            fb_index += 2
            src_x += 1

            if src_x == earth.WIDTH:
                src_x = 0

    screen.blit_buffer(framebuffer, 0, 0, SCREEN_W, SCREEN_H)

def draw_iss(lat, lon, screen, scroll, bitmap = issBitmap):
    # full map position
    map_x = int((lon + 180) * earth.WIDTH / 360)
    map_y = int((90 - lat) * earth.HEIGHT / 180)

    # viewport position
    screen_x = (map_x - scroll) % earth.WIDTH
    screen_y = map_y

    if 0 <= screen_x < SCREEN_W and 0 <= screen_y < SCREEN_H:
        screen.bitmap(bitmap, screen_x - bitmap.WIDTH//2,
                   screen_y - bitmap.HEIGHT//2)


def drawTexts(screen, lat, lon, ):
    screen.text(font=font, text="ISS Tracker", x0=10, y0=10, color=WHITE)
    screen.text(font=font, text="Lat: {:.2f}".format(lat),
                x0=10, y0=40, color=WHITE)
    screen.text(font=font, text="Lon: {:.2f}".format(lon),
            x0=10, y0=60, color=WHITE)


def update_track(x, y, track):
    track.append((x,y))
    if len(track) > 120:
        track.pop(0)

def draw_track(track, scroll, screen):
    for p in track:
        # full map position
        map_x = int((p[0] + 180) * earth.WIDTH / 360)
        map_y = int((90 - p[1]) * earth.HEIGHT / 180)

        # viewport position
        screen_x = (map_x - scroll) % earth.WIDTH
        screen_y = map_y

        screen.pixel(screen_x, screen_y, 0xF800)

def generateShadeLUT():
    print("Generating shade LUT...")

    for color in range(65536):

        r = (color >> 11) & 0x1F
        g = (color >> 5) & 0x3F
        b = color & 0x1F

        r >>= 1
        g >>= 1
        b >>= 1

        dark = (r << 11) | (g << 5) | b

        shade_lut[color*2]   = dark >> 8
        shade_lut[color*2+1] = dark & 0xFF

    print("LUT ready")

# ========== GEO CONVERTION ==========
def lon_to_x(lon):
    return int((lon + 180) * earth.WIDTH / 360)

def lat_to_y(lat):
    return int((90 - lat) * SCREEN_H / 180)

def lon_to_map_x(lon):
    return int((lon + 180) * earth.WIDTH / 360)

def lat_to_map_y(lat):
    return int((90 - lat) * earth.HEIGHT / 180)


def get_day_offset():
    seconds = time.time() % 86400
    return int((seconds / 86400) * earth.WIDTH)