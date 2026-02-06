from models import db

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Permission {self.code}>'
