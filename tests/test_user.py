from testcontainers.postgres import PostgresContainer
import psycopg2
import pytest
from fastapi.testclient import TestClient
import models
from app import make_app


@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:16", driver=None) as postgres:
        with psycopg2.connect(postgres.get_connection_url()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("create table if not exists user_app (id serial primary key, name text constraint namechk check(char_length(name)<=50),avatar_url text constraint avatar_urlchk check(char_length(avatar_url)<=255));")
                cursor.execute("create table if not exists user_credential (user_id integer REFERENCES user_app, login text unique constraint loginchk check(char_length(login)<=50), password text constraint passwchk check(char_length(password)<=255), salt text constraint saltchk check(char_length(salt)<=255));")
                connection.commit()
        yield postgres


@pytest.fixture(scope="function")
def connection(postgres):
    with psycopg2.connect(postgres.get_connection_url()) as connection:
        yield connection


@pytest.fixture(scope="function")
def client(postgres):
    pool = psycopg2.pool.SimpleConnectionPool(2, 3, user=postgres.username, password=postgres.password, 
                                          host='localhost', port=postgres.get_exposed_port(postgres.port), database=postgres.dbname)
    app = make_app(pool)
    client = TestClient(app)
    yield client


@pytest.fixture(scope="function", autouse=True)
def clean_db(connection):
    yield
    with connection.cursor() as cursor:
        cursor.execute("delete from user_credential;")
        cursor.execute("delete from user_app;")
        connection.commit()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == "health OK"
    

user_auth = models.UserAuth(name='bobob', login='bobob', password='12345', avatar_url='some_url')
user_login = models.UserLogin(login=user_auth.login, password=user_auth.password)


def test_create_user_correct(client):
                response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                            "password":user_auth.password, "avatar_url":user_auth.avatar_url})
                assert response.status_code == 200


def test_create_user_invalid_name(client):
                response = client.post('/api/v1/users', json={"name":user_auth.name[:4], "login":user_auth.login, 
                                                            "password":user_auth.password, "avatar_url":user_auth.avatar_url})
                assert response.status_code == 422


def test_create_user_invalid_login(client):
    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":'1'+user_auth.login, 
                                                  "password":user_auth.password, "avatar_url":user_auth.avatar_url})
    assert response.status_code == 422


def test_create_user_invalid_password(client):
    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                  "password":user_auth.password+'@#$', "avatar_url":user_auth.avatar_url})
    assert response.status_code == 422


def test_login_correct(client):
    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                  "password":user_auth.password, "avatar_url":user_auth.avatar_url})
    assert response.status_code == 200
    user_id = int(response.json())

    response = client.post("/api/v1/auth", json={"login":user_login.login,"password":user_login.password})
    assert response.status_code == 200


def test_login_invalid_login(client):
    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                  "password":user_auth.password, "avatar_url":user_auth.avatar_url})
    assert response.status_code == 200

    response = client.post("/api/v1/auth", json={"login":user_login.login+'ooo',"password":user_login.password})
    assert response.status_code == 401


def test_login_invalid_password(client):
    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                  "password":user_auth.password, "avatar_url":user_auth.avatar_url})
    assert response.status_code == 200

    response = client.post("/api/v1/auth", json={"login":user_login.login,"password":user_login.password+'aaa'})
    assert response.status_code == 401


def test_get_info_correct(client):

    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                  "password":user_auth.password, "avatar_url":user_auth.avatar_url})
    assert response.status_code == 200
    user_id = int(response.json())

    response = client.post("/api/v1/auth", json={"login":user_login.login,"password":user_login.password})
    assert response.status_code == 200
    token = response.json()

    response = client.get("/api/v1/users",params={"user_id":user_id}, headers={'Authorization':token})
    assert response.status_code == 200


def test_get_info_wrond_user_id(client):

    response = client.post('/api/v1/users', json={"name":user_auth.name, "login":user_auth.login, 
                                                  "password":user_auth.password, "avatar_url":user_auth.avatar_url})
    assert response.status_code == 200
    user_id = int(response.json())

    response = client.post("/api/v1/auth", json={"login":user_login.login,"password":user_login.password})
    assert response.status_code == 200
    token = response.json()

    response = client.get("/api/v1/users",params={"user_id":user_id-1}, headers={'Authorization':token})
    assert response.status_code == 401
