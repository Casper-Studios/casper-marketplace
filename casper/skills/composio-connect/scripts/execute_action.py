#!/usr/bin/env python3
"""
Composio Action Executor - Universal fallback for 1,000+ app integrations.

This script provides a unified interface to execute actions across any
Composio-supported app when no other skill is available.

Usage:
    # Natural language action
    python execute_action.py "Create a Notion page titled 'Meeting Notes'"

    # List available apps
    python execute_action.py --list-apps
    python execute_action.py --list-apps --category crm

    # List actions for an app
    python execute_action.py --list-actions notion

    # Connect to an app (OAuth)
    python execute_action.py --connect notion

    # Execute specific action
    python execute_action.py --app notion --action create_page --params '{"title": "Test"}'

    # Check connection status
    python execute_action.py --check-connection notion

Environment:
    COMPOSIO_API_KEY - Your Composio API key from platform.composio.dev
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Check for composio package
try:
    from composio import Composio, Action
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# =============================================================================
# App Categories (for listing)
# =============================================================================

APP_CATEGORIES = {
    'productivity': [
        'notion', 'asana', 'trello', 'monday', 'clickup', 'coda',
        'airtable', 'todoist', 'evernote', 'onenote'
    ],
    'crm': [
        'hubspot', 'salesforce', 'pipedrive', 'zoho_crm', 'close',
        'freshsales', 'copper', 'insightly'
    ],
    'development': [
        'jira', 'linear', 'gitlab', 'bitbucket', 'confluence',
        'github', 'azure_devops', 'clubhouse'
    ],
    'support': [
        'zendesk', 'intercom', 'freshdesk', 'help_scout', 'crisp',
        'drift', 'front', 'groove'
    ],
    'communication': [
        'microsoft_teams', 'zoom', 'discord', 'twilio', 'sendgrid',
        'mailchimp', 'telegram', 'whatsapp'
    ],
    'finance': [
        'stripe', 'quickbooks', 'xero', 'square', 'paypal',
        'braintree', 'chargebee', 'recurly'
    ],
    'ecommerce': [
        'shopify', 'woocommerce', 'bigcommerce', 'magento',
        'etsy', 'amazon_seller', 'ebay'
    ],
    'storage': [
        'dropbox', 'box', 'onedrive', 'google_drive', 's3',
        'wasabi', 'backblaze'
    ],
    'design': [
        'figma', 'canva', 'miro', 'invision', 'sketch',
        'adobe_creative_cloud', 'zeplin'
    ],
    'analytics': [
        'google_analytics', 'mixpanel', 'amplitude', 'segment',
        'heap', 'hotjar', 'fullstory'
    ],
    'marketing': [
        'mailchimp', 'klaviyo', 'constant_contact', 'activecampaign',
        'drip', 'convertkit', 'facebook_ads', 'google_ads'
    ],
    'social': [
        'twitter', 'linkedin', 'facebook', 'instagram', 'tiktok',
        'pinterest', 'youtube', 'reddit'
    ],
}


# =============================================================================
# Helper Functions
# =============================================================================

def check_api_key() -> str | None:
    """Check if Composio API key is configured."""
    api_key = os.getenv('COMPOSIO_API_KEY')
    if not api_key:
        print("ERROR: COMPOSIO_API_KEY not found in environment")
        print("\nSetup instructions:")
        print("1. Get free API key from https://platform.composio.dev")
        print("2. Add to .env file: COMPOSIO_API_KEY=your_key_here")
        print("3. Or export: export COMPOSIO_API_KEY=your_key_here")
        return None
    return api_key


def get_client():
    """Initialize Composio client."""
    if not COMPOSIO_AVAILABLE:
        print("ERROR: composio package not installed")
        print("Run: pip install composio-core")
        sys.exit(1)

    api_key = check_api_key()
    if not api_key:
        sys.exit(1)

    try:
        client = Composio(api_key=api_key)
        return client
    except Exception as e:
        print(f"ERROR: Failed to initialize Composio client: {e}")
        sys.exit(1)


def save_result(result: dict, output_file: str | None = None):
    """Save result to file if specified."""
    if output_file:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = Path('.tmp/composio') / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Result saved to: {output_path}")


# =============================================================================
# Core Functions
# =============================================================================

def list_apps(category: str | None = None) -> list[str]:
    """List available apps, optionally filtered by category."""
    if category:
        category = category.lower()
        if category in APP_CATEGORIES:
            apps = APP_CATEGORIES[category]
            print(f"\n{category.upper()} Apps ({len(apps)}):")
            for app in sorted(apps):
                print(f"  - {app}")
            return apps
        else:
            print(f"Unknown category: {category}")
            print(f"Available categories: {', '.join(APP_CATEGORIES.keys())}")
            return []
    else:
        print("\nAll App Categories:")
        total = 0
        for cat, apps in sorted(APP_CATEGORIES.items()):
            print(f"\n{cat.upper()} ({len(apps)}):")
            for app in sorted(apps):
                print(f"  - {app}")
            total += len(apps)
        print(f"\nTotal listed: {total} apps")
        print("(Composio supports 1,000+ apps - this is a curated subset)")
        print("\nTo see all apps, visit: https://app.composio.dev/apps")
        return []


def list_actions(app_name: str) -> list[dict]:
    """List available actions for an app."""
    client = get_client()

    try:
        # Get actions for the app
        actions = client.actions.get(apps=[app_name])

        print(f"\nActions for {app_name.upper()}:")
        action_list = []
        for action in actions:
            action_info = {
                'name': action.name,
                'description': action.description,
                'parameters': [p.name for p in action.parameters] if hasattr(action, 'parameters') else []
            }
            action_list.append(action_info)
            print(f"\n  {action.name}")
            if action.description:
                print(f"    Description: {action.description[:100]}...")
            if action_info['parameters']:
                print(f"    Parameters: {', '.join(action_info['parameters'][:5])}")

        print(f"\nTotal: {len(action_list)} actions")
        return action_list

    except Exception as e:
        print(f"ERROR: Failed to list actions for {app_name}: {e}")
        return []


def check_connection(app_name: str) -> bool:
    """Check if an app is connected."""
    client = get_client()

    try:
        connections = client.connected_accounts.get()
        for conn in connections:
            if conn.appUniqueId.lower() == app_name.lower():
                print(f"✓ {app_name} is connected")
                print(f"  Account: {conn.id}")
                return True

        print(f"✗ {app_name} is NOT connected")
        print(f"  Run: python execute_action.py --connect {app_name}")
        return False

    except Exception as e:
        print(f"ERROR: Failed to check connection: {e}")
        return False


def connect_app(app_name: str) -> bool:
    """Initiate OAuth connection to an app."""
    client = get_client()

    try:
        # Check if already connected
        connections = client.connected_accounts.get()
        for conn in connections:
            if conn.appUniqueId.lower() == app_name.lower():
                print(f"✓ {app_name} is already connected")
                return True

        # Initiate connection via entity (correct SDK method)
        print(f"Connecting to {app_name}...")
        entity = client.get_entity('default')
        connection_request = entity.initiate_connection(
            app_name=app_name,
            redirect_url="https://app.composio.dev/redirect"
        )

        print(f"\nPlease authorize Composio to access {app_name}:")
        print(f"\n  {connection_request.redirectUrl}\n")
        print("Open this URL in your browser and complete authorization.")

        # Wait for confirmation
        response = input("\nAuthorization complete? (y/n): ").strip().lower()
        if response == 'y':
            # Verify connection
            if check_connection(app_name):
                print(f"\n✓ Successfully connected to {app_name}!")
                return True
            else:
                print(f"\n✗ Connection verification failed. Please try again.")
                return False
        else:
            print("Connection cancelled.")
            return False

    except Exception as e:
        print(f"ERROR: Failed to connect to {app_name}: {e}")
        return False


def execute_natural_language(query: str, output_file: str | None = None) -> dict:
    """
    Execute an action using natural language.

    Composio's Tool Router automatically determines the right app and action.
    """
    client = get_client()

    result = {
        'query': query,
        'success': False,
        'timestamp': datetime.now().isoformat(),
        'response': None,
        'error': None
    }

    try:
        print(f"Processing: {query[:80]}...")

        # Use Composio's tool router to find and execute the right action
        response = client.execute_action(
            action=Action.TOOL_ROUTER,
            params={"query": query}
        )

        result['success'] = True
        result['response'] = response

        print("\n✓ Action executed successfully!")
        print(f"Response: {json.dumps(response, indent=2, default=str)[:500]}")

    except Exception as e:
        result['error'] = str(e)
        error_msg = str(e).lower()

        if 'not connected' in error_msg or 'unauthorized' in error_msg:
            # Extract app name from error if possible
            print(f"\n✗ Action failed: App not connected")
            print("Please connect the required app first:")
            print("  python execute_action.py --connect <app_name>")
        elif 'rate limit' in error_msg:
            print(f"\n✗ Rate limited. Please wait and try again.")
        else:
            print(f"\n✗ Action failed: {e}")

    save_result(result, output_file)
    return result


def execute_specific_action(
    app_name: str,
    action_name: str,
    params: dict,
    output_file: str | None = None
) -> dict:
    """Execute a specific action with explicit parameters."""
    client = get_client()

    result = {
        'app': app_name,
        'action': action_name,
        'params': params,
        'success': False,
        'timestamp': datetime.now().isoformat(),
        'response': None,
        'error': None
    }

    try:
        print(f"Executing {app_name}.{action_name}...")

        # Get the action
        actions = client.actions.get(apps=[app_name])
        target_action = None
        for action in actions:
            if action.name.lower() == action_name.lower():
                target_action = action
                break

        if not target_action:
            raise ValueError(f"Action '{action_name}' not found for app '{app_name}'")

        # Execute
        response = client.execute_action(
            action=target_action,
            params=params
        )

        result['success'] = True
        result['response'] = response

        print("\n✓ Action executed successfully!")
        print(f"Response: {json.dumps(response, indent=2, default=str)[:500]}")

    except Exception as e:
        result['error'] = str(e)
        print(f"\n✗ Action failed: {e}")

    save_result(result, output_file)
    return result


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Composio Action Executor - Universal fallback for 1,000+ apps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Natural language (Composio figures out the app/action)
  %(prog)s "Create a Notion page titled 'Meeting Notes'"
  %(prog)s "Add a task to Asana: Review Q4 budget"
  %(prog)s "Send a Slack message to #general: Hello team!"

  # List apps and actions
  %(prog)s --list-apps
  %(prog)s --list-apps --category crm
  %(prog)s --list-actions notion

  # Connect to an app (first time)
  %(prog)s --connect notion

  # Execute specific action
  %(prog)s --app notion --action create_page --params '{"title": "Test"}'
        """
    )

    # Positional argument for natural language query
    parser.add_argument('query', nargs='?', help='Natural language action to execute')

    # List operations
    parser.add_argument('--list-apps', action='store_true',
                        help='List available apps')
    parser.add_argument('--list-actions', metavar='APP',
                        help='List actions for an app')
    parser.add_argument('--category', '-c',
                        help='Filter apps by category (with --list-apps)')

    # Connection operations
    parser.add_argument('--connect', metavar='APP',
                        help='Connect to an app (OAuth)')
    parser.add_argument('--check-connection', metavar='APP',
                        help='Check if an app is connected')

    # Specific action execution
    parser.add_argument('--app', '-a', help='App name for specific action')
    parser.add_argument('--action', help='Action name to execute')
    parser.add_argument('--params', '-p', help='JSON parameters for action')

    # Output
    parser.add_argument('--output', '-o', help='Save result to JSON file')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Minimal output')

    args = parser.parse_args()

    # Handle different modes
    if args.list_apps:
        list_apps(args.category)

    elif args.list_actions:
        list_actions(args.list_actions)

    elif args.connect:
        success = connect_app(args.connect)
        sys.exit(0 if success else 1)

    elif args.check_connection:
        connected = check_connection(args.check_connection)
        sys.exit(0 if connected else 1)

    elif args.app and args.action:
        # Specific action execution
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON params: {e}")
                sys.exit(1)

        result = execute_specific_action(
            app_name=args.app,
            action_name=args.action,
            params=params,
            output_file=args.output
        )
        sys.exit(0 if result['success'] else 1)

    elif args.query:
        # Natural language execution
        result = execute_natural_language(args.query, args.output)
        sys.exit(0 if result['success'] else 1)

    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("TIP: For natural language, just provide your request:")
        print('  python execute_action.py "Send email to john@example.com"')
        sys.exit(1)


if __name__ == '__main__':
    main()
