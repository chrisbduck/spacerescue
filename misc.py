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
import sys

CENTRE = -1			# constant for text centring

IN_GAME_MUSIC = 0
MENU_MUSIC = 1

# turrets, spacemen, and turret shot speed for each level
LEVEL_DATA = [
	[7, 7, 1.0],
	[10, 10, 1.5],
	[12, 12, 2.0],
	[14, 14, 3.0],
	[20, 20, 4.5],
	[20, 20, 7.0],
	[20, 20, 10.0]
]

num_turrets = None
num_spacemen = None
turret_shot_speed = None
player_shot_speed = 10.0

score = 0
deaths = 0
rescued = 0
level = 0
_default_font = None
_screen = None
_screen_rect = None
debug = "--debug" in sys.argv

#-------------------------------------------------------------------------------
def init(screen, screen_rect):
	global _default_font, _screen, _screen_rect
	_screen = screen
	_screen_rect = screen_rect
	_default_font = getFont(16)

#-------------------------------------------------------------------------------
if debug:
	def debugMsg(text):
		print text
else:
	debugMsg = lambda text: None

#-------------------------------------------------------------------------------
def setLevel(new_level):
	"Sets the game level (0-based)."
	global level, num_turrets, num_spacemen, turret_shot_speed
	debugMsg('Starting level %d' % new_level)
	level = new_level		# ignore clamping for the display
	level_data = LEVEL_DATA[max(0, min(new_level, len(LEVEL_DATA) - 1))]	# clamp
	num_turrets = level_data[0]
	num_spacemen = level_data[1]
	turret_shot_speed = level_data[2]

#-------------------------------------------------------------------------------
def getFont(pixel_size):
	# Select a font
	if 'ubuntu' in pygame.font.get_fonts():
		try:
			return pygame.font.SysFont('ubuntu', pixel_size, bold=True)
		except IOError:
			pass
	try:
		return pygame.font.Font(pygame.font.get_default_font(), pixel_size, bold=True)
	except IOError:
		pass
	return pygame.font.Font(None, pixel_size, bold=True)

#-------------------------------------------------------------------------------
def renderText(text, pos, col, font=None):
	if font is None:
		font = _default_font
	text_surface = font.render(text, True, col)
	rect = text_surface.get_rect()
	if pos[0] == CENTRE:
		rect.left += (_screen_rect.width - rect.width) / 2
	elif pos[0] < 0:
		rect.right = _screen_rect.width + pos[0]	# right justify
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
def reset():
	global score, deaths, rescued
	score = 0
	deaths = 0
	rescued = 0
	setLevel(0)

#-------------------------------------------------------------------------------
