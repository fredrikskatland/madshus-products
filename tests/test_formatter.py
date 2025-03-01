"""
Tests for the product formatter.

This module contains tests for the product formatter functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from madshus.formatters import ProductFormatter
from madshus.models.product import (
    Product,
    ProductFeature,
    ProductPrice,
    ProductSpec,
    ProductTechnology,
)


class TestProductFormatter(unittest.TestCase):
    """
    Tests for the ProductFormatter class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.db = MagicMock(spec=Session)
        self.formatter = ProductFormatter(self.db)
        
        # Create a test product
        self.product = Product(
            uid="test-uid",
            title="Test Product",
            display_title="Test Product Display",
            url="/test-product",
            description="Test description",
            tagline="Test tagline",
        )
        
        # Create test specifications
        self.specs = [
            ProductSpec(
                product_uid="test-uid",
                spec_id="test-spec-1",
                title="Test Spec 1",
                value="Test value 1",
            ),
            ProductSpec(
                product_uid="test-uid",
                spec_id="test-spec-2",
                title="Test Spec 2",
                value="Test value 2",
            ),
        ]
        
        # Create test prices
        self.prices = [
            ProductPrice(
                product_uid="test-uid",
                region="no",
                price="100 NOK",
            ),
            ProductPrice(
                product_uid="test-uid",
                region="se",
                price="100 SEK",
            ),
        ]
        
        # Create test technologies
        self.technologies = [
            ProductTechnology(
                product_uid="test-uid",
                title="Test Technology 1",
                content="Test technology content 1",
            ),
            ProductTechnology(
                product_uid="test-uid",
                title="Test Technology 2",
                content="Test technology content 2",
            ),
        ]
        
        # Create test features
        self.features = [
            ProductFeature(
                product_uid="test-uid",
                group_title="Test Feature Group 1",
                content="Test feature content 1",
            ),
            ProductFeature(
                product_uid="test-uid",
                group_title="Test Feature Group 1",
                content="Test feature content 2",
            ),
            ProductFeature(
                product_uid="test-uid",
                group_title="Test Feature Group 2",
                content="Test feature content 3",
            ),
        ]
    
    def test_format_product(self):
        """
        Test formatting a product.
        """
        # Mock database queries
        self.db.query.return_value.filter.return_value.first.return_value = self.product
        self.db.query.return_value.filter.return_value.all.side_effect = [
            self.specs,
            self.prices,
            self.technologies,
            self.features,
        ]
        
        # Call format_product
        result = self.formatter.format_product("test-uid")
        
        # Check that the result is not None
        self.assertIsNotNone(result)
        
        # Check that the result has the correct attributes
        self.assertEqual(result.uid, "test-uid")
        self.assertEqual(result.display_title, "Test Product Display")
        self.assertEqual(result.url, "/test-product")
        self.assertEqual(result.description, "Test description")
        self.assertEqual(result.tagline, "Test tagline")
        
        # Check that the formatted text contains the expected information
        self.assertIn("Product: Test Product Display", result.formatted_text)
        self.assertIn("Tagline: Test tagline", result.formatted_text)
        self.assertIn("URL: /test-product", result.formatted_text)
        self.assertIn("UID: test-uid", result.formatted_text)
        self.assertIn("Description: Test description", result.formatted_text)
        self.assertIn("Specifications: Test Spec 1: Test value 1; Test Spec 2: Test value 2", result.formatted_text)
        self.assertIn("Prices: NO: 100 NOK; SE: 100 SEK", result.formatted_text)
        self.assertIn("Technology: Test Technology 1: Test technology content 1 | Test Technology 2: Test technology content 2", result.formatted_text)
        self.assertIn("Features: Test Feature Group 1: Test feature content 1, Test feature content 2 | Test Feature Group 2: Test feature content 3", result.formatted_text)
    
    def test_format_products(self):
        """
        Test formatting multiple products.
        """
        # Mock database queries
        self.db.query.return_value.filter.return_value.all.return_value = [self.product]
        
        # Mock format_product method
        self.formatter.format_product = MagicMock(return_value="formatted-product")
        
        # Call format_products
        result = self.formatter.format_products(["test-uid"])
        
        # Check that format_product was called for each product
        self.formatter.format_product.assert_called_with("test-uid")
        
        # Check that the result contains the formatted products
        self.assertEqual(result, ["formatted-product"])


if __name__ == "__main__":
    unittest.main()
