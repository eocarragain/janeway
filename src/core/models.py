__copyright__ = "Copyright 2017 Birkbeck, University of London"
__author__ = "Martin Paul Eve & Andy Byers"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck Centre for Technology and Publishing"
import os
import uuid
import statistics
import json
from datetime import timedelta
from bs4 import BeautifulSoup
from hvad.models import TranslatableModel, TranslatedFields

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from core import files
from review import models as review_models
from copyediting import models as copyediting_models
from submission import models as submission_models

fs = FileSystemStorage(location=settings.MEDIA_ROOT)


def profile_images_upload_path(instance, filename):
    try:
        filename = str(uuid.uuid4()) + '.' + str(filename.split('.')[1])
    except IndexError:
        filename = str(uuid.uuid4())

    path = "profile_images/"
    return os.path.join(path, filename)


SALUTATION_CHOICES = (
    ('Miss', 'Miss'),
    ('Ms', 'Ms'),
    ('Mrs', 'Mrs'),
    ('Mr', 'Mr'),
    ('Dr', 'Dr'),
    ('Prof.', 'Prof.'),
)

COUNTRY_CHOICES = [(u'AF', u'Afghanistan'), (u'AX', u'\xc5land Islands'), (u'AL', u'Albania'),
                   (u'DZ', u'Algeria'), (u'AS', u'American Samoa'), (u'AD', u'Andorra'), (u'AO', u'Angola'),
                   (u'AI', u'Anguilla'), (u'AQ', u'Antarctica'), (u'AG', u'Antigua and Barbuda'), (u'AR', u'Argentina'),
                   (u'AM', u'Armenia'), (u'AW', u'Aruba'), (u'AU', u'Australia'), (u'AT', u'Austria'),
                   (u'AZ', u'Azerbaijan'), (u'BS', u'Bahamas'), (u'BH', u'Bahrain'), (u'BD', u'Bangladesh'),
                   (u'BB', u'Barbados'), (u'BY', u'Belarus'), (u'BE', u'Belgium'), (u'BZ', u'Belize'),
                   (u'BJ', u'Benin'), (u'BM', u'Bermuda'), (u'BT', u'Bhutan'),
                   (u'BO', u'Bolivia, Plurinational State of'), (u'BQ', u'Bonaire, Sint Eustatius and Saba'),
                   (u'BA', u'Bosnia and Herzegovina'), (u'BW', u'Botswana'), (u'BV', u'Bouvet Island'),
                   (u'BR', u'Brazil'), (u'IO', u'British Indian Ocean Territory'), (u'BN', u'Brunei Darussalam'),
                   (u'BG', u'Bulgaria'), (u'BF', u'Burkina Faso'), (u'BI', u'Burundi'), (u'KH', u'Cambodia'),
                   (u'CM', u'Cameroon'), (u'CA', u'Canada'), (u'CV', u'Cape Verde'), (u'KY', u'Cayman Islands'),
                   (u'CF', u'Central African Republic'), (u'TD', u'Chad'), (u'CL', u'Chile'), (u'CN', u'China'),
                   (u'CX', u'Christmas Island'), (u'CC', u'Cocos (Keeling) Islands'), (u'CO', u'Colombia'),
                   (u'KM', u'Comoros'), (u'CG', u'Congo'), (u'CD', u'Congo, The Democratic Republic of the'),
                   (u'CK', u'Cook Islands'), (u'CR', u'Costa Rica'), (u'CI', u"C\xf4te d'Ivoire"), (u'HR', u'Croatia'),
                   (u'CU', u'Cuba'), (u'CW', u'Cura\xe7ao'), (u'CY', u'Cyprus'), (u'CZ', u'Czech Republic'),
                   (u'DK', u'Denmark'), (u'DJ', u'Djibouti'), (u'DM', u'Dominica'), (u'DO', u'Dominican Republic'),
                   (u'EC', u'Ecuador'), (u'EG', u'Egypt'), (u'SV', u'El Salvador'), (u'GQ', u'Equatorial Guinea'),
                   (u'ER', u'Eritrea'), (u'EE', u'Estonia'), (u'ET', u'Ethiopia'),
                   (u'FK', u'Falkland Islands (Malvinas)'), (u'FO', u'Faroe Islands'), (u'FJ', u'Fiji'),
                   (u'FI', u'Finland'), (u'FR', u'France'), (u'GF', u'French Guiana'), (u'PF', u'French Polynesia'),
                   (u'TF', u'French Southern Territories'), (u'GA', u'Gabon'), (u'GM', u'Gambia'), (u'GE', u'Georgia'),
                   (u'DE', u'Germany'), (u'GH', u'Ghana'), (u'GI', u'Gibraltar'), (u'GR', u'Greece'),
                   (u'GL', u'Greenland'), (u'GD', u'Grenada'), (u'GP', u'Guadeloupe'), (u'GU', u'Guam'),
                   (u'GT', u'Guatemala'), (u'GG', u'Guernsey'), (u'GN', u'Guinea'), (u'GW', u'Guinea-Bissau'),
                   (u'GY', u'Guyana'), (u'HT', u'Haiti'), (u'HM', u'Heard Island and McDonald Islands'),
                   (u'VA', u'Holy See (Vatican City State)'), (u'HN', u'Honduras'), (u'HK', u'Hong Kong'),
                   (u'HU', u'Hungary'), (u'IS', u'Iceland'), (u'IN', u'India'), (u'ID', u'Indonesia'),
                   (u'IR', u'Iran, Islamic Republic of'), (u'IQ', u'Iraq'), (u'IE', u'Ireland'),
                   (u'IM', u'Isle of Man'), (u'IL', u'Israel'), (u'IT', u'Italy'), (u'JM', u'Jamaica'),
                   (u'JP', u'Japan'), (u'JE', u'Jersey'), (u'JO', u'Jordan'), (u'KZ', u'Kazakhstan'), (u'KE', u'Kenya'),
                   (u'KI', u'Kiribati'), (u'KP', u"Korea, Democratic People's Republic of"),
                   (u'KR', u'Korea, Republic of'), (u'KW', u'Kuwait'), (u'KG', u'Kyrgyzstan'),
                   (u'LA', u"Lao People's Democratic Republic"), (u'LV', u'Latvia'), (u'LB', u'Lebanon'),
                   (u'LS', u'Lesotho'), (u'LR', u'Liberia'), (u'LY', u'Libya'), (u'LI', u'Liechtenstein'),
                   (u'LT', u'Lithuania'), (u'LU', u'Luxembourg'), (u'MO', u'Macao'), (u'MK', u'Macedonia, Republic of'),
                   (u'MG', u'Madagascar'), (u'MW', u'Malawi'), (u'MY', u'Malaysia'), (u'MV', u'Maldives'),
                   (u'ML', u'Mali'), (u'MT', u'Malta'), (u'MH', u'Marshall Islands'), (u'MQ', u'Martinique'),
                   (u'MR', u'Mauritania'), (u'MU', u'Mauritius'), (u'YT', u'Mayotte'), (u'MX', u'Mexico'),
                   (u'FM', u'Micronesia, Federated States of'), (u'MD', u'Moldova, Republic of'), (u'MC', u'Monaco'),
                   (u'MN', u'Mongolia'), (u'ME', u'Montenegro'), (u'MS', u'Montserrat'), (u'MA', u'Morocco'),
                   (u'MZ', u'Mozambique'), (u'MM', u'Myanmar'), (u'NA', u'Namibia'), (u'NR', u'Nauru'),
                   (u'NP', u'Nepal'), (u'NL', u'Netherlands'), (u'NC', u'New Caledonia'), (u'NZ', u'New Zealand'),
                   (u'NI', u'Nicaragua'), (u'NE', u'Niger'), (u'NG', u'Nigeria'), (u'NU', u'Niue'),
                   (u'NF', u'Norfolk Island'), (u'MP', u'Northern Mariana Islands'), (u'NO', u'Norway'),
                   (u'OM', u'Oman'), (u'PK', u'Pakistan'), (u'PW', u'Palau'), (u'PS', u'Palestine, State of'),
                   (u'PA', u'Panama'), (u'PG', u'Papua New Guinea'), (u'PY', u'Paraguay'), (u'PE', u'Peru'),
                   (u'PH', u'Philippines'), (u'PN', u'Pitcairn'), (u'PL', u'Poland'), (u'PT', u'Portugal'),
                   (u'PR', u'Puerto Rico'), (u'QA', u'Qatar'), (u'RE', u'R\xe9union'), (u'RO', u'Romania'),
                   (u'RU', u'Russian Federation'), (u'RW', u'Rwanda'), (u'BL', u'Saint Barth\xe9lemy'),
                   (u'SH', u'Saint Helena, Ascension and Tristan da Cunha'), (u'KN', u'Saint Kitts and Nevis'),
                   (u'LC', u'Saint Lucia'), (u'MF', u'Saint Martin (French part)'),
                   (u'PM', u'Saint Pierre and Miquelon'), (u'VC', u'Saint Vincent and the Grenadines'),
                   (u'WS', u'Samoa'), (u'SM', u'San Marino'), (u'ST', u'Sao Tome and Principe'),
                   (u'SA', u'Saudi Arabia'), (u'SN', u'Senegal'), (u'RS', u'Serbia'), (u'SC', u'Seychelles'),
                   (u'SL', u'Sierra Leone'), (u'SG', u'Singapore'), (u'SX', u'Sint Maarten (Dutch part)'),
                   (u'SK', u'Slovakia'), (u'SI', u'Slovenia'), (u'SB', u'Solomon Islands'), (u'SO', u'Somalia'),
                   (u'ZA', u'South Africa'), (u'GS', u'South Georgia and the South Sandwich Islands'),
                   (u'ES', u'Spain'), (u'LK', u'Sri Lanka'), (u'SD', u'Sudan'), (u'SR', u'Suriname'),
                   (u'SS', u'South Sudan'), (u'SJ', u'Svalbard and Jan Mayen'), (u'SZ', u'Swaziland'),
                   (u'SE', u'Sweden'), (u'CH', u'Switzerland'), (u'SY', u'Syrian Arab Republic'),
                   (u'TW', u'Taiwan, Province of China'), (u'TJ', u'Tajikistan'),
                   (u'TZ', u'Tanzania, United Republic of'), (u'TH', u'Thailand'), (u'TL', u'Timor-Leste'),
                   (u'TG', u'Togo'), (u'TK', u'Tokelau'), (u'TO', u'Tonga'), (u'TT', u'Trinidad and Tobago'),
                   (u'TN', u'Tunisia'), (u'TR', u'Turkey'), (u'TM', u'Turkmenistan'),
                   (u'TC', u'Turks and Caicos Islands'), (u'TV', u'Tuvalu'), (u'UG', u'Uganda'), (u'UA', u'Ukraine'),
                   (u'AE', u'United Arab Emirates'), (u'GB', u'United Kingdom'), (u'US', u'United States'),
                   (u'UM', u'United States Minor Outlying Islands'), (u'UY', u'Uruguay'), (u'UZ', u'Uzbekistan'),
                   (u'VU', u'Vanuatu'), (u'VE', u'Venezuela, Bolivarian Republic of'), (u'VN', u'Viet Nam'),
                   (u'VG', u'Virgin Islands, British'), (u'VI', u'Virgin Islands, U.S.'), (u'WF', u'Wallis and Futuna'),
                   (u'EH', u'Western Sahara'), (u'YE', u'Yemen'), (u'ZM', u'Zambia'), (u'ZW', u'Zimbabwe')]


