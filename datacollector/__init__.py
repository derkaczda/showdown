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
        self.tmp_filepath = os.path.join(self.tmp_directory, self.filename)
        self.filepath = os.path.join(self.directory, self.filename)

        # The filepath where the actions of this agents are stored
        self.action_path = os.path.join(self.tmp_directory, f"actions_{self.username}_{self.filename}")

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
        self._save_json(self.tmp_filepath, {"game": self.battle_log})

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


    def add_battle_state(self, msg):
        """Add the response of the eval request to a list. This
        list will then be saved at the end of the battle"""
        self.battle_log.append(self._parse_msg(msg))
        self.turn = self.battle_log[-1]['turn']

    def add_action(self, action):
        """Append the chosen action for this turn."""
        self.action_list.append({"turn": self.turn, "action": action})     

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
        msg = f'''
        let b = battle.toJSON();
        var l = [
            "debugMode", "log", "inputLog","gameType", 
            "reportExactHP", "strictChoices", "rated",
            "messageLog", "formatData", "sides", "field",
            "prngSeed", "reportPercentages", "supportCancel",
            "effect", "effectState", "event", "prng", "hints",
            "queue", "formatid"
        ];
        var size = l.length;
        for (var i = 0;i < size; i++)
            delete b[l[i]];
        JSON.stringify(b)
        '''
        msg = msg.split('\n')
        msg = ' '.join(msg)
        return msg