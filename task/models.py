from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.validators import FileExtensionValidator

class Order(models.Model):
	# customer info
	customer_name = models.CharField(max_length = 100)
	customer_email = models.CharField(default = 'hello@iitg.ac.in', max_length = 100)
	otp = models.IntegerField(default = -1)

	# shopkeeper info
	shopkeeper_email = models.EmailField(default='shopkeeper@iitg.ac.in')
	shopkeeper_location = models.CharField(max_length=100,default='library')

	# doc info(files, pages to be printed, black/white or colour, etc)
	docfile = models.FileField(default = 'blank.pdf', upload_to = '')
	no_of_copies = models.IntegerField(default = 1)
	black_and_white = models.BooleanField(default = True, blank = True)
	
	# order details
	cost = models.IntegerField(default = 1)
	date_ordered = models.DateTimeField(default = timezone.now)
	printing_status = models.BooleanField(default = False)
	collected_status = models.BooleanField(default = False)

	#payment details
	payment_id = models.CharField(default = '0000000000', max_length=100)
	payment_status = models.BooleanField(default = False)

	def __str__(self):
			return self.customer_name