class Country(models.Model):
    code = models.TextField(max_length=5)
    name = models.TextField(max_length=255)

    class Meta:
        ordering = ('name', 'code')
        verbose_name_plural = 'countries'

    def __str__(self):
        return self.name


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username', None):
            raise ValueError('Users must have a valid username.')

        account = self.model(
            email=self.normalize_email(email), username=kwargs.get('username')
        )

        account.set_password(password)
        account.save()

        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_staff = True
        account.is_admin = True
        account.is_active = True
        account.is_superuser = True
        account.save()

        return account


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    username = models.CharField(max_length=48, unique=True, verbose_name=_('Username'))

    first_name = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('First name'))
    middle_name = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('Middle name'))
    last_name = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('Last name'))

    activation_code = models.CharField(max_length=100, null=True, blank=True)
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, null=True, blank=True,
                                  verbose_name=_('Salutation'))
    biography = models.TextField(null=True, blank=True, verbose_name=_('Biography'))
    orcid = models.CharField(max_length=40, null=True, blank=True, verbose_name=_('ORCiD'))
    institution = models.CharField(max_length=1000, verbose_name=_('Institution'))
    department = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('Department'))
    twitter = models.CharField(max_length=300, null=True, blank=True, verbose_name="Twitter Handle")
    facebook = models.CharField(max_length=300, null=True, blank=True, verbose_name="Facebook Handle")
    linkedin = models.CharField(max_length=300, null=True, blank=True, verbose_name="Linkedin Profile")
    website = models.URLField(max_length=300, null=True, blank=True, verbose_name="Website")
    github = models.CharField(max_length=300, null=True, blank=True, verbose_name="Github Username")
    profile_image = models.ImageField(upload_to=profile_images_upload_path, null=True, blank=True, storage=fs)
    email_sent = models.DateTimeField(blank=True, null=True)
    date_confirmed = models.DateTimeField(blank=True, null=True)
    confirmation_code = models.CharField(max_length=200, blank=True, null=True)
    signature = models.TextField(null=True, blank=True)
    interest = models.ManyToManyField('Interest', null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, verbose_name=_('Country'))

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    enable_digest = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        self.username = self.email.lower()
        self.email = self.email.lower()
        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name()

    def string_id(self):
        return str(self.id)

    def get_full_name(self):
        return '{0} {1}{2}{3}'.format(self.first_name, self.middle_name, ' ' if self.middle_name != "" else "",
                                      self.last_name)

    def get_short_name(self):
        return self.first_name

    @property
    def first_names(self):
        return '{0}{1}{2}'.format(self.first_name, ' ' if self.middle_name is not None else '',
                                  self.middle_name if self.middle_name is not None else '')

    def full_name(self):
        if self.middle_name:
            return u"%s %s %s" % (self.first_name, self.middle_name, self.last_name)
        else:
            return u"%s %s" % (self.first_name, self.last_name)

    def salutation_name(self):
        if self.salutation:
            return u"%s %s" % (self.salutation, self.last_name)
        else:
            return u"%s %s" % (self.first_name, self.last_name)

    def initials(self):
        if self.first_name and self.last_name:
            if self.middle_name:
                return u"%s%s%s" % (self.first_name[:1], self.middle_name[:1], self.last_name[:1])
            else:
                return u"%s%s" % (self.first_name[:1], self.last_name[:1])
        else:
            return 'N/A'

    def affiliation(self):
        if self.department:
            return "{0}, {1}".format(self.department, self.institution)

        return self.institution

    def active_reviews(self):
        return review_models.ReviewAssignment.objects.filter(reviewer=self, is_complete=False)

    def active_copyedits(self):
        return copyediting_models.CopyeditAssignment.objects.filter(copyeditor=self, copyedit_acknowledged=False)

    def add_account_role(self, role_slug, journal):
        role = Role.objects.get(slug=role_slug)
        AccountRole.objects.get_or_create(role=role, user=self, journal=journal)

    def remove_account_role(self, role_slug, journal):
        role = Role.objects.get(slug=role_slug)
        AccountRole.objects.get(role=role, user=self, journal=journal).delete()

    def check_role(self, journal, role):
        return AccountRole.objects.filter(user=self, journal=journal, role__slug=role).count() > 0 or self.is_staff

    def is_editor(self, request, journal=None):
        if not journal:
            return self.check_role(request.journal, 'editor')
        else:
            return self.check_role(journal, 'editor')

    def is_section_editor(self, request):
        return self.check_role(request.journal, 'section-editor')

    def is_reviewer(self, request):
        return self.check_role(request.journal, 'reviewer')

    def is_author(self, request):
        return self.check_role(request.journal, 'author')

    def is_proofreader(self, request):
        return self.check_role(request.journal, 'proofreader')

    def is_production(self, request):
        return self.check_role(request.journal, 'production')

    def is_copyeditor(self, request):
        return self.check_role(request.journal, 'copyeditor')

    def is_typesetter(self, request):
        return self.check_role(request.journal, 'typesetter')

    def is_proofing_manager(self, request):
        return self.check_role(request.journal, 'proofing_manager')

    def snapshot_self(self, article):
        frozen_dict = {
            'article': article,
            'author': self,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'institution': self.institution,
            'department': self.department,
        }

        frozen_author = self.frozen_author(article)

        if frozen_author:
            for k, v in frozen_dict.items():
                setattr(frozen_author, k, v)
                frozen_author.save()
        else:
            submission_models.FrozenAuthor.objects.create(**frozen_dict)

    def frozen_author(self, article):
        try:
            return submission_models.FrozenAuthor.objects.get(article=article, author=self)
        except submission_models.FrozenAuthor.DoesNotExist:
            return None

    @property
    def average_reviewer_score(self):
        reviewer_ratings = review_models.ReviewerRating.objects.filter(assignment__reviewer=self)
        ratings = [reviewer_rating.rating for reviewer_rating in reviewer_ratings]

        return statistics.mean(ratings) if ratings else 0


