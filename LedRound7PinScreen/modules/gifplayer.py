import os, time

class AnimationPlayer:
    def __init__(self, display, anim_root="/anim", fps=12, switch_time=30.0):
        self.display = display
        self.anim_root = anim_root
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.switch_time = switch_time

        self.FRAME_W = 240
        self.FRAME_H = 240
        self.FRAME_SIZE = self.FRAME_W * self.FRAME_H * 2

        # Bufory
        self.buf_a = bytearray(self.FRAME_SIZE)
        self.buf_b = bytearray(self.FRAME_SIZE)
        self.current_buf = self.buf_a
        self.next_buf = self.buf_b

        # Lista animacji
        self.animations = self._preload_animations()
        if not self.animations:
            raise RuntimeError(f"Brak animacji w {anim_root}")

    def _preload_animations(self):
        anims = []
        try:
            entries = sorted(os.listdir(self.anim_root))
        except Exception:
            return []

        for d in entries:
            path = f"{self.anim_root}/{d}"
            try:
                if os.stat(path)[0] & 0o40000:  # katalog
                    frames = [f for f in sorted(os.listdir(path)) if f.lower().endswith('.bmp')]
                    if frames:
                        anims.append((d, frames))
            except Exception:
                continue
        return anims

    def _load_bmp_frame(self, path, target_buf):
        with open(path, "rb") as f:
            f.read(54)  # WBMP/BMP header
            read_bytes = f.readinto(target_buf)
            if read_bytes != self.FRAME_SIZE:
                print(f"!!! Niepełna klatka {path}")

    def play_all(self):
        anim_idx = 0
        while True:
            folder_name, frame_files = self.animations[anim_idx]
            folder = f"{self.anim_root}/{folder_name}"
            if not frame_files:
                anim_idx = (anim_idx + 1) % len(self.animations)
                continue

            start_anim = time.ticks_ms()
            frame_idx = 0

            # Pierwsza klatka synchronicznie
            self._load_bmp_frame(f"{folder}/{frame_files[0]}", self.current_buf)
            self.display.blit_buffer(self.current_buf, 0, 0, self.FRAME_W, self.FRAME_H)

            while time.ticks_diff(time.ticks_ms(), start_anim) < self.switch_time*1000:
                t_frame_start = time.ticks_ms()

                # Wczytaj następną klatkę
                next_idx = (frame_idx + 1) % len(frame_files)
                self._load_bmp_frame(f"{folder}/{frame_files[next_idx]}", self.next_buf)

                # Blit aktualnej
                self.display.blit_buffer(self.current_buf, 0, 0, self.FRAME_W, self.FRAME_H)

                # Swap buforów
                self.current_buf, self.next_buf = self.next_buf, self.current_buf
                frame_idx = next_idx

                # Czekaj do następnej klatki
                t_elapsed = (time.ticks_ms() - t_frame_start)/1000
                sleep_time = self.frame_time - t_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

            # Zmień animację
            anim_idx = (anim_idx + 1) % len(self.animations)