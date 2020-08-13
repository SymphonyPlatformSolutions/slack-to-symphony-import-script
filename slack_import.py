import re
from slack import WebClient
from slack.errors import SlackApiError
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig

class SlackImport():

    def __init__(self, slack_token, room_obj):
        self.slack_token = slack_token
        self.user_id_map = {"U015552PASZ" : 349026222344902, "U015CQTAX3N" : 349026222342182, "U014RRQNMT9": 349026222349151, "U014SCKJWDV": 349026222349151}
        self.client = WebClient(token=self.slack_token)
        self.room_obj = room_obj

    #returns array of all slack channels your app/bot is a member of:
    def get_slack_channels(self):
        response = client.conversations_list().get('channels')
        rooms = []
        for i in response:
            room_attributes = {"name": "", "description": "", "public": "", "creator": "", "conversation_id": ""}
            room_attributes.update(name = i.get('name'))
            room_attributes.update(description = i.get('purpose').get('value'))
            room_attributes.update(public = not i.get('is_private'))
            room_attributes.update(creator = i.get('creator'))
            room_attributes.update(conversation_id = i.get('id'))
            rooms.append(room_attributes)
        return rooms

    def clean_messages(self, channel_id, symphony_stream_id):
        #get messages from desired chatroom
        slack_messages = self.client.conversations_history(channel=channel_id)
        #array to store cleaned messages
        cleaned_messages = []

        for i in slack_messages.get('messages'):
            cleaned_message = {"message": "", "intendedMessageTimestamp": "", "intendedMessageFromUserId": "", "originatingSystemId" : "Slack", "streamId": symphony_stream_id}
            cleaned_message.update(message = '<messageML>' + i.get('text') + "</messageML>")
            cleaned_message.update(intendedMessageTimestamp = int(i.get('ts').split('.')[0] + i.get('ts').split('.')[1][:3]))
            cleaned_message.update(intendedMessageFromUserId = i.get('user'))

            if i.get('user') in self.user_id_map:
                cleaned_message.update(intendedMessageFromUserId = self.user_id_map.get(i.get('user')))
            cleaned_messages.append(cleaned_message)
        return cleaned_messages

    def format_mentions(self, msg_array):
        regex_pattern = '<@...........>'
        for i in msg_array:
            match = re.findall(regex_pattern, i.get('message'))
            if match:
                if match[0][2:-1] in self.user_id_map:
                    i.update(message = i.get('message').replace(match[0], "<mention uid=\"" + str(self.user_id_map.get(match[0][2:-1])) + "\"/>"))
        return msg_array

    #imports cleaned messages array into desired room:
    #cleaned_messages -> array of cleaned message objected returned from clean_messages()
    def import_messages(self, bot_client, cleaned_messages):
        print('----------------------')
        print(cleaned_messages)
        bot_client.get_message_client().import_message(cleaned_messages)
        return None

    def run_import(self, bot_client):
        print(self.room_obj)
        for i in self.room_obj:
            formatted_messages = self.format_mentions(self.clean_messages(i.get("conversation_id"), i.get("stream_id")))
            self.import_messages(bot_client, formatted_messages)
