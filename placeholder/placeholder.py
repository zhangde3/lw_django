import sys
import os

from django.conf import settings

DEBUG = os.environ.get('DEBUG','on') == 'on'

SECRET_KEY=os.environ.get('SECRET_KEY','uoj(at1xi_v#5y&-1^9amng&)aw@hle$h3p7(gqmcnk4e%(%yc')

ALLOWED_HOSTS=os.environ.get('ALLOWED_HOSTS','localhost').split(',')

settings.configure(
	DEBUG=DEBUG,
	SECRET_KEY=SECRET_KEY,
	ALLOWED_HOSTS = ALLOWED_HOSTS,
	ROOT_URLCONF=__name__,
	MIDDLEWARE_CLASSES=(
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware',
	),
)


from django import forms
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from io import BytesIO
from PIL import Image,ImageDraw
from django.core.cache import cache

application = get_wsgi_application()

class ImageForm(forms.Form):
	"""Form to validate requestd placeholder images."""

	height = forms.IntegerField(min_value=1,max_value=2000)
	width = forms.IntegerField(min_value=1,max_value=2000)
	def generate(self,image_format='PNG'):
		"""Generate an  image of the given type and return as raw bytes."""
		height = self.cleaned_data['height']
		width = self.cleaned_data['width']
		key = '{}.{}.{}'.format(width,height,image_format)
		content = cache.get(key)
		if content is None:
			image = Image.new('RGB',(width,height))
			draw = ImageDraw.Draw(image)
			text = '{} X {}'.format(width,height)
			textwidth, textheight = draw.textsize(text)
			if textwidth < width and textheight < height:
				texttop = (height - textheight) // 2
				textleft = (width - textwidth) //2
				draw.text((textleft, texttop),text,fill=(255,255,255))
			content = BytesIO()
			image.save(content,image_format)
			content.seek(0)
			cache.set(key,content, 60*60)
		return content

def placeholder(request,width, height):
	form = ImageForm({'height':height,'width':width})
	if form.is_valid():
		image = form.generate()
		return HttpResponse(image,content_type='image/png')
	else:
		return HttpResponseBadRequest('Invalid Image Request')
	

def index(request):
	return HttpResponse('Hello World')


urlpatterns = (
	url(r'^image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$',placeholder,name='placeholder'),
	url(r'^$',index),
)

if __name__ == '__main__':
	from django.core.management import execute_from_command_line
	
	execute_from_command_line(sys.argv)
