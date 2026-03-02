HEIGHT = 358
WIDTH = 717
def getBitmap():
    with open("images/earthfull.raw", "rb") as f:
        return bytearray(f.read())