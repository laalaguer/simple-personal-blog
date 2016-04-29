### Folder structure

`db.py` all database related about articles

`handlers.py` example web handlers about how to add/remove articles. 

### RESTful API design in http, of articles

The RESTful url match here shall look like: 
```
POST /article 				# create article by post a json, get back article id
GET  /article/<hash_id> 	# read article, get back a json-represented article.
PUT  /article/<hash_id> 	# update article parts, can update parts of article.
DELETE /article/<hash_id> 	# delete article, get back true or false.
```

Design in Details:
```
create an article
POST /article
request
{
	'article':{
		'title': 'My Awesome Title',
		'author': 'John Lenen',
		'html_body': '<html><p></p></html>',
		'tags':['work','travel',],
		'language_tags':['english','chinese',],
	}
	
}
response
{
	'success' : true/false,
	'public_hash_id': 'abc123',
	'fail_reason' : 'A String...'
}

```

Get all the articles, by page and offset
```
GET /article?offset, amount, chrono
response:
{
	"count" : 10,
	"articles" : [
		{
			"public_hash_id": xxx,
			"last_touch_date_str": xxx,
			"author":xxx,
			"title":xxx,
			"tags" : [],
		},
		{
			...
		}
		
	]
}
```

```
get an article
GET  /article/<hash_id>
response
{
	'success' : true/false,
	'fail_reason' : 'a string'
	'article':{
		"author": "Tom John",
	    "html_body": "<p>good</p>",
	    "language_tags": [
	      "english",
	      "chinese"
	    ],
	    "last_touch_date_str": "2016/04/25 00:13:20",
	    "public_hash_id": "1be6df08ea5fcff522f02807aa5fe336",
	    "tags": [
	      "work",
	      "travel"
	    ],
	    "title": "Good title"
	},
}
```

```
update an article
PUT  /article/<hash_id>
request: # these fields can be optional, but the other fileds will be omitted by server.
{
	'article':{
		'title': 'My Awesome Title',
		'author': 'John Lenen',
		'html_body': '<html><p></p></html>',
		'tags':['work','travel',],
		'language_tags':['english','chinese',],
	}
	
}

response
{
	'success' : true/false,
}

```

```
delete an article
DELETE /article/<hash_id>
response
{
	'success' : true/false,
}

```

### RESTful API design in http, of tags, languages, and search articles by tags, languages

List all the tags
```
GET /tags
response
{
	"count" : 10,
	"tags" : ["work","play",]
}
```

List all the languages
```
GET /language_tags
response
{
	"count" : 10,
	"tags" : ["chinese","japanese",]
}
```

List all the articles with a tag, language_tag or both
```
GET /search_article?tag=xxx&language_tag=xxx
response

{
	"count" : 10,
	"articles" : [
		{
			"public_hash_id": xxx,
			"last_touch_date_str": xxx,
			"author":xxx,
			"title":xxx,
			"tags" : [],
		},
		{
			...
		}
		
	]
}
```