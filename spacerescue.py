#!/usr/bin/python
#-------------------------------------------------------------------------------
# Space Rescue game - main file.
# 
# Feel free to do what you like with this code, application, and data...
# except sell it :)
# 
# - Chris Bevan, 21-22 April, 2012
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

from entity import entities

#-------------------------------------------------------------------------------
class App(object):
	
	CENTRE = -1			# constant for text centring
	
	def __init__(self):
		self._screen_rect = pygame.Rect(0, 0, 640, 480)
		self._screen = pygame.display.set_mode(self._screen_rect.size)
		self._clock = pygame.time.Clock()
		self._paused = False
		self._font = pygame.font.Font(pygame.font.get_default_font(), 16)
		
	def run(self):
		while True:
			if not self.updateEvents():
				break
			if not self._paused:
				entities.update()
			self.render()
		
	def updateEvents(self):
		"Returns False iff exited."
		self._clock.tick(MAX_FPS)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				elif event.key == pygame.K_SPACE:
					self._paused = not self._paused
		
		return True
		
	def render(self):
		self._screen.fill(BG_COLOUR)
		entities.render(self._screen)
		self.renderAllText()
		pygame.display.flip()
		
	def renderAllText(self):
		self.renderText("Paused" if self._paused else "Running",
						pos=(App.CENTRE, 5), col=(220, 220, 220))
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


#-------------------------------------------------------------------------------

App().run()
