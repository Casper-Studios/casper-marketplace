#!/usr/bin/env python3
"""
Attio CRM API Client
Provides methods to interact with Attio CRM: fetch companies, create notes, search records.

Directive: directives/attio_crm_integration.md

Usage:
    # Get company by ID
    python execution/attio_api.py get-company e26784a0-0933-45f2-99ea-e432ac41142e

    # Search companies by name
    python execution/attio_api.py search-companies "Acme Corp"

    # Create note on company
    python execution/attio_api.py create-note e26784a0-0933-45f2-99ea-e432ac41142e "Proposal Generated" "Link: https://docs.google.com/..."

    # Extract company ID from Attio URL
    python execution/attio_api.py parse-url "https://app.attio.com/yourworkspace/companies/view/e26784a0-0933-45f2-99ea-e432ac41142e"
"""

import os
import re
import sys
import argparse
import json
import time
from typing import Optional
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"


class AttioAPIError(Exception):
    """Custom exception for Attio API errors."""
    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class AttioClient:
    """Client for interacting with Attio CRM API."""

    def __init__(self, api_key: str = None):
        """
        Initialize Attio client.

        Args:
            api_key: Attio API access token. Defaults to ATTIO_API_KEY env var.
        """
        self.api_key = api_key or ATTIO_API_KEY
        if not self.api_key:
            raise ValueError(
                "Attio API key required. Set ATTIO_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.base_url = ATTIO_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None,
        max_retries: int = 3
    ) -> dict:
        """
        Make API request with retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            max_retries: Maximum retry attempts for rate limiting

        Returns:
            API response data

        Raises:
            AttioAPIError: On API errors
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                )

                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = 2 ** attempt
                    print(f"   Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                # Raise for other HTTP errors
                if not response.ok:
                    error_body = None
                    try:
                        error_body = response.json()
                    except:
                        pass
                    raise AttioAPIError(
                        f"API request failed: {response.status_code} {response.reason}",
                        status_code=response.status_code,
                        response_body=error_body
                    )

                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   Request failed, retrying in {wait_time}s... ({e})")
                    time.sleep(wait_time)
                else:
                    raise AttioAPIError(f"Request failed after {max_retries} attempts: {e}")

        raise AttioAPIError(f"Max retries ({max_retries}) exceeded")

    # =========================================================================
    # COMPANY METHODS
    # =========================================================================

    def get_company(self, record_id: str) -> dict:
        """
        Get a company record by its ID.

        Args:
            record_id: UUID of the company record

        Returns:
            Company record data
        """
        response = self._request("GET", f"/objects/companies/records/{record_id}")
        return response.get("data", {})

    def search_companies(
        self,
        name_query: str = None,
        domain: str = None,
        limit: int = 10,
        offset: int = 0
    ) -> list:
        """
        Search for companies by name or domain.

        Args:
            name_query: Company name to search (partial match)
            domain: Company domain to search
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of matching company records
        """
        filter_obj = {}
        if name_query:
            filter_obj["name"] = name_query
        if domain:
            filter_obj["domains"] = domain

        payload = {
            "limit": limit,
            "offset": offset
        }
        if filter_obj:
            payload["filter"] = filter_obj

        response = self._request("POST", "/objects/companies/records/query", data=payload)
        return response.get("data", [])

    def get_company_name(self, company_data: dict) -> str:
        """
        Extract company name from Attio record.

        Args:
            company_data: Company record from API

        Returns:
            Company name string
        """
        values = company_data.get("values", {})
        name_values = values.get("name", [])
        if name_values and len(name_values) > 0:
            return name_values[0].get("value", "Unknown")
        return "Unknown"

    def get_company_domain(self, company_data: dict) -> Optional[str]:
        """
        Extract primary domain from Attio company record.

        Args:
            company_data: Company record from API

        Returns:
            Domain string or None
        """
        values = company_data.get("values", {})
        domains = values.get("domains", [])
        if domains and len(domains) > 0:
            return domains[0].get("domain")
        return None

    # =========================================================================
    # NOTES METHODS
    # =========================================================================

    def create_note(
        self,
        parent_record_id: str,
        title: str,
        content: str,
        parent_object: str = "companies",
        format: str = "plaintext"
    ) -> dict:
        """
        Create a note attached to a record.

        Args:
            parent_record_id: UUID of the record to attach note to
            title: Note title
            content: Note body (supports markdown if format="markdown")
            parent_object: Object type ("companies", "people", etc.)
            format: Content format ("plaintext" or "markdown")

        Returns:
            Created note data
        """
        payload = {
            "data": {
                "parent_object": parent_object,
                "parent_record_id": parent_record_id,
                "title": title,
                "format": format,
                "content": content
            }
        }
        response = self._request("POST", "/notes", data=payload)
        return response.get("data", {})

    def list_notes(
        self,
        parent_record_id: str = None,
        parent_object: str = None,
        limit: int = 10,
        offset: int = 0
    ) -> list:
        """
        List notes, optionally filtered by parent record.

        Args:
            parent_record_id: Filter by parent record UUID
            parent_object: Filter by object type
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of notes
        """
        params = {"limit": limit, "offset": offset}
        if parent_record_id:
            params["parent_record_id"] = parent_record_id
        if parent_object:
            params["parent_object"] = parent_object

        response = self._request("GET", "/notes", params=params)
        return response.get("data", [])

    def get_note(self, note_id: str) -> dict:
        """
        Get a single note by ID.

        Args:
            note_id: UUID of the note

        Returns:
            Note data
        """
        response = self._request("GET", f"/notes/{note_id}")
        return response.get("data", {})

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.

        Args:
            note_id: UUID of the note

        Returns:
            True if deleted successfully
        """
        self._request("DELETE", f"/notes/{note_id}")
        return True

    # =========================================================================
    # PEOPLE METHODS
    # =========================================================================

    def create_person(
        self,
        email: str,
        first_name: str = None,
        last_name: str = None,
        company_record_id: str = None,
        phone: str = None,
        linkedin_url: str = None
    ) -> dict:
        """
        Create a person record in Attio.

        Args:
            email: Email address (required, used as unique identifier)
            first_name: First name
            last_name: Last name
            company_record_id: UUID of company to link this person to
            phone: Phone number
            linkedin_url: LinkedIn profile URL

        Returns:
            Created person record data
        """
        values = {
            "email_addresses": [{"email_address": email}]
        }

        # Add name if provided
        if first_name or last_name:
            name_obj = {}
            if first_name:
                name_obj["first_name"] = first_name
            if last_name:
                name_obj["last_name"] = last_name
            if first_name and last_name:
                name_obj["full_name"] = f"{first_name} {last_name}"
            values["name"] = [name_obj]

        # Link to company if provided
        if company_record_id:
            values["company"] = [{
                "target_record_id": company_record_id,
                "target_object": "companies"
            }]

        if phone:
            values["phone_numbers"] = [{"original_phone_number": phone}]

        if linkedin_url:
            values["linkedin"] = linkedin_url

        payload = {"data": {"values": values}}
        response = self._request("POST", "/objects/people/records", data=payload)
        return response.get("data", {})

    def assert_person(
        self,
        email: str,
        first_name: str = None,
        last_name: str = None,
        company_record_id: str = None
    ) -> dict:
        """
        Create or update a person by email (upsert).

        Args:
            email: Email address (used as matching attribute)
            first_name: First name
            last_name: Last name
            company_record_id: UUID of company to link to

        Returns:
            Person record data (created or updated)
        """
        values = {
            "email_addresses": [{"email_address": email}]
        }

        if first_name or last_name:
            name_obj = {}
            if first_name:
                name_obj["first_name"] = first_name
            if last_name:
                name_obj["last_name"] = last_name
            if first_name and last_name:
                name_obj["full_name"] = f"{first_name} {last_name}"
            values["name"] = [name_obj]

        if company_record_id:
            values["company"] = [{
                "target_record_id": company_record_id,
                "target_object": "companies"
            }]

        payload = {"data": {"values": values}}
        response = self._request(
            "PUT",
            "/objects/people/records?matching_attribute=email_addresses",
            data=payload
        )
        return response.get("data", {})

    def get_person(self, record_id: str) -> dict:
        """
        Get a person record by ID.

        Args:
            record_id: UUID of the person record

        Returns:
            Person record data
        """
        response = self._request("GET", f"/objects/people/records/{record_id}")
        return response.get("data", {})

    def search_people(
        self,
        email: str = None,
        name_query: str = None,
        limit: int = 10
    ) -> list:
        """
        Search for people by email or name.

        Args:
            email: Email address to search
            name_query: Name to search (partial match)
            limit: Maximum results

        Returns:
            List of matching person records
        """
        filter_obj = {}
        if email:
            filter_obj["email_addresses"] = email
        if name_query:
            filter_obj["name"] = name_query

        payload = {"limit": limit}
        if filter_obj:
            payload["filter"] = filter_obj

        response = self._request("POST", "/objects/people/records/query", data=payload)
        return response.get("data", [])

    # =========================================================================
    # CREATE/UPDATE COMPANY METHODS
    # =========================================================================

    def create_company(
        self,
        name: str,
        domain: str = None,
        customer_status: str = None,
        description: str = None
    ) -> dict:
        """
        Create a company record in Attio.

        Args:
            name: Company name (required)
            domain: Company website domain (e.g., 'microsoft.com')
            customer_status: Status field value (e.g., 'Active Prospect')
            description: Company description

        Returns:
            Created company record data
        """
        values = {
            "name": [{"value": name}]
        }

        if domain:
            values["domains"] = [{"domain": domain}]

        if customer_status:
            values["customer_status"] = customer_status

        if description:
            values["description"] = [{"value": description}]

        payload = {"data": {"values": values}}
        response = self._request("POST", "/objects/companies/records", data=payload)
        return response.get("data", {})

    def assert_company(
        self,
        name: str,
        domain: str = None,
        customer_status: str = None
    ) -> dict:
        """
        Create or update a company by domain (upsert).
        If domain exists, updates the record. Otherwise creates new.

        Args:
            name: Company name
            domain: Company domain (used as matching attribute)
            customer_status: Status field value

        Returns:
            Company record data (created or updated)
        """
        values = {
            "name": [{"value": name}]
        }

        if domain:
            values["domains"] = [{"domain": domain}]

        if customer_status:
            values["customer_status"] = customer_status

        payload = {"data": {"values": values}}

        # Use domain as matching attribute if provided
        endpoint = "/objects/companies/records"
        if domain:
            endpoint += "?matching_attribute=domains"

        response = self._request("PUT", endpoint, data=payload)
        return response.get("data", {})

    def update_company(
        self,
        record_id: str,
        updates: dict
    ) -> dict:
        """
        Update a company record with new values.

        Args:
            record_id: UUID of the company record
            updates: Dict of attribute slugs to new values
                     Example: {
                         'prospect_slack_channel': 'https://slack.com/...',
                         'google_drive_folder_url': 'https://drive.google.com/...'
                     }

        Returns:
            Updated company record data
        """
        # Format values for Attio API
        values = {}
        for key, value in updates.items():
            # Most text/URL fields expect array of objects with 'value' key
            if isinstance(value, str):
                values[key] = [{"value": value}]
            elif isinstance(value, list):
                values[key] = value
            else:
                values[key] = value

        payload = {"data": {"values": values}}
        response = self._request(
            "PATCH",
            f"/objects/companies/records/{record_id}",
            data=payload
        )
        return response.get("data", {})

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    @staticmethod
    def parse_attio_url(url: str) -> dict:
        """
        Parse an Attio URL to extract workspace, object type, and record ID.

        Args:
            url: Attio URL like https://app.attio.com/workspace/companies/view/uuid

        Returns:
            Dict with workspace_slug, object_type, record_id

        Raises:
            ValueError: If URL format is invalid
        """
        # Pattern: https://app.attio.com/{workspace}/{object_type}/view/{record_id}
        pattern = r'https?://app\.attio\.com/([^/]+)/([^/]+)/view/([a-f0-9-]+)'
        match = re.match(pattern, url)

        if not match:
            raise ValueError(
                f"Invalid Attio URL format: {url}\n"
                "Expected: https://app.attio.com/{workspace}/{object}/view/{record_id}"
            )

        return {
            "workspace_slug": match.group(1),
            "object_type": match.group(2),
            "record_id": match.group(3)
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point for Attio API operations."""
    parser = argparse.ArgumentParser(
        description="Attio CRM API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Get company command
    get_company_parser = subparsers.add_parser("get-company", help="Get company by ID")
    get_company_parser.add_argument("record_id", help="Company record UUID")

    # Search companies command
    search_parser = subparsers.add_parser("search-companies", help="Search companies by name")
    search_parser.add_argument("name", help="Company name to search")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # Create note command
    note_parser = subparsers.add_parser("create-note", help="Create note on company")
    note_parser.add_argument("record_id", help="Company record UUID")
    note_parser.add_argument("title", help="Note title")
    note_parser.add_argument("content", help="Note content")

    # Parse URL command
    url_parser = subparsers.add_parser("parse-url", help="Parse Attio URL")
    url_parser.add_argument("url", help="Attio URL to parse")

    # List notes command
    list_notes_parser = subparsers.add_parser("list-notes", help="List notes for a record")
    list_notes_parser.add_argument("record_id", help="Parent record UUID")
    list_notes_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # Create company command
    create_company_parser = subparsers.add_parser("create-company", help="Create a company record")
    create_company_parser.add_argument("name", help="Company name")
    create_company_parser.add_argument("--domain", help="Company domain (e.g., microsoft.com)")
    create_company_parser.add_argument("--status", help="Customer status")

    # Create person command
    create_person_parser = subparsers.add_parser("create-person", help="Create a person record")
    create_person_parser.add_argument("email", help="Email address")
    create_person_parser.add_argument("--first-name", help="First name")
    create_person_parser.add_argument("--last-name", help="Last name")
    create_person_parser.add_argument("--company-id", help="Company record ID to link to")

    # Update company command
    update_company_parser = subparsers.add_parser("update-company", help="Update company record")
    update_company_parser.add_argument("record_id", help="Company record UUID")
    update_company_parser.add_argument("--slack-channel", help="Slack channel URL")
    update_company_parser.add_argument("--drive-folder", help="Google Drive folder URL")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Parse URL doesn't need API key
        if args.command == "parse-url":
            result = AttioClient.parse_attio_url(args.url)
            print(json.dumps(result, indent=2))
            return 0

        # Initialize client for other commands
        client = AttioClient()

        if args.command == "get-company":
            print(f"Fetching company: {args.record_id}")
            company = client.get_company(args.record_id)
            name = client.get_company_name(company)
            print(f"\nCompany: {name}")
            print(f"Web URL: {company.get('web_url', 'N/A')}")
            print(f"\nFull data:")
            print(json.dumps(company, indent=2))

        elif args.command == "search-companies":
            print(f"Searching for companies matching: {args.name}")
            companies = client.search_companies(name_query=args.name, limit=args.limit)
            print(f"\nFound {len(companies)} companies:")
            for c in companies:
                name = client.get_company_name(c)
                record_id = c.get("id", {}).get("record_id", "N/A")
                print(f"  - {name} ({record_id})")

        elif args.command == "create-note":
            print(f"Creating note on record: {args.record_id}")
            note = client.create_note(
                parent_record_id=args.record_id,
                title=args.title,
                content=args.content
            )
            note_id = note.get("id", {}).get("note_id", "N/A")
            print(f"Note created: {note_id}")
            print(json.dumps(note, indent=2))

        elif args.command == "list-notes":
            print(f"Listing notes for record: {args.record_id}")
            notes = client.list_notes(parent_record_id=args.record_id, limit=args.limit)
            print(f"\nFound {len(notes)} notes:")
            for n in notes:
                title = n.get("title", "Untitled")
                note_id = n.get("id", {}).get("note_id", "N/A")
                print(f"  - {title} ({note_id})")

        elif args.command == "create-company":
            print(f"Creating company: {args.name}")
            company = client.create_company(
                name=args.name,
                domain=args.domain,
                customer_status=args.status
            )
            record_id = company.get("id", {}).get("record_id", "N/A")
            print(f"Company created: {record_id}")
            print(f"URL: {company.get('web_url', 'N/A')}")
            print(json.dumps(company, indent=2))

        elif args.command == "create-person":
            print(f"Creating person: {args.email}")
            person = client.create_person(
                email=args.email,
                first_name=args.first_name,
                last_name=args.last_name,
                company_record_id=args.company_id
            )
            record_id = person.get("id", {}).get("record_id", "N/A")
            print(f"Person created: {record_id}")
            print(f"URL: {person.get('web_url', 'N/A')}")
            print(json.dumps(person, indent=2))

        elif args.command == "update-company":
            print(f"Updating company: {args.record_id}")
            updates = {}
            if args.slack_channel:
                updates["prospect_slack_channel"] = args.slack_channel
            if args.drive_folder:
                updates["google_drive_folder_url"] = args.drive_folder

            if not updates:
                print("No updates specified. Use --slack-channel or --drive-folder")
                return 1

            company = client.update_company(args.record_id, updates)
            print("Company updated successfully")
            print(json.dumps(company, indent=2))

        return 0

    except AttioAPIError as e:
        print(f"Attio API Error: {e.message}")
        if e.response_body:
            print(f"Response: {json.dumps(e.response_body, indent=2)}")
        return 1
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
