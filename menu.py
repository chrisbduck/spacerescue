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
import pygame
import time

#-------------------------------------------------------------------------------

class Menu(object):
	def __init__(self, screen, screen_rect):
		self._screen = screen
		self._screen_rect = screen_rect
		self._bg = pygame.image.load('data/menu-bg.png')
		self._bg_rect = self._bg.get_rect()
		self._accepted = False
		self._next_frame_tick = 0
		
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
				if event.key == pygame.K_ESCAPE:
					return False
				if event.key == pygame.K_RETURN:
					self._accepted = True
		
		return True

	def render(self):
		self._screen.blit(self._bg, self._bg_rect)
		pygame.display.flip()
		
	def run(self):
		"Returns False iff quit."
		while True:
			if not self.updateEvents():
				return False
			if self._accepted:
				return True
			self.render()
			
#-------------------------------------------------------------------------------
