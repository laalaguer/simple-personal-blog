from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import images
import webapp2
import json
from google.appengine.api import urlfetch
import db
import time
from cStringIO import StringIO
from PIL import Image as PILImage
from PIL import ImageOps as PILImageOps
from util import MyEncoder

class ServeBlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
    ''' Serve the images to the public '''
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

class RefreshUploadUrlHandler(webapp2.RequestHandler):
    ''' get a refresh uploading url where user can upload a picture
    You can use it inside a <form action="">, or , from a javascript ajax
    Return: the uploading url
    '''
    def get(self):
        # Upload of an image url
        upload_url = blobstore.create_upload_url(self.app.config['blob_process'])
        self.response.out.write(upload_url)


class DropzoneExampleHandler(webapp2.RequestHandler):
    ''' Human user upload one image to datastore by drag and drop '''
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
        alreay_exist = db.ProcessedImages.query_whole() # a list returned
        for each in alreay_exist:
            d['already_on_server'].append(each.to_dict(exclude=['add_date']))
        
        jinja_environment = self.app.config['jinja2_env']
        template = jinja_environment.get_template('/html/dropzone-upload-example.html')
        self.response.out.write(template.render(d)) # render complete


class ImagePreProcessHandler(blobstore_handlers.BlobstoreUploadHandler):
    ''' Gets an image and transform it into different scale using GAE Image Service.Then call another handler to handle it'''
    @classmethod
    def encode_multipart_formdata(cls, fields, files, mimetype='image/jpeg'):
        """
        Args:
          fields: A sequence of (name, value) elements for regular form fields.
          files: A sequence of (name, filename, value) elements for data to be
            uploaded as files.

        Returns:
          A sequence of (content_type, body) ready for urlfetch.
        """
        boundary = 'paLp12Buasdasd40tcxAp97curasdaSt40bqweastfarcUNIQUE_STRING'
        crlf = '\r\n'
        line = []
        for (key, value) in fields:
            line.append('--' + boundary)
            line.append('Content-Disposition: form-data; name="%s"' % key)
            line.append('')
            line.append(value)
        for (key, filename, value) in files:
            line.append('--' + boundary)
            line.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            line.append('Content-Type: %s' % mimetype)
            line.append('')
            line.append(value)
        line.append('--%s--' % boundary)
        line.append('')
        body = crlf.join(line)
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body

    @classmethod
    def is_image(cls, blobinfo):
        big_url = images.get_serving_url(blobinfo.key(), size=1600, crop=False)
        response = urlfetch.fetch(
                            url=big_url, # the url
                            method=urlfetch.GET,
                            deadline=30,
                            validate_certificate=False)

        if response.status_code >= 299:
            raise Exception('Not an Image')

    def post(self):
        # get all the uploaded file info
        myfile = self.get_uploads('file')[0] # this is a blob key info
        
        # too large file, we bail out
        if myfile.size > self.app.config['max_upload_size'] * 1000000:  # in B, so kb = 1000B, mb==1000000B
            self.error(413)
            self.response.out.write('file too large: %s Max allowed: %s MB' % (str(myfile.size), self.app.config['max_upload_size']))
            # delete the original file uploaded to blobstore,all of them
            [blobstore.delete(each.key()) for each in self.get_uploads('file')]
            return

        # if not image, we bail out
        try:
            ImagePreProcessHandler.is_image(myfile)
        except Exception as ex:
            self.error(406)
            self.response.out.write(str(ex))
            self.response.out.write(' Image in "file" Field is danmaged, or not image')
            # delete the original file uploaded to blobstore,all of them
            [blobstore.delete(each.key()) for each in self.get_uploads('file')]
            return

        
        start_time = time.time()
        ### Use PIL library to transform image transformation
        ### But this process is slow and memory too huge to consume, quality is high
        # im = PILImage.open(myfile.open())
        # if im.mode not in ("L","RGB"):
        #     im = im.convert("RGB")

        # im.thumbnail((1600,1600)) # if the image size is smaller than this size, it will not stretch
        # buf_1600 = StringIO()
        # im.save(buf_1600,"JPEG",quality=95) # 95% can save 1/2 space
        # data_1600 = buf_1600.getvalue()
        # buf_1600.close() # free memory

        # im.thumbnail((800,800))
        # buf_800 = StringIO()
        # im.save(buf_800,"JPEG",quality=95)
        # data_800 = buf_800.getvalue()
        # buf_800.close()

        # im3 = PILImageOps.fit(im, (512, 512),PILImage.ANTIALIAS)
        # buf_512 = StringIO()
        # im3.save(buf_512,"JPEG",quality=95)
        # data_512 = buf_512.getvalue()
        # buf_512.close()
        

        # im4 = PILImageOps.fit(im, (256, 256),PILImage.ANTIALIAS) # let the edge soft, not so sharp
        # buf_256 = StringIO()
        # im4.save(buf_256,"JPEG",quality=95)
        # data_256 = buf_256.getvalue()
        # buf_256.close()

        # thumbnails = [data_1600,data_800,data_512,data_256]
        
        
        ### This is using google image service to perform image transforation
        ### Which will result quite blur in the final quality, but it is fast
        thumbnails = []
        img = images.Image(blob_key=myfile.key())
        img.resize(width=1600, height=1600) # if image size is smaller than this size, it will stretch to this size
        thumbnail_1600 = img.execute_transforms(output_encoding=images.JPEG, quality=95)
        thumbnails.append(thumbnail_1600)
        img.resize(width=800, height=800)
        thumbnail_800 = img.execute_transforms(output_encoding=images.JPEG, quality=95)
        thumbnails.append(thumbnail_800)
        img.resize(width=512, height=512,crop_to_fit=True)
        thumbnail_512 = img.execute_transforms(output_encoding=images.JPEG, quality=95)
        thumbnails.append(thumbnail_512)
        img.resize(width=256, height=256,crop_to_fit=True)
        thumbnail_256 = img.execute_transforms(output_encoding=images.JPEG, quality=95)
        thumbnails.append(thumbnail_256)
        ### end
        end_time = time.time()
        elapsed_time = str(end_time - start_time)

        content_type_str = 'image/jpeg'
        format_size_list = ['1600','800','512','256']
        args_list = [ ('file', 'processed_file_'+ y, x) for x,y in zip(thumbnails, format_size_list)]
        ###

        ### This is transformation using url get, I think it is slow, so deprecated
        #2. get the compressed files as different size
        # start_time = time.time()
        # compressed_file_url_list = [
        #     images.get_serving_url(myfile.key(), size=1600, crop=False),
        #     images.get_serving_url(myfile.key(), size=800, crop=False),
        #     images.get_serving_url(myfile.key(), size=512, crop=True),
        #     images.get_serving_url(myfile.key(), size=256, crop=True),
        # ]

        # format_size_list = ['1600','800','512','256']

        # response_list = []
        # for each_url in compressed_file_url_list:
        #     response = urlfetch.fetch(
        #                     url=each_url, # the url
        #                     method=urlfetch.GET,
        #                     deadline=30,
        #                     validate_certificate=False)
        #     response_list.append(response)
        # end_time = time.time()
        # elapsed_time = str(end_time - start_time)
        
        # content_type_str = response_list[0].headers['content-type'] # maybe image/jpeg
        # args_list = [ ('file', 'processed_file_'+ y, x.content) for x,y in zip(response_list, format_size_list)]

        # 3. write the picture to blob, again
        content_type, body = ImagePreProcessHandler.encode_multipart_formdata(
          [], args_list, content_type_str)
        #4. upload to the image storage handler
        #when success, store a DB storage object that holds these images
        response2 = urlfetch.fetch(
          url=blobstore.create_upload_url(self.app.config['blob_store_final']),
          payload=body,
          method=urlfetch.POST,
          headers={'Content-Type': content_type},
          deadline=30
        )

        if response2.status_code == 200:
            response2_loaded_object = json.loads(response2.content,'utf-8')
            arg_list_db = {
                'blob_256' : None,
                'blob_512' : None,
                'blob_800' : None,
                'blob_1600' : None,
            }
            for each in response2_loaded_object['stored']:
                if '256' in each['filename']:
                    arg_list_db['blob_256'] = blobstore.BlobKey(each['blob_key'])
                if '512' in each['filename']:
                    arg_list_db['blob_512'] = blobstore.BlobKey(each['blob_key'])
                if '800' in each['filename']:
                    arg_list_db['blob_800'] = blobstore.BlobKey(each['blob_key'])
                if '1600' in each['filename']:
                    arg_list_db['blob_1600'] = blobstore.BlobKey(each['blob_key'])

            public_hash_id = db.add_processed_image(**arg_list_db) # add the image information into db.
            
            response2_loaded_object['public_hash_id'] = public_hash_id
            response2_loaded_object['process_time'] = elapsed_time
            
            self.response.charset = 'utf-8'
            self.response.content_type = response2.headers['content-type']
            self.response.out.write(json.dumps(response2_loaded_object,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            # delete the original file uploaded to blobstore,all of them
            [blobstore.delete(each.key()) for each in self.get_uploads('file')]
             

class ImageStoreHandler(blobstore_handlers.BlobstoreUploadHandler):
    '''  Store the blob one by one and return the blob key.
        Return: a json, structure like
        {
            'stored':[
                {'blob_key': xxxx, 'filename': xxx,},
                {'blob_key': xxxx, 'filename': xxx,},
                ...
            ]
        }
    '''
    def post(self):
        raw_list = self.get_uploads('file') # get all the files
        d = {}
        d['stored'] = []
        for each in raw_list:
            single_obj = {}
            single_obj['blob_key'] = str(each.key())
            single_obj['filename'] = str(each.filename)
            d['stored'].append(single_obj)

        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))

