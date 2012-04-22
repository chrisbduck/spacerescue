#!/usr/bin/python
#-------------------------------------------------------------------------------
# Space Rescue game - game entities and management.
# 
# Feel free to do what you like with this code, application, and data...
# except sell it :)
# 
# - Chris Bevan, 21-22 April, 2012
#-------------------------------------------------------------------------------

from common import *
import math
import misc
import pygame
import random
from misc import debugMsg

TWO_PI = 2 * math.pi
DEG_TO_RAD = math.pi / 180
RAD_TO_DEG = 180 / math.pi

DEATH_SCORE_PENALTY = 5
RESCUE_SCORE = 3
PLAYER_INITIAL_POS = (30.0, 300.0)
LEVEL_UP_DISPLAY_SEC = 4

_screen = None
_screen_rect = None
level_up_countdown = None

#-------------------------------------------------------------------------------
class EntityManager(object):
	#-------------------------------------------------------------------------------
	def __init__(self):
		self.clear()
		
	#-------------------------------------------------------------------------------
	def clear(self):
		self._entities = []
		global asteroid
		asteroid = None
		global player
		player = None
		PlayerEntity._instance = None
		
	#-------------------------------------------------------------------------------
	def clearBullets(self):
		self._entities = [entity for entity in self._entities \
							if not isinstance(entity, BulletEntity)]
		
	#-------------------------------------------------------------------------------
	def generate(self):
		global asteroid
		asteroid = AsteroidEntity((500, 300))
		self._generatePlacements()
		global player
		player = PlayerEntity(PLAYER_INITIAL_POS)
		
	#-------------------------------------------------------------------------------
	def _generatePlacementAngles(self, count, place_around_entrance=True, avoid_angles=None):
		# Start with two around the entrance
		if place_around_entrance:
			result_angles = [ENTRANCE_MIN_ANGLE_DEG, ENTRANCE_MAX_ANGLE_DEG]
		else:
			result_angles = []
		while len(result_angles) < count:
			new_angle = random.randint(0, 359)
			# Don't put near the entrance
			if new_angle >= ENTRANCE_MIN_ANGLE_DEG and new_angle <= ENTRANCE_MAX_ANGLE_DEG:
				continue
			# Don't put them too close to another
			if not any([abs(new_angle - angle) < 12 for angle in result_angles]):
				if avoid_angles is None or \
						not any([abs(new_angle - angle) < 3 for angle in avoid_angles]):
					result_angles.append(new_angle)
		return result_angles
		
	#-------------------------------------------------------------------------------
	def _generatePlacements(self):
		"Generates placed entities: turrets and spacemen."
		# Determine placements
		outside_turret_angles = self._generatePlacementAngles(misc.num_turrets,
															  place_around_entrance=True)
		inside_turret_angles = self._generatePlacementAngles(misc.num_turrets,
															 place_around_entrance=True)
		spaceman_angles = self._generatePlacementAngles(misc.num_spacemen,
														place_around_entrance=False,
														avoid_angles=inside_turret_angles)
		
		# Construct
		[TurretEntity(asteroid, angle, outside=True) for angle in outside_turret_angles]
		[TurretEntity(asteroid, angle, outside=False) for angle in inside_turret_angles]
		[SpacemanEntity(asteroid, angle) for angle in spaceman_angles]

	#-------------------------------------------------------------------------------
	def update(self):
		# Update all
		[entity.update() for entity in self._entities]
		# Collide
		self.testForCollisions()
		# Level logic
		self.updateLevel()
		# Remove dead stuff
		self._entities = [entity for entity in self._entities if entity.alive]
		
	#-------------------------------------------------------------------------------
	def render(self, screen):
		[entity.render(screen) for entity in self._entities]
		
	#-------------------------------------------------------------------------------
	def add(self, entity):
		self._entities.append(entity)
		
	#-------------------------------------------------------------------------------
	def updateLevel(self):
		# Check for level finish
		global level_up_countdown
		if level_up_countdown is None:
			# Check for level completion
			if not any((isinstance(entity, SpacemanEntity) for entity in self._entities)) \
					and asteroid._hollow_opacity < 0.5:
				# Level up (start timer)
				level_up_sound = Entity.getSound('data/sfx/Powerup2')
				level_up_sound.play()
				level_up_countdown = LEVEL_UP_DISPLAY_SEC * MAX_FPS
		else:
			# Check for display completion & actual level change
			level_up_countdown -= 1
			if level_up_countdown <= 0:
				new_level_sound = Entity.getSound('data/sfx/Powerup1')
				new_level_sound.play()
				level_up_countdown = None
				misc.setLevel(misc.level + 1)
				self.clear()
				self.generate()
		
	#-------------------------------------------------------------------------------
	def testForCollisions(self):
		bullets = [entity for entity in self._entities if isinstance(entity, BulletEntity)]
		vulnerables = [entity for entity in self._entities if entity.vulnerable]
		bullet_rects = [entity._rect for entity in bullets]
		vulnerable_rects = [entity._rect for entity in vulnerables]
		
		# Collide bullets with vulnerables
		for b in bullets:
			collided_with_index = b._rect.collidelist(vulnerable_rects)
			if collided_with_index >= 0:
				collided_with = vulnerables[collided_with_index]
				debugMsg('%s was shot by %s' % (collided_with.name, b.name))
				if b._shot_by_player:
					# Lose points for shooting spacemen; gain points for shooting anything else
					# that's vulnerable
					if isinstance(collided_with, SpacemanEntity):
						misc.score -= 1
					else:
						misc.score += 1
				b.destroy()
				collided_with.destroy()
		
		# Collide vulnerables with other vulnerables
		for v in (player,):		# was vulnerables; avoiding turret-turret collisions for now
			# Remove this vulnerable from the list to check, or it'll always collide with itself
			vuln_test = vulnerables
			vuln_rects_test = vulnerable_rects
			for v2_index in range(len(vuln_test)):
				if vuln_test[v2_index] is v:
					vuln_test = vuln_test[:v2_index] + vuln_test[v2_index + 1:]
					vuln_rects_test = vuln_rects_test[:v2_index] + vuln_rects_test[v2_index + 1:]
					break
			
			collided_with_index = v._rect.collidelist(vuln_rects_test)
			if collided_with_index > 0:
				collided_with = vulnerables[collided_with_index]
				# If it's a spaceman, they get rescued; otherwise, the player dies
				if v is player and isinstance(collided_with, SpacemanEntity):
					debugMsg('player rescued %s' % collided_with.name)
					collided_with.rescue()
				else:
					debugMsg('%s ran into %s' % (v.name, collided_with.name))
					v.destroy()
					collided_with.destroy()
		
		# Collide the player and all bullets with the asteroid surface
		# Easiest way is intersecting two spheres with the entity's rect
		asteroid_tests = list(bullets)
		asteroid_rects = list(bullet_rects)
		if player.alive:
			asteroid_tests.append(player)
			asteroid_rects.append(player._rect)
		asteroid_ctr = asteroid.getCentre()
		asteroid_outer_radius = asteroid.getRadius()
		asteroid_inner_radius = asteroid.getInnerRadius()
		for index in xrange(len(asteroid_tests)):
			# Doing sphere-sphere collision here for now because it's easier
			entity = asteroid_tests[index]
			rect = asteroid_rects[index]
			entity_radius = entity.getRadius()
			offset = (rect.centerx - asteroid_ctr[0], rect.centery - asteroid_ctr[1])
			offset_dist = math.sqrt(offset[0] * offset[0] + offset[1] * offset[1])
			entity_outer_dist = offset_dist + entity_radius
			entity_inner_dist = offset_dist - entity_radius
			# Collision if offset distance < asteroid outer radius + entity
			if entity_outer_dist > asteroid_inner_radius \
					and entity_inner_dist < asteroid_outer_radius:
				# Check the offset angles to see if the entity went through the entrance
				in_entrance = False
				offset_dir = (offset[0] / offset_dist, offset[1] / offset_dist)
				offset_angle_rad = math.atan2(offset_dir[1], offset_dir[0])
				if offset_angle_rad < 0:
					offset_angle_rad += TWO_PI
				safe_min_angle_rad = 170 * DEG_TO_RAD
				safe_max_angle_rad = 190 * DEG_TO_RAD
				if offset_angle_rad > safe_min_angle_rad and offset_angle_rad < safe_max_angle_rad:
					# The angle to the ship centre was in the safe range.  Now check its extents
					offset_tangent_angle_rad = offset_angle_rad + math.pi / 2
					tangent_cos = math.cos(offset_tangent_angle_rad)
					tangent_sin = math.sin(offset_tangent_angle_rad)
					tangent_dir = (offset_dir[0] * tangent_cos - offset_dir[1] * tangent_sin,
								   offset_dir[0] * tangent_sin + offset_dir[1] * tangent_cos)
					tangent = (tangent_dir[0] * entity_radius, tangent_dir[1] * entity_radius)
					extent1 = (offset[0] + tangent[0], offset[1] + tangent[1])
					extent2 = (offset[0] - tangent[0], offset[1] - tangent[1])
					extent1_angle_rad = math.atan2(extent1[1], extent1[0])
					if extent1_angle_rad < 0:
						extent1_angle_rad += TWO_PI
					extent2_angle_rad = math.atan2(extent2[1], extent2[0])
					if extent2_angle_rad < 0:
						extent2_angle_rad += TWO_PI
					if min(extent1_angle_rad, extent2_angle_rad) > safe_min_angle_rad \
							and max(extent1_angle_rad, extent2_angle_rad) < safe_max_angle_rad:
						in_entrance = True
				
				if not in_entrance:
					debugMsg('%s hit %s' % (entity.name, asteroid.name))
					entity.destroy()

