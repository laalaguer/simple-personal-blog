from google.appengine.ext import ndb

class AllowedBlogAuthor(ndb.Model):
	''' Your co-worker, the same person who edits the blog site
		Well, as admin user of this site you can bring co-worker in
		and kick him out. :D
	'''
	email = ndb.StringProperty(default='')

	@classmethod
	def query_whole(cls):
		return cls.query().fetch()

	@classmethod
	def is_in_db_by_email(cls, email):
		return True if cls.query(cls.email == email).count() else False

	@classmethod
	def query_by_email(cls, email):
		return cls.query(cls.email == email).fetch()

def add_blog_author(email):
	item = AllowedBlogAuthor(email=email)
	item.put()

def delete_blog_author(email):
	items = AllowedBlogAuthor.query_by_email(email)
	for each in items:
		each.key.delete()