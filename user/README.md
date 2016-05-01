### Folder Structure

`db.py` Where you store the allowed collaborate authors to your blog site

`handlers.py` where all web handlers stay. The `BaseHandler` is the most important one. Its the fundation class of all the handlers if you wish to use Google Account as your site's login provider.

Check out the `user_app.py` in the toppest root directory to see how to use this handler.