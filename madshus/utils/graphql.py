"""
GraphQL utility module for the Madshus Products Pipeline.

This module provides functions for making GraphQL requests to the Madshus API.
"""

import json
from typing import Any, Dict, Optional

import requests
from loguru import logger

from madshus.config.settings import settings


class GraphQLClient:
    """
    Client for making GraphQL requests to the Madshus API.
    """
    
    def __init__(self, url: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the GraphQL client.
        
        Args:
            url: GraphQL endpoint URL
            headers: HTTP headers for requests
        """
        self.url = url or settings.graphql_url
        self.headers = headers or settings.headers
    
    def execute(
        self, query: str, variables: Optional[Dict[str, Any]] = None, operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Variables for the query
            operation_name: Name of the operation
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        payload = {"query": query}
        
        if variables:
            payload["variables"] = variables
        
        if operation_name:
            payload["operationName"] = operation_name
        
        logger.debug(f"Executing GraphQL query: {operation_name or 'unnamed'}")
        logger.debug(f"Variables: {json.dumps(variables) if variables else 'None'}")
        
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                raise GraphQLError(data["errors"])
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"GraphQL request failed: {str(e)}")
            raise


class GraphQLError(Exception):
    """
    Exception raised when a GraphQL query returns errors.
    """
    
    def __init__(self, errors: Any):
        """
        Initialize the exception.
        
        Args:
            errors: GraphQL errors
        """
        self.errors = errors
        super().__init__(f"GraphQL errors: {errors}")


# Create a global GraphQL client instance
client = GraphQLClient()


# GraphQL queries
GET_PAGINATED_PRODUCT_GRID_QUERY = """
query GetPaginatedProductGrid($queryString: String!, $bcRegion: String!) {
  paginatedProductGrid(queryString: $queryString) {
    products {
      uid
      title
      display_title
      regions
      price_range
      url
      bc_products
      is_new {
        value
      }
      is_redesigned {
        value
      }
      prices {
        au
        at
        ca
        cz
        fr
        de
        it
        jp
        nl
        no
        ru
        pl
        es
        se
        ch
        gb
      }
      image {
        amplience_id
        imageset
      }
      bcProduct(bcRegion: $bcRegion) {
        id
        calculatedPrice {
          value
        }
        retailPrice(bcRegion: $bcRegion) {
          value
        }
        inventory_tracking
        inventoryLevel
        isInStock
        availability
        categories {
          id
        }
        variants(bcRegion: $bcRegion) {
          id
          inventoryLevel
          isInStock
          isPurchasable
          calculatedPrice {
            value
          }
          option_values {
            id
            option_display_name
            values {
              id
              label
            }
          }
        }
      }
    }
    total
  }
}
"""

GET_PRODUCT_QUERY = """
query GetProduct($url: String!, $locale: String!, $bcRegion: String!) {
  product(url: $url, locale: $locale) {
    url
    uid
    description
    display_title
    title
    tagline
    updated_product_specs
    bc_products
    regions
    product_notice
    image {
      amplience_id
      imageset
    }
    is_new { value }
    is_redesigned { value }
    prices {
      au
      at
      ca
      cz
      fr
      de
      it
      jp
      nl
      no
      ru
      pl
      es
      se
      ch
      gb
    }
    video {
      video_id
      video_platform
    }
    yotpo_instagram {
      title
      gallery_id
    }
    seo_meta {
      imageset
      seo_title
      seo_description
      og_title
      og_description
      og_image
      twitter_title
      twitter_description
      twitter_image
    }
    details(locale: $locale) {
      excerpt
      specifications_table
      awards {
        title
        image {
          amplience_id
        }
      }
      banner {
        title
        content
        uid
        dark_overlay_on_banner_image
        disable_link
        content_layout
        background {
          type
          imageset
          amplience_id
          content {
            amplienceId
            enableHotspots
            hotspots
          }
        }
        cta_button_global {
          button_text
          button_class
          external_link {
            title
            href
          }
          internal_link
          type
          disable_link
          new_tab
        }
      }
      best_for_image {
        title
        image {
          amplience_id
          best_for_display_title
        }
      }
      construction {
        title
        content
        image {
          amplience_id
        }
      }
      excerpts {
        title
        content
      }
      size_chart {
        title
        size_chart_copy
        size_chart_data
      }
      technology {
        title
        content
        video {
          video_id
          video_platform
        }
        image {
          amplience_id
          image_display_options
        }
      }
      resources {
        title
        content
        video {
          video_id
          video_platform
          title
        }
      }
      warranty {
        title
        content
        link {
          title
          type
          internal_link
          external_link {
            title
            href
          }
          new_tab
        }
      }
      feature_details {
        group_title
        group {
          title
          content
          image {
            amplience_id
          }
        }
      }
      related_products {
        uid
        title
        regions
        url
        bc_products
      }
    }
    bcProduct(bcRegion: $bcRegion) {
      id
      name
      calculatedPrice {
        value
        currencyCode
      }
      retailPrice(bcRegion: $bcRegion) {
        value
      }
      sku
      categories {
        id
        name
      }
      inventory_tracking
      inventoryLevel
      isInStock
      availability
      variants(bcRegion: $bcRegion) {
        id
        sku
        upc
        inventoryLevel
        isInStock
        isPurchasable
        calculatedPrice {
          value
          currencyCode
        }
        retailPrice(bcRegion: $bcRegion) {
          value
        }
        option_values {
          id
          option_display_name
          values {
            id
            label
          }
        }
      }
    }
  }
}
"""


def get_paginated_products(
    query_string: str, bc_region: str = "no", operation_name: str = "GetPaginatedProductGrid"
) -> Dict[str, Any]:
    """
    Get paginated products from the Madshus API.
    
    Args:
        query_string: Query string for filtering products
        bc_region: Region code
        operation_name: Name of the GraphQL operation
        
    Returns:
        Dict[str, Any]: Response data
    """
    # Handle Typer OptionInfo objects
    if hasattr(query_string, '__class__') and query_string.__class__.__name__ == 'OptionInfo':
        logger.warning("Query string is a Typer OptionInfo, using its value")
        query_string = getattr(query_string, 'value', "")
    
    if hasattr(bc_region, '__class__') and bc_region.__class__.__name__ == 'OptionInfo':
        logger.warning("BC region is a Typer OptionInfo, using its value")
        bc_region = getattr(bc_region, 'value', "no")
    
    if hasattr(operation_name, '__class__') and operation_name.__class__.__name__ == 'OptionInfo':
        logger.warning("Operation name is a Typer OptionInfo, using its value")
        operation_name = getattr(operation_name, 'value', "GetPaginatedProductGrid")
    
    variables = {"queryString": query_string, "bcRegion": bc_region}
    return client.execute(GET_PAGINATED_PRODUCT_GRID_QUERY, variables, operation_name)


def get_product(
    url: str, locale: str = "en-us", bc_region: str = "no", operation_name: str = "GetProduct"
) -> Dict[str, Any]:
    """
    Get a product from the Madshus API.
    
    Args:
        url: Product URL
        locale: Locale code
        bc_region: Region code
        operation_name: Name of the GraphQL operation
        
    Returns:
        Dict[str, Any]: Response data
    """
    # Handle Typer OptionInfo objects
    if hasattr(url, '__class__') and url.__class__.__name__ == 'OptionInfo':
        logger.warning("URL is a Typer OptionInfo, using its value")
        url = getattr(url, 'value', "")
    
    if hasattr(locale, '__class__') and locale.__class__.__name__ == 'OptionInfo':
        logger.warning("Locale is a Typer OptionInfo, using its value")
        locale = getattr(locale, 'value', "en-us")
    
    if hasattr(bc_region, '__class__') and bc_region.__class__.__name__ == 'OptionInfo':
        logger.warning("BC region is a Typer OptionInfo, using its value")
        bc_region = getattr(bc_region, 'value', "no")
    
    if hasattr(operation_name, '__class__') and operation_name.__class__.__name__ == 'OptionInfo':
        logger.warning("Operation name is a Typer OptionInfo, using its value")
        operation_name = getattr(operation_name, 'value', "GetProduct")
    
    variables = {"url": url, "locale": locale, "bcRegion": bc_region}
    return client.execute(GET_PRODUCT_QUERY, variables, operation_name)
