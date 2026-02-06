from models import db

# Association table for Many-to-Many relationship between Role and Permission
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), default='blue') # e.g., 'blue', 'red', 'green'

    # Relationship to permissions
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery',
        backref=db.backref('roles', lazy=True))

    # Relationship to users
    users = db.relationship('User', backref='user_role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'
