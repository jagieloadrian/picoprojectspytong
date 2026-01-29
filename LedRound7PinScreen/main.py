from modules.config import getSpi, getDisplay
from modules.gifplayer import AnimationPlayer


def main() -> None:
    spi = getSpi()
    display = getDisplay(spi)
    player = AnimationPlayer(display)
    player.play_all()

if __name__ == "__main__":
    main()