#-------------------------------------------------------------------------------
class Entity(object):
	
	_images = {}
	_sounds = {}
	debug_rects = False
	
	#-------------------------------------------------------------------------------
	def __init__(self, centre_pos, image, name):
		if image is not None:
			self._image = Entity.getImage(image)
			self._rect = self._image.get_rect()
			self._fpos = [centre_pos[0] - self._rect.width / 2.0,
						centre_pos[1] - self._rect.height / 2.0]
			self._rect.move_ip(self._fpos)
		self._fvel = [0.0, 0.0]
		self._angle_deg = None
		self.name = name
		self.vulnerable = False		# can be shot
		self.alive = True
		mgr.add(self)
		
	#-------------------------------------------------------------------------------
	@staticmethod
	def getImage(image_name):
		if image_name not in Entity._images:
			Entity._images[image_name] = pygame.image.load(image_name + '.png')
		return Entity._images[image_name]
		
	#-------------------------------------------------------------------------------
	@staticmethod
	def getSound(sound_name):
		if sound_name not in Entity._sounds:
			Entity._sounds[sound_name] = pygame.mixer.Sound(sound_name + '.ogg')
		return Entity._sounds[sound_name]
		
	#-------------------------------------------------------------------------------
	@staticmethod
	def playRandomSound(snd_list):
		snd_list[random.randint(0, len(snd_list) - 1)].play()
		
	#-------------------------------------------------------------------------------
	def getCentre(self):
		return (self._fpos[0] + self._rect.width / 2.0,
				self._fpos[1] + self._rect.height / 2.0)
		
	#-------------------------------------------------------------------------------
	def getRadius(self):
		return self._rect.width / 2.0
	
	#-------------------------------------------------------------------------------
	def setRect(self, x, y, width, height):
		self._rect = pygame.Rect(x, y, width, height)
		self._fpos = [float(x), float(y)]
		
	#-------------------------------------------------------------------------------
	def hasCollidedWith(self, entity):
		if not self._rect.colliderect(entity):
			return False
		# TO DO: add masks
		return True
		
	#-------------------------------------------------------------------------------
	def destroy(self):
		self.alive = False
	
	#-------------------------------------------------------------------------------
	def update(self):
		self._fpos[0] += self._fvel[0]
		self._fpos[1] += self._fvel[1]
		self._rect.left = int(self._fpos[0])
		self._rect.top = int(self._fpos[1])
	
	#-------------------------------------------------------------------------------
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
		if Entity.debug_rects:
			pygame.draw.rect(screen, (128, 128, 128, 128), self._rect, 1)
	
