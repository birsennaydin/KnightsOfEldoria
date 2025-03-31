# tests/test_hunter.py
import unittest
from models.hunter import Hunter
from controllers.hunter_controller import HunterController
from utils.enums import CellType, HunterSkill, TreasureType
from ai.pathfinding.astar import astar
from models.grid import Grid
from models.knight import Knight
from models.treasure import Treasure

class TestHunterMovement(unittest.TestCase):

    def setUp(self):
        """Set up a simple grid and Hunter for testing pathfinding."""
        self.grid = Grid(size=10)
        self.hunter = Hunter("Hunter-1", HunterSkill.NAVIGATION, 5, 5)
        self.hunter_controller = HunterController(self.grid)
        self.grid.place_hunter(self.hunter)

    def test_astar_no_obstacle(self):
        """Test if A* pathfinding works without obstacles."""
        goal = (8, 8)  # a simple goal position
        path = astar(self.grid, (5, 5), goal)
        self.assertTrue(path, "A* should return a valid path.")
        self.assertEqual(path[-1], goal, "The path should end at the goal.")

    def test_astar_with_knight_obstacle(self):
        """Test if A* avoids knights blocking the path."""
        self.grid.place_knight(Knight("Knight-1", 6, 6))  # Place a knight blocking the path
        goal = (8, 8)
        path = astar(self.grid, (5, 5), goal)
        self.assertTrue(path, "A* should return a valid path even with a knight.")
        self.assertNotIn((6, 6), path, "Path should not pass through knight's position.")

    def test_hunter_movement_towards_treasure(self):
        """Test if the hunter moves towards the treasure correctly."""
        treasure_pos = (8, 8)
        self.grid.place_treasure(Treasure(TreasureType.GOLD, treasure_pos[0], treasure_pos[1]))

        # Simulating multiple steps
        for _ in range(10):  # Test several iterations
            self.hunter_controller.process(self.hunter)

        self.assertEqual(self.hunter.x, 6, "Hunter should move towards the treasure.")
        self.assertEqual(self.hunter.y, 6, "Hunter should move towards the treasure.")

    def test_no_path_to_treasure(self):
        """Test if A* handles the situation when there's no path to the treasure."""
        self.grid.place_knight(Knight("Knight-2", 6, 6))  # Block the path with a knight
        path = astar(self.grid, (5, 5), (8, 8))  # Trying to reach treasure
        self.assertEqual(path, [], "A* should return an empty path if no path exists.")

if __name__ == '__main__':
    unittest.main()
