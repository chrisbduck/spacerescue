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

CENTRE = -1			# constant for text centring

score = 0
font = None
_screen = None
_screen_rect = None

#-------------------------------------------------------------------------------
def init(screen, screen_rect):
	global font, _screen, _screen_rect
	_screen = screen
	_screen_rect = screen_rect
	font = pygame.font.Font(pygame.font.get_default_font(), 16)

#-------------------------------------------------------------------------------
def renderText(text, pos, col):
	text_surface = font.render(text, True, col)
	rect = text_surface.get_rect()
	if pos[0] == CENTRE:
		rect.left += (_screen_rect.width - rect.width) / 2
	else:
		rect.left += pos[0]
	if pos[1] == CENTRE:
		rect.top += (_screen_rect.height - rect.height) / 2
	else:
		rect.top += pos[1]
	_screen.blit(text_surface, rect)

#-------------------------------------------------------------------------------
def startMusic():
	pygame.mixer.music.load('data/music/body-demoscene.ogg')
	pygame.mixer.music.play(-1)		# loop forever

#-------------------------------------------------------------------------------
