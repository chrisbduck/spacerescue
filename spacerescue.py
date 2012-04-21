#!/usr/bin/python
#-------------------------------------------------------------------------------
# Space Rescue game.
# 
# Feel free to do what you like with this code, application, and data...
# except sell it :)
# 
# - Chris Bevan 21-22 April, 2012
#-------------------------------------------------------------------------------

import os
import pygame
import random
import sys

BG_COLOUR = (0, 0, 0)
MAX_FPS = 60

#-------------------------------------------------------------------------------

# Override buffer size to 2k for better responsiveness on sounds
pygame.mixer.pre_init(22050, -16, 2, 2048)

pygame.init()

#-------------------------------------------------------------------------------
class App(object):
	def __init__(self):
		self._screen_rect = pygame.Rect(0, 0, 640, 480)
		self._screen = pygame.display.set_mode(self._screen_rect.size)
		self._clock = pygame.time.Clock()
		self._paused = False
		
	def run(self):
		while True:
			if not self.update():
				break
			if self._paused:
				continue
			
			self._screen.fill(BG_COLOUR)
			pygame.display.flip()
		
	def update(self):
		"Returns False iff exited."
		self._clock.tick(MAX_FPS)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
		
		return True

#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------

App().run()
