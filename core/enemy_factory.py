from entities.dino import Dino, TRex, Triceratops


class EnemyFactory:
    _registry = {"triceratops": Triceratops, "t_rex": TRex}

    @staticmethod
    def create_enemy(enemy_type: str, grid_y: int, grid_x: int, waypoints: list):
        builder = EnemyFactory._registry.get(enemy_type)

        if builder:
            return builder(grid_y=grid_y, grid_x=grid_x, waypoints=waypoints)
        else:
            return Dino(
                grid_y=grid_y, grid_x=grid_x, dino_type=enemy_type, waypoints=waypoints
            )
