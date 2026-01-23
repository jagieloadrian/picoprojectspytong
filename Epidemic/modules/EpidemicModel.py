import os
import time

import ujson as json
from urandom import randint, random, uniform
from modules.HumanStates import HumanStates, HumanType
from modules.config import getISO8601Time


class Epidemic:
    def __init__(self):
        self.cells = {} # (x,y) -> [state, ttl, type]
        self.populationSize = 150

        self.generation = 0
        self.runCount = 1

        # -- infection --
        self.baseInfectionProb = 0.8
        self.infectionProb = self.baseInfectionProb
        self.incubationMin = 2
        self.incubationMax = 5
        self.infectionMin = 3
        self.infectionMax = 6

        # --- lockdown ---
        self.lockdownActive = False
        self.lockdownThreshold = 36.0
        self.lockdownMultiplier = 0.4
        self.mobilityMultiplier = 1.0

        self.lastSaveTimestamp = None

        self.stats = {}

    # ------------------------------------------------------
    # python
    def evolve(self):
        neighbors = [(-1,-1),(-1,0),(-1,1),
                     (0,-1),        (0,1),
                     (1,-1),(1,0),(1,1)]

        infectedNeighbors = {}
        newExposed = set()
        updated = {}

        # --- preserve dead positions so they cannot be overwritten ---
        dead_positions = {pos for pos, (state, _, _) in self.cells.items() if state == HumanStates.D}

        # --- move ---
        movedCells = {}
        # first reserve dead cells (immutable)
        for pos in dead_positions:
            movedCells[pos] = self.cells[pos]

        for (x, y), cell in self.cells.items():
            state, ttl, t = cell

            # already reserved dead
            if state == HumanStates.D:
                continue

            nx, ny = self.moveAgent(x, y, t)
            target = (nx, ny)

            # never place into a reserved dead position or already occupied moved cell
            if target in movedCells or target in dead_positions:
                # try to keep agent in original cell if free and not dead
                if (x, y) not in movedCells and (x, y) not in dead_positions:
                    movedCells[(x, y)] = cell
                else:
                    # find a nearby free & non-dead cell
                    placed = False
                    for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                        pos = (x + dx, y + dy)
                        if pos not in movedCells and pos not in dead_positions:
                            movedCells[pos] = cell
                            placed = True
                            break
                    if not placed:
                        # last resort: keep at original if it's not a dead position (avoid overwriting dead)
                        if (x, y) not in dead_positions:
                            movedCells[(x, y)] = cell
                        # otherwise skip placing to avoid overwriting a dead cell
            else:
                movedCells[target] = cell

        self.cells = movedCells

        #  count infected neighbors
        for (x, y), (state, ttl, t) in self.cells.items():
            if state == HumanStates.I:
                for dx, dy in neighbors:
                    pos = (x+dx, y+dy)
                    if pos in self.cells:
                        infectedNeighbors[pos] = infectedNeighbors.get(pos, 0) + 1

        # --- new infections (S -> E) ---
        for pos, count in infectedNeighbors.items():
            # skip dead positions
            if pos in dead_positions:
                continue
            state, ttl, t = self.cells[pos]
            if state == HumanStates.S:
                mul = HumanType.TYPE_PROFILE[t]["infectMul"]
                prob = 1 - (1 - self.infectionProb * mul) ** count
                if random() < prob:
                    newExposed.add(pos)

        # --- state evolution ---
        # start by preserving dead cells in updated
        for pos in dead_positions:
            # keep original type for dead cells
            s, ttl, t = self.cells[pos]
            updated[pos] = [HumanStates.D, None, t]

        for pos, (state, ttl, t) in self.cells.items():
            # already preserved dead
            if pos in dead_positions:
                continue

            if state == HumanStates.E:  # incubation
                if ttl <= 1:
                    updated[pos] = [HumanStates.I, randint(self.infectionMin, self.infectionMax), t]
                else:
                    updated[pos] = [HumanStates.E, ttl-1, t]

            elif state == HumanStates.I:
                if random() < HumanType.TYPE_PROFILE[t]["mortality"]:
                    # newly dead — allowed
                    updated[pos] = [HumanStates.D, None, t]
                    # ensure newly dead position is reserved for this tick (avoid future overwrites within same evolve)
                    dead_positions.add(pos)
                elif ttl <= 1:
                    updated[pos] = [HumanStates.R, None, t]
                else:
                    updated[pos] = [HumanStates.I, ttl-1, t]  # illness

            else:
                updated[pos] = [state, ttl, t]

        #  add new exposed (skip dead positions and never overwrite dead)
        for pos in newExposed:
            if pos in dead_positions:
                continue
            t = self.cells[pos][2]
            updated[pos] = [HumanStates.E, randint(self.incubationMin, self.incubationMax), t]

        self.cells = updated
        self.generation += 1

        self.updateStats()
        self.handleLockdown()

        if self.stats["infected"] == 0 and self.generation > 15:
            print("Epidemic ended – restarting…")
            self.restartGame()

    def moveAgent(self, x, y, t):
        mobility = HumanType.TYPE_PROFILE[t]["mobility"] * self.mobilityMultiplier
        if random() > mobility:
            return x, y
        return x + randint(-1, 1), y + randint(-1, 1)

    def handleLockdown(self):
        """Lockdown logic - separately"""
        infectedPct = round(self.stats['infected']/self.populationSize * 100,2)

        if not self.lockdownActive and infectedPct >= self.lockdownThreshold:
            self.lockdownActive = True
            self.infectionProb = self.baseInfectionProb * self.lockdownMultiplier
            self.mobilityMultiplier = 0.3
            print("🔒 LOCKDOWN ON")

        elif self.lockdownActive and infectedPct < self.lockdownThreshold * 0.5:
            self.lockdownActive = False
            self.infectionProb = self.baseInfectionProb
            self.mobilityMultiplier = 1.0
            print("🔓 LOCKDOWN OFF")

    # ------------------------------------------------------
    def getRandomInfectionTTL(self):
        return randint(2, 5)

    # ------------------------------------------------------
    def restartGame(self, isFirst=False):
        self.populationSize = randint(100, 300)
        seed = max(1, int(self.populationSize * uniform(0.1, 0.3)))

        grid = int((self.populationSize ** 0.5) * 1.4)
        offset = grid // 2

        self.cells = {}
        for i in range(self.populationSize):
            pos = (randint(-offset, offset), randint(-offset, offset))
            t = randint(0,2)
            if i < seed:
                self.cells[pos] = [HumanStates.I, randint(self.infectionMin, self.infectionMax), t]
            else:
                self.cells[pos] = [HumanStates.S, None, t]

        self.generation = 0
        self.lockdownActive = False
        self.infectionProb = self.baseInfectionProb
        self.mobilityMultiplier = 1.0
        self.lastSaveTimestamp = None
        if not isFirst:
            self.runCount += 1
        self.updateStats()
        self.handleLockdown()

        print(f"--- NEW EPIDEMIC #{self.runCount} ---")
        print(f"Population = {self.populationSize} | infected = {seed}")
        print(f"Infection probability = {round(self.infectionProb * 100, 2)}%")
        print("-----------------------------------")

    # ------------------------------------------------------
    def updateStats(self):
        for v in self.cells.values():
            if len(v) != 3:
                print("BAD CELL:", v)
        s=e=i=r=d=0
        byType = {
            HumanType.CHILD: {"dead":0, "infected": 0, "recovered":0, "exposed":0, "susceptible":0},
            HumanType.ADULT: {"dead":0, "infected": 0, "recovered":0, "exposed":0, "susceptible":0},
            HumanType.SENIOR:{"dead":0, "infected": 0, "recovered":0, "exposed":0, "susceptible":0}
        }

        for state, ttl, t in self.cells.values():
            if state == HumanStates.S:
                s+=1
                byType[t]["susceptible"] += 1
            elif state == HumanStates.E:
                e+=1
                byType[t]["exposed"] += 1
            elif state == HumanStates.I:
                i+=1
                byType[t]["infected"] += 1
            elif state == HumanStates.R:
                r+=1
                byType[t]["recovered"] += 1
            elif state == HumanStates.D:
                d+=1
                byType[t]["dead"] += 1

        self.stats = {
            "susceptible": s,
            "exposed": e,
            "infected": i,
            "recovered": r,
            "dead": d,

            "lockdown": self.lockdownActive,
            "mobilityMul": self.mobilityMultiplier,

            "byType": byType,
            "population": self.populationSize,
        }

    # ------------------------------------------------------
    def getState(self):
        return {
            "version": 1,
            "meta": {
                "generation": self.generation,
                "runCount": self.runCount,
                "populationSize": self.populationSize,
                "lastSaveTimestamp": self.lastSaveTimestamp
            },
            "params": {
                "infectionProb": self.infectionProb,
                "baseInfectionProb": self.baseInfectionProb,
                "lockdownActive": self.lockdownActive,
                "mobilityMultiplier": self.mobilityMultiplier
            },
            "cells": [
                (x, y, s, ttl, t)
                for (x, y), (s, ttl, t) in self.cells.items()
            ]
        }

    # ------------------------------------------------------
    def saveState(self):
        try:
            t = time.localtime()
            self.lastSaveTimestamp = "%04d-%02d-%02d %02d:%02d:%02d" % t[:6]
            with open("game_state.json", "w") as f:
                json.dump(self.getState(), f)
            print("Saved.")
        except Exception as e:
            print("Save error:", e)

    def loadState(self):
        try:
            if "game_state.json" in os.listdir():
                with open("game_state.json") as f:
                    data = json.load(f)
                if data["version"] != 1:
                    raise ValueError("State version mismatch")

                self.generation = data["meta"]["generation"]
                self.runCount = data["meta"]["runCount"]
                self.populationSize = data["meta"]["populationSize"]
                self.lastSaveTimestamp = data["meta"]["lastSaveTimestamp"]


                self.infectionProb = data["params"]["infectionProb"]
                self.baseInfectionProb = data["params"]["baseInfectionProb"]
                self.lockdownActive = data["params"]["lockdownActive"]
                self.mobilityMultiplier = data["params"]["mobilityMultiplier"]

                self.cells = {}
                for x, y, s, ttl, t in data["cells"]:
                    self.cells[(x, y)] = [s, ttl, t]

                self.updateStats()
                print("✔ State restored")
                print("Loaded.")
            else:
                self.restartGame(True)
        except Exception as e:
            print("❌ Invalid state file:", e)
            self.restartGame(True)

    def getPostPayload(self, deviceId):
        return {
            "meta": {
                "deviceId": deviceId,
                "runId": self.runCount,
                "generation": self.generation,
                "timestamp": getISO8601Time()
            },
            "state": self.stats,
        }
