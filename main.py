#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logzero
import numpy as np
import pandas as pd
from logzero import logger

from excp import (OutOfBounds, RoverExists)

logzero.logfile("./log/mars.log", maxBytes=1e6, backupCount=2, disableStderrLogger=True)


class Plateau:
    """
        Main class for landing a rover and moving it around.
    """
    pl = None
    active_hover = None
    actions = {'L': -1, 'R': 1, 'M': 0}
    cardinals = {'N': 0,
                 'E': 1,
                 'S': 2,
                 'W': 3}
    movement = {0: 1,
                1: 1,
                2: -1,
                3: -1}

    def __init__(self, size=None):
        """
        creates our grid plateau
        PS. the dataframe is not really needed, but using grid positioning over dataframes is fast and easily upgradable
        :param size: multi-dimensional list
        """
        if size is None:
            # Note, for the sake of simplicity I created a plateau with 40x30 as rectangular grid
            size = [[np.nan] * 6] * 6
        self.pl = pd.DataFrame(size)

    def add_rover(self, x: int, y: int, face: int) -> tuple:
        """
        lands a rover on the plateau
        :param x: integer position x of the grid
        :param y: integer position y of the grid
        :param face: integer rover facing
        :return: tuple x, y, face
        """
        if str(self.pl.iloc[x, y]) != 'nan':
            raise RoverExists('Rover {} already in position {}, {}'.format(self.pl.iloc[x, y], x, y))

        self.pl.iloc[x, y] = face
        logger.debug(('ADD', x, y, face))
        return x, y, face

    def move_hover(self, x: int, y: int, action: int) -> tuple:
        """
        moves our landed rover
        :param x: integer position x of the grid
        :param y: integer position y of the grid
        :param action: integer move or turn
        :return: tuple x, y, face
        """
        current = self.pl.iloc[x, y]

        if action != 0:
            turn = current + action
            self.pl.iloc[x, y] = 0 if turn > 3 else 3 if turn < 0 else turn
            logger.debug(('MOVE', action, x, y, self.pl.iloc[x, y]))
            return x, y, self.pl.iloc[x, y]

        nx = x
        ny = y

        if current in [0, 2]:
            ny += self.movement[current]
        else:
            nx += self.movement[current]

        if ny < 0 or nx < 0:
            raise OutOfBounds("Can't move a rover outside the plateau")

        if str(self.pl.iloc[nx, ny]) != 'nan':
            raise RoverExists()

        self.pl.iloc[nx, ny] = current
        self.pl.iloc[x, y] = np.nan
        logger.debug(('MOVE', action, nx, ny, current))
        return nx, ny, current

    def command(self, command: str) -> None:
        """
        parses and trigger the command action
        :param command: string
        :return: None
        """
        try:
            if ' ' in command:
                self.active_hover = None
                x, y, face = self.add_rover(*self.validate_command(command))
                self.active_hover = (x, y)
                return x, y, face

            x, y = self.active_hover
            for c in list(command):
                face = self.validate_command(c)
                x, y, face = self.move_hover(x, y, face)

            self.active_hover = None
            print(x, y, list(self.cardinals.keys())[list(self.cardinals.values()).index(face)])

        except (ValueError, TypeError, KeyError) as e:
            self.active_hover = None
            logger.exception(e)

        except (OutOfBounds, IndexError) as e:
            self.active_hover = None
            logger.exception(e)

    def validate_command(self, command: str) -> tuple or str:
        """
        validates the entered command
        :param command: string
        :return: normalized command as tuple or integer
        """
        if ' ' in command:
            x, y, face = command.split(' ')
            x = int(x)
            y = int(y)
            face = self.cardinals[face]
            return x, y, face

        return self.actions[command]


if __name__ == "__main__":
    commands = ('5 5',
                '1 2 N',
                'LMLMLMLMM',
                '3 3 E',
                'MMRMMRMRRM',
                )

    mars = Plateau()

    for c in commands:
        mars.command(c)
