"""
Utilities package for the Madshus Products Pipeline.

This package provides utility functions for the application.
"""

from madshus.utils.graphql import (
    GraphQLClient,
    GraphQLError,
    client,
    get_paginated_products,
    get_product,
)

__all__ = [
    "GraphQLClient",
    "GraphQLError",
    "client",
    "get_paginated_products",
    "get_product",
]
