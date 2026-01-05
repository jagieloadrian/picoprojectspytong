class HumanStates:
    S = 0  # Susceptible
    E = 1  # Exposed
    I = 2  # Infected
    R = 3  # Recovered
    D = 4  # Dead

class HumanType:
    CHILD = 0
    ADULT = 1
    SENIOR = 2

    TYPE_PROFILE = {
        CHILD:  {
            "infectMul": 0.7,
            "mortality": 0.001,
            "mobility": 1.2
        },
        ADULT:  {
            "infectMul": 1.0,
            "mortality": 0.005,
            "mobility": 1.0
        },
        SENIOR: {
            "infectMul": 1.3,
            "mortality": 0.03,
            "mobility": 0.5
        }
    }