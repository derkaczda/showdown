import hashlib
import time
import os
import json
import time

class DataCollector():
    def __init__(self, directory, battle_tag, is_merger):
        self.directory = directory
        self.is_merger = is_merger
        self.battle_tag = battle_tag
        
        self.filename_extension = ".txt"
        if self.is_merger:
            self.filename = "0_" + battle_tag 
            self.other_filename = "1_" + battle_tag
        else:
            self.filename = "1_" + battle_tag #self._create_filename()

        self.merged_dir_name = "merged"
        self.raw_dir_name = "raw"
        self.raw_directory = os.path.join(self.directory, self.raw_dir_name)
        self.merged_directory = os.path.join(self.directory, self.merged_dir_name)

        self.filepath = os.path.join(self.directory,self.raw_dir_name, self.filename)
        self.filepath_merged = os.path.join(self.directory, self.merged_dir_name, self.filename)

        self._create_data_directory()
        self.battle_log = {}

        self.turn = 0

    def _create_filename(self):
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        return str(hash.hexdigest()) + self.filename_extension

    def _create_data_directory(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        if not os.path.exists(self.raw_directory):
            os.mkdir(self.raw_directory)
        if not os.path.exists(self.merged_directory):
            os.mkdir(self.merged_directory)

    def tag_dataset(self, battle_tag):
        with open(self.filepath, "w") as f:
            f.write(f"{battle_tag}\n")

    def save(self):
        with open(self.filepath, "a") as f:
            f.write(str(self.battle_log))

    def add(self, battle):
        state = {
            "weather": battle.weather,
            "started": battle.started,
            "field": battle.field,
            "user": battle.user.to_dict(),
            "opponent": battle.opponent.to_dict()
        }
        self.battle_log.update({str(self.turn): state})
        self.turn += 1

    def merge(self):
        if not self.is_merger:
            return

        other_filepath = os.path.join(self.raw_directory, self.other_filename)
        if not os.path.exists(other_filepath):
            print("MERGE FAILED!!!")
        

    def _find_filename_of_other_agent(self):
        file_list = os.listdir(self.raw_directory)
        for filename in file_list:
            path = os.path.join(self.raw_directory, filename)
            with open(path, 'r') as f:
                battle_tag = f.readline()
                if battle_tag == self.battle_tag:
                    return path
        print("MERGING: file of second agent not found")
        return ""

    def msg_for_collector(self, msg):
        lines = msg.split('\n')
        response = f"||>>> {self.request_msg()}"
        if response in lines:
            return True
        return False

    def parse_msg(self, msg):
        lines = msg.split('\n')
        state_line = lines[2]
        with open('log.txt', 'a') as f:
            f.write(f"{state_line}\n\n")


    def request_msg(self):
        return 'let b = battle.toJSON(); delete b["log"]; delete b["inputLog"]; b'