def generate_expiry_date():
    return timezone.now() + timedelta(days=1)


class OrcidToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4)
    orcid = models.CharField(max_length=200)
    expiry = models.DateTimeField(default=generate_expiry_date, verbose_name='Expires on')

    def __str__(self):
        return "ORCiD Token [{0}] - {1}".format(self.orcid, self.token)


class PasswordResetToken(models.Model):
    account = models.ForeignKey(Account)
    token = models.CharField(max_length=300, default=uuid.uuid4)
    expiry = models.DateTimeField(default=generate_expiry_date, verbose_name='Expires on')
    expired = models.BooleanField(default=False)

    def __str__(self):
        return "Account: {0}, Expiry: {1}, [{2}]".format(self.account.full_name(),
                                                         self.expiry,
                                                         'Expired' if self.expired else 'Active')

    def has_expired(self):
        if self.expired:
            return True
        elif self.expiry < timezone.now():
            return True
        else:
            return False


class Role(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)

    class Meta:
        ordering = ('name', 'slug')

    def __str__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s' % self.name


class AccountRole(models.Model):
    journal = models.ForeignKey('journal.Journal')
    user = models.ForeignKey(Account)
    role = models.ForeignKey(Role)

    def __str__(self):
        return "{0} {1} {2}".format(self.user, self.journal, self.role.name)