#-------------------------------------------------------------------------------
class AsteroidEntity(Entity):
	_count = 0
	
	#-------------------------------------------------------------------------------
	def __init__(self, pos):
		AsteroidEntity._count += 1
		name = 'asteroid%d' % AsteroidEntity._count
		super(AsteroidEntity, self).__init__(pos, 'data/asteroid', name)
		self._hollow_image = Entity.getImage('data/asteroid-hollow')
		self._hollow_opacity = 0.0
		self._is_hollow = False
		
	#-------------------------------------------------------------------------------
	def getInnerRadius(self):
		return self.getRadius() * 0.9
	
	#-------------------------------------------------------------------------------
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
			self._is_hollow = True
		else:
			self._is_hollow = False
			if dist_outside_radius > 100:
				self._hollow_opacity = 0.0
			else:
				self._hollow_opacity = 1.0 - dist_outside_radius / 100.0
		
	#-------------------------------------------------------------------------------
	def render(self, screen):
		if self._hollow_opacity < 1.0:
			screen.blit(self._image, self._rect)
		if self._hollow_opacity > 0.0:
			self._hollow_image.set_alpha(self._hollow_opacity * 255)
			screen.blit(self._hollow_image, self._rect)
		if misc.debug:
			misc.renderText('Hollow asteroid alpha: %d%%' % (self._hollow_opacity * 100),
							(5, 25), (255, 255, 255))

