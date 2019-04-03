import matplotlib.pyplot as plt
import pandas as pd
import sys
import datetime
from utils import PLOT_DIR, create_plot_dir

def date_str(td):
    """
        Convert time delta to a string.
    """
    return str( str(td.seconds//3600) + ":" +     # hour
                str((td.seconds//60)%60) + ":" +  # minutes
                str((td.seconds//60)%60%60))      # seconds

def parse_file(file):
    """
        Parse log file passed as param.
    """
    db = []
    timestamps = []
    with open(file, "rt") as f:
        for line in f:
            date, time, val = line.split(" ")
            tmp_date = datetime.datetime.strptime(time, "%H:%M:%S,%f")
            timestamps.append(tmp_date.strftime("%H:%M:%S"))
            db.append(float(val))

    return date, db, timestamps

def plot(date, db, timestamps):
    """
        Plot data.
    """
    #time_delta = timestamps[-1] - timestamps[0]
    plt.title("Variation of db {} \nstarted at: {} \nended at: {}".format(date, timestamps[0], timestamps[-1]))
    plt.xlabel("Seconds")
    plt.xticks(rotation=90, fontsize=6) # vertical label
    plt.ylabel("dB")
    plt.grid(axis="y")
    plt.plot(timestamps, db)
    #plt.legend()
    plt.savefig(PLOT_DIR + "/" + str(datetime.date.today()) + '.png')

    plt.clf()

def plot_dist(db):
    db.plot.hist(50)
    plt.xlabel("dB")
    #plt.legend()
    plt.savefig(PLOT_DIR + "/dB_distribution_" + str(datetime.date.today()) + '.png')

    plt.clf()

# Call main program.
if __name__ == "__main__":
    nome_script, file = sys.argv

    # Create plot dir if it doesn't exist.
    create_plot_dir()

    date, db, timestamps = parse_file(file)

    # Plot data.
    plot(date, db, timestamps)

    # Pandas series from data.
    series = pd.Series(db.copy())
    #print(series)

    #Grafico sulla distribuzione.
    plot_dist(series)
