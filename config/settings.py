import os
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY='dev-only-not-for-prod'
DEBUG=True
ALLOWED_HOSTS=['*']
INSTALLED_APPS=['django.contrib.contenttypes','django.contrib.staticfiles','reconcile']
MIDDLEWARE=[]
ROOT_URLCONF='config.urls'
WSGI_APPLICATION='config.wsgi.application'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.path.join(BASE_DIR,'db.sqlite3')}}
STATIC_URL='/static/'
USE_TZ=False
