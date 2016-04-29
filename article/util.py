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