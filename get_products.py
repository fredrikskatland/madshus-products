import requests
import logging
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO)

# GraphQL endpoint and headers (shared between requests)
GRAPHQL_URL = "https://madshus.com/api/graphql"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json"
}

# GraphQL query to get a paginated product grid.
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

def fetch_products(query_string, bcRegion="no"):
    """
    Executes the GetPaginatedProductGrid query with the given query string.
    
    Args:
      query_string (str): The JSON-encoded filter and pagination parameters.
      bcRegion (str): The region parameter.
      
    Returns:
      A tuple (products, total) where products is a list of product dicts.
    """
    payload = {
        "query": GET_PAGINATED_PRODUCT_GRID_QUERY,
        "variables": {"queryString": query_string, "bcRegion": bcRegion},
        "operationName": "GetPaginatedProductGrid"
    }
    response = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    grid = data.get("data", {}).get("paginatedProductGrid", {})
    products = grid.get("products", [])
    total = grid.get("total", 0)
    return products, total

def main():

    all_products = []
    categories = range(1,300)
    for category in categories:
        query_string = (
            f'{{"bc_products.no.categories":{{"$in":[{category}]}},'
            f'"regions":{{"$in":["no"]}}}}'
            f"&limit=30&skip=0&include_count=true&asc=bc_products.no.sort_order"
            f"&locale=en-us&include_fallback=true"
        )
    
        # Fetch products for this category
        category_products, total = fetch_products(query_string)
        logging.info("Fetched %s products for category %s out of total %s", len(category_products), category, total)
        # Tag each product with the current category for reference
        for prod in category_products:
            prod["category_id"] = category
        all_products.extend(category_products)

    if not all_products:
        logging.warning("No products were fetched from any category.")
        return
    
    # Display the combined product list in a table
    console = Console()
    table = Table(title="Combined Product List")
    table.add_column("Product Number", style="blue")
    table.add_column("UID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Display Title", style="green")
    table.add_column("URL", style="yellow")
    table.add_column("Category", style="red")
    
    product_number = 0
    for prod in all_products:
        product_number += 1
        uid = prod.get("uid", "N/A")
        title = prod.get("title", "N/A")
        display_title = prod.get("display_title", "N/A")
        url = prod.get("url", "N/A")
        category = prod.get("category_id", "N/A")
        table.add_row(str(uid), str(title), str(display_title), str(url), str(category))
    
    console.print(table)
    
    # Now you have a list (all_products) that you can pass to your getProducts script
    # for further processing.

if __name__ == "__main__":
    main()
