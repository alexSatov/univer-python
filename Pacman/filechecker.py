import os
import sys

all_files = os.listdir('.')
impotent_files = ['Blinky.png', 'bluePortal.png', 'Clyde.png', 'death.wav',
                  'FireBall.png', 'FireBallDeath.png', 'food.png',
                  'graphic.py', 'logic.py', 'statistics.py',
                  'ghostHouse1.png', 'ghostHouse2.png', 'ghostHouse3.png',
                  'ghostHouse4.png', 'ghostHouse5.png', 'help.txt', 'Inky.png',
                  'level1.txt', 'level2.txt', 'level3.txt', 'logo.png',
                  'main.py', 'music.py', 'orangePortal.png', 'Pacman.png',
                  'PacmanDeath.png', 'Pinky.png', 'README.txt', 'records.txt',
                  'start.wav', 'waka.wav', 'wall.png']
error = False
for file in impotent_files:
    if file not in all_files:
        print('File {} isn\'t finded. Try reinstall game'.format(file))
        error = True
if error:
    sys.exit()


