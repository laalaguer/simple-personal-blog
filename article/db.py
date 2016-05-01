# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import hashlib
import datetime
import random

class ArticleTag(ndb.Model):
    ''' A module that represent tags of articles, dont forget tags in your blogs! They are like keywords '''
    tags = ndb.StringProperty(repeated=True) # tags name
    add_date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_one(cls):
        return cls.query().order(-cls.add_date).fetch(1)

    @classmethod
    def add_tags(cls, tags):
        new_tags = list(set(tags))
        # the last tag collection
        existing = cls.query_one()
        if len(existing)>0:
            the_last = existing[0]
            for each in new_tags:
                if not (each in the_last.tags):
                    the_last.tags.append(each.lower())
            the_last.put()
        else:
            # we dont have tags object, then we create one
            cls(tags=new_tags).put()


class LanguageTag(ndb.Model):
    ''' A module that represent tags of language '''
    tags = ndb.StringProperty(repeated=True) # tag name
    add_date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_one(cls):
        return cls.query().order(-cls.add_date).fetch(1)

    @classmethod
    def add_tags(cls, tags):
        new_tags = list(set(tags))
        # the last tag collection
        existing = cls.query_one()
        if len(existing)>0:
            the_last = existing[0]
            for each in new_tags:
                if not (each in the_last.tags):
                    the_last.tags.append(each.lower())
            the_last.put()
        else:
            # we dont have tags object, then we create one
            cls(tags=new_tags).put()


class Article(ndb.Model):
    ''' A module that represent an article, it shall have:
        title: that will appear on the title bar.
        author: who wrote it, name.
        article: the real article itself, html tags.
        tags: list of text, represents the tags.
        language: list of text, represents what is the language on this page
    '''
    title = ndb.StringProperty(default='') # title of article
    author = ndb.StringProperty(default='') # author of article
    html_body = ndb.TextProperty(default='') # actual text of article, this is the pure html part.
    tags = ndb.StringProperty(repeated=True) # tags, keywords of an article, a list
    language_tags = ndb.StringProperty(repeated=True) # languages of an article, a list.
    public = ndb.BooleanProperty(default=True) # if this article is private or not
    importance = ndb.IntegerProperty(default=0) # if this article shall be on top of all the blogs, like really important blogs
    
    public_hash_id = ndb.StringProperty(default='') # a random job id, for marking purpose.
    last_touch_date = ndb.DateTimeProperty(auto_now=True)
    add_date = ndb.DateTimeProperty(auto_now_add=True)
    
    # Generate a public hash, we don't want to use the urlsafe hash from GAE
    def _pre_put_hook(self):
        m = hashlib.md5()
        factor_one = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        factor_two = str(random.getrandbits(128))
        m.update(factor_one)
        m.update(factor_two)
        if not self.public_hash_id: # if the hash is not available
            self.public_hash_id = m.hexdigest()

        # convert all the tags and language tags into lowercase
        for each in self.tags:
            each = each.lower()

        for each in self.language_tags:
            each = each.lower()
    @classmethod
    def make_query(cls, allowed_user=True):
        if allowed_user:
            return cls.query()
        else:
            return cls.query(cls.public == True)

    @classmethod
    def query_whole(cls, allowed_user=True):
        return cls.make_query(allowed_user).order(-cls.add_date).fetch()
    
    @classmethod
    def query_by_importance(cls, allowed_user=True, amount=10):
        return cls.make_query(allowed_user).order(-cls.importance).order(-cls.add_date).fetch(amount)
    
    @classmethod
    def query_recently(cls, allowed_user=True, amount=10):
        return cls.make_query(allowed_user).order(-cls.add_date).fetch(amount)
    
    @classmethod
    def query_by_page(cls, page_offset, each_page_amount, chrono=False, allowed_user=True):
        ''' if chronological, from far to near, query a results page by page''' 
        if chrono == True:
            return cls.make_query(allowed_user).order(cls.add_date).fetch(offset=page_offset,limit=each_page_amount)
            # return from offset, each page result limit.
        else:
            return cls.make_query(allowed_user).order(-cls.add_date).fetch(offset=page_offset,limit=each_page_amount)
    
    @classmethod
    def query_by_hash(cls, hash_value, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.public_hash_id == hash_value).order(-cls.add_date).fetch()
    
    @classmethod
    def query_by_author(cls, author, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.author == author).order(-cls.add_date).fetch()
    
    @classmethod
    def count_by_author(cls, author, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.author == author).count()
    
    @classmethod
    def query_by_tag(cls, tag, allowed_user=True, amount=10):
        return cls.make_query(allowed_user).filter(cls.tags == tag).order(-cls.add_date).fetch(amount)
    
    @classmethod
    def query_by_tags(cls, tags, allowed_user=True, amount=10):
        return cls.make_query(allowed_user).filter(cls.tags.IN(tags)).order(-cls.add_date).fetch(amount)
    
    @classmethod
    def count_by_tag(cls, tag, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.tags == tag).count()

    @classmethod
    def query_by_language(cls, language, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.language_tags == language).order(-cls.add_date).fetch()

    @classmethod
    def query_by_language_and_tag(cls, language, tag, allowed_user=True):
        return cls.make_query(allowed_user).filter(cls.language_tags == language, cls.tags == tag).order(-cls.add_date).fetch()