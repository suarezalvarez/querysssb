#!/usr/bin/env python3
"""
SSSB Housing Query Script

This script automatically queries the SSSB (Stockholm Student Housing) portal,
retrieves available housing with filtering options, and extracts key information:
- Name/Address
- Availability (queue days)
- Best bid (highest credit days among applicants)
- Closing date (application deadline)

Usage:
    python query_sssb.py [options]

Options:
    --type TYPE         Filter by housing type: room, studio, apartment, all (default: all)
    --output FORMAT     Output format: table, json, csv (default: table)
    --headless          Run browser in headless mode (default: True)
    --no-headless       Run browser in visible mode
    --max-rent AMOUNT   Filter by maximum rent (optional)
    --area AREA         Filter by housing area (optional)
"""

import argparse
import csv
import io
import json
import re
import sys
from datetime import datetime
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    HAS_WEBDRIVER_MANAGER = False


class Housing:
    """Represents a housing listing from SSSB."""
    
    def __init__(
        self,
        name: str,
        area: str,
        address: str,
        housing_type: str,
        floor: str,
        living_space: str,
        rent: str,
        move_in_date: str,
        queue_days: str,
        applicants: str,
        link: str
    ):
        self.name = name
        self.area = area
        self.address = address
        self.housing_type = housing_type
        self.floor = floor
        self.living_space = living_space
        self.rent = rent
        self.move_in_date = move_in_date
        self.queue_days = queue_days  # Best bid (highest credit days)
        self.applicants = applicants
        self.link = link
        self.closing_date: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert housing to dictionary."""
        return {
            "name": self.name,
            "area": self.area,
            "address": self.address,
            "type": self.housing_type,
            "floor": self.floor,
            "living_space": self.living_space,
            "rent": self.rent,
            "move_in_date": self.move_in_date,
            "best_bid": self.queue_days,
            "applicants": self.applicants,
            "closing_date": self.closing_date,
            "link": self.link
        }
    
    def __str__(self) -> str:
        return (
            f"{self.name} ({self.area}) - {self.housing_type}\n"
            f"  Address: {self.address}\n"
            f"  Rent: {self.rent} | Space: {self.living_space} | Floor: {self.floor}\n"
            f"  Move-in: {self.move_in_date}\n"
            f"  Best Bid: {self.queue_days} days | Applicants: {self.applicants}\n"
            f"  Closing Date: {self.closing_date or 'N/A'}\n"
            f"  Link: {self.link}"
        )


class SSSBScraper:
    """Scraper for SSSB housing portal."""
    
    BASE_URL = "https://sssb.se/en/looking-for-housing/apply-for-apartment/available-apartments/"
    LIST_URL = BASE_URL + "available-apartments-list/"
    
    HOUSING_TYPE_CODES = {
        "room": "BOASR",
        "studio": "BOAS1",
        "apartment": "BOASL",
        "all": ""
    }
    
    # Number of fields per listing row in the SSSB listing page
    FIELDS_PER_LISTING = 8
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
    
    def _create_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        if HAS_WEBDRIVER_MANAGER:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        else:
            return webdriver.Chrome(options=options)
    
    def _build_url(
        self,
        housing_type: str = "all",
        max_rent: Optional[int] = None,
        area: Optional[str] = None
    ) -> str:
        """Build the query URL with filters."""
        type_code = self.HOUSING_TYPE_CODES.get(housing_type.lower(), "")
        
        params = [
            f"objektTyper={type_code}" if type_code else "",
            f"hyraMax={max_rent}" if max_rent else "",
            f"omraden={area}" if area else "",
            "paginationantal=100"  # Get up to 100 results
        ]
        
        # Filter out empty params
        params = [p for p in params if p]
        query_string = "&".join(params)
        
        return f"{self.LIST_URL}?{query_string}"
    
    def _parse_listing_row(self, row_text: str, link: str) -> Optional[Housing]:
        """Parse a single row of listing data."""
        # SSSB listing format: Area, Address, Type, Floor, Living space, Rent, Moving date, Days (applicants)
        parts = row_text.split("\n")
        
        if len(parts) < 8:
            return None
        
        try:
            area = parts[0].strip()
            address = parts[1].strip()
            housing_type = parts[2].strip()
            floor = parts[3].strip()
            living_space = parts[4].strip()
            rent = parts[5].strip()
            move_in_date = parts[6].strip()
            queue_info = parts[7].strip()
            
            # Parse queue days and applicants from format like "1234 (5 st)"
            queue_days = queue_info.split(" ")[0] if queue_info else "0"
            applicants = "0"
            if "(" in queue_info and ")" in queue_info:
                applicants = queue_info.split("(")[1].split(")")[0].replace(" st", "").strip()
            
            return Housing(
                name=f"{area} - {address}",
                area=area,
                address=address,
                housing_type=housing_type,
                floor=floor,
                living_space=living_space,
                rent=rent,
                move_in_date=move_in_date,
                queue_days=queue_days,
                applicants=applicants,
                link=link
            )
        except (IndexError, ValueError):
            return None
    
    def _get_closing_date(self, housing: Housing) -> Optional[str]:
        """Fetch the closing date for a specific housing listing."""
        if not self.driver:
            return None
        
        try:
            self.driver.get(housing.link)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SubNavigationContentContainer"))
            )
            
            # Look for application deadline text
            page_text = self.driver.page_source
            
            # Try to find deadline in the page
            deadline_elem = None
            try:
                deadline_elem = self.driver.find_element(
                    By.XPATH, 
                    "//div[contains(text(), 'Application deadline') or contains(text(), 'Ansökan senast')]"
                )
            except Exception:
                pass
            
            if deadline_elem:
                text = deadline_elem.text
                # Extract date from text like "Application deadline: 2024-01-15 at 12:00"
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
                if date_match:
                    return date_match.group(1)
            
            return None
        except Exception:
            return None
    
    def query(
        self,
        housing_type: str = "all",
        max_rent: Optional[int] = None,
        area: Optional[str] = None,
        fetch_closing_dates: bool = True
    ) -> list[Housing]:
        """
        Query SSSB for available housing.
        
        Args:
            housing_type: Type of housing (room, studio, apartment, all)
            max_rent: Maximum monthly rent filter
            area: Housing area filter
            fetch_closing_dates: Whether to fetch closing dates (slower)
        
        Returns:
            List of Housing objects
        """
        housings: list[Housing] = []
        
        try:
            self.driver = self._create_driver()
            url = self._build_url(housing_type, max_rent, area)
            
            print(f"Querying SSSB: {url}", file=sys.stderr)
            self.driver.get(url)
            
            # Wait for the listing to load
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "media-body"))
                )
            except TimeoutException:
                print("No listings found or page failed to load.", file=sys.stderr)
                return housings
            
            # Get all listing elements
            listing_container = self.driver.find_element(
                By.XPATH, 
                "//*[@id='SubNavigationContentContainer']/div[3]/div[4]/div"
            )
            listing_links = self.driver.find_elements(
                By.XPATH, 
                "//*[@id='SubNavigationContentContainer']/div[3]/div[4]/div/a"
            )
            
            listing_text = listing_container.text
            rows = listing_text.split("\n")
            
            # Parse each listing (each listing has FIELDS_PER_LISTING lines)
            links = [link.get_attribute("href") for link in listing_links]
            
            # Group rows into listings
            for i, link in enumerate(links):
                start_idx = i * self.FIELDS_PER_LISTING
                end_idx = start_idx + self.FIELDS_PER_LISTING
                if end_idx <= len(rows):
                    row_text = "\n".join(rows[start_idx:end_idx])
                    housing = self._parse_listing_row(row_text, link)
                    if housing:
                        housings.append(housing)
            
            # Optionally fetch closing dates for each listing
            if fetch_closing_dates and housings:
                print(f"Fetching closing dates for {len(housings)} listings...", file=sys.stderr)
                for i, housing in enumerate(housings):
                    print(f"  Processing {i+1}/{len(housings)}...", file=sys.stderr)
                    housing.closing_date = self._get_closing_date(housing)
            
            return housings
            
        except WebDriverException as e:
            print(f"WebDriver error: {e}", file=sys.stderr)
            return housings
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None


def format_table(housings: list[Housing]) -> str:
    """Format housings as a text table."""
    if not housings:
        return "No housing listings found."
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"SSSB Available Housing - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Total listings: {len(housings)}")
    lines.append("=" * 80)
    
    for housing in housings:
        lines.append("")
        lines.append(str(housing))
        lines.append("-" * 80)
    
    return "\n".join(lines)


def format_json(housings: list[Housing]) -> str:
    """Format housings as JSON."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "total": len(housings),
        "listings": [h.to_dict() for h in housings]
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_csv(housings: list[Housing]) -> str:
    """Format housings as CSV using the csv module for proper formatting."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    headers = [
        "Name", "Area", "Address", "Type", "Floor", "Living Space", 
        "Rent", "Move-in Date", "Best Bid", "Applicants", "Closing Date", "Link"
    ]
    writer.writerow(headers)
    
    for h in housings:
        row = [
            h.name, h.area, h.address, h.housing_type, h.floor, h.living_space,
            h.rent, h.move_in_date, h.queue_days, h.applicants, 
            h.closing_date or "", h.link
        ]
        writer.writerow(row)
    
    return output.getvalue().rstrip('\n')


def main():
    parser = argparse.ArgumentParser(
        description="Query SSSB housing portal for available listings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python query_sssb.py
    python query_sssb.py --type apartment --output json
    python query_sssb.py --type room --max-rent 5000
    python query_sssb.py --output csv > listings.csv
        """
    )
    parser.add_argument(
        "--type", 
        choices=["room", "studio", "apartment", "all"],
        default="all",
        help="Filter by housing type (default: all)"
    )
    parser.add_argument(
        "--output",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode"
    )
    parser.add_argument(
        "--max-rent",
        type=int,
        help="Filter by maximum monthly rent"
    )
    parser.add_argument(
        "--area",
        help="Filter by housing area"
    )
    parser.add_argument(
        "--no-closing-dates",
        action="store_true",
        help="Skip fetching closing dates (faster)"
    )
    
    args = parser.parse_args()
    
    headless = not args.no_headless
    fetch_closing_dates = not args.no_closing_dates
    
    scraper = SSSBScraper(headless=headless)
    
    try:
        housings = scraper.query(
            housing_type=args.type,
            max_rent=args.max_rent,
            area=args.area,
            fetch_closing_dates=fetch_closing_dates
        )
        
        if args.output == "table":
            print(format_table(housings))
        elif args.output == "json":
            print(format_json(housings))
        elif args.output == "csv":
            print(format_csv(housings))
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
