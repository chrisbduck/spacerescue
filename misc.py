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

IN_GAME_MUSIC = 0
MENU_MUSIC = 1

score = 0
_default_font = None
_screen = None
_screen_rect = None

#-------------------------------------------------------------------------------
def init(screen, screen_rect):
	global _default_font, _screen, _screen_rect
	_screen = screen
	_screen_rect = screen_rect
	_default_font = getFont(16)

#-------------------------------------------------------------------------------
def getFont(pixel_size):
	# Select a font
	if 'ubuntu' in pygame.font.get_fonts():
		try:
			return pygame.font.Font('ubuntu', pixel_size)
		except IOError:
			pass
	return pygame.font.Font(pygame.font.get_default_font(), pixel_size)

#-------------------------------------------------------------------------------
def renderText(text, pos, col, font=None):
	if font is None:
		font = _default_font
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
def startMusic(music_id):
	if music_id == MENU_MUSIC:
		file_name = 'castles-village'
	elif music_id == IN_GAME_MUSIC:
		file_name = 'body-demoscene'
	else:
		raise RuntimeError("Unrecognised music! (%s)" % music_id)
	pygame.mixer.music.load('data/music/' + file_name + '.ogg')
	pygame.mixer.music.play(-1)		# loop forever

#-------------------------------------------------------------------------------
