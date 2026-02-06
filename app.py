from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='statics', static_url_path='/static')
app.secret_key = 'super_secret_key_dev_mode'

# --- MOCK DATA ---

MOCK_STATS = {
    'orders_count': 12,
    'pending_count': 3,
    'projects_count': 5
}

MOCK_ORDERS = [
    {'id': 'CMD-2024-001', 'project': 'Résidence Al Manar', 'date': '12/10/2024', 'status': 'Validé'},
    {'id': 'CMD-2024-002', 'project': 'Villa Jasmine', 'date': '14/10/2024', 'status': 'Soumis'},
    {'id': 'CMD-2024-003', 'project': 'Complexe Sportif', 'date': '15/10/2024', 'status': 'Brouillon'},
    {'id': 'CMD-2024-004', 'project': 'Résidence Al Manar', 'date': '18/10/2024', 'status': 'Soumis'},
]

MOCK_PROJECTS = [
    {'name': 'Résidence Al Manar', 'city': 'Casablanca'},
    {'name': 'Villa Jasmine', 'city': 'Marrakech'},
    {'name': 'Complexe Sportif', 'city': 'Rabat'},
    {'name': 'Immeuble Hicham', 'city': 'Tanger'},
    {'name': 'École Primaire B', 'city': 'Fès'},
]

MOCK_LEXIQUE = [
    {'fr': 'Béton armé', 'ar': 'خرسانة مسلحة', 'darija': 'Béton armé', 'en': 'Reinforced concrete', 'category': 'Gros Œuvre'},
    {'fr': 'Grue à tour', 'ar': 'رافعة برجية', 'darija': 'Gru', 'en': 'Tower crane', 'category': 'Outillage'},
    {'fr': 'Maçonnerie', 'ar': 'بناء', 'darija': 'Bni', 'en': 'Masonry', 'category': 'Gros Œuvre'},
    {'fr': 'Peinture', 'ar': 'صباغة', 'darija': 'Sbigha', 'en': 'Painting', 'category': 'Second Œuvre'},
    {'fr': 'Carrelage', 'ar': 'تبليط', 'darija': 'Zellij', 'en': 'Tiling', 'category': 'Second Œuvre'},
]

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('dashboard.html',
                           stats=MOCK_STATS,
                           orders=MOCK_ORDERS,
                           projects=MOCK_PROJECTS)

@app.route('/commandes')
def commandes():
    # Placeholder: Reusing dashboard layout or specific view if requested.
    # For now, listing orders.
    return render_template('dashboard.html',
                           stats=MOCK_STATS,
                           orders=MOCK_ORDERS,
                           projects=MOCK_PROJECTS) # Or a dedicated list page

@app.route('/chantiers')
def chantiers():
    return render_template('dashboard.html',
                           stats=MOCK_STATS,
                           orders=MOCK_ORDERS,
                           projects=MOCK_PROJECTS)

@app.route('/articles')
def articles():
    return render_template('dashboard.html',
                           stats=MOCK_STATS,
                           orders=MOCK_ORDERS,
                           projects=MOCK_PROJECTS)

@app.route('/dictionnaire', methods=['GET', 'POST'])
def dictionnaire():
    if request.method == 'POST':
        new_term = {
            'fr': request.form.get('fr'),
            'ar': request.form.get('ar'),
            'darija': request.form.get('darija'),
            'en': request.form.get('en'),
            'category': request.form.get('category')
        }
        MOCK_LEXIQUE.insert(0, new_term) # Add to top
        return redirect(url_for('dictionnaire'))
    
    return render_template('dictionnaire.html', lexique_entries=MOCK_LEXIQUE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
