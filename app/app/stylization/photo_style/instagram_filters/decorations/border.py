from instagram_filters.filter import Filter

class Border(Filter):
	
	def border(self, color = 'black', width = 20, height = 20):
		self.execute("convert {filename} -bordercolor {color} -border {bwidth}x{bheight} {filename}",
			color = color,
			bwidth = width,
                        bheight = height
		)