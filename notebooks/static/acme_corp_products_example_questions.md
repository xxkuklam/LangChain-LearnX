---

# Sample RAG Test Queries (English)

Example questions designed to test semantic retrieval across different aspects of the dataset:

### Query 1: Troubleshooting & Environmental Limitations
* **Question:** *"Why isn't my invisibility cap working while it's raining outside?"*
* **Expected Retrieval Target:** Section 1 (`InvisiCap 3000`), under *Safety Instructions & Warnings*.
* **RAG Goal:** Demonstrates semantic matching for weather-related performance issues.

### Query 2: Safety Hazards & Nested Conditions
* **Question:** *"What happens if I put one portable hole inside another hole?"*
* **Expected Retrieval Target:** Section 3 (`Portable Hole v4.2`), under *Critical Legal & Safety Warning*.
* **RAG Goal:** Tests precise rule retrieval regarding dangerous combinations and physical constraints.

### Query 3: Multi-Product / Specific Specs
* **Question:** *"Which ACME product requires a SmartID badge to safely pass through wall barriers?"*
* **Expected Retrieval Target:** Section 4 (`TunnelPaint Pro`), under *Product Overview* and *Guidelines & Liability*.
* **RAG Goal:** Tests entity-specific feature retrieval and authorization conditions.