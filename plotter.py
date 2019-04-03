import matplotlib.pyplot as plt
import sys
import pandas as pd
from datetime import datetime


def parse_file(file):
    db = []
    timestamps = []
    with open(file, "rt") as f:
        for line in f:
            date, time, val = line.split(" ")
            timestamps.append(datetime.strptime(time, '%b %d %Y %I:%M%p'))
            db.append(float(val))
    return date

def plot(db, timestamps, date):
    plt.title("Variation of db {} during {}".format(date, timestamps[-1] - timestamps[0]))
    plt.xlabel("Seconds")
    plt.ylabel("db")
    plt.grid(axis="y")
    plt.plot(timestamps, db)

# Call main program.
if __name__ == "__main__":
    nome_script, file = sys.argv
    date = parse_file(file)

    # Create pandas series


    # Plot data.
    #plot()
