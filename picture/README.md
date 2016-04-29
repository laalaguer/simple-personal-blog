## Picture related GAE processing and store
### Folder structure
`db.py` the database, blobstore or NDB store

`handlers.py` the related web handlers to deal around database, CRUD operations via http
### Design of API and datastructure

see [Design Document](./DESIGN.md)

### A blog site, a shopping site, not a Dropbox
So this question is easy to answer. The images user upload maybe 3.4Mb but we can only serve the readers
800 per picture for network performance. Either we do it on the clientside in javascript or server side via python.
But, we are not going to keep the original 3.4Mb file as user have uploaded, only the transformed light-weight picture.

However the `file` api of blobstore is deprecated, so it becomes a bit messy how to store your thumbnails back into datastore.

Solution is: we upload a blob, then put it on a "pre-process" list. We get to a background jobs. We transform it into 2-3 types of thumbnails. Use a `urlfetch()` method to store thumbnails again into blob store. reuturn the thumbnail keys. Then we get back to remove original blobs that user uploaded.

### Another question about thumbnails
Google suggest: to use the get `get_serving_url()` on the fly to generate different size of thumbnails.
Doing so have two problems:

1. Doing it over and over again on daily-use images can make you hit the quota limit of Image API. (eg.User profile pic)

2. You have to store the original pic as all thumbnails are generated from it. Its a waste of storage. As the usual 10M image on the 1600px scale is only 130k, almost 100 times the storage space.

### Discuss: A question about blobstore, blobkey and user behavior

You can notice that, without the blob key, you cannot fetch the blob from store.
So without the blob key, you are going to have no clue about where it is.
As nowadays user prefers to upload the pic, then input some dates and comments about it,

So we have two choices, one is upload the picture alongside the descriptions, this is 
what I called "one-time" uploading. You should think carefully about what info shall 
comes along with the picture(s) and the datastructure shall never change after that.
As the "descriptions+blobs" inside one structure, you have hold the path to the blobs.

As a result, the user shall provide the information all at once when uploading.
Pros: The client side html is simple, just a form.
Cons: The blobs are "private" to each item. You have no way to access it outside the item.

The second choice is uploading the picture(s) and actually return the blob keys via json.
Then the client side javascript application record those blobkeys.
When the user finishes the description(s) as key information of blob, we store the item back in database.
But this again create a risk that the picture maybe orphaned. How do we track it?
And the user input maybe malicious.
Maybe we shall check with the content-type when uploading?
User can provide nothing as the information when uploadin pictures.
The clientside js is a bit complicated.
Pros: The blob is "public" to inside the whole application.
Cons: But we may lose track to each and every blob that we have uploaded.
Solution: we may need to keep a record of "uploaded blobs" and, further more, split the record
into records so we have a improved performance.


### File processing speed:
The `image` library if faster than `get_serviing_url()` when we transform images, I made a speed test below.
Check out the code in `handlers.py` file and starting from line `120`. The speed is almost 2x speed. And sometimes the `get_serving_url()` is unstable, the return time not sure.

####Local machine:
transform using `get_serving_url()`:
* 9.2MB = 9.2 (s)
* 9.6MB = 8.9 (s)
* 10 MB = 12  (s)

using internal `image` library to transform:
* 9.2MB = 3.5 (s)
* 9.6MB = 3.4 (s)
* 10 MB = 4.0 (s)

####GAE Machine:
transform using `get_serving_url()`:
* 350kb = 0.66 (s)
* 500kb = 0.46 (s)
* 700kb = 1.13 (s)
* 3.0MB = 0.59 (s)
* 5.8MB = 1.16 (s)
* 6.9MB = 0.73 (s)
* 9.2MB = 1.26 (s)
* 9.6MB = 1.03 (s)
* 10 MB = 0.71 (s)

using internal `image` library to transform:
* 350kb = 0.24 (s)
* 500kb = 0.27 (s)
* 700kb = 0.26 (s)
* 3.0MB = 0.49 (s)
* 5.8MB = 0.53 (s)
* 6.9MB = 0.54 (s)
* 9.2MB = 0.62 (s)
* 9.6MB = 0.71 (s)
* 10 MB = 0.61 (s)