import hashlib
import time
import os
import json
import time

class DataCollector():
    def __init__(self, directory, is_collector, username):
        self.directory = directory
        self.username = username

        # Only one agent needs to collect the battle states
        # the other agent only collects his chosen actions.
        # This can be controlled with the env variable DATA_COLLECTOR=True
        self.is_collector = is_collector
        
        self.filename_extension = ".json"
        self.filename = self._create_filename()

        self.tmp_directory = os.path.join(self.directory, "tmp")
        self._create_directories([self.tmp_directory])

        # The filepath where the battle state is stored.
        # First we store it in a tmp directory because
        # we need to merge the chosen actions into it.
        # Afterwards we move it into the real directory
        self.filepath = os.path.join(self.directory, self.filename)

        # The filepath where the actions of this agents are stored
        self.action_filename = f"actions_{self.username}_{self.filename}"
        self.action_path = os.path.join(self.tmp_directory, self.action_filename)

        # Generate the eval request message so we don't need to
        # create it with every request.
        self.eval_msg = self._generate_eval_msg()

        self.turn = 0
        self.action_list = []
        self.battle_log = []

    def _create_filename(self):
        """Create a unique hash for the filename"""
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        return str(hash.hexdigest()) + self.filename_extension

    def _create_directories(self, dir_list):
        for dir in dir_list:
            os.makedirs(dir, exist_ok=True)

    def save_battle_state(self):
        """Save the collected results from the eval request to disk."""
        self._merge_actions_and_state()
        self._save_json(self.filepath, {"game": self.battle_log})
        self._delete_directory(self.tmp_directory)

    def save_actions(self):
        """Save the chosen actions of the agent into a tmp file"""
        self._save_json(self.action_path, {"actions": self.action_list})

    # Save dictionary as json.
    # Formated allows for a more readable result.
    def _save_json(self, file_name, data, formated=True):
        with open(file_name, 'a') as f:
            if formated:
                f.write(json.dumps(data, indent=4, separators=(',', ': ')))
            else:
                f.write(json.dumps(data))

    def _merge_actions_and_state(self):
        actions_other_agent = self._get_other_agent_actions()
        print(f"length of battle log {len(self.battle_log)}, length of my actions {len(self.action_list)}, of other agent {len(actions_other_agent)}")

        for i in range(0, len(self.battle_log)):
            # the sides key is a list with two entries, one for each player
            # we need to find our list entry to append the action to it
            list_index = 0 if self.battle_log[i]["sides"][0]["name"] == self.username else 1
            other_list_index = 1 if list_index == 0 else 0

            self.battle_log[i]["sides"][list_index].update({"action": self.action_list[i]})
            if i >= len(actions_other_agent):
                self.battle_log[i]["sides"][other_list_index].update({"action": "None"})
            else:
                self.battle_log[i]["sides"][other_list_index].update({"action": actions_other_agent[i]})


    def _get_other_agent_actions(self):
        """Search for the action file of the other agent
        and parse these actions"""
        other_filename = self._get_other_agent_file()
        print(f"the other filename is {other_filename}")
        return self._read_json(os.path.join(self.tmp_directory, other_filename))["actions"]

    def _read_json(self, file):
        with open(file, 'r') as f:
            return json.load(f)

    def _get_other_agent_file(self):
        file_list = os.listdir(self.tmp_directory)
        for filename in file_list:
            if (filename != self.filename and
                filename != self.action_filename):
                return filename

    def _delete_directory(self, directory):
        file_list = os.listdir(directory)
        for filename in file_list:
            os.remove(os.path.join(directory, filename))
        os.rmdir(directory)

    def add_battle_state(self, msg):
        """Add the response of the eval request to a list. This
        list will then be saved at the end of the battle"""
        self.battle_log.append(self._parse_msg(msg))
        self.turn = self.battle_log[-1]['turn']

    def add_action(self, action):
        """Append the chosen action for this turn."""
        self.action_list.append(action)     

    def msg_for_collector(self, msg):
        """Check if the message is the response to a eval request, 
        if not it is not interesting for us"""
        lines = msg.split('\n')
        response = f"||>>> {self.eval_msg}"
        if response in lines:
            return True
        return False

    def _parse_msg(self, msg):
        """Parse the eval response message"""
        lines = msg.split('\n')
        state_line = lines[2].replace("||<<< ", "")
        state_line = state_line[1:-1]
        return json.loads(state_line)


    def _generate_eval_msg(self):
        """Generate a string to send as a eval response"""

        # Bool state variables which should not be interesting for
        # learning the game:
        # debugMode, rated, reportExactHP, strictChoices

        # Logs which should not be interesting (and grow very fast in size):
        # log, inputLog, messageLog

        # Positional information which should not be interesting:
        # sentLogPos, lastMoveLine

        # Misc:
        # queue, faintQueue
        msg = f'''
        let b = battle.toJSON();
        var l = [
            "debugMode", "rated", "reportExactHP", "strictChoices",

            "log", "inputLog", "messageLog",

            "sentLogPos", "lastMoveLine",

            "queue", "faintQueue"
        ];
        var size = l.length;
        for (var i = 0;i < size; i++)
            delete b[l[i]];
        JSON.stringify(b)
        '''
        msg = msg.split('\n')
        msg = ' '.join(msg)
        return msg