#-------------------------------------------------------------------------------
class TurretEntity(Entity):
	SHOOT_RANGE = 150	# if the player is within this range, the turret will shoot occasionally
	SHOOT_RANGE_SQ = SHOOT_RANGE * SHOOT_RANGE
	SECS_PER_SHOT = 1.0
	
	_count = 0
	
	_shoot_sounds = [Entity.getSound('data/sfx/Turret_shoot%d' % n) for n in range(1, 5)]
	_explosion_sounds = [Entity.getSound('data/sfx/Explosion%d' % n) for n in (11, 13)]
	
	#-------------------------------------------------------------------------------
	def __init__(self, asteroid, angle_deg, outside=True):
		TurretEntity._count += 1
		angle_rad = angle_deg * DEG_TO_RAD
		self._point_dir = (math.cos(angle_rad), -math.sin(angle_rad))
		if outside:
			radius = asteroid.getRadius()
			radius += 4 	# slight fudge factor :) - half of turret pixel radius
		else:
			radius = asteroid.getInnerRadius()
			radius -= 10	# fudge factor again
		pos = list(asteroid.getCentre())
		pos[0] += radius * self._point_dir[0]
		pos[1] += radius * self._point_dir[1]
		super(TurretEntity, self).__init__(pos, 'data/gun-turret',
			'gun-turret%d' % TurretEntity._count)
		
		# Match the turret orientation to its angle from the asteroid centre
		self._angle_deg = angle_deg - 90	# base image is straight up, so rotate 90 degrees CW
		if not outside:
			self._point_dir = (-self._point_dir[0], -self._point_dir[1])
			self._angle_deg += 180
		
		self._shoot_interval = int(TurretEntity.SECS_PER_SHOT * MAX_FPS *
									(0.9 + 0.2 * random.random()))
		self._shot_cooldown = 0
		self.vulnerable = True
		self._outside = outside
		
		# Turret's max shooting angle => min dot product for vector comparison
		# Turrets inside the asteroid need to be more restrained or they always shoot each other`
		self._min_shoot_dot_product = 0.1 if outside else 0.4
		
	#-------------------------------------------------------------------------------
	def destroy(self):
		super(TurretEntity, self).destroy()
		Entity.playRandomSound(TurretEntity._explosion_sounds)
		
	#-------------------------------------------------------------------------------
	def update(self):
		super(TurretEntity, self).update()
		# Don't update the inside turrets unless the asteroid is in its hollow state
		if not self._outside and not asteroid._is_hollow:
			return
		# Wind down the shooting timer if needed
		if self._shot_cooldown > 0:
			self._shot_cooldown -= 1
		elif player.alive:
			# See if the player is in range to shoot at
			offset_to_player = (player._fpos[0] - self._fpos[0],
								player._fpos[1] - self._fpos[1])
			dist_sq_to_player = offset_to_player[0] * offset_to_player[0] \
								+ offset_to_player[1] * offset_to_player[1]
			if dist_sq_to_player < TurretEntity.SHOOT_RANGE_SQ:
				# Check that the angle isn't more than a set amount from the turret's orientation
				dist_to_player = math.sqrt(dist_sq_to_player)
				dir_to_player = (offset_to_player[0] / dist_to_player,
								 offset_to_player[1] / dist_to_player)
				dot_product = self._point_dir[0] * dir_to_player[0] \
							+ self._point_dir[1] * dir_to_player[1]
				# Dot product must be above a threshold to shoot
				if dot_product >= self._min_shoot_dot_product:
					# Shoot at the player
					shot_start_distance = self.getRadius() + 2
					turret_centre = self.getCentre()
					BulletEntity((turret_centre[0] + dir_to_player[0] * shot_start_distance,
								turret_centre[1] + dir_to_player[1] * shot_start_distance),
								(dir_to_player[0] * misc.turret_shot_speed,
								dir_to_player[1] * misc.turret_shot_speed),
								shot_by_player=False, shot_by_name=self.name)
					Entity.playRandomSound(TurretEntity._shoot_sounds)
					self._shot_cooldown = self._shoot_interval
		
	def render(self, screen):
		# Don't render the inside turrets unless the asteroid is in its hollow state
		if not self._outside and not asteroid._is_hollow:
			return
		super(TurretEntity, self).render(screen)

