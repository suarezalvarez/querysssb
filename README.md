# querysssb

Query the SSSB (Stockholm Student Housing) portal for available housing listings.

## Overview

This script automatically queries the SSSB housing portal and retrieves available housing with the following information:

- **Name/Address**: The housing location and address
- **Availability**: Queue days required (credit days)
- **Best Bid**: The highest credit days among current applicants
- **Closing Date**: Application deadline
- **Housing Type**: Room, studio, or apartment
- **Rent**: Monthly rent
- **Living Space**: Size in square meters

## Requirements

- Python 3.9+
- Google Chrome browser installed
- ChromeDriver (automatically managed by webdriver-manager)

## Installation

```bash
# Clone the repository
git clone https://github.com/suarezalvarez/querysssb.git
cd querysssb

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Query all available housing
python query_sssb.py

# Query only apartments
python query_sssb.py --type apartment

# Query only rooms
python query_sssb.py --type room

# Query only studios
python query_sssb.py --type studio
```

### Output Formats

```bash
# Default table format
python query_sssb.py

# JSON output
python query_sssb.py --output json

# CSV output (can be redirected to file)
python query_sssb.py --output csv > listings.csv
```

### Filtering Options

```bash
# Filter by maximum rent
python query_sssb.py --max-rent 5000

# Filter by housing area
python query_sssb.py --area Kungshamra

# Combine filters
python query_sssb.py --type apartment --max-rent 7000
```

### Performance Options

```bash
# Skip fetching individual closing dates (faster)
python query_sssb.py --no-closing-dates

# Run with visible browser (for debugging)
python query_sssb.py --no-headless
```

## Output Example

### Table Format

```
================================================================================
SSSB Available Housing - 2024-01-15 14:30
Total listings: 25
================================================================================

Kungshamra - Professorsslingan 5 (Kungshamra) - 1 room & kitchenette
  Address: Professorsslingan 5
  Rent: 4500 kr | Space: 22 m² | Floor: 3
  Move-in: 2024-02-01
  Best Bid: 1234 days | Applicants: 5
  Closing Date: 2024-01-20
  Link: https://sssb.se/...
--------------------------------------------------------------------------------
```

### JSON Format

```json
{
  "timestamp": "2024-01-15T14:30:00",
  "total": 25,
  "listings": [
    {
      "name": "Kungshamra - Professorsslingan 5",
      "area": "Kungshamra",
      "address": "Professorsslingan 5",
      "type": "1 room & kitchenette",
      "floor": "3",
      "living_space": "22 m²",
      "rent": "4500 kr",
      "move_in_date": "2024-02-01",
      "best_bid": "1234",
      "applicants": "5",
      "closing_date": "2024-01-20",
      "link": "https://sssb.se/..."
    }
  ]
}
```

## Housing Types

| Type | Description |
|------|-------------|
| `room` | Room with shared facilities |
| `studio` | Studio apartment (1 room & kitchenette) |
| `apartment` | Larger apartment (2+ rooms) |
| `all` | All housing types (default) |

## License

MIT License
