# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import hashlib
import datetime
import random

class SitePreference(ndb.Model):
    site_name = ndb.StringProperty(default='')
    profile_pic_url = ndb.StringProperty(default='')
    site_title = ndb.StringProperty(default='')
    site_sub_title = ndb.StringProperty(default='')
    background_image_url = ndb.StringProperty(default='')
    
    add_date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_one(cls):
        return cls.query().order(-cls.add_date).fetch(1)

def query_preference():
    hits = SitePreference.query_one()
    if len(hits)>0:
        return hits[0]
    else:
        item = SitePreference(site_name='John Smith',
                                profile_pic_url='/img/goodprofilepic.jpg',
                                site_title='Simple Personal Blog',
                                site_sub_title='Adapted from Start Bootstrap - Clean Blog',
                                background_image_url='/img/home-bg.jpg')
        item.put()
        return item

def update_preference(site_name, profile_pic_url, site_title, site_sub_title, background_image_url):
    ''' User pdate all of the preferences'''
    hits = SitePreference.query_one()
    if len(hits)>0:
        hits[0].site_name = site_name
        hits[0].profile_pic_url = profile_pic_url
        hits[0].site_title = site_title
        hits[0].site_sub_title = site_sub_title
        hits[0].background_image_url = background_image_url
        hits[0].put()
    else:
        item = SitePreference(site_name=site_name,profile_pic_url=profile_pic_url,site_title=site_title,site_sub_title=site_sub_title,background_image_url=background_image_url)
        item.put()