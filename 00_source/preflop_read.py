

import pandas
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
        object = {"name": name+nameSuited, "value":df.at[ii, Cname]}
        allCombinations.append(object);

print(allCombinations)