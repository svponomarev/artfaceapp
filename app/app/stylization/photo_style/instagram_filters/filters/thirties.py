from instagram_filters.filter import Filter
from instagram_filters.decorations import Frame

class Thirties(Filter, Frame):
	
	def apply(self):
		self.frame('Oldfilm.png');
