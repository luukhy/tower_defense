"""This module contains the implementation for wave manager class."""

import random

from entities.dino import Dino


class WaveManager:
    """Wave Manager holds logic for spawning - when and where, according to the current state of the game."""

    def __init__(self, game_map, target_x, target_y):
        self.game_map = game_map
        self.target_x = target_x
        self.target_y = target_y

    def spawn_wave(self, config) -> list[Dino]:
        """Calculates a wave and RETURNS a list of ready-to-go Dinos."""
        dinos_num = config["num_dinos"]
        dinos_type = config["first_wave_type"]
        dinos_pos = self.generate_dinos_pos(dinos_num)

        new_wave = []

        for pos in dinos_pos:
            start_x = pos["x"]
            start_y = pos["y"]

            path = self.game_map.get_path_a_star(
                start_x, start_y, self.target_x, self.target_y
            )

            if path:
                new_dino = Dino(
                    grid_y=start_y, grid_x=start_x, dino_type=dinos_type, waypoints=path
                )
                new_wave.append(new_dino)  # Add to our local list
            else:
                print(f"Skipped dino at {start_x}, {start_y}: No path to base!")

        return new_wave

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
