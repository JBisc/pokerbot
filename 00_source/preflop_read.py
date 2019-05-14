

import pandas
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.table import Table


def checkerboard_table(data, fmt='{:.2f}', bkg_colors=['yellow', 'white']):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    tb = Table(ax, bbox=[0,0,1,1])

    nrows, ncols = data.shape
    width, height = 1.0 / ncols, 1.0 / nrows

    # Add cells
    for (i,j), val in np.ndenumerate(data):
        # Index either the first or second item of bkg_colors based on
        # a checker board pattern
        idx = [j % 2, (j + 1) % 2][i % 2]
        color = bkg_colors[idx]

        tb.add_cell(i, j, width, height, text=val,
                    loc='center', facecolor=color)

    # Row Labels...
    for i, label in enumerate(data.index):
        tb.add_cell(i, -1, width, height, text=label, loc='right',
                    edgecolor='none', facecolor='none')
    # Column Labels...
    for j, label in enumerate(data.columns):
        tb.add_cell(-1, j, width, height/2, text=label, loc='center',
                           edgecolor='none', facecolor='none')
    ax.add_table(tb)
    return fig



import xlrd
df = pandas.read_excel('../01_templates/preflop.xlsx',skicolums=1)
#print the column names
print(df.columns)
df.replace
#get the values for a given column
#values = df['K'].values
#get a data frame with selected columns

names= df['Names'];
df= df.fillna(0)

names= df['Names'];
allCombinations =[]
for i,name in enumerate(names):
    name = name.replace("s", "")
    Cname= 'C'+name
    print(name)

    for ii,nameSuited in enumerate(names):
        #object = {"name": name+nameSuited, "value":}
        if ii < i:
            object = dict([('name', nameSuited.replace("s", "")+name), ('value', df.at[ii, Cname])])
        else:
            object = dict([('name', name + nameSuited), ('value', df.at[ii, Cname])])
        allCombinations.append(object);

print(allCombinations)
checkerboard_table(df)
plt.show()
