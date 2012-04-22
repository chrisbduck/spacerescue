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
import misc
import pygame
import time

SELECTED_COL = (8, 8, 64)
UNSELECTED_COL = (8, 8, 8)
CREDITS_COL = (220, 180, 60)

credit_text = """
Many thanks go to:
- All the Ludum Dare organisers
- GreaseMonkey, for the music generator!
- increpare, for Bfxr! (and others for
  sfxr and co)
- vilya, for convincing me to give this
  competition a go :)
""".split('\n')

#-------------------------------------------------------------------------------

class Menu(object):
	def __init__(self, screen, screen_rect):
		self._screen = screen
		self._screen_rect = screen_rect
		self._bg = pygame.image.load('data/menu-bg.png')
		self._bg_rect = self._bg.get_rect()
		self._next_frame_tick = 0
		self._big_font = misc.getFont(64)
		self._mid_font = misc.getFont(32)
		self._options = ['Start Game', 'Credits', 'Quit']
		self._START_INDEX = 0
		self._CREDITS_INDEX = 1
		self._QUIT_INDEX = 2
		self._selected_index = self._START_INDEX
		self._option_count = len(self._options)
		self._show_credits = False
		
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
				if self._show_credits:
					if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
						self._show_credits = False
				else:
					if event.key == pygame.K_ESCAPE:
						return False
					if event.key == pygame.K_RETURN:
						if self._selected_index == self._START_INDEX:
							self._accepted = True
						elif self._selected_index == self._CREDITS_INDEX:
							self._show_credits = True
						else:	# _QUIT_INDEX
							return False
					elif event.key == pygame.K_KP8 or event.key == pygame.K_UP:
						if self._selected_index == 0:
							self._selected_index = self._option_count
						self._selected_index -= 1
					elif event.key == pygame.K_KP2 or event.key == pygame.K_DOWN:
						self._selected_index += 1
						if self._selected_index >= self._option_count:
							self._selected_index = 0
		
		return True

	def renderSelectableText(self, text, pos, is_selected):
		if is_selected:
			text = "-> " + text + " <-"
		col = SELECTED_COL if is_selected else UNSELECTED_COL
		misc.renderText(text, pos, col, self._mid_font)
		
	def renderMenuOptions(self):
		y = 300
		for opt_index in range(self._option_count):
			self.renderSelectableText(self._options[opt_index], (misc.CENTRE, y),
										opt_index == self._selected_index)
			y += 40
	
	def renderCredits(self):
		y = self._screen_rect.centery
		total_lines = len(credit_text)
		spacing = 40
		y -= (total_lines - 2) * spacing / 2
		for line in credit_text:
			if line.strip() != "":
				misc.renderText(line, (50, y), CREDITS_COL, self._mid_font)
				y += spacing
	
	def render(self):
		self._screen.blit(self._bg, self._bg_rect)
		if self._show_credits:
			misc.renderText('CREDITS', (misc.CENTRE, 70), (255, 255, 255), self._big_font)
			self.renderCredits()
			self.renderSelectableText('Back', (misc.CENTRE, 500), self._mid_font)
		else:
			misc.renderText('SPACE RESCUE!', (misc.CENTRE, 100), (255, 235, 50), self._big_font)
			self.renderMenuOptions()
		pygame.display.flip()
		
	def run(self):
		"Returns False iff quit."
		self._accepted = False
		misc.startMusic(misc.MENU_MUSIC)
		
		while True:
			if not self.updateEvents():
				return False
			if self._accepted:
				return True
			self.render()
			
#-------------------------------------------------------------------------------
