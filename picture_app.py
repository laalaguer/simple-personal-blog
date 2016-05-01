import webapp2
import os
import jinja2
import picture.handlers
import blogadmins

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
config['blog_admins'] = blogadmins.blogadmins
config['blob_store_secret'] = 'MY_SECRET_STORE_KEY'

app = webapp2.WSGIApplication(routes=[
	# private to admin
    # webapp2.Route('/picture/dropzone_upload_example', handler=picture.handlers.DropzoneExampleHandler),
    # private to admin
    webapp2.Route('/picture/refresh_url', handler=picture.handlers.RefreshUploadUrlHandler),
    # private to admin
    webapp2.Route('/picture/pre_receive', handler=picture.handlers.ImagePreProcessHandler),
    # private to admin
    webapp2.Route('/picture/blob_store_final', handler=picture.handlers.ImageStoreHandler),
    # public, no restriction
    webapp2.Route('/picture/view_photo/<photo_key>', handler=picture.handlers.ServeBlobHandler),
    # private to admin
    webapp2.Route('/picture/delete_by_hash/<public_hash_id>', handler=picture.handlers.DeleteProcessedImageHandler),
    # public
    webapp2.Route('/picture/get_by_hash/<public_hash_id>', handler=picture.handlers.GetProcessedImageHandler),
    # private to admin
    webapp2.Route('/picture/update_description/<public_hash_id>', handler=picture.handlers.UpdateProcessedImageDescriptionHandler),
    # public
    webapp2.Route('/picture/list_all', handler=picture.handlers.ListProcessedImageHandler),
], debug=True, config=config)