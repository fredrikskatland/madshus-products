"""
Product formatter module for the Madshus Products Pipeline.

This module provides functionality for formatting product data into clean text.
"""

import re
from typing import Dict, List, Optional, Union

from loguru import logger
from sqlalchemy.orm import Session

from madshus.models.product import (
    Product,
    ProductFeature,
    ProductPrice,
    ProductSpec,
    ProductTechnology,
)
from madshus.schemas.product import ProductTextOutputSchema


class ProductFormatter:
    """
    Formatter for product data.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the product formatter.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def format_product(self, uid: str) -> Optional[ProductTextOutputSchema]:
        """
        Format a product into clean text.
        
        Args:
            uid: Product UID
            
        Returns:
            Optional[ProductTextOutputSchema]: Formatted product data
        """
        logger.info(f"Formatting product {uid}")
        
        # Get product from database
        product = self.db.query(Product).filter(Product.uid == uid).first()
        if not product:
            logger.warning(f"Product {uid} not found")
            return None
        
        # Get related data
        specs = self.db.query(ProductSpec).filter(ProductSpec.product_uid == uid).all()
        prices = self.db.query(ProductPrice).filter(ProductPrice.product_uid == uid).all()
        technologies = self.db.query(ProductTechnology).filter(ProductTechnology.product_uid == uid).all()
        features = self.db.query(ProductFeature).filter(ProductFeature.product_uid == uid).all()
        
        # Format specifications
        specs_text = self._format_specs(specs)
        
        # Format prices
        prices_text = self._format_prices(prices)
        
        # Format technologies
        technologies_text = self._format_technologies(technologies)
        
        # Format features
        features_text = self._format_features(features)
        
        # Create full formatted text
        formatted_text = self._create_formatted_text(
            product, specs_text, prices_text, technologies_text, features_text
        )
        
        # Create output schema
        output = ProductTextOutputSchema(
            uid=product.uid,
            display_title=product.display_title,
            url=product.url,
            description=product.description,
            tagline=product.tagline,
            specs_text=specs_text,
            prices_text=prices_text,
            technologies_text=technologies_text,
            features_text=features_text,
            formatted_text=formatted_text,
        )
        
        return output
    
    def format_products(self, uids: Optional[List[str]] = None) -> List[ProductTextOutputSchema]:
        """
        Format multiple products into clean text.
        
        Args:
            uids: List of product UIDs to format. If None, all products will be formatted.
            
        Returns:
            List[ProductTextOutputSchema]: List of formatted products
        """
        logger.info(f"Formatting {'all' if uids is None else len(uids)} products")
        
        # Get products from database
        query = self.db.query(Product)
        if uids:
            query = query.filter(Product.uid.in_(uids))
        
        products = query.all()
        logger.info(f"Found {len(products)} products")
        
        # Format each product
        formatted_products = []
        for product in products:
            formatted_product = self.format_product(product.uid)
            if formatted_product:
                formatted_products.append(formatted_product)
        
        return formatted_products
    
    def _format_specs(self, specs: List[ProductSpec]) -> Optional[str]:
        """
        Format product specifications into clean text.
        
        Args:
            specs: List of product specifications
            
        Returns:
            Optional[str]: Formatted specifications text
        """
        if not specs:
            return None
        
        # Group specifications by title
        specs_by_title = {}
        for spec in specs:
            specs_by_title[spec.title] = spec.value
        
        # Format specifications
        specs_lines = []
        for title, value in specs_by_title.items():
            if value:
                specs_lines.append(f"{title}: {value}")
        
        if not specs_lines:
            return None
        
        return "; ".join(specs_lines)
    
    def _format_prices(self, prices: List[ProductPrice]) -> Optional[str]:
        """
        Format product prices into clean text.
        
        Args:
            prices: List of product prices
            
        Returns:
            Optional[str]: Formatted prices text
        """
        if not prices:
            return None
        
        # Format prices
        price_lines = []
        for price in prices:
            if price.price:
                price_lines.append(f"{price.region.upper()}: {price.price}")
        
        if not price_lines:
            return None
        
        return "; ".join(price_lines)
    
    def _format_technologies(self, technologies: List[ProductTechnology]) -> Optional[str]:
        """
        Format product technologies into clean text.
        
        Args:
            technologies: List of product technologies
            
        Returns:
            Optional[str]: Formatted technologies text
        """
        if not technologies:
            return None
        
        # Format technologies
        tech_lines = []
        for tech in technologies:
            if tech.content:
                tech_lines.append(f"{tech.title}: {tech.content}")
            else:
                tech_lines.append(tech.title)
        
        if not tech_lines:
            return None
        
        return " | ".join(tech_lines)
    
    def _format_features(self, features: List[ProductFeature]) -> Optional[str]:
        """
        Format product features into clean text.
        
        Args:
            features: List of product features
            
        Returns:
            Optional[str]: Formatted features text
        """
        if not features:
            return None
        
        # Group features by group title
        features_by_group = {}
        for feature in features:
            group_title = feature.group_title or "General"
            if group_title not in features_by_group:
                features_by_group[group_title] = []
            features_by_group[group_title].append(feature.content)
        
        # Format features
        feature_lines = []
        for group_title, contents in features_by_group.items():
            if contents:
                feature_lines.append(f"{group_title}: {', '.join(contents)}")
        
        if not feature_lines:
            return None
        
        return " | ".join(feature_lines)
    
    def _create_formatted_text(
        self,
        product: Product,
        specs_text: Optional[str],
        prices_text: Optional[str],
        technologies_text: Optional[str],
        features_text: Optional[str],
    ) -> str:
        """
        Create fully formatted product text.
        
        Args:
            product: Product
            specs_text: Formatted specifications text
            prices_text: Formatted prices text
            technologies_text: Formatted technologies text
            features_text: Formatted features text
            
        Returns:
            str: Fully formatted product text
        """
        lines = []
        
        # Header: title and tagline
        lines.append(f"Product: {product.display_title}")
        if product.tagline:
            lines.append(f"Tagline: {product.tagline}")
        
        # URL and UID
        lines.append(f"URL: {product.url}")
        lines.append(f"UID: {product.uid}")
        
        # Description
        if product.description:
            lines.append(f"Description: {product.description}")
        
        # Specifications
        if specs_text:
            lines.append(f"Specifications: {specs_text}")
        
        # Prices
        if prices_text:
            lines.append(f"Prices: {prices_text}")
        
        # Technologies
        if technologies_text:
            lines.append(f"Technology: {technologies_text}")
        
        # Features
        if features_text:
            lines.append(f"Features: {features_text}")
        
        return "\n".join(lines)


class MarkdownProductFormatter(ProductFormatter):
    """
    Markdown formatter for product data.
    """
    
    def _create_formatted_text(
        self,
        product: Product,
        specs_text: Optional[str],
        prices_text: Optional[str],
        technologies_text: Optional[str],
        features_text: Optional[str],
    ) -> str:
        """
        Create fully formatted product text in Markdown format.
        
        Args:
            product: Product
            specs_text: Formatted specifications text
            prices_text: Formatted prices text
            technologies_text: Formatted technologies text
            features_text: Formatted features text
            
        Returns:
            str: Fully formatted product text in Markdown format
        """
        lines = []
        
        # Header: title and tagline
        lines.append(f"# {product.display_title}")
        if product.tagline:
            lines.append(f"*{product.tagline}*")
        
        lines.append("")
        
        # URL and UID
        lines.append(f"**URL:** {product.url}")
        lines.append(f"**UID:** {product.uid}")
        
        lines.append("")
        
        # Description
        if product.description:
            lines.append("## Description")
            lines.append(product.description)
            lines.append("")
        
        # Specifications
        if specs_text:
            lines.append("## Specifications")
            for spec in specs_text.split("; "):
                lines.append(f"- {spec}")
            lines.append("")
        
        # Prices
        if prices_text:
            lines.append("## Prices")
            for price in prices_text.split("; "):
                lines.append(f"- {price}")
            lines.append("")
        
        # Technologies
        if technologies_text:
            lines.append("## Technology")
            for tech in technologies_text.split(" | "):
                lines.append(f"- {tech}")
            lines.append("")
        
        # Features
        if features_text:
            lines.append("## Features")
            for feature in features_text.split(" | "):
                lines.append(f"- {feature}")
            lines.append("")
        
        return "\n".join(lines)


class JSONProductFormatter(ProductFormatter):
    """
    JSON formatter for product data.
    """
    
    def format_product(self, uid: str) -> Optional[Dict]:
        """
        Format a product into JSON.
        
        Args:
            uid: Product UID
            
        Returns:
            Optional[Dict]: Formatted product data as a dictionary
        """
        # Get formatted product
        formatted_product = super().format_product(uid)
        if not formatted_product:
            return None
        
        # Convert to dictionary
        return formatted_product.dict()
    
    def format_products(self, uids: Optional[List[str]] = None) -> List[Dict]:
        """
        Format multiple products into JSON.
        
        Args:
            uids: List of product UIDs to format. If None, all products will be formatted.
            
        Returns:
            List[Dict]: List of formatted products as dictionaries
        """
        # Get formatted products
        formatted_products = super().format_products(uids)
        
        # Convert to dictionaries
        return [product.dict() for product in formatted_products]
