from google.appengine.ext import ndb

class VisitorCount(ndb.Model):
    name = ndb.StringProperty() # name of the count
    count = ndb.IntegerProperty() # count of the count
    
    touch_date = ndb.DateTimeProperty(auto_now=True) # the date it is touched
    add_date = ndb.DateTimeProperty(auto_now_add=True) # the date it is created
    
    @classmethod
    def query_by_name(cls, name):
        return cls.query(cls.name == name).get()
    
def add_a_visitor(name):
    m = VisitorCount.query_by_name(name)
    if m:
        m.count = m.count + 1
        m.put()
    else:
        item = VisitorCount(name=name,count=1)
        item.put()

def get_visitor_count(name):
    m = VisitorCount.query_by_name(name)
    if m:
        return m.count
    else:
        return 0