import asyncio
import framebuf

async def displayScroll(oled, aht, lines=None, delay=0.001):
    oled_width = oled.width
    line_height = 8

    while True:
        # pobierz aktualne dane i przygotuj linie
        if lines is None:
            lines = [
                f"Temperature: {aht.temperature:.2f} C",
                f"Humidity: {aht.relative_humidity:.2f} %",
                f"Status: {aht.status}"
            ]

        # przygotowanie buforów dla każdej linii
        line_buffers = []
        max_scroll = 0
        for line in lines:
            text_width = len(line) * 8
            buf = bytearray(text_width * line_height // 8)
            fb = framebuf.FrameBuffer(buf, text_width, line_height, framebuf.MONO_VLSB)
            fb.fill(0)
            fb.text(line, 0, 0, 1)
            line_buffers.append((fb, text_width))
            if text_width > max_scroll:
                max_scroll = text_width

        # scrolluj w poziomie
        for offset in range(max_scroll + oled_width):
            oled.fill(0)
            for i, (fb, width) in enumerate(line_buffers):
                x_pos = oled_width - offset
                if x_pos + width > 0 and x_pos < oled_width:
                    oled.blit(fb, x_pos, i * line_height)
            oled.show()
            await asyncio.sleep(delay)