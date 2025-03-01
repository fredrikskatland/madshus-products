# Database Schema

```mermaid
erDiagram
    Product {
        string uid PK
        string title
        string display_title
        string url
        string description
        string tagline
        datetime created_at
        datetime updated_at
    }
    ProductSpec {
        int id PK
        string product_uid FK
        string spec_id
        string title
        string value
    }
    ProductPrice {
        int id PK
        string product_uid FK
        string region
        string price
    }
    ProductTechnology {
        int id PK
        string product_uid FK
        string title
        string content
    }
    ProductFeature {
        int id PK
        string product_uid FK
        string group_title
        string content
    }
    
    Product ||--o{ ProductSpec : has
    Product ||--o{ ProductPrice : has
    Product ||--o{ ProductTechnology : has
    Product ||--o{ ProductFeature : has