#-------------------------------------------------------------------------------
class BulletEntity(Entity):
	_count = 0
	#-------------------------------------------------------------------------------
	def __init__(self, pos, vel, shot_by_player=True, shot_by_name=''):
		BulletEntity._count += 1
		if shot_by_player:
			name = 'player_'
		else:
			name = shot_by_name
			if shot_by_name != '':
				name += '_'
		name += 'bullet%d' % BulletEntity._count
		super(BulletEntity, self).__init__(pos, None, name)
		
		vel = [float(vel[0]), float(vel[1])]
		self._fvel = vel
		self._shot_by_player = shot_by_player
		# Set up the rect to be the bounding box of the bullet line.
		# It will be drawn either top-left to bottom-right, or bottom-left to top-right.
		self._bl_to_tr = (vel[0] <= 0.0 and vel[1] > 0.0) or (vel[0] > 0.0 and vel[1] <= 0.0)
		shot_length = 8 if shot_by_player else 4
		vel_length = math.sqrt(vel[0] * vel[0] + vel[1] * vel[1])
		shot_offset = (shot_length * vel[0] / vel_length,
						shot_length * vel[1] / vel_length)
		other_corner = (pos[0] + shot_offset[0],
						pos[1] + shot_offset[1])
		self.setRect(min(pos[0], other_corner[0]), min(pos[1], other_corner[1]),
					 abs(shot_offset[0]), abs(shot_offset[1]))
		
	#-------------------------------------------------------------------------------
	def update(self):
		super(BulletEntity, self).update()
		# Standard easy "remove bullets when off screen" system for now
		if not self._rect.colliderect(_screen_rect):
			self.alive = False
	
	#-------------------------------------------------------------------------------
	def render(self, screen):
		col = (255, 220, 0) if self._shot_by_player else (255, 40, 0)	# yellowish / reddish
		start_pos = (self._rect.left, self._rect.bottom if self._bl_to_tr else self._rect.top)
		end_pos = (self._rect.right, self._rect.top if self._bl_to_tr else self._rect.bottom)
		pygame.draw.line(screen, col, start_pos, end_pos)

