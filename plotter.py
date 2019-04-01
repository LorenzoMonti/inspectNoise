import matplotlib.pyplot as plt
import sys
import pandas as pd


def parse_file(file):
    db = []
    timestamps = []
    with open(file, "rt") as f:
        for line in f:
            time, val = line.split(" ")
            timestamps.append(time)
            db.append(float(val))

def plot():
    pass

# Call main program.
if __name__ == "__main__":
    nome_script, file = sys.argv
    parse_file(file)

    # Creare una serie in pandas che ha come valori i db e come etichette i timestamp.


    # fare garfico.
    plot()
