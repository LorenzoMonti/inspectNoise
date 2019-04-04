import matplotlib.pyplot as plt
import pandas as pd
import sys
import datetime
import numpy as np
from utils import PLOT_DIR, create_plot_dir

#my_dpi = 120

def parse_file(file):
    """
        Parse log file passed as param.
    """
    db = []
    timestamps = []
    with open(file, "rt") as f:
        for line in f:
            date, time, val = line.split(" ")
            tmp_time = datetime.datetime.strptime(time, "%H:%M:%S,%f").time()
            time = datetime.time(hour=tmp_time.hour, minute=tmp_time.minute, second=tmp_time.second)
            timestamps.append(time);
            db.append(float(val))

    return date, db, timestamps

def plot(date, db, timestamps, my_dpi):
    """
        Plot data.
    """
    fig = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    ax = fig.subplots()
    ax.set_title("Variation of dB {} \nstarted at: {} \nended at: {}".format(date, timestamps[0], timestamps[-1], "%H:%M:%S"))
    ax.set_xlabel("Seconds")
    ax.set_ylabel("dB")
    plt.plot(timestamps, db)
    plt.savefig(PLOT_DIR + "/" + str(datetime.date.today()) + '.png', bbox_inches='tight', dpi=my_dpi)

    plt.clf()

def plot_dist(data, date, db, timestamps, my_dpi):
    """
        Plot distribution of dB.
    """
    fig = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    bins = np.linspace(30, 130, 100)
    ax = fig.subplots()
    ax.set_title("Distribution of dB {} \nstarted at: {} \nended at: {}".format(date, timestamps[0], timestamps[-1], "%H:%M:%S"))
    ax.set_xlabel("dB")
    ax.set_ylabel("Frequency")
    plt.hist(db, bins, 50)
    plt.savefig(PLOT_DIR + "/dB_distribution_" + str(datetime.date.today()) + '.png', bbox_inches='tight', dpi=my_dpi)

    plt.clf()

# Call main program.
if __name__ == "__main__":
    """
        Main of program.
    """
    if len(sys.argv) != 3:
        raise Exception("Usage: python plotter.py inputfile my_dpi")

    nome_script, file, my_dpi = sys.argv

    # Create plot dir if it doesn't exist.
    create_plot_dir()

    date, db, timestamps = parse_file(file)

    # Plot data.
    plot(date, db, timestamps, int(my_dpi))

    # Pandas series from data.
    series = pd.Series(db)

    # Dist. graph.
    plot_dist(series, date, db, timestamps, int(my_dpi))
