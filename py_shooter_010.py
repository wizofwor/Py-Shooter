'''Python_Shooter 10

Intro Ekranı eklendi
Gameover ekranı düzenlendi

'''

import sys
import pygame as pg
import xml.etree.ElementTree as ET
import math

# Global Constants
VERSION = "0.10"
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

class Sounds:
	''' Oyunda kullanılacak sesler '''

	def __init__(self):
		self.fire = pg.mixer.Sound("assets/shoot-01.wav")
		self.fire.set_volume(.1)
		self.enemy_fire = pg.mixer.Sound("assets/shoot-03.wav")
		self.enemy_fire.set_volume(.1)
		self.explosion = pg.mixer.Sound("assets/explosion-02.wav")
		self.explosion.set_volume(.2)
		self.game_over = pg.mixer.Sound("assets/sfx_lose.ogg")
		self.game_over.set_volume(.2)

class Actor(pg.sprite.Sprite):
	''' Hareketli grafik obje sınıfı '''

	def __init__(self, image, x=0, y=0):
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

	def __init__(self, parent):
		image = parent.sheet.get_image("playerShip3_blue.png")
		super().__init__(image)
		self.gun_delay = 25
		self.bullets = []
		self.parent = parent

	def fire(self):
		if (self.gun_delay == 0):
			bullet1 = Bullet(self.parent)
			bullet2 = Bullet(self.parent)
			bullet1.set_pos(self.rect.x, self.rect.y)
			bullet2.set_pos(self.rect.x + 45, self.rect.y)

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

	def explode(self):
		self.parent.sounds.explosion.play()
		explosion = Explosion(self.parent, self.rect.x, self.rect.y)
		self.parent.sprite_list.add(explosion)
		self.kill()			

class Enemy(Actor):
	''' Düşman Uçağı Sınıfı '''

	def __init__(self, parent):
		image = parent.sheet.get_image("enemyBlack2.png")
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
			self.explode()

		if self.timer > 50:
			self.fire()
			self.timer = 0
		else:
			self.timer += 1

	def fire(self):
		bullet = EnemyBullet(self.parent)
		bullet.set_pos(
			self.rect.x + self.rect.width/2 - 2,
			self.rect.bottom
			)
		self.parent.enemy_bullets.add(bullet)
		self.parent.sprite_list.add(bullet)

	def explode(self):
		self.parent.sounds.explosion.play()
		explosion = Explosion(self.parent, self.rect.x, self.rect.y)
		self.parent.sprite_list.add(explosion)
		self.kill()

	def set_pos(self, x, y):
		self.x_offset = x
		self.rect.y = y	

class Bullet(Actor):
	''' Mermi obje sınıfı '''
	def __init__(self, parent):
		image = parent.sheet.get_image("laserBlue01.png")
		super().__init__(image)
		parent.sounds.fire.play()

	def update(self):
		# Mermiyi hareket ettir
		self.rect.y += -20
		# Mermi tepeye ulaştığında kendini öldür
		if(self.rect.bottom < 0):
			self.kill()

class EnemyBullet(Actor):
	''' Düşman Mermileri '''
	def __init__(self, parent):
		image = parent.sheet.get_image("laserRed02.png")
		super().__init__(image)
		parent.sounds.enemy_fire.play()

	def update(self):
		self.rect.y += 10
		if(self.rect.top > SCREEN_SIZE[1]):
			self.kill()

class Explosion(Actor):
	''' Patlama '''

	def __init__(self, parent, x, y):
		self.images = []
		for i in range (0,8):
			path = "assets/explosion0{}.png".format(i)
			image = pg.image.load(path).convert_alpha()
			image = pg.transform.scale(image, (80, 80))
			self.images.append(image)
		super().__init__(self.images[0])	
		self.rect = self.images[0].get_rect()
		self.rect.x = x
		self.rect.y = y

		self.frame = 0
	
	def update(self):
		if self.frame != 8:
			self.image = self.images[self.frame]
			self.frame += 1
		else:
			self.kill()

class LevelMap():
	''' Zamana bağlı olarak hangi düşmanların gönderileceğini belirten 
	Sınıf '''

	def __init__(self):
		data_source = open('level_data.xml')
		tree = ET.parse(data_source)
		self.root = tree.getroot()
		self.iteration = 0

	def get_trigger(self):
		''' Sıradaki olayın zamanını döndürür
		(Sıradaki olay 'END' ise -1 döndürür.) '''

		if self.root[self.iteration].tag == 'END':
			return -1
		else:
			return int(self.root[self.iteration].attrib['Time'])

	def get_attrib(self):
		''' Tanımlanacak düşmanların listesini döndürür
		ve iteration değerini bir arttırır '''

		enemy_attrib = []
		for subelem in self.root[self.iteration]:
			enemy_attrib.append(subelem.attrib)

		self.iteration +=1

		return enemy_attrib 	

	def print_all(self):
		# all items data
		print('\nAll Item attributes & data:')  
		for elem in self.root:
			print("event time: {}"
				.format(elem.attrib['Time'])
				)  
			for subelem in elem:
				print("   attrib: {}"
					.format(
						subelem.attrib
						)
					)


