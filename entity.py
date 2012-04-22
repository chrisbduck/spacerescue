#!/usr/bin/python
#-------------------------------------------------------------------------------
# Space Rescue game - game entities and management.
# 
# Feel free to do what you like with this code, application, and data...
# except sell it :)
# 
# - Chris Bevan, 21-22 April, 2012
#-------------------------------------------------------------------------------

import math
import pygame
import random

NUM_TURRETS = 10

_screen = None
_renderText = None

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
	
	def __init__(self, centre_pos, image, name):
		self._image = Entity.getImage(image)
		self._rect = self._image.get_rect()
		self._fpos = [centre_pos[0] - self._rect.width / 2.0,
					  centre_pos[1] - self._rect.height / 2.0]
		self._rect.move_ip(self._fpos)
		self._fvel = [0.0, 0.0]
		self._angle_deg = None
		self._alive = True
		mgr.add(self)
		
	@staticmethod
	def getImage(image_name):
		if image_name not in Entity._images:
			Entity._images[image_name] = pygame.image.load(image_name + '.png')
		return Entity._images[image_name]
		
	def getCentre(self):
		return (self._fpos[0] + self._rect.width / 2.0,
				self._fpos[1] + self._rect.height / 2.0)
		
	def update(self):
		self._fpos[0] += self._fvel[0]
		self._fpos[1] += self._fvel[1]
		self._rect.left = int(self._fpos[0])
		self._rect.top = int(self._fpos[1])
	
	def render(self, screen):
		if self._angle_deg is not None:
			# Rotated render
			rotated = pygame.transform.rotate(self._image, self._angle_deg)
			rotated_rect = rotated.get_rect()
			rotated_rect.move_ip(self._fpos[0] + (self._rect.width - rotated_rect.width) / 2.0,
								 self._fpos[1] + (self._rect.height - rotated_rect.height) / 2.0)
			screen.blit(rotated, rotated_rect)
		else:
			# Simple render
			screen.blit(self._image, self._rect)
	
#-------------------------------------------------------------------------------
class AsteroidEntity(Entity):
	def __init__(self, pos):
		super(AsteroidEntity, self).__init__(pos, 'data/asteroid', 'asteroid')
		self._hollow_image = Entity.getImage('data/asteroid-hollow')
		self._hollow_opacity = 0.0
		
	def getRadius(self):
		return self._rect.width / 2.0
		
	def update(self):
		# Work out how far away the player is from the asteroid centre
		asteroid_ctr = self.getCentre()
		player_ctr = player.getCentre()
		ctr_to_player = (asteroid_ctr[0] - player_ctr[0], asteroid_ctr[1] - player_ctr[1])
		dist_ctr_to_player = math.sqrt(ctr_to_player[0] * ctr_to_player[0]
										+ ctr_to_player[1] * ctr_to_player[1])
		# Opacity of hollow image = 1.0 when player distance <= surface radius
		#                   down to 0.0 at, say, 100 units beyond that
		dist_outside_radius = dist_ctr_to_player - self.getRadius()
		if dist_outside_radius <= 0:
			self._hollow_opacity = 1.0
		elif dist_outside_radius > 100:
			self._hollow_opacity = 0.0
		else:
			self._hollow_opacity = 1.0 - dist_outside_radius / 100.0
		
	def render(self, screen):
		screen.blit(self._image, self._rect)
		if self._hollow_opacity > 0.0:
			self._hollow_image.set_alpha(self._hollow_opacity * 255)
			screen.blit(self._hollow_image, self._rect)
		_renderText('Asteroid alpha: %d%%' % (self._hollow_opacity * 100), (0, 0), (255, 255, 255))

#-------------------------------------------------------------------------------
class TurretEntity(Entity):
	_count = 0
	def __init__(self, asteroid, angle_deg):
		TurretEntity._count += 1
		angle_rad = angle_deg * math.pi / 180
		radius = asteroid.getRadius()
		radius += 4 	# slight fudge factor :) - half of turret pixel radius
		pos = list(asteroid.getCentre())
		pos[0] += radius * math.cos(angle_rad)
		pos[1] -= radius * math.sin(angle_rad)
		super(TurretEntity, self).__init__(pos, 'data/gun-turret',
			'gun-turret%d' % TurretEntity._count)
		# Match the turret orientation to its angle from the asteroid centre
		self._angle_deg = angle_deg - 90	# base image is straight up, so rotate 90 degrees CW

#-------------------------------------------------------------------------------
class PlayerEntity(Entity):
	_instance = None
	def __init__(self, pos):
		assert(PlayerEntity._instance is None)
		PlayerEntity._instance = self
		super(PlayerEntity, self).__init__(pos, 'data/player-ship', 'player')
		self._accel_multiplier = 10.0
		
	def accelerate(self, amount):
		self._fvel[0] += amount[0] * self._accel_multiplier
		self._fvel[1] += amount[1] * self._accel_multiplier
		if amount[1] == 0.0:
			self._angle_deg = 0 if amount[0] > 0.0 else 180
		else:
			self._angle_deg = math.atan2(-amount[1], amount[0]) * 180 / math.pi
		
	def reset(self):
		global _screen_rect
		self._fpos[0] = (_screen_rect.width - self._rect.width) / 2.0
		self._fpos[1] = (_screen_rect.height - self._rect.height) / 2.0
		self._fvel[:] = [0.0, 0.0]
		
#-------------------------------------------------------------------------------
def init(screen, screen_rect, renderText):
	global _screen, _screen_rect, _renderText
	_screen = screen
	_screen_rect = screen_rect
	_renderText = renderText

#-------------------------------------------------------------------------------

mgr = EntityManager()

asteroid = AsteroidEntity((500, 300))
[TurretEntity(asteroid, random.randint(0, 359)) for n in range(NUM_TURRETS)]
player = PlayerEntity((30, 300))

