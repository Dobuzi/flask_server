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
git clone git@github.com:Dobuzi/flask_server.git
cd flask_server
python3 -m venv venv
source venv/bin/activate # windows: who use the windows for server?!
pip install -r requirements.txt
venv/bin/flask --app flaskr init-db
```

### Dev

```
venv/bin/flask --app flaskr --debug run
# connect the http://127.0.0.1:5000 via browser
```

### Production

```
waitress-serve --call 'flaskr:create_app'
```

---

## Reference
> [Flask Server](https://flask.palletsprojects.com/en/2.2.x/tutorial)
