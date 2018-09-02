'''Python_Shooter 4

Main sınıfı
Mermi sınıfı
'''

import sys
import pygame as pg
import xml.etree.ElementTree as ET

# Global Constants
VERSION = "0.04"
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
		# Obje ekranın dışına çıkmasın
		if(self.rect.right < 0 + self.rect.width/2):
			self.rect.right = 0 + self.rect.width/2
		if(self.rect.left > (SCREEN_SIZE[0]-self.rect.width/2)):
			self.rect.left = SCREEN_SIZE[0]-self.rect.width/2
		if(self.rect.bottom > SCREEN_SIZE[1]):
			self.rect.bottom = SCREEN_SIZE[1]
		if(self.rect.top < 0):
			self.rect.top = 0

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

class Bullet(Actor):
	''' Mermi obje sınıfı '''

	def update(self):
		# Mermiyi hareket ettir
		self.rect.y += -4
		# Mermi tepeye ulaştığında kendini öldürk
		if(self.rect.bottom < 0):
			self.kill()

class main():
	''' Ana program '''

	def __init__(self):

		self.clock = pg.time.Clock()

		pg.init()
		self.screen = pg.display.set_mode(SCREEN_SIZE)
		caption = pg.display.set_caption(NAME)

		#Arka ekran resmini ekle
		self.bg_image = pg.image.load("assets/back.png").convert()

		# Sprite Tanımları
		self.sheet = SpriteSheet("assets/sheet.png","assets/sheet.xml")
		self.player = Actor(self.sheet.get_image("playerShip3_blue.png"))
		self.player.set_pos(190, 500)

		# Sprite Listesi
		self.sprite_list = pg.sprite.Group()
		self.sprite_list.add(self.player)

		self.gun_delay = 0
		self.y_scroll = 0
		self.x_scroll = 0

		self.game_loop()

	def game_loop(self):
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
				self.player.go_left()
				self.x_scroll += 1
			if keys[pg.K_RIGHT]:
				self.player.go_right()
				self.x_scroll -= 1
			if keys[pg.K_UP]:
				self.player.go_up()
			if keys[pg.K_DOWN]:
				self.player.go_down()
			if keys[pg.K_SPACE]:
				''' Boşluk tuşuna basıldığında eğer silah hazırsa (delay==0)
				iki adet bir mermi yarat.
				'''
				if (self.gun_delay == 0):
					bullet1 = Bullet(self.sheet.get_image("laserBlue01.png"))
					bullet2 = Bullet(self.sheet.get_image("laserBlue01.png"))
					bullet1.rect.x = self.player.rect.x
					bullet1.rect.y = self.player.rect.y
					bullet2.rect.x = self.player.rect.x + 45
					bullet2.rect.y = self.player.rect.y	
					# Mermiyi sprite Listesine ekle
					self.sprite_list.add(bullet1)
					self.sprite_list.add(bullet2)
					# Bir sonraki atış için gecikme sayacını başlat
					self.gun_delay = 25

			# Bekle
			self.clock.tick(FPS)

			# Sayaçları güncelle
			
			# Mermi gecikme sayacını
			if(self.gun_delay > 0):
				self.gun_delay -= 1

			# Dikey kaydırma
			if(self.y_scroll == 256):
				self.y_scroll = 0
			else:
				self.y_scroll += 1	

			# Yatay kaydırma
			if(abs(self.x_scroll) == 256):
				self.x_scroll = 0

			# Arka ekran resmini kopyala
			for i in range(0, 4):
				for j in range(0, 4):
					self.screen.blit(
						self.bg_image,
							(
							256*(i-1)+self.x_scroll,
							256*(j-1)+self.y_scroll
							))
			# Spriteları ve görüntü yüzeyini güncelle
			self.sprite_list.update()
			self.sprite_list.draw(self.screen)
			pg.display.flip()

if __name__ == '__main__':
			main()		