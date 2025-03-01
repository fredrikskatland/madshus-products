import re
import requests
import json
import logging
from rich.console import Console
from rich.panel import Panel

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

# Define the GraphQL endpoint and headers
GRAPHQL_URL = "https://madshus.com/api/graphql"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json"
}

# Define your GraphQL query (this one returns all product data)
GRAPHQL_QUERY = """
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

# Define variables for your query
variables = {
    "url": "/redline-skate-f2-skis-2025",
    "locale": "en-us",
    "bcRegion": "no"
}

# Assemble the payload for the request
payload = {
    "query": GRAPHQL_QUERY,
    "variables": variables,
    "operationName": "GetProduct"
}

def fetch_product_data():
    """Fetches full product data from the GraphQL endpoint."""
    try:
        logging.info("Sending request to GraphQL endpoint...")
        response = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        logging.info("Data received successfully.")
        return data
    except requests.exceptions.RequestException as e:
        logging.error("Request failed: %s", e)
        return None

def strip_html_tags(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def format_product_info(product):
    """
    Formats product information into a compact text format suitable for an LLM prompt.
    
    Fields included:
      - Product title, tagline, URL, UID, and description.
      - Prices (only non-empty values).
      - Updated product specs.
      - Technology details (each with title and content).
      - Feature details.
    """
    lines = []
    
    # Header: title and tagline
    display_title = product.get("display_title", "No Title")
    tagline = product.get("tagline", "")
    lines.append(f"[bold]Product:[/bold] {display_title}")
    if tagline:
        lines.append(f"[italic]Tagline:[/italic] {tagline}")
    
    # URL and UID
    url = product.get("url", "")
    uid = product.get("uid", "")
    lines.append(f"[bold]URL:[/bold] {url}")
    lines.append(f"[bold]UID:[/bold] {uid}")
    
    # Description (strip HTML tags)
    description = product.get("description", "")
    clean_description = strip_html_tags(description).strip()
    lines.append(f"[bold]Description:[/bold] {clean_description}")
    
    # Prices: include only non-empty entries
    prices = product.get("prices", {})
    price_lines = []
    for key, value in prices.items():
        if value and value.strip():
            price_lines.append(f"{key.upper()}: {value.strip()}")
    if price_lines:
        lines.append("[bold]Prices:[/bold] " + "; ".join(price_lines))
    
    # Updated product specs
    specs = product.get("updated_product_specs", [])
    if specs:
        specs_lines = []
        for spec in specs:
            spec_title = spec.get("title") or spec.get("id", "")
            spec_value = spec.get("value", "")
            if isinstance(spec_value, list):
                spec_value = ", ".join(spec_value)
            specs_lines.append(f"{spec_title}: {spec_value}")
        lines.append("[bold]Specifications:[/bold] " + "; ".join(specs_lines))
    
    # Technology details
    technology = product.get("technology")
    tech_lines = []
    if technology:
        if isinstance(technology, list):
            for tech in technology:
                title = tech.get("title", "")
                content = strip_html_tags(tech.get("content", "")).strip()
                tech_lines.append(f"{title}: {content}")
        elif isinstance(technology, dict):
            title = technology.get("title", "")
            content = strip_html_tags(technology.get("content", "")).strip()
            tech_lines.append(f"{title}: {content}")
    if tech_lines:
        lines.append("[bold]Technology:[/bold] " + " | ".join(tech_lines))
    
    # Feature details
    feature_details = product.get("feature_details", [])
    feat_lines = []
    if feature_details:
        for group in feature_details:
            group_title = group.get("group_title", "")
            group_features = group.get("group", [])
            feature_items = [feat.get("content", "").strip() for feat in group_features if feat.get("content", "")]
            if group_title and feature_items:
                feat_lines.append(f"{group_title}: " + ", ".join(feature_items))
            elif feature_items:
                feat_lines.append(", ".join(feature_items))
    if feat_lines:
        lines.append("[bold]Features:[/bold] " + " | ".join(feat_lines))
    
    formatted_text = "\n".join(lines)
    return formatted_text

def save_json(data, filename="filtered_product.json"):
    """Saves the provided data to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info("Data successfully saved to %s", filename)
    except IOError as e:
        logging.error("Failed to write JSON file: %s", e)

