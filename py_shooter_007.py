'''Python_Shooter 7

Düşmanlarda ateş edebilsinler
Game Over Ekranı

'''

import sys
import pygame as pg
import xml.etree.ElementTree as ET
import math

# Global Constants
VERSION = "0.07"
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

class Player(Actor):
	''' Oyuncu Uçağı Sınıfı '''

	def __init__(self, parent, image):
		super().__init__(image)
		self.dx = 0
		self.dy = 0
		self.gun_delay = 25
		self.bullets = []
		self.parent = parent 

	def fire(self):
		if (self.gun_delay == 0):
			bullet1 = Bullet(self.parent.sheet.get_image("laserBlue01.png"))
			bullet2 = Bullet(self.parent.sheet.get_image("laserBlue01.png"))
			bullet1.rect.x = self.rect.x
			bullet1.rect.y = self.rect.y
			bullet2.rect.x = self.rect.x + 45
			bullet2.rect.y = self.rect.y

			# Mermiyi sprite Listelerine ekle
			self.bullets.append(bullet1)
			self.bullets.append(bullet2)
			self.parent.sprite_list.add(bullet1)
			self.parent.sprite_list.add(bullet2)
			
			# Bir sonraki atış için gecikme sayacını başlat
			self.gun_delay = 25

	def update(self):
		super().update()
		if self.gun_delay > 0:
			self.gun_delay -= 1		

class Enemy(Actor):
	''' Düşman Uçağı Sınıfı '''

	def __init__(self, parent, image):
		super().__init__(image)
		self.x_offset = None
		self.is_hit = False
		self.parent = parent
		self.timer = 0

	def update(self):
		self.rect.y += +2
		self.rect.x = self.x_offset+math.sin(math.radians(self.rect.y))*50

		if(self.rect.top > SCREEN_SIZE[1]):
			self.kill()

		if self.is_hit:
			self.kill()

		if self.timer > 50:
			self.fire()
			self.timer = 0
		else:
			self.timer += 1

	def fire(self):
		bullet = EnemyBullet(self.parent.sheet.get_image("laserRed02.png"))
		bullet.rect.x = self.rect.x + self.rect.width/2 - 2
		bullet.rect.y = self.rect.bottom
		self.parent.enemy_bullets.add(bullet)
		self.parent.sprite_list.add(bullet)

class Bullet(Actor):
	''' Mermi obje sınıfı '''

	def update(self):
		# Mermiyi hareket ettir
		self.rect.y += -20
		# Mermi tepeye ulaştığında kendini öldür
		if(self.rect.bottom < 0):
			self.kill()

class EnemyBullet(Actor):
	''' Düşman Mermileri '''

	def update(self):
		self.rect.y += 10
		if(self.rect.top > SCREEN_SIZE[1]):
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
		self.player = Player(self, self.sheet.get_image("playerShip3_blue.png"))
		self.player.set_pos(190, 500)

		# Sprite Listeleri
		self.sprite_list = pg.sprite.Group()
		self.enemies = pg.sprite.Group()
		self.player_bullets = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group() 

		self.sprite_list.add(self.player)

		# Sayaçlar
		self.gun_delay = 0
		self.y_scroll = 0
		self.x_scroll = 0
		self.game_time = 0

		# Gösterilecek Metinler
		self.font = pg.font.SysFont('Consolas', 18)
		self.game_time_text = None
		self.score_text = None

		self.score = 0


		self.game_loop()

	def game_loop(self):
		# Ana Oyun Döngüsü
		while True:
			# Kullanıcı girişlerini denetle
			self.check_user_events()
			# Oyun motoru
			self.core_engine()
			# Ekranı güncelle
			self.update_game_screen()

			# Bekle			
			self.clock.tick(FPS)

	def check_user_events(self):
		# Kullanıcı olaylarının kontrolü

			# Olay Kontrolü
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()

			# Hareket kontrol
			keys = pg.key.get_pressed()
			if keys[pg.K_r]:
				self.__init__()
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
				self.player.fire()


	def core_engine(self):
		# 250 ms aralıkla düşman gönder	
		if (self.game_time%500==0):
			enemy = Enemy(self, self.sheet.get_image("enemyBlack2.png"))
			self.sprite_list.add(enemy)
			self.enemies.add(enemy)
			enemy.y = 100
			enemy.x_offset = 100

		elif(self.game_time%250==0):
			enemy = Enemy(self, self.sheet.get_image("enemyBlack2.png"))
			self.sprite_list.add(enemy)
			self.enemies.add(enemy)
			enemy.y = 100
			enemy.x_offset = 300	

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

		# Zaman
		self.game_time += 1

		# Gösterilecek metinleri hazırla 
		self.game_time_text = (
			"Süre: {}"
			.format(str(self.game_time//100).rjust(3))
			)
		self.score_text = (
			"Puan: {}"
			.format(str(self.score))
			)

	def update_game_screen(self):
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
		
		# Çakışma kontrolleri
		# Düşman isabet aldı mı?
		for bullet in self.player.bullets:
			hits = pg.sprite.spritecollide(bullet, self.enemies, False)
			for enemy in hits:
				enemy.is_hit = True
				self.score += 500
				hits = None
		
		# Çarpışma
		hits = pg.sprite.spritecollide(self.player, self.enemies, False)
		if hits:
			print("Carpisma!")
			self.game_over()
		else: 
			hits = pg.sprite.spritecollide(self.player, self.enemy_bullets, False)
			if hits: 
				print("Carpisma!")
				self.game_over()

		# Zamanı güncelle
		self.screen.blit(self.font.render(self.game_time_text, True, (0, 128, 0)), (140, 10))
		self.screen.blit(self.font.render(self.score_text, True, (0, 128, 0)), (320, 10))
		pg.display.flip()

	def game_over(self):
		self.screen.fill((0,0,0))

		font = pg.font.SysFont('Consolas', 30)
		self.screen.blit(font.render(
			"Python Shooter Game",
			True,
			(0, 128, 0)),
			(60,50)
			)

		self.screen.blit(font.render(
			"Oyun Bitti",
			True,
			(0, 128, 0)),
			(130, 250)
			)

		self.screen.blit(font.render(
			self.score_text, 
			True,
			(0, 128, 0)),
			(130, 350)
			)

		pg.display.flip()

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()
				if event.type == pg.KEYDOWN:
					self.__init__()



if __name__ == '__main__':
			main()		