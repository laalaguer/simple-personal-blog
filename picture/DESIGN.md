# WEB API Restful for `picture` module
This is a after think about the difficulties in reality in Google app engine. But we still need to get out a design documentation for the standard, ideal blog `picture` module. Regardless of the platform or backend we are using.

### Work Flow
1. A User uploads a bunch of pictures. For each of the picture, we generate some thumbnails to store on the server. And this collection of thumbnails, belongs to a single object and has a description, a date and a privacy trigger called 'public' - if he/she wishes to let the public view it.

2. A User can upload a picture without description at first, and then update the privacy and description about it.

3. A User can delete the image on the server.

### API
User Create an image object
```
POST /pre_receive
file: an image file
Response as json object
{
	'public_hash_id': xxx,
	'process_time' : 3.6, # in seconds
    'stored':[
        {'blob_key': xxxx, 'filename': xxx,},
        {'blob_key': xxxx, 'filename': xxx,},
        ...
    ]
}
```

User delete an image object
```
DELETE GET /delete_by_hash/<public_hash_id>
Response as json object (always success if no server error pops)
{
	'success': true/false,
	'fail_reason': 'xxxx',
}
```

User update an image object with description or publicity
```
POST /update_description/<public_hash_id>
Request as ordinary post
{
	description: '',
	public: true/false,
}

Response as json object (always success if no server error pops)
{
	'success': true/false,
	'fail_reason': 'xxxx',
}

```

User get an image object by hash id
```
GET /get_by_hash/<public_hash_id>
Response as json object
{
	'pictures': [
		{
			'public_hash_id': xxx,
			'blob_256': xxx,
			'blob_512': xxx,
			'blob_800': xxx,
			'blob_1600': xxx,
			'descriptions' : xxx,
			'tags':[x,x,x],
		},
		... another picture object
	]
}
```

User get an image list by time (default) or by tag
```
GET /list?tag=xxx&offset=xxx&amount=xxx
Response as json object
{
	'pictures': [
		{
			'public_hash_id': xxx,
			'blob_256': xxx,
			'blob_512': xxx,
			'blob_800': xxx,
			'blob_1600': xxx,
			'descriptions' : xxx,
			'tags':[x,x,x],
		},
		... another picture object
	]
}

```