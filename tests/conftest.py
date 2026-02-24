import sys
import sqlalchemy.types as sqltypes
from types import ModuleType

# Patch for SQLAlchemy > 2.0 on Python 3.12 causing metaclass conflict in sqlite dialect
# We inject a fake sqlalchemy.dialects.sqlite.json module to bypass the broken one.

try:
    import sqlalchemy.dialects.sqlite.json
except (TypeError, ImportError):
    # Only patch if it fails or hasn't been imported yet
    if 'sqlalchemy.dialects.sqlite.json' not in sys.modules:
        mock_json_mod = ModuleType('sqlalchemy.dialects.sqlite.json')

        # Define _FormatTypeMixin dummy
        class _FormatTypeMixin(object):
            def _format_value(self, value):
                return value
            def bind_processor(self, dialect):
                return None
            def literal_processor(self, dialect):
                return None

        # Define JSON class that mimics sqlite.JSON but safely
        class JSON(sqltypes.JSON):
            pass

        # Define JSONIndexType that mimics sqlite.JSONIndexType but safely
        # We inherit from sqltypes.JSON.JSONIndexType to be compatible with whatever expected checks
        # But we don't mix in the problematic Mixin if it causes conflict.
        # Actually, here we just define it simply.
        class JSONIndexType(sqltypes.JSON.JSONIndexType):
            pass

        mock_json_mod.JSON = JSON
        mock_json_mod.JSONIndexType = JSONIndexType
        mock_json_mod._FormatTypeMixin = _FormatTypeMixin

        # Inject into sys.modules
        sys.modules['sqlalchemy.dialects.sqlite.json'] = mock_json_mod
