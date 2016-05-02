from google.appengine.api import users
import webapp2
import db
import json
from util import MyEncoder

class UserDetector():
    ''' single class used to detect if user is loggedin or an admin or something else '''
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
            
class BaseHandler(webapp2.RequestHandler):
    def user_is_logged_in(self):
        user = users.get_current_user()
        return True if user else False

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
            elif users.is_current_user_admin():
                return True
            else:
                return False
        return None

    def user_is_allowed_author(self):
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

    def add_allowed_author(self, email):
        ''' add an allowed author into db'''
        db.add_blog_author(email)

    def get_login_url(self,dest=None):
        return users.create_login_url(dest_url=dest if dest else self.request.url)

    def get_logout_url(self,dest=None):
        return users.create_logout_url(dest_url=dest if dest else self.request.url)

    def get_user_nickname_email(self):
        if self.user_is_logged_in:
            user = users.get_current_user()
            return user.nickname(), user.email()
        else:
            return None, None

class DetectUser(BaseHandler):
    def get(self):
        d = {}
        if self.user_is_blog_admin() is None:
            d['user_is_admin'] = False
            d['user_logged_in'] = False
            d['login_url'] = self.get_login_url()
        elif self.user_is_blog_admin() is False:
            d['user_is_admin'] = False
            d['user_is_allowed_author'] = self.user_is_allowed_author()
            d['user_logged_in'] = True
            d['user_nickname'],d['user_email'] = self.get_user_nickname_email()
            d['logout_url'] = self.get_logout_url()
        else:
            d['user_is_admin'] = True
            d['user_is_allowed_author'] = self.user_is_allowed_author()
            d['user_logged_in'] = True
            d['action_url'] = self.app.config['action_url']
            d['user_nickname'],d['user_email'] = self.get_user_nickname_email()
            d['logout_url'] = self.get_logout_url()

        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/html/detectuser.html')
        self.response.out.write(template.render(d)) # render complete
            

class CreateOrListAllowedAuthor(BaseHandler):
    def post(self):
        ''' Create a new author '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}

        email = self.request.get('email', None)
        if self.user_is_blog_admin():
            db.add_blog_author(email)
            d['success'] = True
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
        else:
            self.error(403)

    def get(self):
        ''' list all the authors in the library '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}

        if self.user_is_blog_admin():
            d['allowed_authors'] = []
            for each in db.AllowedBlogAuthor.query_whole():
                d['allowed_authors'].append(each.to_dict(include=['email']))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
        else:
            self.error(403)

class SingleAllowedAuthor(BaseHandler):
    def delete(self, email):
        ''' delete the author with the email '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        if self.user_is_blog_admin():
            db.delete_blog_author(email)
            d['success'] = True
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))

        else:
            self.error(403)