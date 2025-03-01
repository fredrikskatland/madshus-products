# Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Collector
    participant Database
    participant Formatter
    participant Output

    User->>Collector: Run collection
    Collector->>Madshus API: Fetch products list
    Madshus API-->>Collector: Return products
    loop For each product
        Collector->>Madshus API: Fetch product details
        Madshus API-->>Collector: Return details
        Collector->>Database: Store product
    end
    Collector-->>User: Collection complete
    
    User->>Formatter: Format products
    Formatter->>Database: Retrieve products
    Database-->>Formatter: Return products
    Formatter->>Formatter: Apply formatting
    Formatter->>Output: Generate output files
    Output-->>User: Output complete
