from PIL import Image
import struct

import argparse

def bmp_to_rgb565_raw(input_file, output_file):
    img = Image.open(input_file).convert("RGB")
    w, h = img.size

    with open(output_file, "wb") as f:
        for y in range(h):
            for x in range(w):
                r, g, b = img.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                f.write(struct.pack(">H", rgb565))  # big endian dla ST7789

def main():
    parser = argparse.ArgumentParser(
        description="Convert image file to raw object",
    )

    parser.add_argument("image_file", help="Name of file containing image to convert")
    parser.add_argument("image_output", help="Name of output file")

    args = parser.parse_args()
    bmp_to_rgb565_raw(args.image_file, args.image_output)

if __name__ == "__main__":
    main()