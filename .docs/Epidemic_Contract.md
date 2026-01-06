# Epidemic Contract

## What is epidemic?
You can find in the module with name Epidemic
It's a small project for developer board like esp32 or rpi pico 2w which simulate in simple way epidemic in small group of people.
Starting with between 100-300 people and 10-30 % of infected people.

## How it will work?

Microcontroller will send data every 30-60 second to the path `/v1/api/stats/epidemic`
with data which server could work.

Example body:
```json
{
  "meta": {
    "deviceId": "ESP32-C3_1",
    "runId": 1,
    "timestamp": "2026-01-05T15:38:14", //ISO-8601 UTC
    "generation": 9
  },
  "state": {
    "mobilityMul": 1.0,
    "susceptible": 49,
    "infected": 40,
    "dead": 8,
    "exposed": 14,
    "lockdown": false,
    "byType": {
      "0": {
        "recovered": 18,
        "susceptible": 23,
        "dead": 0,
        "exposed": 4,
        "infected": 8
      },
      "1": {
        "recovered": 20,
        "susceptible": 13,
        "dead": 1,
        "exposed": 3,
        "infected": 10
      },
      "2": {
        "recovered": 18,
        "susceptible": 13,
        "dead": 7,
        "exposed": 7,
        "infected": 22
      }
    },
    "recovered": 56,
    "population": 293
  }
}
```

field byType means state of maturity of person: 
0 - Child, 1 - Mature, 2 - Senior