# -*- coding: utf-8 -*-
import random
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from django.utils.safestring import mark_safe 

from fields import District, Classification, StatusProperty, AditionalThings, PositionOfSun
from real_estate_app.apps.propertys.manager import PropertyManager
from real_estate_app.apps.propertys.utils import make_dv
from real_estate_app.apps.realtors.models import Realtor
from real_estate_app.conf.settings import REAL_ESTATE_PROPERTY_UNKNOW_IMG
from real_estate_app.models import RealEstateAppBaseModel

# TODO: better import STATE_CHOICE based on LANGUAGE_CODE
from django.contrib.localflavor.br.br_states import STATE_CHOICES

LANGUAGE_CODE=getattr(settings,'LANGUAGE_CODE')
GMAP_DEFAULT=getattr(settings,'GMAP_DEFAULT',('-15.793905','-47.882395'))

class Property(RealEstateAppBaseModel):

	code_property=models.CharField(
							_('code property'),
							max_length=8,
							help_text=_('Automatically built from utils.')
	)

	address=models.CharField(
							_('address'),
							max_length=255,
							help_text=_('Entry with address of property')
	)

	slug = models.SlugField(
        _('slug'),
        unique=True,
        help_text=_('Automatically built from the caption. A slug is a short '
                    'label generally used in URLs.'),
    )


	zip_code=models.CharField(
							_('ZIP'),
							max_length=9,
							help_text=_('Entry with ZIP of property')
	)

	price=models.DecimalField(
							_('price'),
							max_digits=12, 
							decimal_places=2,
							help_text=_('Entry with price of property'),
	)

	district_fk = models.ForeignKey(
							District,
							limit_choices_to ={'logical_exclude':False},
							blank=True,
							null=True,
							help_text=_('Entry with district of property'),
							verbose_name=_("District")
	)

	if LANGUAGE_CODE=='pt-br':

		condominio = models.DecimalField(
							u'Condomínio',
							max_digits=12,
							decimal_places=2,
							blank=True,
							null=True,
							help_text=_('Entry with condominium of property')

		)

		iptu = models.DecimalField(
							u'IPTU',
							max_digits=12,
							decimal_places=2,
							blank=True,
							null=True,
							help_text=_('Entry with IPUT of property')
		)
	
	classification_fk = models.ForeignKey(
							Classification,
							limit_choices_to ={'logical_exclude':False},
							help_text=_('Entry with classification of property'),
							verbose_name=_("Classification")
	)
	statusproperty_fk = models.ForeignKey(
							StatusProperty,
							limit_choices_to ={'logical_exclude':False},
							help_text=_('Entry with type of property'),
							verbose_name=_("Status")
	)

	state = models.CharField(
					_('State'),
					choices=STATE_CHOICES,
					max_length=2,
					help_text=_('State of that belongs to district'),
					default='DF',
	)

	aditionalthings_fk = models.ManyToManyField(
							AditionalThings,
							limit_choices_to ={'logical_exclude':False},
							help_text=_('Entry with aditional things of property')
	)

	rooms=models.IntegerField(
							_('Rooms'),
							blank=True,
							null=True,
							help_text=_('Entry with numbers of room of property')
	)
	baths=models.IntegerField(
							_('Baths'),
							blank=True,
							null=True,
							help_text=_('Entry with numbers of bath of property')
	)


	garage=models.IntegerField(
							_('Garage'),
							blank=True,
							null=True,
							help_text=_('Entry with numbers of garage of property')
	)

	elevator=models.IntegerField(
							_('Elevator'),
							blank=True,
							null=True,
							help_text=_('Entry with numbers of elevator of property')
	)

	furnishing=models.BooleanField(
							_('Furnishing'),
							help_text=_('Entry with this property is furnishing'),
							default=False
	)

	featured=models.BooleanField(
							_('Featured'),
							help_text=_('Entry with this property is published in featured images'),
							default=False
	)
	
	under_contruction=models.BooleanField(
							_('Under construction'),
							help_text=_('Entry with this property is under construction.'),
							default=False,
	)

	private_area = models.DecimalField(
							_('Private area'),
							max_digits=12, 
							decimal_places=2,
							blank=True,
							null=True,
							help_text=_('Set value in m²'),
	)

	position_of_sun = models.ForeignKey(
						PositionOfSun,
						limit_choices_to={'logical_exclude':False},
						blank=True,
						null=True,
						verbose_name=_("Position of sun")
	)
	
	description = models.TextField(
							_('Description'),
							blank=True,
							null=True,
							help_text=_('Entry with description of property')
	)

	domain = models.ManyToManyField(
					        Site,
							default=[settings.SITE_ID],
					        verbose_name=_('publish on'),
							help_text=_('Entry with a site')
	)
	
	gmap_point_x = models.CharField(
							max_length=255,
							default=GMAP_DEFAULT[0],
							blank=True,
							null=True
	)

	gmap_point_y = models.CharField(
							max_length=255,
							default=GMAP_DEFAULT[1],
							blank=True,
							null=True
	)

	realtor_fk = models.ManyToManyField(
						Realtor,
						limit_choices_to={'logical_exclude':False},
						blank=True,
						null=True,
						help_text=_('Entry the name of realtor. ex.: Jonh'),
						verbose_name=_("Realtors")
	)

	pub_date = models.DateField(
				_('Date init'),
				default=datetime.now()
	)

	pub_date_end = models.DateField(
				_('Date end'),
				null=True,
				blank=True,
	)

	def __unicode__(self):
		return self.address

	objects = PropertyManager()

	class Meta:
		app_label = 'propertys'
		db_table  = 'real_estate_app_apps_propertys_property'
		get_latest_by='address'
		ordering=('address',)
		verbose_name=_('Propety')
		verbose_name_plural=_('Propetys')

	def agenda(self):
		agenda_url = reverse('admin:admin_visitcalendar_list_property_visit',args=(self.slug,))
		return u'<a href="%s"><img src="%s" alt="%s"/></a>' % (agenda_url,settings.ADMIN_MEDIA_PREFIX+'img/admin/icon_calendar.gif',_('Agenda'))
	agenda.short_description=_('Agenda')
	agenda.allow_tags=True

	def get_random_photo(self):
		queryset = self.photo_set.all().filter(enable_publish=True)
		if queryset:
			return queryset.order_by('?')[0]
		return REAL_ESTATE_PROPERTY_UNKNOW_IMG
	get_random_photo.short_description=_('Photo')
	get_random_photo.allow_tags=True


	def _get_all_photos(self):
		photos =self.photo_set.all().filter(enable_publish=True)
		if photos:
			return photos.order_by('?')

		return None
	
	photos=property(_get_all_photos)

	def _get_absolute_url(self):
		return ('property-detail',None, {
				'slug' : str(self.slug),
				})
	get_absolute_url=permalink(_get_absolute_url)
	
	def _state(self):
		state=dict(STATE_CHOICES)
		return state.get(self.state) or ''

	state_name=property(_state)

	def _gmap(self):
		return  (str(self.gmap_point_x) != GMAP_DEFAULT[0] or str(self.gmap_point_y) != GMAP_DEFAULT[1]) \
		 		or (str(self.gmap_point_x) != GMAP_DEFAULT[0] and str(self.gmap_point_y) != GMAP_DEFAULT[1])
	gmap=property(_gmap)

	def admin_link(self):
		if self.pk:
			return mark_safe(u'<a target="_blank" href="%s/%s/%s/">%s</a>' % (self._meta.app_label, self._meta.object_name.lower(), self.pk, self))
		else:
			return mark_safe(u'')
	
	def save(self,*args,**kwargs):
		if not self.code_property:
			code_property=make_dv(''.join(random.sample('0123456789',6)),max_num=8)
			if Property.objects.filter(code_property=code_property):
				code_property=make_dv(''.join(random.sample('0123456789',6)),max_num=8)
			self.code_property=code_property
		super(Property,self).save(*args,**kwargs)

	def clone(self):
		from django.core.files.base import ContentFile
		from django.template.defaultfilters import slugify

		from real_estate_app.apps.photos.models import Photo

		new_kwargs = dict([(fld.name, getattr(self, fld.name)) for fld in self._meta.fields if fld.name not in ('id','code_property') ]);

		slug_max=self._meta.get_field_by_name('slug')[0].max_length-5
		if (len(new_kwargs['slug']) < slug_max):
			new_kwargs['slug']+='-copy'
		else:
			new_kwargs['slug']=new_kwargs['slug'][:slug_max]+'-copy'

		obj=self.__class__.objects.create(**new_kwargs)
		
		[obj.aditionalthings_fk.add(_aditional) for _aditional in self.aditionalthings_fk.all()]
		[obj.domain.add(_domain) for _domain in self.domain.all()]
		[obj.realtor_fk.add(_realtor) for _realtor in self.realtor_fk.all()]
		
		if self.photos:
			for _photo in self.photos:
				file_name='copy-'+_photo.photo.name.split('/')[-1:][0]
				p=Photo(
						album_property=obj,
						description=_photo.description,
						slug=slugify(_photo.slug+'-copy'),
						image_destaque=_photo.image_destaque,
						enable_publish=_photo.enable_publish,
						pub_date=_photo.pub_date,
						width=_photo.width,
						height=_photo.height,
				)
				p.photo.save(file_name,ContentFile(_photo.photo.file.read()))
				p.save()
		return obj
