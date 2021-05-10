import hashlib
import time
import os

class DataCollector():
    def __init__(self, directory, battle_tag):
        self.directory = directory
        self.raw_dir_name = "raw"
        self.filename_extension = ".txt"
        self.filename = self._create_filename()
        self.filepath = os.path.join(self.directory,self.raw_dir_name, self.filename)

        self._create_data_directory()
        self._tag_dataset(battle_tag)
        self.battle_log = []

    def _create_filename(self):
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        return str(hash.hexdigest()) + self.filename_extension

    def _create_data_directory(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        if not os.path.exists(os.path.join(self.directory, self.raw_dir_name)):
            os.mkdir(os.path.join(self.directory, self.raw_dir_name))

    def _tag_dataset(self, battle_tag):
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
        self.battle_log.append(state)

