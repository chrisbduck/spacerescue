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
		if image in Entity._images:
			self._image = Entity._images[image]
		else:
			self._image = pygame.image.load('placeholders/%s.png' % image)
			Entity._images[image] = self._image
		self._rect = self._image.get_rect()
		self._rect.move_ip(pos)
		self._alive = True
		entities.add(self)
		
	def update(self):
		pass
	
	def render(self, screen):
		screen.blit(self._image, self._rect)
	
#-------------------------------------------------------------------------------

entities = EntityManager()

Entity((50, 50), 'bob', 'player')