class DeleteProcessedImageHandler(webapp2.RequestHandler):
    def get(self, public_hash_id):
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        try:
            db.delete_processed_image(public_hash_id)
            d['success'] = True
            self.response.out.write(json.dumps(d,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
    
    def delete(self, public_hash_id):
        self.get(public_hash_id)

class GetProcessedImageHandler(webapp2.RequestHandler):
    def get(self, public_hash_id):
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        try:
            d['pictures'] = []
            hits = db.ProcessedImages.query_by_hash(public_hash_id)
            for each in hits:
                d['pictures'].append(each.to_dict())
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return


class ListProcessedImageHandler(webapp2.RequestHandler):
    def get(self):
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        try:
            tag = self.request.get('tag', None)
            offset = int(self.request.get('offset',0))
            amount = int(self.request.get('amount',10))
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
                hits = db.ProcessedImages.query_by_tags([tag])
            else:
                hits = db.ProcessedImages.query_by_page(offset, amount, chrono=chrono)
                d['count'] = len(hits)
                d['has_next'] = True if d['count'] == amount else False
                if d['count'] == amount:
                    d['next_offset'] = next_offset
                
                d['has_previous'] = True if offset > 0 else False
                if offset > 0:
                    d['previous_offset'] = previous_offset

            for each in hits:
                d['pictures'].append(each.to_dict())
            
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return


class UpdateProcessedImageDescriptionHandler(webapp2.RequestHandler):
    '''update the image description
        Return {
            'success': true/false,
        }
    '''
    def post(self, public_hash_id):
        description = self.request.get('description',None)
        public = self.request.get('public',None)
        if public: # if we have some content inside the public
            public = False if public.lower() == 'false' else True
        
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        try:
            db.update_processed_image(public_hash_id,description,public)
            d['success'] = True
            self.response.out.write(json.dumps(d,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return