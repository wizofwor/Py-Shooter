'''Python_Shooter 2

SpriteSheet ile grafik yükleme
'''

import sys
import pygame as pg
import xml.etree.ElementTree as ET

# Global Constants
VERSION = "0.02"
NAME = "Python Shooter " + VERSION
SCREEN_SIZE = (450,600)
FPS = 50



class SpriteSheet:
	''' Kenny.nl dosyaları için Sprite Sheet imaj ve XML dosyalarını yükler
	'''
	def __init__(self, img_file, data_file):
		self.spritesheet = pg.image.load(img_file).convert_alpha()

		tree = ET.parse(data_file)
		self.map = {}
		for node in tree.iter():
			if node.attrib.get('name'):
				name = node.attrib.get('name')
				self.map[name] = {}
				self.map[name]['x'] = int(node.attrib.get('x'))/2+1
				self.map[name]['y'] = int(node.attrib.get('y'))/2+1
				self.map[name]['width'] = int(node.attrib.get('width'))/2-1
				self.map[name]['height'] = int(node.attrib.get('height'))/2-1

	def get_image(self, name):
		rect = pg.Rect(self.map[name]['x'], self.map[name]['y'],
				self.map[name]['width'], self.map[name]['height'])
		return self.spritesheet.subsurface(rect)


clock = pg.time.Clock()

pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)
caption = pg.display.set_caption(NAME)

# Sprite Definitions
sheet = SpriteSheet("assets/sheet.png","assets/sheet.xml")
playerSprite = sheet.get_image("playerShip3_blue.png")

# Game Loop
while True:
        for event in pg.event.get():
                if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()

        screen.blit(playerSprite, (160,500))   
        clock.tick(FPS)
        pg.display.flip()