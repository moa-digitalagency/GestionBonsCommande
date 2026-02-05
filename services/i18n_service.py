import json
import os
from flask import request, session, current_app
from config.settings import Config

class I18nService:
    def __init__(self, app=None):
        self._translations = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.load_translations(app)

        # Inject into Jinja
        app.jinja_env.globals['get_locale'] = self.get_locale
        app.jinja_env.globals['_'] = self.translate

    def load_translations(self, app):
        # We assume 'translations' folder is at the same level as app.py (root)
        # app.root_path usually points to the folder containing the app module.
        # If app.py is in root, app.root_path is root.
        base_path = os.path.join(app.root_path, 'translations')

        for lang in Config.SUPPORTED_LANGUAGES:
            file_path = os.path.join(base_path, f'{lang}.json')
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._translations[lang] = json.load(f)
                else:
                    self._translations[lang] = {}
                    print(f"Warning: Translation file not found: {file_path}")
            except Exception as e:
                print(f"Error loading translation for {lang}: {e}")
                self._translations[lang] = {}

    def get_locale(self):
        if 'lang' in session:
            return session['lang']
        return request.accept_languages.best_match(Config.SUPPORTED_LANGUAGES) or Config.DEFAULT_LANGUAGE

    def translate(self, key):
        locale = self.get_locale()

        # 1. Try target locale
        if locale in self._translations and key in self._translations[locale]:
            return self._translations[locale][key]

        # 2. Try default locale (if different)
        default_lang = Config.DEFAULT_LANGUAGE
        if locale != default_lang and default_lang in self._translations and key in self._translations[default_lang]:
             return self._translations[default_lang][key]

        # 3. Return key
        return key

i18n = I18nService()
