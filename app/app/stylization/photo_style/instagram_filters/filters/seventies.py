from instagram_filters.filter import Filter
from instagram_filters.decorations import Border

class Seventies(Filter, Border):
	
	def apply(self):
		self.border('white');
