import unittest
import main
from excp import (BadCommand, OutOfBounds, RoverExists, RoverNotSelected)

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.plateau = main.Plateau()

    def test_plateau_size(self):
        self.assertEqual(self.plateau.pl.size, 36)

    def test_add_rover(self):
        x, y, face = self.plateau.add_rover(1, 1, 2)
        self.assertEqual(self.plateau.pl.iloc[x, y], float(face))

        with self.assertRaises(IndexError):
            self.plateau.add_rover(100, 100, 0)

        with self.assertRaises(RoverExists):
            self.plateau.add_rover(x, y, 2)

    def test_move_hover(self):

        with self.assertRaises(OutOfBounds):
            x, y, face = self.plateau.add_rover(0, 0, 2)
            self.plateau.move_hover(0, 0, 0)

        with self.assertRaises(RoverExists):
            self.plateau.add_rover(x, y+1, 2)
            self.plateau.move_hover(x, y+1, 0)

        x, y, face = self.plateau.move_hover(0, 0, 1)
        self.assertEqual(face, 3)

        x, y, face = self.plateau.add_rover(3, 3, 0)
        x, y, face = self.plateau.move_hover(x, y, 0)
        self.assertEqual((x, y, face), (3, 4, 0))

    def test_command(self):
        self.plateau.command('4 4 N')
        self.assertIsNotNone(self.plateau.active_hover)
        self.plateau.command('4 4')
        self.assertIsNone(self.plateau.active_hover)

if __name__ == '__main__':
    unittest.main()
