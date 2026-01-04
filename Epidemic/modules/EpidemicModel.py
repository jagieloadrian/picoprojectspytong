import os
import time

import ujson as json
from urandom import randint, random, uniform


class Epidemic:
    def __init__(self):
        self.cells = {}
        self.populationPositions = []
        self.populationSize = 100

        self.generation = 0
        self.runCount = 1
        self.lastSaveTimestamp = None
        self.infectionProb = 0.3

        self.stats = {
            "infected": 0, "recovered": 0, "susceptible": 0,
            "infectedPct": 0.0, "recoveredPct": 0.0
        }

    # ------------------------------------------------------
    def evolve(self):
        neighbors = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                     if not (dx == 0 and dy == 0)]

        infectedNeighborsCount = {}
        newInfected = set()

        for pos, (state, ttl) in self.cells.items():
            if state == "I":
                x, y = pos
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in self.cells:
                        infectedNeighborsCount[(nx, ny)] = infectedNeighborsCount.get((nx, ny), 0) + 1

        for pos, count in infectedNeighborsCount.items():
            state, ttl = self.cells[pos]
            if state == "S":
                prob = 1 - (1 - self.infectionProb) ** count
                if random() < prob:
                    newInfected.add(pos)

        updated = {}
        for pos, (state, ttl) in list(self.cells.items()):
            if state == "I":
                if ttl <= 1:
                    updated[pos] = ["R", None]
                else:
                    updated[pos] = ["I", ttl - 1]
            else:
                updated[pos] = [state, ttl]

        self.cells = updated

        for pos in newInfected:
            self.cells[pos] = ["I", self.getRandomInfectionTTL()]

        self.generation += 1
        self.updateStats()

        if self.stats["infected"] == 0 and self.generation > 10:
            print("Epidemic ended – restarting…")
            self.restartGame()

    # ------------------------------------------------------
    def getRandomInfectionTTL(self):
        return randint(2, 5)

    # ------------------------------------------------------
    def restartGame(self, isFirst=False):
        self.populationSize = randint(100, 300)
        infectedSeed = max(1, int(self.populationSize * uniform(0.1, 0.3)))
        grid = max(int((self.populationSize ** 0.5) * 1.5), 8)

        self.infectionProb = uniform(0.1, 0.5)

        offset = grid // 2
        self.populationPositions = [
            (randint(-offset, offset), randint(-offset, offset))
            for _ in range(self.populationSize)
        ]

        self.cells = {}
        for i, pos in enumerate(self.populationPositions):
            if i < infectedSeed:
                self.cells[pos] = ["I", self.getRandomInfectionTTL()]
            else:
                self.cells[pos] = ["S", None]

        self.generation = 0
        self.lastSaveTimestamp = None
        if not isFirst:
            self.runCount += 1

        print(f"--- NEW EPIDEMIC #{self.runCount} ---")
        print(f"Population = {self.populationSize} | infected = {infectedSeed}")
        print(f"Infection probability = {round(self.infectionProb * 100, 2)}%")
        print("-----------------------------------")

    # ------------------------------------------------------
    def updateStats(self):
        infected = sum(1 for s, t in self.cells.values() if s == "I")
        recovered = sum(1 for s, t in self.cells.values() if s == "R")
        susceptible = self.populationSize - infected - recovered

        self.stats = {
            "infected": infected,
            "recovered": recovered,
            "susceptible": susceptible,
            "infectedPct": round(infected / self.populationSize * 100, 2),
            "recoveredPct": round(recovered / self.populationSize * 100, 2),
        }

    # ------------------------------------------------------
    def getState(self):
        return {
            "generation": self.generation,
            "runCount": self.runCount,
            "lastSaveTimestamp": self.lastSaveTimestamp,
            "populationSize": self.populationSize,
            "cells": [(x, y, s, ttl) for (x, y), (s, ttl) in self.cells.items()],
            "stats": self.stats
        }

    def getStats(self):
        return {"generation": self.generation, "runCount": self.runCount,
                "lastSaveTimestamp": self.lastSaveTimestamp, "stats": self.stats}

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
                self.populationSize = data["populationSize"]
                self.cells = {(x, y): [s, ttl] for x, y, s, ttl in data["cells"]}
                self.generation = data["generation"]
                self.runCount = data["runCount"]
                self.lastSaveTimestamp = data["lastSaveTimestamp"]
                print("Loaded.")
            else:
                self.restartGame(True)
        except:
            self.restartGame(True)

    def getPostPayload(self, deviceId):
        return {
            "meta": {
                "deviceId": deviceId,
                "runId": self.runCount,
                "generation": self.generation,
                "timestamp": time.time()
            },
            "params": {
                "populationSize": self.populationSize,
                "infectionProb": self.infectionProb,
                "infectionTtlMin": 2,
                "infectionTtlMax": 5
            },
            "state": {
                "susceptible": self.stats['susceptible'],
                "infected": self.stats['infected'],
                "recovered": self.stats['recovered']
            }
        }
