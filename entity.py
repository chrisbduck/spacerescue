#!/usr/bin/python
#-------------------------------------------------------------------------------
# Space Rescue game - game entities and management.
# 
# Feel free to do what you like with this code, application, and data...
# except sell it :)
# 
# - Chris Bevan, 21-22 April, 2012
#-------------------------------------------------------------------------------

import pygame

_screen = None

#-------------------------------------------------------------------------------
class EntityManager(object):
	def __init__(self):
		self._entities = []
		
	def update(self):
		[entity.update() for entity in self._entities]
		
	def render(self, screen):
		[entity.render(screen) for entity in self._entities]
		
	def add(self, entity):
		self._entities.append(entity)
		
	def remove(self, entity):
		self._entities.remove(entity)

#-------------------------------------------------------------------------------
class Entity(object):
	
	_images = {}
	
	def __init__(self, pos, image, name):
		if image not in Entity._images:
			Entity._images[image] = pygame.image.load(image + '.png')
		self._image = Entity._images[image]
		self._rect = self._image.get_rect()
		self._rect.move_ip(pos)
		self._fpos = [float(pos[0]), float(pos[1])]		# float pos for precision movement
		self._fvel = [0.0, 0.0]
		self._alive = True
		mgr.add(self)
		
	def update(self):
		self._fpos[0] += self._fvel[0]
		self._fpos[1] += self._fvel[1]
		self._rect.left = int(self._fpos[0])
		self._rect.top = int(self._fpos[1])
	
	def render(self, screen):
		screen.blit(self._image, self._rect)
	
#-------------------------------------------------------------------------------
class PlayerEntity(Entity):
	_instance = None
	def __init__(self):
		assert(PlayerEntity._instance is None)
		PlayerEntity._instance = self
		super(PlayerEntity, self).__init__((0, 0), 'placeholders/big-bob', 'player')
		self._accel_multiplier = 10.0
		
	def accelerate(self, amount):
		self._fvel[0] += amount[0] * self._accel_multiplier
		self._fvel[1] += amount[1] * self._accel_multiplier
		
	def reset(self):
		global _screen_rect
		self._fpos[0] = (_screen_rect.width - self._rect.width) / 2.0
		self._fpos[1] = (_screen_rect.height - self._rect.height) / 2.0
		self._fvel[:] = [0.0, 0.0]
		
#-------------------------------------------------------------------------------
def init(screen, screen_rect):
	global _screen, _screen_rect
	_screen = screen
	_screen_rect = screen_rect
	player.reset()

#-------------------------------------------------------------------------------

mgr = EntityManager()

player = PlayerEntity()
