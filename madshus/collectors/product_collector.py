"""
Product collector module for the Madshus Products Pipeline.

This module provides functionality for collecting product data from the Madshus API.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Union

from loguru import logger
from sqlalchemy.orm import Session

from madshus.config.settings import settings
from madshus.models.product import (
    Product,
    ProductFeature,
    ProductPrice,
    ProductSpec,
    ProductTechnology,
)
from madshus.schemas.product import (
    ProductCreateSchema,
    ProductFeatureSchema,
    ProductPriceSchema,
    ProductSpecSchema,
    ProductTechnologySchema,
)
from madshus.utils.graphql import get_paginated_products, get_product


class ProductCollector:
    """
    Collector for product data from the Madshus API.
    """
    
    def __init__(
        self,
        db: Session,
        region: str = settings.default_region,
        locale: str = settings.default_locale,
    ):
        """
        Initialize the product collector.
        
        Args:
            db: Database session
            region: Region code
            locale: Locale code
        """
        self.db = db
        
        # Handle Typer OptionInfo objects
        if hasattr(region, '__class__') and region.__class__.__name__ == 'OptionInfo':
            logger.warning("Region is a Typer OptionInfo, using its value")
            self.region = getattr(region, 'value', settings.default_region)
        else:
            self.region = region
        
        if hasattr(locale, '__class__') and locale.__class__.__name__ == 'OptionInfo':
            logger.warning("Locale is a Typer OptionInfo, using its value")
            self.locale = getattr(locale, 'value', settings.default_locale)
        else:
            self.locale = locale
    
    def collect_products(
        self, categories: Optional[List[int]] = None, limit: Optional[int] = None
    ) -> List[str]:
        """
        Collect products from the Madshus API.
        
        Args:
            categories: List of category IDs to collect products from
            limit: Maximum number of products to collect
            
        Returns:
            List[str]: List of collected product UIDs
        """
        # Handle Typer OptionInfo objects
        if hasattr(categories, '__class__') and categories.__class__.__name__ == 'OptionInfo':
            logger.warning("Categories is a Typer OptionInfo, using None instead")
            categories = None
        
        if hasattr(limit, '__class__') and limit.__class__.__name__ == 'OptionInfo':
            logger.warning("Limit is a Typer OptionInfo, using None instead")
            limit = None
        
        if categories is None:
            # Default to categories 1-300
            categories = list(range(1, 301))
        
        logger.info(f"Collecting products from {len(categories)} categories")
        
        collected_uids: Set[str] = set()
        product_urls: Set[str] = set()
        
        for category in categories:
            if limit and len(collected_uids) >= limit:
                logger.info(f"Reached limit of {limit} products")
                break
            
            logger.info(f"Collecting products from category {category}")
            
            query_string = (
                f'{{"bc_products.{self.region}.categories":{{"$in":[{category}]}},'
                f'"regions":{{"$in":["{self.region}"]}}}}' 
                f"&limit=30&skip=0&include_count=true&asc=bc_products.{self.region}.sort_order"
                f"&locale={self.locale}&include_fallback=true"
            )
            
            try:
                response = get_paginated_products(query_string, self.region)
                products_data = response.get("data", {}).get("paginatedProductGrid", {}).get("products", [])
                total = response.get("data", {}).get("paginatedProductGrid", {}).get("total", 0)
                
                logger.info(f"Found {len(products_data)} products in category {category} (total: {total})")
                
                for product_data in products_data:
                    if limit and len(collected_uids) >= limit:
                        break
                    
                    url = product_data.get("url")
                    if not url or url in product_urls:
                        continue
                    
                    product_urls.add(url)
                    
                    try:
                        uid = self.collect_product(url)
                        if uid:
                            collected_uids.add(uid)
                    except Exception as e:
                        logger.error(f"Error collecting product {url}: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error collecting products from category {category}: {str(e)}")
        
        logger.info(f"Collected {len(collected_uids)} products")
        return list(collected_uids)
    
    def collect_product(self, url: str) -> Optional[str]:
        """
        Collect a product from the Madshus API.
        
        Args:
            url: Product URL
            
        Returns:
            Optional[str]: Product UID if successful, None otherwise
        """
        logger.info(f"Collecting product {url}")
        
        try:
            response = get_product(url, self.locale, self.region)
            product_data = response.get("data", {}).get("product", {})
            
            if not product_data:
                logger.warning(f"No product data found for {url}")
                return None
            
            uid = product_data.get("uid")
            if not uid:
                logger.warning(f"No UID found for product {url}")
                return None
            
            # Check if product already exists
            existing_product = self.db.query(Product).filter(Product.uid == uid).first()
            if existing_product:
                logger.info(f"Product {uid} already exists, updating")
                return self._update_product(existing_product, product_data)
            else:
                logger.info(f"Creating new product {uid}")
                return self._create_product(product_data)
        
        except Exception as e:
            logger.error(f"Error collecting product {url}: {str(e)}")
            return None
    
    def _create_product(self, product_data: Dict) -> str:
        """
        Create a new product in the database.
        
        Args:
            product_data: Product data from the API
            
        Returns:
            str: Product UID
        """
        # Extract basic product data
        uid = product_data.get("uid")
        title = product_data.get("title", "")
        display_title = product_data.get("display_title", "")
        url = product_data.get("url", "")
        description = self._clean_html(product_data.get("description", ""))
        tagline = product_data.get("tagline", "")
        
        # Create product
        product = Product(
            uid=uid,
            title=title,
            display_title=display_title,
            url=url,
            description=description,
            tagline=tagline,
        )
        
        # Add product to database
        self.db.add(product)
        self.db.flush()
        
        # Extract and create specifications
        specs = self._extract_specs(product_data)
        for spec in specs:
            product_spec = ProductSpec(
                product_uid=uid,
                spec_id=spec.spec_id,
                title=spec.title,
                value=spec.value if isinstance(spec.value, str) else ", ".join(spec.value) if spec.value else None,
            )
            self.db.add(product_spec)
        
        # Extract and create prices
        prices = self._extract_prices(product_data)
        for region, price in prices.items():
            if price:
                product_price = ProductPrice(
                    product_uid=uid,
                    region=region,
                    price=price,
                )
                self.db.add(product_price)
        
        # Extract and create technologies
        technologies = self._extract_technologies(product_data)
        for tech in technologies:
            product_tech = ProductTechnology(
                product_uid=uid,
                title=tech.title,
                content=tech.content,
            )
            self.db.add(product_tech)
        
        # Extract and create features
        features = self._extract_features(product_data)
        for feature in features:
            product_feature = ProductFeature(
                product_uid=uid,
                group_title=feature.group_title,
                content=feature.content,
            )
            self.db.add(product_feature)
        
        # Commit changes
        self.db.commit()
        
        return uid
    
    def _update_product(self, product: Product, product_data: Dict) -> str:
        """
        Update an existing product in the database.
        
        Args:
            product: Existing product
            product_data: New product data from the API
            
        Returns:
            str: Product UID
        """
        # Update basic product data
        product.title = product_data.get("title", product.title)
        product.display_title = product_data.get("display_title", product.display_title)
        product.url = product_data.get("url", product.url)
        product.description = self._clean_html(product_data.get("description", product.description))
        product.tagline = product_data.get("tagline", product.tagline)
        
        # Delete existing specifications, prices, technologies, and features
        self.db.query(ProductSpec).filter(ProductSpec.product_uid == product.uid).delete()
        self.db.query(ProductPrice).filter(ProductPrice.product_uid == product.uid).delete()
        self.db.query(ProductTechnology).filter(ProductTechnology.product_uid == product.uid).delete()
        self.db.query(ProductFeature).filter(ProductFeature.product_uid == product.uid).delete()
        
        # Extract and create specifications
        specs = self._extract_specs(product_data)
        for spec in specs:
            product_spec = ProductSpec(
                product_uid=product.uid,
                spec_id=spec.spec_id,
                title=spec.title,
                value=spec.value if isinstance(spec.value, str) else ", ".join(spec.value) if spec.value else None,
            )
            self.db.add(product_spec)
        
        # Extract and create prices
        prices = self._extract_prices(product_data)
        for region, price in prices.items():
            if price:
                product_price = ProductPrice(
                    product_uid=product.uid,
                    region=region,
                    price=price,
                )
                self.db.add(product_price)
        
        # Extract and create technologies
        technologies = self._extract_technologies(product_data)
        for tech in technologies:
            product_tech = ProductTechnology(
                product_uid=product.uid,
                title=tech.title,
                content=tech.content,
            )
            self.db.add(product_tech)
        
        # Extract and create features
        features = self._extract_features(product_data)
        for feature in features:
            product_feature = ProductFeature(
                product_uid=product.uid,
                group_title=feature.group_title,
                content=feature.content,
            )
            self.db.add(product_feature)
        
        # Commit changes
        self.db.commit()
        
        return product.uid
    
    def _extract_specs(self, product_data: Dict) -> List[ProductSpecSchema]:
        """
        Extract product specifications from product data.
        
        Args:
            product_data: Product data from the API
            
        Returns:
            List[ProductSpecSchema]: List of product specifications
        """
        specs = []
        
        # Extract updated_product_specs
        updated_product_specs = product_data.get("updated_product_specs", [])
        for spec in updated_product_specs:
            spec_id = spec.get("id", "")
            title = spec.get("title", "")
            value = spec.get("value", "")
            
            if spec_id and title:
                specs.append(
                    ProductSpecSchema(
                        spec_id=spec_id,
                        title=title,
                        value=value,
                    )
                )
        
        return specs
    
    def _extract_prices(self, product_data: Dict) -> Dict[str, Optional[str]]:
        """
        Extract product prices from product data.
        
        Args:
            product_data: Product data from the API
            
        Returns:
            Dict[str, Optional[str]]: Dictionary of region codes to prices
        """
        prices = {}
        
        # Extract prices
        prices_data = product_data.get("prices", {})
        for region, price in prices_data.items():
            prices[region] = price
        
        return prices
    
    def _extract_technologies(self, product_data: Dict) -> List[ProductTechnologySchema]:
        """
        Extract product technologies from product data.
        
        Args:
            product_data: Product data from the API
            
        Returns:
            List[ProductTechnologySchema]: List of product technologies
        """
        technologies = []
        
        # Extract technology from details
        details = product_data.get("details", {})
        technology_data = details.get("technology", [])
        
        if isinstance(technology_data, list):
            for tech in technology_data:
                title = tech.get("title", "")
                content = self._clean_html(tech.get("content", ""))
                
                if title:
                    technologies.append(
                        ProductTechnologySchema(
                            title=title,
                            content=content,
                        )
                    )
        elif isinstance(technology_data, dict):
            title = technology_data.get("title", "")
            content = self._clean_html(technology_data.get("content", ""))
            
            if title:
                technologies.append(
                    ProductTechnologySchema(
                        title=title,
                        content=content,
                    )
                )
        
        return technologies
    
    def _extract_features(self, product_data: Dict) -> List[ProductFeatureSchema]:
        """
        Extract product features from product data.
        
        Args:
            product_data: Product data from the API
            
        Returns:
            List[ProductFeatureSchema]: List of product features
        """
        features = []
        
        # Extract feature_details from details
        details = product_data.get("details", {})
        feature_details = details.get("feature_details", [])
        
        for feature_group in feature_details:
            group_title = feature_group.get("group_title", "")
            group = feature_group.get("group", [])
            
            for feature in group:
                content = feature.get("content", "")
                
                if content:
                    features.append(
                        ProductFeatureSchema(
                            group_title=group_title,
                            content=content,
                        )
                    )
        
        return features
    
    def _clean_html(self, html: Optional[str]) -> str:
        """
        Remove HTML tags from a string.
        
        Args:
            html: HTML string
            
        Returns:
            str: Cleaned string
        """
        if not html:
            return ""
        
        # Remove HTML tags
        clean = re.compile("<.*?>")
        text = re.sub(clean, "", html)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()
