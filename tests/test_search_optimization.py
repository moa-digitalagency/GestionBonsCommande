import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Set dummy environment variable for Config
os.environ['SESSION_SECRET'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Mock models and db before importing routes
sys.modules['models'] = MagicMock()
sys.modules['models.product'] = MagicMock()
sys.modules['models.company'] = MagicMock()
sys.modules['services.tenant_service'] = MagicMock()
sys.modules['security.decorators'] = MagicMock()
sys.modules['flask_login'] = MagicMock()
# Mock sqlalchemy
sys.modules['sqlalchemy'] = MagicMock()

from config.settings import Config

# Mock Product model
class MockProductModel:
    reference = MagicMock()
    labels = MagicMock()
    # Return a Mock object, not a string, so it mimics an expression
    reference.ilike = MagicMock(return_value=MagicMock(name='reference_ilike_expr'))

    class LabelsCol:
        def __getitem__(self, key):
            item = MagicMock()
            item.astext.ilike = MagicMock(return_value=MagicMock(name=f'labels_{key}_ilike_expr'))
            return item
    labels = LabelsCol()

sys.modules['models.product'].Product = MockProductModel
sys.modules['services.tenant_service'].TenantService = MagicMock()

def mock_decorator(f):
    return f
sys.modules['security.decorators'].tenant_required = mock_decorator
sys.modules['security.decorators'].admin_required = mock_decorator
sys.modules['flask_login'].login_required = mock_decorator

# Import the module under test
import routes.products as products_module

class TestSearchOptimization(unittest.TestCase):
    def setUp(self):
        self.mock_tenant_service = products_module.TenantService
        self.mock_product = products_module.Product

    def test_search_optimization_query_construction(self):
        # Manually patch request and jsonify
        original_request = products_module.request
        original_jsonify = products_module.jsonify

        mock_request = MagicMock()
        mock_jsonify = MagicMock()

        products_module.request = mock_request
        products_module.jsonify = mock_jsonify

        try:
            # Setup
            mock_request.args.get.return_value = 'hammer'

            mock_query = MagicMock()
            self.mock_tenant_service.get_tenant_products.return_value = mock_query

            mock_filter_result = MagicMock()
            mock_query.filter.return_value = mock_filter_result

            mock_limit_result = MagicMock()
            mock_filter_result.limit.return_value = mock_limit_result

            mock_limit_result.all.return_value = []

            # Act
            products_module.search()

            # Assert

            # 1. Verify get_tenant_products called
            self.mock_tenant_service.get_tenant_products.assert_called_once()

            # 2. Verify .all() was NOT called on the base query
            mock_query.all.assert_not_called()

            # 3. Verify filter was called
            mock_query.filter.assert_called_once()

            # 5. Verify limit called
            mock_filter_result.limit.assert_called_with(20)

            # 6. Verify .all() called on limited result
            mock_limit_result.all.assert_called_once()

        finally:
            products_module.request = original_request
            products_module.jsonify = original_jsonify

if __name__ == '__main__':
    unittest.main()
