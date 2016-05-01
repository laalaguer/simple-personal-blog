import webapp2
import os
import jinja2
from google.appengine.ext import blobstore
from picture import db as MyImagedb
from article import db as MyArticledb
from user.handlers import UserDetector # the authorization handler
from user.handlers import BaseHandler # a webapp2 request handler
import blogadmins
from preference import db as MyPreferencedb

static_path = '/'.join([os.path.dirname(__file__),'html'])
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(static_path))

# this config is shared accross all the application, so use wisely.
config = {}
# default config on the backend, that we use on front end
config['jinja2_env'] = jinja_environment
config['max_upload_size'] = 10

config['blob_serving_url'] = '/picture/view_photo/'

config['blob_process'] = '/picture/pre_receive'
config['refresh_url'] = '/picture/refresh_url'
config['delete_image_collection'] = '/picture/delete_by_hash/'

config['delete_blog'] = '/article/' # used for DELETE
config['update_article'] = '/article/' # used for PUT
config['create_article'] = '/article' # only used for create here
# default config on the front end
config['update_blog'] = '/update_blog/'
config['view_blog'] = '/view_blog/'
config['list_blog'] = '/list_blog'
config['search_blog'] = '/search_blog'
config['list_image'] = '/list_image'
config['edit_site_appearance'] = '/edit_site_appearance'
# default config for the user
config['blog_admins'] = blogadmins.blogadmins

# development server or not
debug_flag = False if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/') else True

class EditSiteAppearanceHanlder(webapp2.RequestHandler,UserDetector):
    def get(self):        
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        d['edit_site_appearance'] = self.app.config['edit_site_appearance']
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        if not d['is_admin']:
            self.redirect('/')
            return
            
        upload_url = blobstore.create_upload_url(self.app.config['blob_process'])
        d['blob_process'] = upload_url
        d['refresh_url'] = self.app.config['refresh_url']
        d['blob_serving_url'] = self.app.config['blob_serving_url']
        d['max_upload_size'] = self.app.config['max_upload_size']
        d['delete_image_collection'] = self.app.config['delete_image_collection']
        
        # image processed, that already on the server
        d['already_on_server'] = []
        alreay_exist = MyImagedb.ProcessedImages.query_by_page(0,20) # a list returned
        for each in alreay_exist:
            d['already_on_server'].append(each.to_dict(exclude=['add_date']))
        
        d['view_blog'] = self.app.config['view_blog']
        d['create_article'] = self.app.config['create_article']
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/editsite.child')
        self.response.out.write(template.render(d)) # render complete
    
    def post(self):
        site_name = self.request.get('site_name','')
        profile_pic_url = self.request.get('profile_pic_url','')
        site_title = self.request.get('site_title','')
        site_sub_title = self.request.get('site_sub_title', '')
        background_image_url = self.request.get('background_image_url', '')
        
        try:
            MyPreferencedb.update_preference(site_name=site_name, profile_pic_url=profile_pic_url, site_title=site_title, site_sub_title=site_sub_title, background_image_url=background_image_url)
        except Exception as ex:
            self.error(500)
            self.response.out.write(str(ex))
            
class EditBlogHandler(webapp2.RequestHandler,UserDetector):
    def get(self):        
        d = {}
        d['is_admin'] = self.user_is_blog_admin()
        if not d['is_admin']:
            self.redirect('/')
            return
            
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        if not d['is_admin']:
            self.error(404)
            return
            
        upload_url = blobstore.create_upload_url(self.app.config['blob_process'])
        d['blob_process'] = upload_url
        d['refresh_url'] = self.app.config['refresh_url']
        d['blob_serving_url'] = self.app.config['blob_serving_url']
        d['max_upload_size'] = self.app.config['max_upload_size']
        d['delete_image_collection'] = self.app.config['delete_image_collection']
        
        # image processed, that already on the server
        d['already_on_server'] = []
        alreay_exist = MyImagedb.ProcessedImages.query_by_page(0,20) # a list returned
        for each in alreay_exist:
            d['already_on_server'].append(each.to_dict(exclude=['add_date']))
        
        d['view_blog'] = self.app.config['view_blog']
        d['create_article'] = self.app.config['create_article']
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/writeblog.child')
        self.response.out.write(template.render(d)) # render complete

