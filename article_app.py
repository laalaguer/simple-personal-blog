import webapp2
import os
import jinja2
import article.handlers
import blogadmins

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# this config is shared accross all the application, so use wisely.
config = {}
config['jinja2_env'] = jinja_environment
config['article_single_service'] = '/article/'
config['blog_admins'] = blogadmins.blogadmins

app = webapp2.WSGIApplication(routes=[
	# create article, or list all the articles , [private to admin]
    webapp2.Route('/article', handler=article.handlers.CreateArticleHandler),
    # get or delete, update an aritcle, [private to admin]
    webapp2.Route('/article/<hash_id>', handler=article.handlers.OperateArticleHandler),
    # get article list with tag, [public, private both]
    webapp2.Route('/search_article', handler=article.handlers.SearchArticleByTagHandler),
    # list all the tags in db [public, private both]
    webapp2.Route('/tags', handler=article.handlers.ListTagsHandler),
    # list all the language_tags in db. [public, private both]
    webapp2.Route('/language_tags', handler=article.handlers.ListLanguageTagsHandler),
], debug=True, config=config)