if __name__ == "__main__":
    # For demonstration, using sample data. Replace with a loop over your products.
    sample_product = {
      "url": "/redline-skate-f2-skis-2025",
      "uid": "blt2f8e35e627a63f64",
      "description": "<p>The Redline Skate F2 is a world-class skate ski designed to excel in universal to firm and fast snow conditions. The ski features our Carbon Power Wrap core construction and the new Power Edge which is a durable, offset edge designed for maximum stability and edge control. A tall camber with medium-long snow contact areas positioned farther toward the tip and tail from the balance point of the ski provides exceptional performance in firm and fast snow conditions. The F2 model is optimized for firmer and faster snow conditions with longer pressure zones to maximize top-end speed and a longer groove to improve stability at high speed on a harder snowpack. The Redline Skate F2 is built with one goal in mind: to get you to the finish line first.</p><p><br /></p>",
      "display_title": "Madshus Redline Skate F2 Skis 2025",
      "tagline": "World-class skate ski designed to excel in universal to firm and fast snow conditions",
      "prices": {
        "au": "",
        "at": "700,00 € incl. VAT",
        "ca": "",
        "cz": " 14.890,00 Kč incl. VAT",
        "fr": "700,00 € incl. VAT",
        "de": "700,00 € incl. VAT",
        "it": "700,00 € incl. VAT",
        "jp": "",
        "nl": "700,00 € incl. VAT",
        "no": " 8.600,00 NOK incl. VAT",
        "ru": "",
        "pl": "2999,00 PLN incl. VAT",
        "es": "700,00 € incl. VAT",
        "se": "8.600,00 SEK incl. VAT",
        "ch": "SFr.750,00 incl. VAT",
        "gb": ""
      },
      "updated_product_specs": [
        {
          "id": "ski-length",
          "title": "Ski - Length",
          "display_text": "Ski Length",
          "value": "172-192cm/5cm"
        },
        {
          "id": "ski-sidecut",
          "title": "Ski - Sidecut",
          "display_text": "Sidecut",
          "value": "43-44-44"
        },
        {
          "id": "ski-weight",
          "title": "All - Weight",
          "display_text": "Weight",
          "value": "800g/187cm (pair)"
        },
        {
          "id": "collection",
          "title": "All - Collection",
          "display_text": "Collection",
          "value": [
            "REDLINE",
            "Skate"
          ]
        },
        {
          "id": "type-of-skiing-skis",
          "title": "Skis+Poles - Type of Skiing",
          "display_text": "Type of Skiing",
          "value": [
            "Skating"
          ]
        },
        {
          "id": "grip-system",
          "title": "Ski - Grip System",
          "display_text": "Grip System",
          "value": [
            "Waxable"
          ]
        },
        {
          "id": "ski-core",
          "title": "Ski - Core",
          "display_text": "Ski Core",
          "value": [
            "Carbon Power Wrap"
          ]
        },
        {
          "id": "ski-base",
          "title": "Ski - Base",
          "display_text": "Ski Base",
          "value": [
            "World Cup Pro"
          ]
        },
        {
          "id": "ski-camber",
          "title": "Ski - Camber",
          "display_text": "Ski Camber",
          "value": [
            "F2"
          ]
        },
        {
          "id": "binding_plate",
          "title": "Ski - Binding Plate",
          "display_text": "",
          "value": [
            "NIS 7-Click"
          ]
        },
        {
          "id": "ski-empower",
          "title": "Ski - Empower",
          "display_text": "Ski Empower",
          "value": "Yes"
        },
        {
          "id": "product_type",
          "title": "All - Product Category",
          "display_text": "Category",
          "value": [
            "Skis"
          ]
        }
      ],
      "technology": [
        {
          "title": "Carbon Power Wrap",
          "content": "<p>A carbon and fiberglass-wrapped and reinforced PR 100X core constructed with low epoxy absorption which makes for extremely low weight, good strength and phenomenal energy return.</p>"
        },
        {
          "title": "Tuned Dynamic Response",
          "content": "<p>A special layup of carbon combined with a complimentary camber profile improves energy return while optimizing the glide surfaces of the ski as it is loaded and unloaded each and every stride.</p>"
        },
        {
          "title": "Madshus Empower",
          "content": "<p>From manufacturing all the way to the end-user, the internal RFID chips embedded in the cores of our empower™ skis provide access to a wealth of data. With the Madshus empower™ app, customers can access ski prep tools like our wax helper, watch videos, or engage with our GPS-enabled workout tracker.</p>"
        },
        {
          "title": "Fluor Free Ski Bases",
          "content": "<p>Everyone in our sport benefits from nature’s beauty, which is why we are working hard to minimize our effect on the environment that we all hold so dear. Skis marked with the «Fluor Free Ski Bases» logo indicate exactly that: a ski which does not use fluorocarbons in the base material.</p>"
        }
      ],
      "feature_details": [
        {
          "group_title": "Ski Characteristics",
          "group": [
            {
              "title": "",
              "content": "Stability Control",
              "image": {
                "amplience_id": "madshus_2324_ski-characteristics_4"
              }
            },
            {
              "title": "",
              "content": "Glide",
              "image": {
                "amplience_id": "madshus_2324_ski-characteristics_4"
              }
            },
            {
              "title": "",
              "content": "Lightness",
              "image": {
                "amplience_id": "madshus_2324_ski-characteristics_4"
              }
            },
            {
              "title": "",
              "content": "Dynamic Response + Energy Return",
              "image": {
                "amplience_id": "madshus_2324_ski-characteristics_4"
              }
            }
          ]
        }
      ]
    }
    
    # Format the product info
    formatted_text = format_product_info(sample_product)
    
    # Create a rich console and print the result in a Panel
    console = Console()
    console.print(Panel(formatted_text, title="Product Information", expand=False))
