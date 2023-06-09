import pytest
from app import app, db, Certificate, Group


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.create_all()
    with app.test_client() as client:
        yield client
    db.session.remove()
    db.drop_all()


def test_create_certificate(client):
    data = {
        "username": "user1",
        "name": "certificate1",
        "description": "This is a test certificate",
        "expiration": 365,
        "groups": []
    }
    response = client.post('/certificados', json=data)
    assert response.status_code == 201
    certificate = Certificate.query.filter_by(username=data['username']).first()
    assert certificate is not None
    assert certificate.username == data['username']
    assert certificate.name == data['name']
    assert certificate.description == data['description']
    assert certificate.expiration == data['expiration']


def test_list_certificates(client):
    certificate1 = Certificate(
        username="user1",
        name="certificate1",
        description="This is a test certificate",
        expiration=365
    )
    certificate2 = Certificate(
        username="user2",
        name="certificate2",
        description="This is another test certificate",
        expiration=30
    )
    db.session.add(certificate1)
    db.session.add(certificate2)
    db.session.commit()
    response = client.get('/certificados')
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['username'] == certificate1.username
    assert response.json[1]['username'] == certificate2.username


def test_create_group(client):
    data = {
        "name": "group1",
        "description": "This is a test group"
    }
    response = client.post('/grupos', json=data)
    assert response.status_code == 201
    group = Group.query.filter_by(name=data['name']).first()
    assert group is not None
    assert group.name == data['name']
    assert group.description == data['description']


def test_list_groups(client):
    group1 = Group(
        name="group1",
        description="This is a test group"
    )
    group2 = Group(
        name="group2",
        description="This is another test group"
    )
    db.session.add(group1)
    db.session.add(group2)
    db.session.commit()
    response = client.get('/grupos')
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['name'] == group1.name
    assert response.json[1]['name'] == group2.name


def test_certificate_expiration(client):
    data = {
        "username": "user1",
        "name": "certificate1",
        "description": "This is a test certificate",
        "expiration": 365,
        "groups": []
    }
    response = client.post('/certificados', json=data)
    assert response.status_code == 201
    certificate = Certificate.query.filter_by(username=data['username']).first()
    assert certificate is not None
    assert certificate.expirated_at is not None


