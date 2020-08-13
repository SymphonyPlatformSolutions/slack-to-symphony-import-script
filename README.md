# slack-to-symphony-import-script
A script for importing a Slack environment into Symphony. 

## Usage:

$ python3 main_slack.py --auth "rsa" --config "PATH_TO_CONFIG_FILE"

## Prerequisites:

#### Symphony Bot:

* Symphony Bot and corresponding service account
* Symphony Bot needs to have Content Management and Content Export Service Roles

#### Slack Bot:

* Slack bot (app) needs to be in the channel that you wish to import over to Symphony
* All channels that app is apart of will be imported into Symphony

#### Slack Bot must be able to:

* View messages and other content in public channels that Conversation Manager has been added to
* View messages and other content in private channels that Conversation Manager has been added to
* View files shared in channels and conversations that Conversation Manager has been added to
* View messages and other content in group direct messages that Conversation Manager has been added to
* View basic information about public channels in the workspace
* View basic information about private channels that Conversation Manager has been added to
* View basic information about direct messages that Conversation Manager has been added to
* View basic information about group direct messages that Conversation Manager has been added to