class main():
	''' Ana program '''

	def __init__(self):

		self.clock = pg.time.Clock()

		pg.init()
		self.screen = pg.display.set_mode(SCREEN_SIZE)
		self.screen_rect = self.screen.get_rect()
		caption = pg.display.set_caption(NAME)

		self.font = pg.font.Font('assets/kenvector_future.ttf', 12)
		self.font_big = pg.font.Font('assets/Venusris.ttf', 21)

		self.title_screen()

		# Arka ekran resmini ekle
		self.bg_image = pg.image.load("assets/back.png").convert()

		# Sesleri tanımla
		self.sounds = Sounds()

		# Sprite Tanımları
		self.sheet = SpriteSheet("assets/sheet.png","assets/sheet.xml")
		self.player = Player(self)
		self.player.set_pos(190, 500)

		# Sprite Listeleri
		self.sprite_list = pg.sprite.Group()
		self.enemies = pg.sprite.Group()
		self.player_bullets = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group() 

		self.sprite_list.add(self.player)
		
		self.game_start()


	def game_start(self):
		''' Oyunun başında sıfırlanması gereken değişkenlerin ayarlanması
		ve oyunu başlat.
		'''
		self.y_scroll = 0
		self.x_scroll = 0
		self.game_time = 0
		self.game_time_text = None
		self.score_text = None
		self.score = 0

		self.level_map = LevelMap()

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

		# Sıradaki saldırı dalgasının zamanını al 
		trigger = self.level_map.get_trigger()
		if trigger == -1:
			self.game_over()

		# Saldırı dalgasını zaman geldiğinde düşman gemilerini yarat
		if (self.game_time > trigger):
			# Düşman gemilerinin özelliklerini al
			attribs_list = self.level_map.get_attrib()
			for attribs in attribs_list:
				enemy = Enemy(self)
				self.sprite_list.add(enemy)
				self.enemies.add(enemy)
				enemy.set_pos(
					int(attribs['x']),
					int(attribs['y'])
					)

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
		def centered_text(message, y):
			''' Metni ortalamak için kullanacağım inner function
			Burada self parametresi yok ve metodun en başında 
			tanımlanmak zorunda. '''

			text_surface = \
				self.font_big.render(
				message,
				True,
				(0, 255, 255)
				)
			text_rect = text_surface.get_rect()
			x, _ = self.screen_rect.center
			x -= text_rect.width/2

			self.screen.blit(text_surface, (x, y))


		self.player.explode()
		self.screen.fill((0,0,0))

		centered_text("Python Shooter Game", 50)
		centered_text("Oyun Bitti !", 250)
		centered_text(self.score_text, 350)

		pg.display.flip()

		self.sounds.game_over.play()

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()
				if event.type == pg.KEYDOWN:
					self.__init__()


	def title_screen(self):
		''' Açılış Ekranı '''

		#font = pg.font.Font('assets/Venusris.ttf', 28)
		bg_image = pg.image.load("assets/intro_screen.png").convert()
		self.screen.blit(bg_image, (0, 0))

		colors = (
			(255, 255, 0),
			(255, 192, 0),
			(192, 127, 0),
			(127, 63,  0),
			(127, 63,  0),
			(63,  0,   0),
			(63,  0,   0),
			(63,  0,   0),			
			(63,  0,   0),
			(63,  0,   0),
			(127, 63,  0),
			(192, 127, 0),
			(127, 63,  0),		
			(255, 192, 0),
			(255, 255, 0)
			)

		color_index = 0

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()
				if event.type == pg.KEYDOWN:
					return

			# Metni ortalamak için biraz cambazlık yapmam gerekecek
			text_surface = \
				self.font.render(
				"Baslamak icin hernagi bir tusa basin",
				True,
				colors[color_index//100])
			text_rect = text_surface.get_rect()
			x, y = self.screen_rect.center
			x -= text_rect.width/2
			y = 540

			self.screen.blit(text_surface,
				(x, y)
				)

			# Renk döngüsünü uygulayalım
			color_index = (color_index + 1) % 1500

			pg.display.flip()

if __name__ == '__main__':
			main()		