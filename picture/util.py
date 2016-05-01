# a util file to encode Blobkey as a string
import json
import datetime
from google.appengine.ext import blobstore


class MyEncoder(json.JSONEncoder):
    '''
    Usage, when you call a json.dumps(), call like
    json.dumps(obj, cls = MyEncoder)
    '''
    def default(self, obj):
        if isinstance(obj, blobstore.BlobKey):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y/%m/%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)

from google.appengine.api import users

class UserDetector():
    ''' single class used to detect if user is loggedin or an admin or something else '''
    @classmethod
    def wrapper_if_logged_in(self, func):
        def logged_in_or_error(self, *args, **kwargs):
            if self.user_is_logged_in():
                return func(self,*args, **kwargs)
            else:
                return self.error(404)
        
        return logged_in_or_error
    
    @classmethod
    def wrapper_if_blog_admin(self, func):
        def logged_in_or_error(self, *args, **kwargs):
            if self.user_is_blog_admin():
                return func(self,*args, **kwargs)
            else:
                return self.error(404)
        
        return logged_in_or_error
    
    @classmethod
    def wrapper_if_app_admin(self, func):
        def logged_in_or_error(self, *args, **kwargs):
            if self.user_is_app_admin():
                return func(self,*args, **kwargs)
            else:
                return self.error(404)
        
        return logged_in_or_error
    
    def user_is_logged_in(self):
        user = users.get_current_user()
        return True if user else False
    
    def user_is_app_admin(self):
        return users.is_current_user_admin()
        
    def user_is_blog_admin(self):
        '''
        Return True if admin, 
        False if not admin,
        None if user not logged in
        '''
        if self.user_is_logged_in():
            user = users.get_current_user()
            if user.email() in self.app.config['blog_admins']:
                return True
            else:
                return False
        return None

    def user_is_allowed_author(self): # never use if no allowed_user in database
        '''
        Return True if author, 
        False if not author,
        None if user not logged in
        '''
        if self.user_is_logged_in:
            user = users.get_current_user()
            if user.email() in self.app.config['blog_admins']:
                return True
            elif db.AllowedBlogAuthor.is_in_db_by_email(user.email()):
                return True
            else:
                return False
        return None

    def add_allowed_author(self, email): # never use if no allowed_user in database
        ''' add an allowed author into db'''
        db.add_blog_author(email)

    def get_login_url(self):
        return users.create_login_url(dest_url=self.request.url)

    def get_logout_url(self):
        return users.create_logout_url(dest_url=self.request.url)

    def get_user_nickname_email(self):
        if self.user_is_logged_in:
            user = users.get_current_user()
            return user.nickname(), user.email()
        else:
            return None, None