class Interest(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s' % self.name


setting_types = (
    ('rich-text', 'Rich Text'),
    ('text', 'Text'),
    ('char', 'Characters'),
    ('number', 'Number'),
    ('boolean', 'Boolean'),
    ('file', 'File'),
    ('select', 'Select'),
    ('json', 'JSON'),
)

privacy_types = (
    ('public', 'Public'),
    ('typesetters', 'Typesetters'),
    ('proofreaders', 'Proofreaders'),
    ('copyeditors', 'Copyedtiors'),
    ('editors', 'Editors'),
    ('owner', 'Owner'),
)


class SettingGroup(models.Model):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s' % self.name


class Setting(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(SettingGroup)
    types = models.CharField(max_length=20, choices=setting_types)
    pretty_name = models.CharField(max_length=100, default='')
    description = models.TextField(null=True, blank=True)

    is_translatable = models.BooleanField(default=False)

    class Meta:
        ordering = ('group', 'name')

    def __str__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s' % self.name


class SettingValue(TranslatableModel):
    journal = models.ForeignKey('journal.Journal')
    setting = models.ForeignKey(Setting)

    translations = TranslatedFields(
        value=models.TextField(null=True, blank=True)
    )

    def __repr__(self):
        return "[{0}]: {1}, {2}".format(self.journal.code, self.setting.name, self.value)

    def __str__(self):
        return "[{0}]: {1}".format(self.journal, self.setting.name)

    @property
    def processed_value(self):
        return self.process_value()

    def process_value(self):
        """ Converts string values of settings to proper values

        :return: a value
        """

        if self.setting.types == 'boolean' and self.value == 'on':
            return True
        elif self.setting.types == 'boolean':
            return False
        elif self.setting.types == 'number':
            try:
                return int(self.value)
            except BaseException:
                return 0
        elif self.setting.types == 'json' and self.value:
            return json.loads(self.value)
        else:
            return self.value


class File(models.Model):
    article_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Article PK")

    mime_type = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=1000)
    uuid_filename = models.CharField(max_length=100)
    label = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Label'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    sequence = models.IntegerField(default=1)
    owner = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    privacy = models.CharField(max_length=20, choices=privacy_types, default="owner")

    date_uploaded = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    is_galley = models.BooleanField(default=False)

    # Remote galley handling
    is_remote = models.BooleanField(default=False)
    remote_url = models.URLField(blank=True, null=True, verbose_name="Remote URL of file")

    history = models.ManyToManyField('FileHistory')

    class Meta:
        ordering = ('sequence', 'pk')

    @property
    def article(self):
        if self.article_id:
            return submission_models.Article.objects.get(pk=self.article_id)

    def delete(self, *args, **kwargs):
        self.unlink_file()
        super(File, self).delete()

    def unlink_file(self, journal=None):
        if self.article_id:
            try:
                path = self.self_article_path()
                os.unlink(path)
            except FileNotFoundError:
                pass
        elif journal:
            try:
                path = self.journal_path(journal)
                os.unlink(path)
            except FileNotFoundError:
                pass

    def press_path(self):
        return os.path.join(settings.BASE_DIR, 'files', 'press', str(self.uuid_filename))

    def journal_path(self, journal):
        return os.path.join(settings.BASE_DIR, 'files', 'journals', str(journal.pk), str(self.uuid_filename))

    def self_article_path(self):
        if self.article_id:
            return os.path.join(settings.BASE_DIR, 'files', 'articles', str(self.article_id), str(self.uuid_filename))

    def get_file(self, article):
        return files.get_file(self, article)

    def get_file_path(self, article):
        return os.path.join(settings.BASE_DIR, 'files', 'articles', str(article.id), str(self.uuid_filename))

    def render_xml(self, article, galley=None):
        return files.render_xml(self, article, galley=galley)

    def get_file_size(self, article):
        return os.path.getsize(os.path.join(settings.BASE_DIR, 'files', 'articles', str(article.id),
                                            str(self.uuid_filename)))

    def get_tree(self):
        return files.file_parents(self)

    def get_children(self):
        return files.file_children(self)

    def next_history_seq(self):
        try:
            last_history_item = self.history.all().reverse()[0]
            return last_history_item.history_seq + 1
        except IndexError:
            return 0

    def __str__(self):
        return u'%s' % self.original_filename

    def __repr__(self):
        return u'%s' % self.original_filename


class FileHistory(models.Model):
    article_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Article PK")

    mime_type = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=1000)
    uuid_filename = models.CharField(max_length=100)
    label = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Label'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    sequence = models.IntegerField(default=1)
    owner = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    privacy = models.CharField(max_length=20, choices=privacy_types, default="owner")

    history_seq = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('history_seq',)