#-------------------------------------------------------------------------------
class SpacemanEntity(Entity):
	_count = 0
	_rescue_sound = Entity.getSound('data/sfx/Pickup_Coin20')
	
	#-------------------------------------------------------------------------------
	def __init__(self, asteroid, angle_deg):
		SpacemanEntity._count += 1
		angle_rad = angle_deg * DEG_TO_RAD
		point_dir = (math.cos(angle_rad), -math.sin(angle_rad))
		radius = asteroid.getInnerRadius()
		radius -= 10	# fudge factor again
		pos = list(asteroid.getCentre())
		pos[0] += radius * point_dir[0]
		pos[1] += radius * point_dir[1]
		super(SpacemanEntity, self).__init__(pos, 'data/spaceman',
			'spaceman%d' % SpacemanEntity._count)
		
		# Match the spaceman's orientation to their angle from the asteroid centre
		self._angle_deg = angle_deg - 90	# base image is straight up, so rotate 90 degrees CW
		self._angle_deg += 180				# put on the inside of the asteroid
		self.vulnerable = True
		
	def rescue(self):
		misc.rescued += 1
		misc.score += RESCUE_SCORE
		SpacemanEntity._rescue_sound.play()
		self.alive = False
		
	def render(self, screen):
		if not asteroid._is_hollow:
			return
		super(SpacemanEntity, self).render(screen)

#-------------------------------------------------------------------------------
class PlayerEntity(Entity):
	_instance = None
	#-------------------------------------------------------------------------------
	def __init__(self, pos):
		assert(PlayerEntity._instance is None)
		PlayerEntity._instance = self
		super(PlayerEntity, self).__init__(pos, 'data/player-ship', 'player')
		self._accel_multiplier = 8.0
		self._angle_deg = 0.0
		self.vulnerable = True
		self._shoot_sound = Entity.getSound('data/sfx/Player_Shoot')
		self._explosion_sound = Entity.getSound('data/sfx/Big_Explosion')
		self._thruster_sound = Entity.getSound('data/sfx/Thruster')
		self._thruster_sound.set_volume(0.15)
		self._thruster_channel = None
		
	#-------------------------------------------------------------------------------
	def accelerate(self, amount):
		if not self.alive:
			return
		self._fvel[0] += amount[0] * self._accel_multiplier
		self._fvel[1] += amount[1] * self._accel_multiplier
		if amount[1] == 0.0:
			self._angle_deg = 0 if amount[0] > 0.0 else 180
		else:
			self._angle_deg = math.atan2(-amount[1], amount[0]) * RAD_TO_DEG
		# Assume this was the player's thruster input (may need to change this later)
		if self._thruster_channel is None or not self._thruster_channel.get_busy():
			self._thruster_channel = self._thruster_sound.play()
		
	#-------------------------------------------------------------------------------
	def reset(self):
		global _screen_rect
		self._fpos = list(PLAYER_INITIAL_POS)
		self._fvel[:] = [0.0, 0.0]
		if not self.alive:
			self.alive = True
			mgr.add(self)
		
	#-------------------------------------------------------------------------------
	def shoot(self):
		if not self.alive:
			return
		# Start the shot away from the player ship in the angle it's facing
		x, y = self.getCentre()
		radius = self.getRadius()
		angle_rad = self._angle_deg * DEG_TO_RAD
		dx = math.cos(angle_rad)
		dy = -math.sin(angle_rad)
		BulletEntity((x + dx * radius, y + dy * radius),
					 (dx * misc.player_shot_speed, dy * misc.player_shot_speed),
					 shot_by_player=True)
		self._shoot_sound.play()
		
	#-------------------------------------------------------------------------------
	def destroy(self):
		super(PlayerEntity, self).destroy()
		misc.score -= DEATH_SCORE_PENALTY
		misc.deaths += 1
		self._explosion_sound.play()
		
#-------------------------------------------------------------------------------
def init(screen, screen_rect):
	global _screen, _screen_rect
	_screen = screen
	_screen_rect = screen_rect

#-------------------------------------------------------------------------------

mgr = EntityManager()

asteroid = None
player = None
