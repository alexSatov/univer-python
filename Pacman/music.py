from PyQt5.QtMultimedia import QSound


class Music:
    waka_sound = QSound('waka.wav')
    start_sound = QSound('start.wav')
    death_sound = QSound('death.wav')

    @staticmethod
    def start():
        Music.start_sound.play()

    @staticmethod
    def waka():
        Music.waka_sound.play()

    @staticmethod
    def death():
        Music.death_sound.play()
