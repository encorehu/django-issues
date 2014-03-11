# -*- coding: utf-8 -*- 
# ------------------------------------------------------------
# Script   Name: signals.py
# Creation Date: 2012-3-11 08:04:55
# Last Modified: 2012-3-11 14:05:08
# Copyright (c)2011, DDTCMS Project
# Purpose: This file used for DDTCMS Project
# ------------------------------------------------------------

# python.
#import datetime
#import urllib
# ------------------------------------------------------------

# django.
from django.dispatch import Signal

# ------------------------------------------------------------

# 3dpart.
#
# ------------------------------------------------------------

# ddtcms.
#from models import MODEL
#from forms  import AForm,BForm
# ------------------------------------------------------------

# config.
#FIELD_MAX_LENGTH = getattr(settings, 'FIELD_MAX_LENGTH', 100)
#n_dict={
#"sitename":"Example",
#}
# ------------------------------------------------------------

# extend from C:\Python25\Lib\site-packages\django\db\models\signals.py
#post_save = Signal(providing_args=["instance", "raw", "created", "using",'msg'])
post_save = Signal(providing_args=["instance", "created", "msg"])