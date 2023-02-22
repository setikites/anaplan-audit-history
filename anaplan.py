# ===============================================================================
# Description:    Main module for invocation of Anaplan operations
# ===============================================================================

import sys
import logging

import utils
import AnaplanOauth
import AuthToken
import AnaplanOps

# Clear the console
utils.clear_console()

# Enable logging
logger = logging.getLogger(__name__)

# Get configurations
settings = utils.read_configuration_settings()
args = utils.read_cli_arguments()

# Set configurations
device_id_uri = settings['get_device_id_uri']
tokens_uri = settings['get_tokens_uri']
users_uri = settings['get_users_uri']
audit_events_uri = settings['get_audit_events_uri']
workspaces_uri = settings['get_workspaces_uri']
register = args.register
database_file = "audit.db3"
AuthToken.Auth.client_id = args.client_id
if args.token_ttl == "":
	AuthToken.Auth.token_ttl = int(args.token_ttl)

# If register flag is set, then request the user to authenticate with Anaplan to create device code
if register:
	logger.info('Registering the device with Client ID: %s' %
	            AuthToken.Auth.client_id)
	AnaplanOauth.get_device_id(device_id_uri)
	AnaplanOauth.get_tokens(tokens_uri)

else:
	print('Skipping device registration and refreshing the access_token')
	logger.info('Skipping device registration and refreshing the access_token')
	AnaplanOauth.refresh_tokens(tokens_uri, 0)

# Start background thread to refresh the `access_token`
refresh_token = AnaplanOauth.refresh_token_thread(
	1, name="Refresh Token", delay=AuthToken.Auth.token_ttl, uri=tokens_uri)
refresh_token.start()

# Load User Activity Codes
AnaplanOps.get_usr_activity_codes(database_file=database_file)

# Get Users
AnaplanOps.get_users(users_uri, database_file)

# Get Workspaces
AnaplanOps.get_anaplan_paged_data(uri=workspaces_uri, token_type="Bearer ", database_file=database_file,
                                  database_table="workspaces", record_path="workspaces", json_path=['meta', 'paging', 'next'])

# Get Models in all Workspace

# Get Import Actions in all Models in all Workspaces

# Get Export Actions in all Models in all Workspaces

# Get Process in all Models in all Workspaces

# Get Actions in all Models in all Workspaces


# Get Import Actions
AnaplanOps.get_anaplan_paged_data(uri=workspaces_uri, token_type="Bearer ", database_file=database_file,
                                  database_table="actions", record_path="imports", json_path=['meta', 'paging', 'next'])

# Get Events
AnaplanOps.get_anaplan_paged_data(uri=audit_events_uri, token_type="AnaplanAuthToken ", database_file=database_file,
                                  database_table="events", record_path="response", json_path=['meta', 'paging', 'nextUrl'])


# Exit with return code 0
sys.exit(0)
