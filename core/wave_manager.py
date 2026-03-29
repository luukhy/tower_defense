"""This module contains the implementation for wave manager class."""

import json
import random

from entities.dino import Dino

with open("core/config.json", "r") as file:
    config = json.load(file)


class WaveManager:
    """Wave Manager holds logic for spawning - when and where, according to the current state of the game."""

    def __init__(self, game_map, target_x, target_y):
        self.game_map = game_map
        self.target_x = target_x
        self.target_y = target_y
        self.config = config

    def spawn_wave(self, wave) -> list[Dino]:
        """Calculates a wave and RETURNS a list of ready-to-go Dinos."""
        wave_config = self.config[str(wave)]
        dinos_num_list = wave_config["dinos_num"]
        dino_types_list = wave_config["dino_types"]

        total_dinos = sum(dinos_num_list)
        dinos_pos = self.generate_dinos_pos(total_dinos)

        new_wave = []

        for i, pos in enumerate(dinos_pos):
            dino_type = self.get_dino_type(i, dino_types_list, dinos_num_list)
            start_x = pos["x"]
            start_y = pos["y"]

            path = self.game_map.get_path_a_star(
                start_x, start_y, self.target_x, self.target_y
            )

            if path:
                new_dino = Dino(
                    grid_y=start_y, grid_x=start_x, dino_type=dino_type, waypoints=path
                )
                new_wave.append(new_dino)
            else:
                print(f"Skipped dino at {start_x}, {start_y}: No path to base!")

        return new_wave

    def get_dino_type(self, curr_id: int, types_list: list, counts_list: list) -> str:
        """
        Determines the dino type based on its index.
        Example: If counts are [20, 10], IDs 0-19 are Type 0, IDs 20-29 are Type 1.
        """
        running_sum = 0
        for i, count in enumerate(counts_list):
            running_sum += count
            if curr_id < running_sum:
                return types_list[i]

        # if anything goes wrong
        return types_list[-1]

    def add_dinos_to_scene(self):
        for dino in self.dinos:
            self.scene.addItem(dino)

    def generate_dinos_pos(self, dinos_num):
        walkable_tiles = self.game_map.get_walkable_tiles()
        if dinos_num > len(walkable_tiles):
            dinos_num = len(walkable_tiles)

        random_idx = set()
        while len(random_idx) < dinos_num:
            random_id = random.randint(0, len(walkable_tiles) - 1)
            random_idx.add(random_id)

        pos = []
        for id in random_idx:
            tile = walkable_tiles[id]
            pos.append({"x": tile.x_grid, "y": tile.y_grid})
        return pos


if __name__ == "__main__":
    print(config)