class UpdateBlogHandler(webapp2.RequestHandler,UserDetector):
    def get(self, public_hash_id):        
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        if not d['is_admin']:
            self.redirect('/')
            return
        
        upload_url = blobstore.create_upload_url(self.app.config['blob_process'])
        d['blob_process'] = upload_url
        d['refresh_url'] = self.app.config['refresh_url']
        d['blob_serving_url'] = self.app.config['blob_serving_url']
        d['max_upload_size'] = self.app.config['max_upload_size']
        d['delete_image_collection'] = self.app.config['delete_image_collection']
        
        # image processed, that already on the server
        d['already_on_server'] = []
        alreay_exist = MyImagedb.ProcessedImages.query_by_page(0,20) # a list returned
        for each in alreay_exist:
            d['already_on_server'].append(each.to_dict(exclude=['add_date']))
        
        d['view_blog'] = self.app.config['view_blog']
        d['update_article'] = self.app.config['update_article']
        
        hits = MyArticledb.Article.query_by_hash(public_hash_id,allowed_user=d['is_admin'])
        d['current_document'] = hits[0]
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/writeblog.child')
        self.response.out.write(template.render(d)) # render complete

class ViewBlogHandler(webapp2.RequestHandler,UserDetector):
    def get(self, public_hash_id):
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        d['update_blog'] = self.app.config['update_blog']
        d['delete_blog'] = self.app.config['delete_blog']
        
        articles = MyArticledb.Article.query_by_hash(public_hash_id)
        if len(articles) > 0:
            d['article'] = articles[0].to_dict()
        else:
            self.error(404)
            return
        recently = MyArticledb.Article.query_recently()
        d['recently'] = recently
        
        related = MyArticledb.Article.query_by_tags(articles[0].tags)
        d['related'] = related
        
        hits = MyArticledb.ArticleTag.query_one()
        d['tags'] = hits[0].tags
        
        d['view_blog'] = self.app.config['view_blog']
        d['come_from'] = self.request.referer
        d['search_blog'] = self.app.config['search_blog']
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/singleblog.child')
        self.response.out.write(template.render(d)) # render complete

class ListBlogHandler(webapp2.RequestHandler,UserDetector):
    def get(self):
        offset = int(self.request.get('offset',0))
        amount = int(self.request.get('amount',10))
        chrono = str(self.request.get('chrono', 'false'))
        
        next_offset = offset + amount
        previous_offset = offset - amount if offset - amount > 0 else 0
        
        
        if chrono == 'true':
            chrono = True
        else:
            chrono = False
        
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        d['update_blog'] = self.app.config['update_blog']
        d['delete_blog'] = self.app.config['delete_blog']
        
        hits = MyArticledb.Article.query_by_page(offset, amount, chrono,allowed_user=d['is_admin'])
        d['count'] = len(hits)
        d['articles'] = []
        for each in hits:
            d['articles'].append(each.to_dict(exclude=['html_body']))
        
        d['has_next'] = True if d['count'] == amount else False
        if d['count'] == amount:
            d['next_offset'] = next_offset
            
        d['has_previous'] = True if offset > 0 else False
        if offset > 0:
            d['previous_offset'] = previous_offset

        d['amount'] = amount
        d['title_part'] = 'Blogs'   
        d['view_blog'] = self.app.config['view_blog']
        d['list_blog'] = self.app.config['list_blog']
        d['search_blog'] = self.app.config['search_blog']
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/blogslist.child')
        self.response.out.write(template.render(d)) # render complete

class SearchBlogHandler(webapp2.RequestHandler,UserDetector):
    def get(self):
        wanted_tag = self.request.get('tag', None)
        wanted_language_tag = self.request.get('language_tag', None)
        
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        d['update_blog'] = self.app.config['update_blog']
        d['delete_blog'] = self.app.config['delete_blog']

        hits = None
        if wanted_tag and wanted_language_tag:
            hits = MyArticledb.Article.query_by_language_and_tag(wanted_language_tag, wanted_tag,allowed_user=d['is_admin'])
        elif wanted_tag:
            hits = MyArticledb.Article.query_by_tag(wanted_tag,allowed_user=d['is_admin'])
        elif wanted_language_tag:
            hits = MyArticledb.Article.query_by_language(wanted_language_tag,allowed_user=d['is_admin'])
        else:
            d['count'] = 0

        if hits:
            d['count'] = len(hits)
            d['articles'] = []
            for each in hits:
                d['articles'].append(each.to_dict(exclude=['html_body']))
        else:
            d['count'] = 0
        
        d['title_part'] = 'Search ' + wanted_tag if wanted_tag else '' + wanted_language_tag if wanted_language_tag else ''
        d['view_blog'] = self.app.config['view_blog']

        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/blogslist.child')
        self.response.out.write(template.render(d)) # render complete

        
