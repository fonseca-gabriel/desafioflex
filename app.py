from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, ValidationError
from marshmallow.validate import Length, And, Regexp, Range
from flask_migrate import Migrate


# mysql ou sqlite3
database = 'sqlite3'

# local ou docker
mysql_host = 'docker'

app = Flask(__name__)

if database == "sqlite3":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certificates.sqlite3'
    db = SQLAlchemy(app)
    app.app_context().push()
    db.create_all()
elif database == "mysql":
    if mysql_host == 'local':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://gabriel:senha@127.0.0.1:3306/desafioflex'
    elif mysql_host == 'docker':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://gabriel:senha@db:3306/desafioflex'
    db = SQLAlchemy(app)
    app.app_context().push()

migrate = Migrate(app, db)  # sql-migrate


cartificate_group = db.Table(
    'certificate_group',
    db.Column('certificate_id', db.Integer, db.ForeignKey('certificates.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)


# Models
class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(255), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)
    expiration = db.Column(db.Integer, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    expirated_at = db.Column(db.DateTime(timezone=True))
    groups = db.relationship('Group', secondary=cartificate_group, backref=db.backref('certificados', lazy='dynamic'))

    def __repr__(self):
        return f"<cert: {self.username}>"


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# Marshmallow schemas
class GroupSchema(Schema):

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    name = fields.String(required=True, validate=Length(max=30))
    description = fields.String(required=True, validate=Length(max=255))

    class Meta:
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')


class CertificateSchema(Schema):

    def dump_groups_ids(self, value):
        return [group.id for group in value.groups]

    def load_groups_ids(self, value):
        return list(value)

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    expirated_at = fields.DateTime()
    username = fields.Str(required=True, validate=And(Length(max=30), Regexp(regex=r'^[a-zA-Z0-9]+$')))
    name = fields.Str(required=True, validate=Length(max=255))
    expiration = fields.Integer(required=True, validate=Range(10, 3650))
    groups = fields.Method("dump_groups_ids", "load_groups_ids")

    class Meta:
        fields = (
            'id',
            'username',
            'name',
            'description',
            'expiration',
            'expiration',
            'created_at',
            'updated_at',
            'expirated_at',
            'groups'
        )


def define_expirated_at(expiration):
    return datetime.utcnow() + timedelta(days=int(expiration))


# Rotas/endpoints
@app.route('/certificados', methods=['GET'])
def list_certificates():

    sort_param = request.args.get('sort')
    filter_name_param = request.args.get('name')
    filter_username_param = request.args.get('username')
    certificates_query = Certificate.query

    # Filter
    if filter_name_param:
        certificates_query = certificates_query.filter(Certificate.name.ilike(f'%{filter_name_param}%'))

    if filter_username_param:
        certificates_query = certificates_query.filter(Certificate.username.ilike(f'%{filter_username_param}%'))

    # Sort
    if sort_param == 'username':
        certificates_query = certificates_query.order_by(Certificate.username.asc())

    if sort_param == 'name':
        certificates_query = certificates_query.order_by(Certificate.name.asc())

    certificates = certificates_query.all()
    certificates_serialized = CertificateSchema(many=True).dump(certificates)

    return jsonify(certificates_serialized)


@app.route('/grupos', methods=['GET'])
def list_groups():
    groups = Group.query.all()
    groups_serialized = GroupSchema(many=True).dump(groups)
    return jsonify(groups_serialized), 200


@app.route('/certificados', methods=['POST'])
def create_certificate():
    with app.app_context():

        try:
            certificate_data = CertificateSchema().load(request.json)
        except ValidationError as err:
            return make_response(jsonify(err.messages), 400)

        if Certificate.query.filter_by(username=certificate_data['username']).first():
            return make_response(jsonify({'message': 'username already exists.'}), 400)

        group_ids = [int(group_id) for group_id in certificate_data['groups']]
        groups = Group.query.filter(Group.id.in_(group_ids)).all()

        certificate = Certificate(
            name=certificate_data['name'],
            username=certificate_data['username'],
            description=certificate_data['description'],
            expiration=certificate_data['expiration'],
            expirated_at=define_expirated_at(certificate_data['expiration']),
            groups=groups
        )

        db.session.add(certificate)
        db.session.commit()

        certificate_serialized = CertificateSchema().dump(certificate)
        return jsonify(certificate_serialized), 201


@app.route('/grupos', methods=['POST'])
def create_group():
    with app.app_context():
        try:
            group_data = GroupSchema().load(request.json)
        except ValidationError as err:
            return jsonify(err.messages), 400

        if Group.query.filter_by(name=group_data['name']).first():
            return make_response(jsonify({'message': 'group already exists.'}), 400)

        group = Group(**group_data)
        db.session.add(group)
        db.session.commit()

        group_serialized = GroupSchema().dump(group)
        return jsonify(group_serialized), 201


@app.route('/certificados/<int:cert_id>', methods=['GET'])
def get_certificate(cert_id):
    try:
        certificate = db.session.get(Certificate, cert_id)

        if certificate:
            certificate_serialized = CertificateSchema(many=False).dump(certificate)
            return jsonify(certificate_serialized), 200
        return make_response(jsonify({'message': 'certificate not found'}), 404)

    except Exception as err:
        print(f"Get by ID error: {err}")
        return make_response(jsonify({'message': 'error getting certificate'}), 500)


@app.route('/grupos/<int:group_id>', methods=['GET'])
def get_group(group_id):
    try:
        group = db.session.get(Group, group_id)

        if group:
            group_serialized = GroupSchema(many=False).dump(group)
            return jsonify(group_serialized), 200

        return make_response(jsonify({'message': 'group not found'}), 404)

    except Exception as err:
        print(f"Get by ID error: {err}")
        return make_response(jsonify({'message': 'error getting group'}), 500)


@app.route('/certificados/<int:cert_id>', methods=['PUT'])
def update_certificate(cert_id):
    try:
        certificate = db.session.get(Certificate, cert_id)

        if certificate:

            data = request.json

            try:
                CertificateSchema(partial=True).load(data)

            except ValidationError as err:
                return make_response(jsonify(err.messages), 400)

            # Verificar se deve permitir a troca do username
            if Certificate.query.filter_by(username=data['username']).first():
                return make_response(jsonify({'message': 'username already exists.'}), 400)

            certificate.username = data['username']
            certificate.name = data['name']
            certificate.description = data['description']

            groups = request.json['groups']
            certificate.groups = Group.query.filter(Group.id.in_(groups)).all()

            db.session.commit()

            return make_response(jsonify({'message': 'certificate updated'}), 200)
        return make_response(jsonify({'message': 'certificate not found'}), 404)

    except Exception as err:
        print(f"Update error: {err}")
        return make_response(jsonify({'message': 'error updating certificate'}), 500)


@app.route('/grupos/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    try:
        group = db.session.get(Group, group_id)

        if group:

            data = request.json

            try:
                GroupSchema(partial=True).load(data)

            except ValidationError as err:
                return make_response(jsonify(err.messages), 400)

            # Verifica se o grupo já existe
            if Group.query.filter_by(name=data.get('name')).first():
                return make_response(jsonify({'message': 'group already exists.'}), 400)

            if data.get('name'):
                group.name = data.get('name')

            if data.get('description'):
                group.description = data.get('description')

            db.session.commit()
            return make_response(jsonify({'message': 'group updated'}), 200)

        return make_response(jsonify({'message': 'group not found'}), 404)

    except Exception as err:
        print(f"Update error: {err}")
        return make_response(jsonify({'message': 'error updating group'}), 500)


@app.route('/certificados/<int:cert_id>', methods=['DELETE'])
def delete_certificate(cert_id):
    try:
        certificate = db.session.get(Certificate, cert_id)
        if certificate:
            db.session.delete(certificate)
            db.session.commit()
            return make_response(jsonify({'message': 'certificate deleted'}), 200)
        return make_response(jsonify({'message': 'certificate not found'}), 404)
    except Exception as err:
        print(f"Delete error: {err}")
        return make_response(jsonify({'message': 'error deleting certificate'}), 500)


@app.route('/grupos/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    try:
        group = db.session.get(Group, group_id)
        if group:
            db.session.delete(group)
            db.session.commit()
            return make_response(jsonify({'message': 'group deleted'}), 200)
        return make_response(jsonify({'message': 'group not found'}), 404)
    except Exception as err:
        print(f"Delete error: {err}")
        return make_response(jsonify({'message': 'error deleting group'}), 500)


if __name__ == "__main__":
    app.run(debug=True)
