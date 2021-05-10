import hashlib
import time
import os

class DataCollector():
    def __init__(self, directory, battle_tag):
        self.directory = directory
        self.filename_extension = ".txt"
        self.filename = self._create_filename()
        self.filepath = os.path.join(self.directory, self.filename)

        self._create_data_directory()
        self._tag_dataset(battle_tag)
        self.tmp_counter = 0

    def _create_filename(self):
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        return str(hash.hexdigest()) + self.filename_extension

    def _create_data_directory(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

    def _tag_dataset(self, battle_tag):
        with open(self.filepath, "w") as f:
            f.write(f"battle tag: {battle_tag}")

    def save(self, battle):
        my_pokemon = battle.user.reserve
        my_pokemon.append(battle.user.active)
        opponent_pokemon = battle.opponent.reserve
        opponent_pokemon.append(battle.opponent.active)
        with open(self.filepath, "a") as f:
            f.write("------------- \n")
            f.write(f"iteration: {self.tmp_counter}")
            f.write(f"my pokemon: {str(my_pokemon)}")
            f.write(f"opponent pokemon: {str(opponent_pokemon)}\n")
            f.write("------------- \n")
        self.tmp_counter += 1

