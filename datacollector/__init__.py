import hashlib
import time
import os
import json
import time
import pickle

class DataCollector():
    def __init__(self, directory, is_collector, username, other_user, battle_tag, save_as_json=False):
        self.directory = directory
        self.username = username
        self.other_user = other_user
        self.battle_tag = battle_tag
        self.save_as_json = save_as_json

        # Only one agent needs to collect the battle states
        # the other agent only collects his chosen actions.
        # This can be controlled with the env variable DATA_COLLECTOR=True
        self.is_collector = is_collector
        
        self.filename_extension = ".pkl"

        self.tmp_directory = os.path.join(self.directory, "tmp")
        self._create_directories([self.tmp_directory])

        # The filepath where the actions of this agents are stored
        self.action_filename = f"{self.battle_tag}_{self.username}"
        self.action_path = os.path.join(self.tmp_directory, self.action_filename)

        # if we are the collector we also save the complete battle state
        self.battle_log_filename = f"battlelog_{self.battle_tag}_{self.username}"
        self.battle_log_path = os.path.join(self.tmp_directory, self.battle_log_filename)

        # Generate the eval request message so we don't need to
        # create it with every request.
        self.eval_msg = self._generate_eval_msg()

        self.turn = 0
        self.action_list = []
        self.action_list_2 = []
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
        self.save_actions()
        if self.is_collector:
            self.save_battle_log()
            self._merge_actions_and_state()
        pass

    def save_actions(self):
        """Save the chosen actions of the agent into a tmp file"""
        self._save_pickle(self.action_path, {"actions": self.action_list})
        if self.save_as_json:
            self._save_json(self.action_path+".json", {"actions": self.action_list_2})

    def save_battle_log(self):
        self._save_pickle(self.battle_log_path, {"battlelog" : self.battle_log})
        if self.save_as_json:
            self._save_json(self.battle_log_path+".json", {"battlelog" : self.battle_log})

    # Save dictionary as json.
    # Formated allows for a more readable result.
    def _save_json(self, file_name, data, formated=True):
        with open(file_name, 'a') as f:
            if formated:
                f.write(json.dumps(data, indent=4, separators=(',', ': ')))
            else:
                f.write(json.dumps(data))

    def _save_pickle(self, filename, data):
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

    def _load_pickle(self, path):
        with open(path, 'rb') as f:
             return pickle.load(f)

    def _merge_actions_and_state(self):
        """
        merge the battlelog and action files
        into one single files
        """
        pairs = self._get_agent_pairs()

        for pair in pairs:
            battle, collector_actions, other_actions = pair
            for i in range(len(battle)):
                # the sides key is a list with two entries, one for each player
                # we need to find our list entry to append the action to it
                list_index = 0 if battle[i]["sides"][0]["name"] == self.username else 1
                other_list_index = 1 if list_index == 0 else 0

                battle[i]["sides"][list_index].update({"action": collector_actions[i]})
                if i >= len(other_actions):
                    battle[i]["sides"][other_list_index].update({"action": "None"})
                else:
                    battle[i]["sides"][other_list_index].update({"action": other_actions[i]})

            path = os.path.join(self.directory, self._create_filename())
            self._save_pickle(path, {"game" : battle})
            if self.save_as_json:
                self._save_json(path+".json", {"game" : battle})



    def _get_other_agent_actions(self):
        """Search for the action file of the other agent
        and parse these actions"""
        other_filename = self._get_other_agent_file()
        print(f"the other filename is {other_filename}")
        return self._load_pickle(os.path.join(self.tmp_directory, other_filename))["actions"]

    def _get_agent_pairs(self):
        """
        find all the data in the tmp directory corresponding
        to a game this agent played. This means battle state, actions
        and actions of the other user. Delete the temporary files afterwards
        """
        filelist = os.listdir(self.tmp_directory)
        collectors = []
        for file in filelist:
            filename_content = file.split("_")
            if filename_content[0] == "battlelog" and filename_content[-1] == self.username:
                collectors.append(file)

        print(f"found {len(collectors)} collectors")

        pairs = []
        for collector in collectors:
            filename_content = collector.split("_")
            battle_tag = filename_content[-2]
            my_actions_file = self._find_user(filelist, self.username, battle_tag)
            other_actions_file = self._find_user(filelist, self.other_user, battle_tag)
            if my_actions_file == "" or other_actions_file == "":
                continue
            
            print(f"found pair {my_actions_file}, {other_actions_file}")
            battle = self._load_pickle(os.path.join(self.tmp_directory, collector))
            my_actions = self._load_pickle(os.path.join(self.tmp_directory, my_actions_file))
            other_actions = self._load_pickle(os.path.join(self.tmp_directory, other_actions_file))
            pairs.append((battle["battlelog"], my_actions["actions"], other_actions["actions"]))
            if self.save_as_json:
                os.remove(os.path.join(self.tmp_directory, collector))
                os.remove(os.path.join(self.tmp_directory, my_actions_file))
                os.remove(os.path.join(self.tmp_directory, other_actions_file))
        return pairs

    def _find_user(self, filelist, username,battle_tag):
        for file in filelist:
            filename_content = file.split("_")
            if (filename_content[-1] == username and filename_content[-2] == battle_tag
                and len(filename_content) == 2):
                return file
        return ""         
        

    def _read_json(self, file):
        with open(file, 'r') as f:
            return json.load(f)

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

    def add_action(self, action, turn):
        """Append the chosen action for this turn."""
        self.action_list.append(action)     
        self.action_list_2.append((action, turn))     

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