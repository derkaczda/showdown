import hashlib
import time
import os
import json
import time

class DataCollector():
    def __init__(self, directory, is_collector, username):
        self.directory = directory
        self.is_collector = is_collector
        self.username = username
        
        self.filename_extension = ".json"
        self.filename = self._create_filename()

        self.merged_dir_name = "merged"
        self.raw_dir_name = "raw"
        self.raw_directory = os.path.join(self.directory, self.raw_dir_name)

        self.filepath = os.path.join(self.directory,self.raw_dir_name, self.filename)
        self.action_path = os.path.join(self.directory, self.raw_dir_name, f"{self.filename}_actions_{self.username}{self.filename_extension}")


        self._create_data_directory()
        self.battle_log = []

        self.turn = 0
        self.action_list = []
        self.eval_msg = self._generate_eval_msg()

    def _create_filename(self):
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        return str(hash.hexdigest()) + self.filename_extension

    def _create_data_directory(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        if not os.path.exists(self.raw_directory):
            os.mkdir(self.raw_directory)

    def save_battle_state(self):
        self._save_json(self.filepath, {"game": self.battle_log})

    def save_actions(self):
        self._save_json(self.action_path, {"actions": self.action_list})

    def _save_json(self, file_name, data):
        with open(file_name, 'a') as f:
            f.write(json.dumps(data, indent=4, separators=(',', ': ')))

    def add_battle_state(self, msg):
        self.battle_log.append(self._parse_msg(msg))
        self.turn = self.battle_log[-1]['turn']

    def add_start_turn(self, msg):
        tmp_msg = self._parse_msg(msg)
        self.start_turn = tmp_msg['turn']

    def add_action(self, action):
        self.action_list.append({"turn": self.turn, "action": action})     

    def msg_for_collector(self, msg):
        lines = msg.split('\n')
        response = f"||>>> {self.eval_msg}"
        if response in lines:
            return True
        return False

    def _parse_msg(self, msg):
        lines = msg.split('\n')
        state_line = lines[2].replace("||<<< ", "")
        state_line = state_line[1:-1]
        return json.loads(state_line)


    def _generate_eval_msg(self):
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