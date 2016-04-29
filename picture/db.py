from google.appengine.ext import ndb
import hashlib
import datetime
import random
from google.appengine.ext import blobstore

class ProcessedImages(ndb.Model):
    ''' A class to get hold of all the processed images that belongs to a single image '''
    public_hash_id = ndb.StringProperty(default='') # a random job id, for marking purpose.

    blob_256 = ndb.BlobKeyProperty()
    blob_512 = ndb.BlobKeyProperty()
    blob_800 = ndb.BlobKeyProperty()
    blob_1600 = ndb.BlobKeyProperty()
    description = ndb.StringProperty(default='') # description of the picture, default is none
    tags = ndb.StringProperty(repeated=True) # the tokenized description of this picture
    public = ndb.BooleanProperty(default=True) # if this image is public accessable
    
    last_touch_date = ndb.DateTimeProperty(auto_now=True)
    add_date = ndb.DateTimeProperty(auto_now_add=True)

    # Generate a public hash, we don't want to use the urlsafe hash from GAE
    def _pre_put_hook(self):
        m = hashlib.md5()
        factor_one = datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')
        factor_two = str(random.getrandbits(128))
        m.update(factor_one)
        m.update(factor_two)
        if not self.public_hash_id: # if the hash is not available
            self.public_hash_id = m.hexdigest()
        
        if self.description: # if description is not none, then update the tags token
            self.tags = list(set(self.description.lower().split()))

    @classmethod
    def make_query(cls, allowed_user=True):
        if allowed_user:
            return cls.query()
        else:
            return cls.query(cls.public == True)

    @classmethod
    def query_by_hash(cls, hash_value, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.public_hash_id == hash_value).order(-cls.add_date).fetch()
    
    @classmethod
    def query_by_tags(cls, tags, allowed_user=True): # tags is a input list []
        return cls.make_query(allowed_user).filter(cls.tags.IN(tags)).order(-cls.add_date).fetch()
    
    @classmethod
    def query_by_page(cls, page_offset, each_page_amount, chrono=False, allowed_user=True):
        ''' if chronological, from far to near, query a results page by page'''
        q = None
        if allowed_user:
            q = cls.query()
        else:
            q = cls.query(cls.public == True)
            
        if chrono == True:
            return q.order(cls.add_date).fetch(offset=page_offset,limit=each_page_amount)
            # return from offset, each page result limit.
        else:
            return q.order(-cls.add_date).fetch(offset=page_offset,limit=each_page_amount)
            
    @classmethod
    def query_whole(cls, allowed_user=True):
        if allowed_user:
            return cls.query().order(-cls.add_date).fetch()
        else:
            return cls.query(cls.public == True).order(-cls.add_date).fetch()

def add_processed_image(blob_256,blob_512,blob_800,blob_1600,description='',public=True):
    ''' public method for adding an processed image collection '''
    item = ProcessedImages(blob_256=blob_256,blob_512=blob_512,blob_800=blob_800,blob_1600=blob_1600,description=description,public=public)
    item_key = item.put()
    return item.public_hash_id # a string

def delete_processed_image(hash_id):
    ''' delete a processed image collection '''
    existing = ProcessedImages.query_by_hash(hash_id)
    length = len(existing)
    for each in existing:
        # delete the blob store key first
        blobstore.delete(each.blob_256)
        blobstore.delete(each.blob_512)
        blobstore.delete(each.blob_800)
        blobstore.delete(each.blob_1600)
        each.key.delete() # delete matching entries.

    return length # return the deleted entries numbers

def update_processed_image(hash_id, description=None, public=None):
    ''' update description and publicity flag of an image '''
    existing = ProcessedImages.query_by_hash(hash_id)
    length = len(existing)
    for each in existing:
        if description:
            each.description = description
        if (public is True) or (public is False):
            each.public = public
        each.put()
    return length