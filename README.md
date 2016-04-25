# Simple Personal Blog on GAE
A personal blog, sits on the Google App Engine and `webapp2` framework

## Design Goal
1. Site contains images, text articles, weblinks and files(like pdf).
2. Internet browsers are free to visit. No user account system.
3. A single Admin to update articles, upload pictures and upload files. No body else is allowed to upload.
4. All the articles on the web site can either be public, or private to admin.

## Website Appearance (to visitors)
1. Front page: title, navbar (blogs, pictures), search bar (search for tags inside blogs, pictures)
2. Front page: Slogan, subslogan, slogan photo
3. Front page: Two columns, Left is recent blogs, right is recent photos
4. Blogs page: title, navbar, like the front page
5. Blogs page: single column, a list of blogs title, author and dates, etc.
6. Pictures page: Instagram like photo wall.
7. Search page: if search for blog, then like 4 and 5 points.
8. Search page: if search for picture, then like 6 point.
9. Single Blog: a html page. right side bar, jump to blogs. Image on hover can create a big box.

## Website Appearance (to Admin)
1. Blog page editor: Edit as you see, the admin can save it to database.
2. Blog page editor: user can upload as many images as you like on the side bar.
3. Photo Wall editor: each item has a update and delete button. Add a string to the photo as message.
4. Photo Wall editor: upload as many photo you like as possible.

## Price of storage
1. Blobstore gives you a free quota of 5GB everyday. Exceeded? Then at $0.026 every month per GB.
2. In general, you won't need to worry about the storage and things.

## Future
1. Add some more templates to make the blog site look better.
