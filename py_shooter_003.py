'''Python_Shooter 3

Actor sınıfı
'''

import sys
import pygame as pg
import xml.etree.ElementTree as ET

# Global Constants
VERSION = "0.03"
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

class Actor(pg.sprite.Sprite):
	''' Hareketli grafik obje sınıfı '''

	def __init__(self, image):
		super().__init__()
		self.dx = 0
		self.dy = 0
		self.image = image
		self.rect = self.image.get_rect()

	def update(self):
		''' Objeyi hareket ettir '''
		self.rect.x += self.dx
		self.rect.y += self.dy
		self.dx = 0
		self.dy = 0

    # Hareket Komutları
	def set_pos(self, xx, yy):
		self.rect.x = xx
		self.rect.y = yy

	def go_left(self):
		self.dx = -2

	def go_right(self):
		self.dx = 2

	def go_up(self):
		self.dy = -2

	def go_down(self):
		self.dy = 2

	def stop(self):
		self.dx = 0
		self.dy = 0


clock = pg.time.Clock()

pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)
caption = pg.display.set_caption(NAME)

#Arka ekran resmini ekle
bg_image = pg.image.load("assets/back.png").convert()

# Sprite Tanımları
sheet = SpriteSheet("assets/sheet.png","assets/sheet.xml")
player = Actor(sheet.get_image("playerShip3_blue.png"))
player.set_pos(190, 500)

# Sprite Listesi
sprite_list = pg.sprite.Group()
sprite_list.add(player)


# Ana Döngü
while True:
	# Olay Kontrolü
	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			sys.exit()

	# Hareket kontrol
	keys = pg.key.get_pressed()
	if keys[pg.K_LEFT]:
		player.go_left()
	if keys[pg.K_RIGHT]:
		player.go_right()
	if keys[pg.K_UP]:
		player.go_up()
	if keys[pg.K_DOWN]:
		player.go_down()

	# Bekle
	clock.tick(FPS)

	# Arka ekran resmini kopyala
	for i in range(0, 2):
		for j in range(0, 3):
			screen.blit(bg_image, (256*i,256*j))
	# Spriteları ve görüntü yüzeyini güncelle
	sprite_list.update()
	sprite_list.draw(screen)
	pg.display.flip()