def galley_type_choices():
    return (
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('html', 'HTML'),
        ('xml', 'XML'),
        ('doc', 'Word (Doc)'),
        ('docx', 'Word (DOCX)'),
        ('odt', 'OpenDocument Text Document'),
        ('tex', 'LaTeX'),
        ('rtf', 'RTF'),
    )


class Galley(models.Model):
    # Local Galley
    article = models.ForeignKey('submission.Article')
    file = models.ForeignKey(File)
    css_file = models.ForeignKey(File, related_name='css_file', null=True, blank=True, on_delete=models.SET_NULL)
    images = models.ManyToManyField(File, related_name='images', null=True, blank=True)

    # Remote Galley
    is_remote = models.BooleanField(default=False)
    remote_file = models.URLField(blank=True, null=True)

    # All Galleys
    label = models.CharField(max_length=400)
    type = models.CharField(max_length=100, choices=galley_type_choices())
    sequence = models.IntegerField(default=0)

    def __str__(self):
        return "{0} ({1}) - {2}".format(self.id, self.label, self.article.title)

    def has_missing_image_files(self):
        xml_file_contents = self.file.get_file(self.article)

        souped_xml = BeautifulSoup(xml_file_contents, 'lxml')

        elements = {
            'img': 'src',
            'graphic': 'xlink:href'
        }

        missing_elements = []

        # iterate over all found elements
        for element, attribute in elements.items():
            images = souped_xml.findAll(element)

            # iterate over all found elements of each type in the elements dictionary
            for idx, val in enumerate(images):
                # attempt to pull a URL from the specified attribute
                url = os.path.basename(val.get(attribute, None))

                try:
                    try:
                        self.images.get(original_filename=url)
                    except File.MultipleObjectsReturned:
                        self.images.filter(original_filename=url).first()
                except File.DoesNotExist:
                    missing_elements.append(url)

        if not missing_elements:
            return []
        else:
            return missing_elements

    def file_content(self):
        if self.file.mime_type == "text/html":
            # get raw HTML and render
            return self.file.get_file(self.article)
        elif self.file.mime_type == "application/xml" or self.file.mime_type == 'text/xml':
            # perform an XSLT render
            return self.file.render_xml(self.article, galley=self)


