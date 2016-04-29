import webapp2
import os
import jinja2
from google.appengine.ext import blobstore
from picture import db as MyImagedb
from article import db as MyArticledb

static_path = '/'.join([os.path.dirname(__file__),'html'])
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(static_path))

# this config is shared accross all the application, so use wisely.
config = {}
config['jinja2_env'] = jinja_environment
config['max_upload_size'] = 10
config['blob_process'] = '/picture/pre_receive'
config['blob_serving_url'] = r'/picture/view_photo/'
config['blob_store_final'] = '/picture/blob_store_final'
config['refresh_url'] = '/picture/refresh_url'
config['delete_image_collection'] = '/picture/delete_by_hash/'

config['view_blog'] = '/view_blog/'
config['list_blog'] = '/list_blog'
config['search_blog'] = '/search_blog'
config['list_image'] = '/list_image'
# development server or not
debug_flag = False if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/') else True

class EditBlogHandler(webapp2.RequestHandler):
    def get(self):        
        d = {}
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
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/writeblog.child')
        self.response.out.write(template.render(d)) # render complete

class ViewBlogHandler(webapp2.RequestHandler):
    def get(self, public_hash_id):
        d = {}
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

class ListBlogHandler(webapp2.RequestHandler):
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
        hits = MyArticledb.Article.query_by_page(offset, amount, chrono)
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

class SearchBlogHandler(webapp2.RequestHandler):
    def get(self):
        wanted_tag = self.request.get('tag', None)
        wanted_language_tag = self.request.get('language_tag', None)
        
        d = {}

        hits = None
        if wanted_tag and wanted_language_tag:
            hits = MyArticledb.Article.query_by_language_and_tag(wanted_language_tag, wanted_tag)
        elif wanted_tag:
            hits = MyArticledb.Article.query_by_tag(wanted_tag)
        elif wanted_language_tag:
            hits = MyArticledb.Article.query_by_language(wanted_language_tag)
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

        
class ListImageHandler(webapp2.RequestHandler):
    def get(self):
        # prepare the response object
        d = {}
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
            hits = MyImagedb.ProcessedImages.query_by_tags([tag])
        else:
            hits = MyImagedb.ProcessedImages.query_by_page(offset, amount, chrono=chrono)
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



class MainHandler(webapp2.RequestHandler):
    def get(self):        
        d = {}
        d['title_part'] = 'Picture Blog'
        d['blob_serving_url'] = self.app.config['blob_serving_url']
        # image processed, that already on the server
        d['pictures'] = MyImagedb.ProcessedImages.query_by_page(0,15) # a list returned
        hits = MyArticledb.Article.query_by_page(0, 6)
        d['articles'] =  []
        for each in hits:
            d['articles'].append(each.to_dict(exclude=['html_body']))

        d['list_image'] = self.app.config['list_image']
        d['list_blog'] = self.app.config['list_blog']
        d['view_blog'] = self.app.config['view_blog']
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/index.child')
        self.response.out.write(template.render(d)) # render complete


app = webapp2.WSGIApplication(routes=[
    webapp2.Route('/', handler=MainHandler),
    webapp2.Route('/edit_blog', handler=EditBlogHandler),
    webapp2.Route('/view_blog/<public_hash_id>', handler=ViewBlogHandler),
    webapp2.Route('/list_blog', handler=ListBlogHandler),
    webapp2.Route('/search_blog', handler=SearchBlogHandler),
    webapp2.Route('/list_image', handler=ListImageHandler),
], debug=debug_flag, config=config)