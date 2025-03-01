"""
Pydantic schemas for product data.

This module provides Pydantic models for validating product data.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ProductSpecSchema(BaseModel):
    """
    Schema for product specifications.
    """
    
    spec_id: str = Field(..., description="Identifier for the specification")
    title: str = Field(..., description="Title of the specification")
    value: Optional[Union[str, List[str]]] = Field(None, description="Value of the specification")


class ProductPriceSchema(BaseModel):
    """
    Schema for product prices.
    """
    
    region: str = Field(..., description="Region code")
    price: Optional[str] = Field(None, description="Price value")


class ProductTechnologySchema(BaseModel):
    """
    Schema for product technologies.
    """
    
    title: str = Field(..., description="Title of the technology")
    content: Optional[str] = Field(None, description="Description of the technology")


class ProductFeatureSchema(BaseModel):
    """
    Schema for product features.
    """
    
    group_title: Optional[str] = Field(None, description="Title of the feature group")
    content: str = Field(..., description="Description of the feature")


class ProductSchema(BaseModel):
    """
    Schema for product data.
    """
    
    uid: str = Field(..., description="Unique identifier for the product")
    title: str = Field(..., description="Product title")
    display_title: str = Field(..., description="Display title for the product")
    url: str = Field(..., description="URL for the product page")
    description: Optional[str] = Field(None, description="Product description")
    tagline: Optional[str] = Field(None, description="Product tagline")
    specs: List[ProductSpecSchema] = Field(default_factory=list, description="Product specifications")
    prices: Dict[str, Optional[str]] = Field(default_factory=dict, description="Product prices")
    technologies: List[ProductTechnologySchema] = Field(default_factory=list, description="Product technologies")
    features: List[ProductFeatureSchema] = Field(default_factory=list, description="Product features")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        """
        Pydantic configuration.
        """
        
        from_attributes = True


class ProductCreateSchema(BaseModel):
    """
    Schema for creating a product.
    """
    
    uid: str = Field(..., description="Unique identifier for the product")
    title: str = Field(..., description="Product title")
    display_title: str = Field(..., description="Display title for the product")
    url: str = Field(..., description="URL for the product page")
    description: Optional[str] = Field(None, description="Product description")
    tagline: Optional[str] = Field(None, description="Product tagline")
    specs: List[ProductSpecSchema] = Field(default_factory=list, description="Product specifications")
    prices: Dict[str, Optional[str]] = Field(default_factory=dict, description="Product prices")
    technologies: List[ProductTechnologySchema] = Field(default_factory=list, description="Product technologies")
    features: List[ProductFeatureSchema] = Field(default_factory=list, description="Product features")


class ProductUpdateSchema(BaseModel):
    """
    Schema for updating a product.
    """
    
    title: Optional[str] = Field(None, description="Product title")
    display_title: Optional[str] = Field(None, description="Display title for the product")
    url: Optional[str] = Field(None, description="URL for the product page")
    description: Optional[str] = Field(None, description="Product description")
    tagline: Optional[str] = Field(None, description="Product tagline")
    specs: Optional[List[ProductSpecSchema]] = Field(None, description="Product specifications")
    prices: Optional[Dict[str, Optional[str]]] = Field(None, description="Product prices")
    technologies: Optional[List[ProductTechnologySchema]] = Field(None, description="Product technologies")
    features: Optional[List[ProductFeatureSchema]] = Field(None, description="Product features")


class ProductTextOutputSchema(BaseModel):
    """
    Schema for text output of product data.
    """
    
    uid: str = Field(..., description="Unique identifier for the product")
    display_title: str = Field(..., description="Display title for the product")
    url: str = Field(..., description="URL for the product page")
    description: Optional[str] = Field(None, description="Product description")
    tagline: Optional[str] = Field(None, description="Product tagline")
    specs_text: Optional[str] = Field(None, description="Formatted specifications text")
    prices_text: Optional[str] = Field(None, description="Formatted prices text")
    technologies_text: Optional[str] = Field(None, description="Formatted technologies text")
    features_text: Optional[str] = Field(None, description="Formatted features text")
    formatted_text: str = Field(..., description="Fully formatted product text")
