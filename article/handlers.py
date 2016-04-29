# -*- coding: utf-8 -*-
# As the article, tag, language_tag are all text based, we use json handlers as a simgle example
# If you wish to see the 
import webapp2
import json
import db
from util import MyEncoder

# the design priciples, you can see the README.md document in the package folder
class CreateArticleHandler(webapp2.RequestHandler):
    def post(self):
        ''' a post handler, receives a json and create an article '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        try:
            jsonstring = self.request.body
            payload = json.loads(jsonstring)
            if payload:
                article = payload['article']
                title = article['title']
                author = article['author']
                html_body = article['html_body']
                tags = [x.lower() for x in article['tags']] # a list
                language_tags = [x.lower() for x in article['language_tags']] # a list
                public = article['public']
                # store article
                item = db.Article(title=title,author=author,html_body=html_body,tags=tags,language_tags=language_tags,public=public)
                item.put()
                # store tags
                db.ArticleTag.add_tags(tags)
                # store language tags
                db.LanguageTag.add_tags(language_tags)
                # prepare reponse
                d['success'] = True
                d['public_hash_id'] = item.public_hash_id
                self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
                return
            else:
                self.error(406)
                d['success'] = False
                d['fail_reason'] = 'json is empty'
                self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
                return
        except Exception as ex:
            self.error(406)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return

    def get(self):
        ''' get all the articles, or part of it, choose by offset, amount and chrono'''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}

        try:
            offset = int(self.request.get('offset',0))
            amount = int(self.request.get('amount',10))
            chrono = str(self.request.get('chrono', 'false'))
            
            next_offset = offset + amount
            previous_offset = offset - amount if offset - amount > 0 else 0
            
            
            if chrono == 'true':
                chrono = True
            else:
                chrono = False

            hits = db.Article.query_by_page(offset, amount, chrono)
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
            
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))

        except Exception as ex:
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return


class OperateArticleHandler(webapp2.RequestHandler):
    ''' GET, PUT, DELETE handler, modify the article '''
    def get(self, hash_id):
        ''' send back user a json-represented article '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        try:
            # search for the article in database, then return the article as json
            articles = db.Article.query_by_hash(hash_id)
            if len(articles) > 0:
                d['success'] = True
                d['article'] = articles[0].to_dict()
            else:
                d['success'] = False
                d['fail_reason'] = 'article not found'

            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return


    def put(self, hash_id):
        ''' modify a field, or fields of an artile '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        # prepare the user uploaded json
        payload = None
        try:
            jsonstring = self.request.body
            payload = json.loads(jsonstring)
            article = payload['article']
        except Exception as ex:
            self.error(406)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
        
        try:
            # search for the article in database, then return the article as json
            articles = db.Article.query_by_hash(hash_id)
            if len(articles) > 0:
                target = articles[0].to_dict(exclude=['add_date','last_touch_date','public_hash_id']) # we don't allow other modification

                for key in article.keys():
                    if key in target.keys():
                        if key == 'tags' :
                            values = [x.lower() for x in article[key]]
                            setattr(articles[0], key, values)
                            # store tags
                            db.ArticleTag.add_tags(article[key])

                        elif key == 'language_tags':
                            values = [x.lower() for x in article[key]]
                            setattr(articles[0], key, values)
                            # store language tags
                            db.LanguageTag.add_tags(article[key])
                        else:
                            setattr(articles[0], key, article[key])

                articles[0].put()
                print 'after put, tags',articles[0].tags
                d['success'] = True
            else:
                d['success'] = False
                d['fail_reason'] = 'article not found'

            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
    
    def delete(self, hash_id):
        ''' delete an article '''
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}

        try:
            # search for the article in database, then return the article as json
            articles = db.Article.query_by_hash(hash_id)
            if len(articles) > 0:
                for each in articles:
                    each.key.delete()
            d['success'] = True
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return


class SearchArticleByTagHandler(webapp2.RequestHandler):
    def get(self):
        wanted_tag = self.request.get('tag', None)
        wanted_language_tag = self.request.get('language_tag', None)

        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}

        try:
            hits = None
            if wanted_tag and wanted_language_tag:
                hits = db.Article.query_by_language_and_tag(wanted_language_tag, wanted_tag)
            elif wanted_tag:
                hits = db.Article.query_by_tag(wanted_tag)
            elif wanted_language_tag:
                hits = db.Article.query_by_language(wanted_language_tag)
            else:
                d['count'] = 0

            if hits:
                d['count'] = len(hits)
                d['articles'] = []
                for each in hits:
                    d['articles'].append(each.to_dict(exclude=['html_body']))
            else:
                d['count'] = 0

            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return
        except Exception as ex:
            self.error(500)
            d['success'] = False
            d['fail_reason'] = 'Exception: %s, Message: %s' % (type(ex).__name__ , str(ex))
            self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))
            return

class ListTagsHandler(webapp2.RequestHandler):
    def get(self):
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        hits = db.ArticleTag.query_one()
        d['tags'] = hits[0].tags
        d['count'] = len(hits[0].tags)
        self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))

class ListLanguageTagsHandler(webapp2.RequestHandler):
    def get(self):
        # prepare the response type
        self.response.charset = 'utf-8'
        self.response.content_type = 'application/json'
        # prepare the response object
        d = {}
        hits = db.LanguageTag.query_one()
        d['tags'] = hits[0].tags
        d['count'] = len(hits[0].tags)
        self.response.out.write(json.dumps(d,cls=MyEncoder,ensure_ascii=False,indent=2, sort_keys=True).encode('utf-8'))