from instagram_filters.filter import Filter
from instagram_filters.decorations import Frame
from instagram_filters.decorations import Border

import os, inspect

class Fifties(Filter, Frame, Border):
	
	def apply(self):
		self.frame("Kodachrome.png")

