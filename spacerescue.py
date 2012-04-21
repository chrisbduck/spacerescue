#!/usr/bin/python
#-------------------------------------------------------------------------------
# Space Rescue game - main file.
# 
# Feel free to do what you like with this code, application, and data...
# except sell it :)
# 
# - Chris Bevan, 21-22 April, 2012
#-------------------------------------------------------------------------------

import math
import os
import pygame
import random
import sys
import time

BG_COLOUR = (0, 0, 0)
MAX_FPS = 60

#-------------------------------------------------------------------------------

# Override buffer size to 2k for better responsiveness on sounds
pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.init()

import entity

#-------------------------------------------------------------------------------
class App(object):
	
	CENTRE = -1			# constant for text centring
	
	UP_LEFT =		(-1, -1)
	UP = 			( 0, -1)
	UP_RIGHT =		( 1, -1)
	LEFT =			(-1,  0)
	RIGHT =			( 1,  0)
	DOWN_LEFT =		(-1,  1)
	DOWN =			( 0,  1)
	DOWN_RIGHT =	( 1,  1)
	ACCEL_DIRS = {
		pygame.K_RIGHT:			RIGHT,
		pygame.K_LEFT:			LEFT,
		pygame.K_UP:			UP,
		pygame.K_DOWN:			DOWN,
		pygame.K_KP7:			UP_LEFT,
		pygame.K_KP8:			UP,
		pygame.K_KP9:			UP_RIGHT,
		pygame.K_KP4:			LEFT,
		pygame.K_KP6:			RIGHT,
		pygame.K_KP1:			DOWN_LEFT,
		pygame.K_KP2:			DOWN,
		pygame.K_KP3:			DOWN_RIGHT,
		pygame.K_w:				UP_LEFT,
		pygame.K_e:				UP,
		pygame.K_r:				UP_RIGHT,
		pygame.K_s:				LEFT,
		pygame.K_f:				RIGHT,
		pygame.K_x:				DOWN_LEFT,
		pygame.K_c:				DOWN,
		pygame.K_v:				DOWN_RIGHT,
	}
	
	#-------------------------------------------------------------------------------
	def __init__(self):
		self._screen_rect = pygame.Rect(0, 0, 800, 600)
		self._screen = pygame.display.set_mode(self._screen_rect.size,
												pygame.DOUBLEBUF | pygame.HWSURFACE)
		self._next_frame_tick = 0
		self._paused = False
		self._font = pygame.font.Font(pygame.font.get_default_font(), 16)
		self._keys_down = set()
		entity.init(self._screen, self._screen_rect, self.renderText)
		
	#-------------------------------------------------------------------------------
	def run(self):
		while True:
			if not self.updateEvents():
				break
			if not self._paused:
				self.processPlayerInput()
				entity.mgr.update()
			self.render()
		
	#-------------------------------------------------------------------------------
	def updateEvents(self):
		"Returns False iff exited."
		# Wait for next frame time
		if self._next_frame_tick <= 0:
			self._next_frame_tick = time.time()
		else:
			time_to_next_frame_sec = self._next_frame_tick - time.time()
			if time_to_next_frame_sec > 0:
				time.sleep(time_to_next_frame_sec)
		self._next_frame_tick += 1.0 / MAX_FPS
		
		# Check events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key in App.ACCEL_DIRS:
					self._keys_down.add(event.key)
				elif event.key == pygame.K_ESCAPE:
					return False
				elif event.key == pygame.K_SPACE:
					self._paused = not self._paused
				elif event.key == pygame.K_HASH:
					entity.player.reset()
			elif event.type == pygame.KEYUP:
				if event.key in App.ACCEL_DIRS:
					# This key should be in the keys down set, but there might be a key event error`
					if event.key in self._keys_down:
						self._keys_down.remove(event.key)
		
		return True
		
	#-------------------------------------------------------------------------------
	def processPlayerInput(self):
		# Sum all of the keys held down and normalise the result to get an acceleration direction
		if not self._keys_down:
			return
		x_sum, y_sum = 0, 0
		for key in self._keys_down:
			kdir = App.ACCEL_DIRS[key]
			x_sum += kdir[0]
			y_sum += kdir[1]
		# Ignore if zero sum
		if x_sum == 0 and y_sum == 0:
			return
		# Normalise and accelerate the player.
		# We divide by the max FPS to get some frame rate independency.  The formula won't be exactly
		# right, but I don't think it matters for now
		length = math.sqrt(x_sum * x_sum + y_sum * y_sum)		# -> float
		length *= MAX_FPS		# effectively divide by FPS
		entity.player.accelerate((x_sum / length, y_sum / length))
		
	#-------------------------------------------------------------------------------
	def render(self):
		self._screen.fill(BG_COLOUR)
		entity.mgr.render(self._screen)
		self.renderAllText()
		pygame.display.flip()
		
	#-------------------------------------------------------------------------------
	def renderAllText(self):
		self.renderText("Paused" if self._paused else "Running",
						pos=(App.CENTRE, 5), col=(220, 220, 220))
		self.renderText("Player is at (%d, %d)" %
						(entity.player._rect.left, entity.player._rect.top),
						pos=(App.CENTRE, 25), col=(128, 128, 128))
		
	#-------------------------------------------------------------------------------
	def renderText(self, text, pos, col):
		text_surface = self._font.render(text, True, col)
		rect = text_surface.get_rect()
		if pos[0] == App.CENTRE:
			rect.left += (self._screen_rect.width - rect.width) / 2
		else:
			rect.left += pos[0]
		if pos[1] == App.CENTRE:
			rect.top += (self._screen_rect.height - rect.height) / 2
		else:
			rect.top += pos[1]
		self._screen.blit(text_surface, rect)

#-------------------------------------------------------------------------------

App().run()