class Task(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='task_content_type', null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey('content_type', 'object_id')

    title = models.CharField(max_length=300)
    description = models.TextField()
    complete_events = models.ManyToManyField('core.TaskCompleteEvents')
    link = models.TextField(null=True, blank=True, help_text='A url name, where the action of this task can undertaken')
    assignees = models.ManyToManyField(Account)
    completed_by = models.ForeignKey(Account, blank=True, null=True, related_name='completed_by')

    created = models.DateTimeField(default=timezone.now)
    due = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)

    @property
    def is_late(self):
        if timezone.now().date() >= self.due.date():
            return True

        return False

    @staticmethod
    def destroyer(**kwargs):
        """
        Destroys tasks where the kwargs matches an entry in complete_events
        :param kwargs: a dictionary containing an event_name key and a task_obj object that points to an object stored
        inside a task.
        :return: None
        """

        # Important safety note:

        # This function does a lookup from tasks based on the task_obj field that is passed. The type of object that
        # is passed could, therefore, lead to arbitrary task deletion. This occurs when, for instance, there is an
        # Article with ID 1 and a ReviewerAssignment with ID 1 that both subscribe to the same event for teardown. If
        # one event fires with an Article and the other fires with a ReviewerAssignment it is the object that is passed
        # that will be used to lookup the task for deletion.

        # To militate against this risk, we recommend that task_obj is _always_ set to an article and that, likewise,
        # task.object is always an article. All other workflow components can be looked up from this point.

        tasks_to_destroy = Task.objects.filter(complete_events__event_name=kwargs['event'],
                                               content_type=ContentType.objects.get_for_model(kwargs['task_obj']),
                                               object_id=kwargs['task_obj'].pk)

        for task in tasks_to_destroy:
            task.completed = timezone.now()
            task.save()

    def __str__(self):
        return "Task for {0} #{1}: {2}".format(self.content_type, self.object_id, self.title)


