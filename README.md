# SMART INVENTORY MANAGEMENT

An intelligent inventory management prototype for college labs and libraries.

## Core Features

- **Predictive restocking:** Forecasts demand from recent daily usage and estimates recommended order quantities.
- **Usage analytics:** Reports total usage, average daily usage, and utilization frequency over configurable windows.
- **Automatic procurement suggestions:** Produces urgency-ranked purchasing suggestions with optional budget constraints.

## Quick Start

```bash
python3 src/demo.py
```

## Run Tests

```bash
python3 -m pytest -q
```

## Domain Model

- `InventoryItem`: Item master data (stock, reorder point, vendor, location).
- `UsageEvent`: Date-stamped item consumption record.
- `SmartInventoryManager`: Main service with analytics, forecasting, and procurement logic.
