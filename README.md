# flask_server

Web Server with Flask

## Check List

- [X] Make the basic frame.
- [X] Implement the **CRUD** system.
- [X] Package the app.
- [X] Test the app
- [X] Deploy the app.

## The way to use

```
$ git clone git@github.com:Dobuzi/flask_server.git
$ cd flask_server
$ python3 -m venv venv
$ source venv/bin/activate # windows: venv\Scripts\activate.bat
$ pip install -r requirements.txt
$ venv/bin/flask --app flaskr init-db
```

### Test
```
$ pytest
$ coverage run -m pytest
$ coverage report
$ coverage html
$ open htmlcov/index.html
```


### Dev

```
$ venv/bin/flask --app flaskr --debug run
$ open http://127.0.0.1:5000
# check the browser opened!
```

### Production

```
$ waitress-serve --call 'flaskr:create_app'
$ open http://0.0.0.0:8080
# check the browser opened!
```

---

## To Do List

- [ ] Detail View: Enter by clicking the post title
- [ ] Like/Unlike a post
- [ ] Comments
- [ ] Tags: Clicking a tag shows all the posts with that tag
- [ ] Search box : Filtering the index page by name
- [ ] Paged display. Only show 5 posts per page
- [ ] Upload an image to go along with a post.
- [ ] Format posts using Markdown
- [ ] An RSS feed of new posts

---

## Reference
> [Flask Server](https://flask.palletsprojects.com/en/2.2.x/tutorial)
