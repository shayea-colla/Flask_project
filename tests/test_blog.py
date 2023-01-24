import pytest 
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b'Log In' in response.data
    assert b'Register' in response.data
    
    auth.login()
    response = client.get('/')
    assert b'Log out' in response.data
    assert b'New' in response.data
    assert b'test title' in response.data
    assert b'by test ' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data
    
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/2/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'auth/login'

def test_author_required(client, app, auth ):
    # change the post author to another use
    with app.app_context():
        db = get_db()
        db.execute(
            "UPDATE post SET author_id = 2 WHERE id = 1"
        )
        db.commit()
        
        auth.login()
        # Current user can't modify other's post
        assert client.post('/1/update').status_code == 403
        assert client.post('/1/delete').status_code == 403
        # Current user can't see the edit link on the index page
        assert b'href="/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', 
        '/2/update',
        '/2/delete'
)
def test_exist_required(client, auth, path):
    auth.login()
    assert client.post(path).satuse_code == 404
    
def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title':'no way', 'body':'home'})
    
    
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post')
        assert count == 2
        
def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title':'so you', 'body':'boot'})
    
    with app.app_context():
        db = get_db()
        result = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert 'so you' == result['title']
        assert 'boot' == result['body']
        
@pytest.mark.parametrize('path',
        '/create',
        '/1/update',
)
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, date={'title': '', 'body':'test'})
    assert b'Title is required' in response.data
    
    
def test_delete(client, auth, app):
    auth.login()
    respones = client.post('/1/delete')
    assert respones.headers['Location'] == '/'
    with app.app_context():
        db = get_db()
        result = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert result == None
        