class ListImageHandler(webapp2.RequestHandler,UserDetector):
    def get(self):
        # prepare the response object
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        
        d['delete_image_collection'] = self.app.config['delete_image_collection']
        d['blob_serving_url'] = self.app.config['blob_serving_url']
        
        tag = self.request.get('tag', None)
        offset = int(self.request.get('offset',0))
        amount = int(self.request.get('amount',9))
        next_offset = offset + amount
        previous_offset = offset - amount if offset - amount > 0 else 0
        
        chrono = str(self.request.get('chrono', 'false'))
        if chrono == 'true':
            chrono = True
        else:
            chrono = False

        d['pictures'] = []
        hits = None
        if tag:
            hits = MyImagedb.ProcessedImages.query_by_tags([tag], allowed_user=d['is_admin'])
        else:
            hits = MyImagedb.ProcessedImages.query_by_page(offset, amount, chrono=chrono,allowed_user=d['is_admin'])
            d['count'] = len(hits)
            d['has_next'] = True if d['count'] == amount else False
            if d['count'] == amount:
                d['next_offset'] = next_offset
            
            d['has_previous'] = True if offset > 0 else False
            if offset > 0:
                d['previous_offset'] = previous_offset
                
        d['amount'] = amount
        d['title_part'] = 'Images'        
        d['pictures'] = hits
        d['list_image'] = self.app.config['list_image']
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/imagelist.child')
        self.response.out.write(template.render(d)) # render complete



class MainHandler(webapp2.RequestHandler,UserDetector):
    def get(self):
        d = {}
        d['sitepreference'] = MyPreferencedb.query_preference()
        
        d['is_admin'] = self.user_is_blog_admin()
        d['logout_url'] = self.get_logout_url()
        
        d['title_part'] = 'Home'
        d['blob_serving_url'] = self.app.config['blob_serving_url']
        # image processed, that already on the server
        d['pictures'] = MyImagedb.ProcessedImages.query_by_page(0,15,allowed_user=d['is_admin']) # a list returned
        hits = MyArticledb.Article.query_by_importance(allowed_user=d['is_admin'],amount=10)
        d['articles'] =  []
        for each in hits:
            d['articles'].append(each.to_dict(exclude=['html_body']))

        d['list_image'] = self.app.config['list_image']
        d['list_blog'] = self.app.config['list_blog']
        d['view_blog'] = self.app.config['view_blog']
        d['search_blog'] = self.app.config['search_blog']
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/index.child')
        self.response.out.write(template.render(d)) # render complete

class AdminLoginHandler(BaseHandler):
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
            d['user_nickname'],d['user_email'] = self.get_user_nickname_email()
            d['logout_url'] = self.get_logout_url()

        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/detectuser.html')
        self.response.out.write(template.render(d)) # render complete
        
app = webapp2.WSGIApplication(routes=[
    webapp2.Route('/', handler=MainHandler),
    webapp2.Route('/edit_site_appearance', handler=EditSiteAppearanceHanlder),
    webapp2.Route('/edit_blog', handler=EditBlogHandler),
    webapp2.Route('/update_blog/<public_hash_id>', handler=UpdateBlogHandler),
    webapp2.Route('/view_blog/<public_hash_id>', handler=ViewBlogHandler),
    webapp2.Route('/list_blog', handler=ListBlogHandler),
    webapp2.Route('/search_blog', handler=SearchBlogHandler),
    webapp2.Route('/list_image', handler=ListImageHandler),
    webapp2.Route('/secret_login_place', handler=AdminLoginHandler),
], debug=debug_flag, config=config)