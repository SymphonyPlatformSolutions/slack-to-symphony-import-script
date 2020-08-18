from slack import WebClient
from slack.errors import SlackApiError
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.exceptions.APIClientErrorException import APIClientErrorException

class SlackRoom():

    def __init__(self, slack_token):
        self.slack_token = slack_token
        self.user_id_map = """{SLACK_USER_ID: SYMPHONY_USER_ID"""
        self.client = WebClient(token=self.slack_token)

    def get_rooms(self):
        response = self.client.conversations_list().get('channels')
        rooms = []
        for i in response:
            room_attributes = {"conversation_id": "", "slack_room_name": "", "stream_id": "", "members": [], "room": {"name": "", "description": "", "public": ""}}
            room_attributes.update(slack_room_name=i.get('name'))
            room_attributes['room'].update(name=i.get('name'))
            room_attributes['room'].update(description = i.get('purpose').get('value'))
            if i.get('purpose').get('value') == '':
                room_attributes['room'].update(description = 'default description')
            room_attributes['room'].update(public = not i.get('is_private'))
            room_attributes.update(conversation_id = i.get('id'))
            rooms.append(room_attributes)
        return rooms

    def add_members_to_rooms_array(self,rooms_array):
        for i in rooms_array:
            i.update(members=self.client.conversations_members(channel=i.get("conversation_id")).get('members'))
        return rooms_array

    def convert_slack_to_sym_ids(self, rooms_array):
        for i in rooms_array:
            updated_members = [self.user_id_map.get(j) for j in i.get('members') if j in self.user_id_map]
            i.update(members=updated_members)
        return rooms_array

    def create_room(self, bot_client, rooms_array):
        for i in range(0, len(rooms_array)):
            try:
                stream_id = bot_client.get_stream_client().create_room(rooms_array[i].get('room')).get('roomSystemInfo').get('id')
            except APIClientErrorException as e:
                if 'Please choose another name' in e.args[0]:
                    rooms_array[i]['room'].update(name='{} PUT DEFUALT NAME HERE'.format(i))
                    stream_id = bot_client.get_stream_client().create_room(rooms_array[i].get('room')).get('roomSystemInfo').get('id')
            #return streamID and update conversation_id with returned streamID
            rooms_array[i].update(stream_id=stream_id)
        return rooms_array

    def add_members_to_symphony_room(self, rooms_array, bot_client):
        for i in rooms_array:
            for j in i.get('members'):
            #add members to given streamID
                bot_client.get_stream_client().add_member_to_room(i.get('stream_id'), j)
        return

    def import_rooms(self, bot_client):
        #Get rooms from Slack:
        rooms = self.get_rooms()[1:]
        #create the room objects, convert slack user ids, to symphony user ids, add updated members to room object:
        updated_rooms = self.create_room(bot_client, self.convert_slack_to_sym_ids(self.add_members_to_rooms_array(rooms)))
        #add members to symphony room:
        self.add_members_to_symphony_room(updated_rooms, bot_client)

        return updated_rooms
