"""
Product models for the Madshus Products Pipeline.

This module provides SQLAlchemy ORM models for products and related entities.
"""

from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from madshus.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """
    Product model representing a Madshus product.
    
    Attributes:
        uid: Unique identifier for the product
        title: Product title
        display_title: Display title for the product
        url: URL for the product page
        description: Product description
        tagline: Product tagline
        specs: List of product specifications
        prices: List of product prices
        technologies: List of product technologies
        features: List of product features
    """
    
    __tablename__ = "products"
    
    uid = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    display_title = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    tagline = Column(String(255), nullable=True)
    
    # Relationships
    specs = relationship("ProductSpec", back_populates="product", cascade="all, delete-orphan")
    prices = relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")
    technologies = relationship("ProductTechnology", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Product(uid={self.uid}, title={self.title})>"


class ProductSpec(Base):
    """
    Product specification model.
    
    Attributes:
        id: Primary key
        product_uid: Foreign key to the product
        spec_id: Identifier for the specification
        title: Title of the specification
        value: Value of the specification
        product: Product that this specification belongs to
    """
    
    __tablename__ = "product_specs"
    
    id = Column(Integer, primary_key=True)
    product_uid = Column(String(50), ForeignKey("products.uid"), nullable=False)
    spec_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="specs")
    
    def __repr__(self) -> str:
        return f"<ProductSpec(id={self.id}, title={self.title}, value={self.value})>"


class ProductPrice(Base):
    """
    Product price model.
    
    Attributes:
        id: Primary key
        product_uid: Foreign key to the product
        region: Region code
        price: Price value
        product: Product that this price belongs to
    """
    
    __tablename__ = "product_prices"
    
    id = Column(Integer, primary_key=True)
    product_uid = Column(String(50), ForeignKey("products.uid"), nullable=False)
    region = Column(String(10), nullable=False)
    price = Column(String(50), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="prices")
    
    def __repr__(self) -> str:
        return f"<ProductPrice(id={self.id}, region={self.region}, price={self.price})>"


class ProductTechnology(Base):
    """
    Product technology model.
    
    Attributes:
        id: Primary key
        product_uid: Foreign key to the product
        title: Title of the technology
        content: Description of the technology
        product: Product that this technology belongs to
    """
    
    __tablename__ = "product_technologies"
    
    id = Column(Integer, primary_key=True)
    product_uid = Column(String(50), ForeignKey("products.uid"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="technologies")
    
    def __repr__(self) -> str:
        return f"<ProductTechnology(id={self.id}, title={self.title})>"


class ProductFeature(Base):
    """
    Product feature model.
    
    Attributes:
        id: Primary key
        product_uid: Foreign key to the product
        group_title: Title of the feature group
        content: Description of the feature
        product: Product that this feature belongs to
    """
    
    __tablename__ = "product_features"
    
    id = Column(Integer, primary_key=True)
    product_uid = Column(String(50), ForeignKey("products.uid"), nullable=False)
    group_title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="features")
    
    def __repr__(self) -> str:
        return f"<ProductFeature(id={self.id}, group_title={self.group_title})>"
