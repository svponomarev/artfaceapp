from instagram_filters.filter import Filter
"""filter is based on http://www.fmwconcepts.com/imagemagick/davehilleffect/index.php"""
brightness = 1
contrast = 0
gain = 40
grayval="gray" + str(gain)
class Davehill(Filter):
	
	def apply(self):
		self.execute("convert {filename} -evaluate multiply " + str(brightness) + " +sigmoidal-contrast " + str(contrast) + "x50% \
\( -clone 0 -bias 50% -define convolve:scale=1 -morphology Convolve DoG:0,0,4 -clamp \) \
-compose vividlight -composite -clamp \
\( -clone 0 -bias 50% -define convolve:scale=1 -morphology Convolve DoG:0,0,6.9 -clamp \) \
\( -clone 0 -fill " + grayval + " -colorize 100 \) \
-compose colorize -composite {filename}");


