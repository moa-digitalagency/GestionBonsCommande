from app import create_app, db
from models.company import Company
from models.user import User
from models.project import Project
from models.product import Product
from models.lexique import LexiqueEntry
from datetime import datetime

app = create_app()

with app.app_context():
    db.create_all()

    # 1. Create Company
    if not Company.query.filter_by(name="BTP Construction SA").first():
        company = Company(
            name="BTP Construction SA",
            ice="123456789",
            city="Casablanca",
            is_active=True,
            default_language='fr',
            currency='MAD',
            settings={'numbering': {'prefix': 'CMD', 'year_format': 'YYYY', 'sequence_length': 4}}
        )
        db.session.add(company)
        db.session.commit()
        print(f"Created Company: {company.name}")
    else:
        company = Company.query.filter_by(name="BTP Construction SA").first()

    # 2. Create Admin User
    if not User.query.filter_by(email="admin@btp.ma").first():
        admin = User(
            email="admin@btp.ma",
            first_name="Admin",
            last_name="BTP",
            role="admin",
            company_id=company.id,
            is_active=True
        )
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()
        print(f"Created User: {admin.email}")

    # 3. Create Super Admin User
    if not User.query.filter_by(email="admin@btpcommande.ma").first():
        super_admin = User(
            email="admin@btpcommande.ma",
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_active=True
        )
        super_admin.set_password("admin123")
        db.session.add(super_admin)
        db.session.commit()
        print(f"Created Super Admin: {super_admin.email}")

    # 4. Create Project
    if not Project.query.filter_by(code="PRJ-001").first():
        project = Project(
            name="Résidence Les Fleurs",
            code="PRJ-001",
            company_id=company.id,
            city="Rabat",
            address="Av. Mohammed VI",
            contact_name="Ahmed Chef",
            is_active=True
        )
        db.session.add(project)
        db.session.commit()
        print(f"Created Project: {project.name}")

    # 5. Create Products
    if not Product.query.first():
        p1 = Product(company_id=company.id, reference="CIM001", category="materiau", unit="sac", unit_price=65.00, labels={'fr': 'Ciment CPJ 45'})
        p2 = Product(company_id=company.id, reference="SAB001", category="materiau", unit="m3", unit_price=200.00, labels={'fr': 'Sable de rivière'})
        p3 = Product(company_id=company.id, reference="PEL001", category="materiel", unit="jour", unit_price=1500.00, labels={'fr': 'Pelle Hydraulique'})
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        print("Created Demo Products")

    print("Demo Data Setup Complete.")
