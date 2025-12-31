import time

import ujson as json
import os

from urandom import randint


class BriansBrain:
    def __init__(self, initialCells = None):
        self.cells = initialCells or {}
        self.generation = 0
        self.runCount = 1
        self.lastSaveTimestamp = None
        self.stats = {'totalActive': 0, 'onCount':0, 'dyingCount':0, 'activityPct': 0.0}

    def evolve(self):
        neighbors = [(dx, dy) for dx in (-1,0,1) for dy in (-1,0,1) if (dx, dy) != (0,0)]
        on_neighbors_count = {}

        for (x, y), state in self.cells.items():
            if state == 1:
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    on_neighbors_count[(nx, ny)] = on_neighbors_count.get((nx, ny), 0) + 1

        new_cells = {}

        for pos, state in self.cells.items():
            if state == 1:
                new_cells[pos] = 2  # on → dying
            elif state == 2:
                pass

        for pos, count in on_neighbors_count.items():
            if count == 2 and pos not in self.cells:
                new_cells[pos] = 1

        self.cells = new_cells
        self.generation += 1

        on = sum(1 for s in self.cells.values() if s == 1)
        dying = len(self.cells) - on
        totalActive = on + dying

        self.stats = {
            'onCount': on,
            'dyingCount': dying,
            'totalActive': totalActive,
            'activityPct': round(on / max(totalActive, 1) * 100, 2) if totalActive else 0
        }

        if totalActive == 0 and self.generation > 10:
            print("Simulation is dead, starting new game")
            self.restartGame()

    def restartGame(self, isFirst = False):
        count = randint(80,150)
        self.cells = randomBrainCells(count, 40)
        self.generation = 0
        self.lastSaveTimestamp = None
        if not isFirst:
            self.runCount += 1
        print(f"New game nr {self.runCount} started with {count} cells!")

    def getState(self):
        return {
            'generation': self.generation,
            'runCount': self.runCount,
            'lastSaveTimestamp': self.lastSaveTimestamp,  # może być None lub string
            'cells': [(x, y, state) for (x, y), state in self.cells.items()],
            'stats': self.stats
        }

    def getStats(self):
        return {
            'generation': self.generation,
            'runCount': self.runCount,
            'lastSaveTimestamp': self.lastSaveTimestamp,
            'stats': self.stats
        }

    def saveState(self):
        try:
            t = time.localtime()
            timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                t[0], t[1], t[2], t[3], t[4], t[5]
            )
            self.lastSaveTimestamp = timestamp_str
            state = self.getState()
            with open('game_state.json', 'w') as f:
                json.dump(state, f)
            print("Saved state.")
        except Exception as e:
            print("Error during save:", e)

    def loadState(self):
        try:
            if 'game_state.json' in os.listdir():
                with open('game_state.json', 'r') as f:
                    data = json.load(f)
                    self.cells = {(x,y): state for x,y,state in data['cells']}
                    self.generation = data.get('generation', 0)
                    self.runCount = data.get('runCount', 1)
                    self.lastSaveTimestamp = data.get('lastSaveTimestamp')
                    self.evolve()
                    self.generation -= 1
                print(f"State loaded from file: Run {self.runCount}, Gen {self.generation}")
            else:
                print("Not found saved state - starting from beginning.")
                self.restartGame(True)
        except Exception as e:
            print("Loading error:", e)
            self.restartGame(True)

def randomBrainCells(count=100, grid=30):
    cells = {}
    offsetX = grid // 2
    offsetY = grid // 2
    for _ in range(count):
        x = randint(-offsetX, offsetX)
        y = randint(-offsetY, offsetY)
        cells[(x,y)] = 1
    return cells