class TaskCompleteEvents(models.Model):
    event_name = models.CharField(max_length=300)

    def __str__(self):
        return self.event_name


class NewsItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='news_content_type', null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey('content_type', 'object_id')

    title = models.CharField(max_length=500)
    body = models.TextField()
    posted = models.DateTimeField(default=timezone.now)
    posted_by = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL)

    start_display = models.DateField(default=timezone.now)
    end_display = models.DateField(blank=True, null=True)
    sequence = models.PositiveIntegerField(default=0)

    large_image_file = models.ForeignKey('core.File', null=True, blank=True, related_name='news_file',
                                         on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-posted', 'title')

    @property
    def url(self):
        if self.content_type.name == 'press':
            secure = self.object.is_secure
        else:
            from utils import setting_handler
            secure = setting_handler.get_setting('general', 'is_secure', self.object).processed_value

        path = reverse('core_news_item', kwargs={'news_pk': self.pk})
        base = "http{0}://{1}".format(
            's' if secure else '',
            self.object.domain
        )
        return base + path

    @property
    def carousel_subtitle(self):
        return ""

    @property
    def carousel_title(self):
        return self.title

    @property
    def carousel_image_resolver(self):
        return 'news_file_download'

    def serve_news_file(self):
        if self.content_type.name == 'press':
            return files.serve_file_to_browser(self.large_image_file.press_path(), self.large_image_file)
        else:
            return files.serve_file_to_browser(self.large_image_file.journal_path(self.object), self.large_image_file)

    def __str__(self):
        if self.posted_by:
            return '{0} posted by {1} on {2}'.format(self.title, self.posted_by.full_name, self.posted)
        else:
            return '{0} posted on {1}'.format(self.title, self.posted)


class EditorialGroup(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    journal = models.ForeignKey('journal.Journal')
    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ('sequence',)

    def next_member_sequence(self):
        orderings = [member.sequence for member in self.editorialgroupmember_set.all()]
        return max(orderings) + 1 if orderings else 0

    def members(self):
        return [member for member in self.editorialgroupmember_set.all()]


class EditorialGroupMember(models.Model):
    group = models.ForeignKey(EditorialGroup)
    user = models.ForeignKey(Account)
    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ('sequence',)


class Contacts(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     related_name='contact_content_type', null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(max_length=300)
    email = models.EmailField()
    role = models.CharField(max_length=200)
    sequence = models.PositiveIntegerField(default=999)

    class Meta:
        verbose_name_plural = 'Journal Contacts'
        ordering = ('sequence', 'name')

    def __str__(self):
        return "{0}, {1} - {2}".format(self.user.full_name(), self.journal, self.role)


class Contact(models.Model):
    recipient = models.EmailField(max_length=200, verbose_name='Who would you like to contact')
    sender = models.EmailField(max_length=200, verbose_name=_('Your contact email address'))
    subject = models.CharField(max_length=300, verbose_name=_('Subject'))
    body = models.TextField(verbose_name=_('Your message'))
    client_ip = models.GenericIPAddressField()
    date_sent = models.DateField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='contact_c_t',
                                     null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey('content_type', 'object_id')


class DomainAlias(models.Model):
    domain = models.CharField(max_length=255)
    redirect = models.BooleanField(default=True, verbose_name="301",
                                   help_text="If enabled, the site will throw a 301 redirect to the master domain.")
    site_id = models.PositiveIntegerField()

    @property
    def site(self):
        return Site.objects.get(pk=self.site_id)

    def build_redirect_url(self, request):
        protocol = 'https' if request.is_secure() else 'http'
        return "{0}://{1}{2}".format(protocol,
                                     self.site.domain,
                                     request.path)


BASE_ELEMENTS = [
    {'name': 'review', 'handshake_url': 'review_unassigned_article', 'stage': submission_models.STAGE_UNASSIGNED},
    {'name': 'copyediting', 'handshake_url': 'article_copyediting',
     'stage': submission_models.STAGE_EDITOR_COPYEDITING},
    {'name': 'production', 'handshake_url': 'production_list', 'stage': submission_models.STAGE_TYPESETTING},
    {'name': 'proofing', 'handshake_url': 'proofing_list', 'stage': submission_models.STAGE_PROOFING},
    {'name': 'prepublication', 'handshake_url': 'publish_article',
     'stage': submission_models.STAGE_READY_FOR_PUBLICATION}
]


class Workflow(models.Model):
    journal = models.ForeignKey('journal.Journal')
    elements = models.ManyToManyField('WorkflowElement')


class WorkflowElement(models.Model):
    journal = models.ForeignKey('journal.Journal')
    element_name = models.CharField(max_length=255)
    handshake_url = models.CharField(max_length=255)
    stage = models.CharField(max_length=255, default=submission_models.STAGE_UNASSIGNED)
    order = models.PositiveIntegerField(default=20)

    class Meta:
        ordering = ('order', 'element_name')

    def __str__(self):
        return self.element_name


class HomepageElement(models.Model):
    # the URL to configure this homepage element, or null/blank if no configuration is needed
    configure_url = models.CharField(max_length=200, blank=True, null=True)

    # The name of this homepage element. This should be unique.
    name = models.CharField(max_length=200, blank=False, null=False)

    # the template path to include
    template_path = models.CharField(max_length=500, blank=False, null=False)

    # the ordering
    sequence = models.PositiveIntegerField(default=999)

    # the associated object
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     related_name='element_content_type',
                                     null=True)

    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey('content_type', 'object_id')

    available_to_press = models.BooleanField(default=False, help_text='Determines if this element is '
                                                                      'available for the press.')

    # whether or not this item is active
    active = models.BooleanField(default=False)

    # whether or not this item has a configuration
    has_config = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Homepage Elements'
        ordering = ('sequence', 'name')
        unique_together = ('name', 'content_type', 'object_id')

    def __str__(self):
        return self.name