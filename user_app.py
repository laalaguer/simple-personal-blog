import webapp2
import os
import jinja2
import user.handlers

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# this config is shared accross all the application, so use wisely.
config = {}
config['jinja2_env'] = jinja_environment
config['blog_admins'] = ['laalaguer@gmail.com']
config['action_url'] = '/user/allowed_author'

app = webapp2.WSGIApplication(routes=[
    # [public] hello world
    # webapp2.Route('/user/hello', handler=user.handlers.DetectUser),
    # [private] add allowed blog author, POST
    # [private] list allowed blog authors, GET
    webapp2.Route('/user/allowed_author', handler=user.handlers.CreateOrListAllowedAuthor),
    # [private] delete allowed blog author, DELETE
    webapp2.Route('/user/allowed_author/<email>', handler=user.handlers.SingleAllowedAuthor),
], debug=True, config=config)