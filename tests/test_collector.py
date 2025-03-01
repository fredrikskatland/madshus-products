"""
Tests for the product collector.

This module contains tests for the product collector functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from madshus.collectors import ProductCollector
from madshus.models.product import Product


class TestProductCollector(unittest.TestCase):
    """
    Tests for the ProductCollector class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.db = MagicMock(spec=Session)
        self.collector = ProductCollector(self.db)
    
    @patch("madshus.collectors.product_collector.get_paginated_products")
    def test_collect_products(self, mock_get_paginated_products):
        """
        Test collecting products.
        """
        # Mock response from get_paginated_products
        mock_get_paginated_products.return_value = {
            "data": {
                "paginatedProductGrid": {
                    "products": [
                        {
                            "uid": "test-uid-1",
                            "title": "Test Product 1",
                            "display_title": "Test Product 1",
                            "url": "/test-product-1",
                        },
                        {
                            "uid": "test-uid-2",
                            "title": "Test Product 2",
                            "display_title": "Test Product 2",
                            "url": "/test-product-2",
                        },
                    ],
                    "total": 2,
                }
            }
        }
        
        # Mock collect_product method
        self.collector.collect_product = MagicMock(return_value="test-uid-1")
        
        # Call collect_products
        result = self.collector.collect_products(categories=[1])
        
        # Check that collect_product was called for each product
        self.assertEqual(self.collector.collect_product.call_count, 2)
        
        # Check that the result contains the collected UIDs
        self.assertEqual(result, ["test-uid-1", "test-uid-1"])
    
    @patch("madshus.collectors.product_collector.get_product")
    def test_collect_product(self, mock_get_product):
        """
        Test collecting a single product.
        """
        # Mock response from get_product
        mock_get_product.return_value = {
            "data": {
                "product": {
                    "uid": "test-uid",
                    "title": "Test Product",
                    "display_title": "Test Product",
                    "url": "/test-product",
                    "description": "Test description",
                    "tagline": "Test tagline",
                    "prices": {
                        "no": "100 NOK",
                    },
                    "updated_product_specs": [
                        {
                            "id": "test-spec",
                            "title": "Test Spec",
                            "value": "Test value",
                        }
                    ],
                    "details": {
                        "technology": {
                            "title": "Test Technology",
                            "content": "Test technology content",
                        },
                        "feature_details": [
                            {
                                "group_title": "Test Feature Group",
                                "group": [
                                    {
                                        "content": "Test feature content",
                                    }
                                ],
                            }
                        ],
                    },
                }
            }
        }
        
        # Mock database query
        self.db.query.return_value.filter.return_value.first.return_value = None
        
        # Call collect_product
        result = self.collector.collect_product("/test-product")
        
        # Check that the result is the product UID
        self.assertEqual(result, "test-uid")
        
        # Check that the product was added to the database
        self.db.add.assert_called()
        self.db.commit.assert_called()


if __name__ == "__main__":
    unittest.main()
