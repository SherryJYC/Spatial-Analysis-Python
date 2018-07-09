import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def radar_chart(n_chart, file_path, sum_col, labels):
    '''
    n_chart = number of radar_charts
    file_path =location of csv file
    sum_col = the name of a column containing sum of each row
    lables = labels of each column
    for example:
    labels=np.array( ['EAST', 'ISLANDS',
               'KOWLOON', 'KWAI TSING',
               'KWUN TONG', 'NORTH',
               'SAI KUNG', 'SHA TIN',
               'SHAM SHUI PO', 'SOUTH',
               'TAI PO', 'TSUEN WAN',
               'TUEN MUN', 'WAN CHAI',
               'WONG TAI SIN', 'YUEN LONG',
               'YAU TSIM MONG', 'CENTRALN']) # All districts' names

    '''
    df = pd.read_csv(file_path, error_bad_lines=False)
    df = pd.DataFrame(df)
    if sum_col != "no":
        df_new = df.iloc[:, 1:-1].div(df[sum_col], axis=0)
        df.iloc[:, 1:-1] = df_new

    labels = np.array(labels)
    for i in range(n_chart):
        stats = df.iloc[i, 1:-1].values
        title = df.iloc[i, 0]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)

        stats = np.concatenate((stats, [stats[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        colors = ['#f9bc08', '#8f8ce7', '#fd4659', '#8f8ce7', '#f9bc08']
        color = colors[i]

        fig = plt.figure()
        fig.set_size_inches(12, 12)
        ax = fig.add_subplot(111, polar=True)
        lines = ax.plot(angles, stats, 'o-', linewidth=2)
        plt.setp(lines, color=color, linewidth=2.0)
        ax.fill(angles, stats, color, alpha=0.35)
        ax.set_thetagrids(angles * 180 / np.pi, labels)
        ax.title.set_text(title)
        ax.grid(True)
        plt.savefig(title + '.png')


if __name__ == '__main__':
    n_chart = 5
    file_path = "../input/hkmap2/hkmap_wareless_join.csv"
    sum_col = "SUM"  # "SUM" , you can write 'no' to reject standarization
    labels = ['CENTRALN', 'EASTERN', 'ISLANDS',
              'KOWLOON', 'KWAI TSING',
              'KWUN TONG', 'NORTH',
              'SAI KUNG', 'SHA TIN',
              'SHAM SHUI PO', 'SOUTH',
              'TAI PO', 'TSUEN WAN',
              'TUEN MUN', 'WAN CHAI',
              'WONG TAI SIN', 'YAU TSIM MONG', 'YUEN LONG'
              ]
    radar_chart(n_chart, file_path, sum_col, labels)