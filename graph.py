import pandas as pd
import csv
import matplotlib.pylab as plt
 
csv = pd.read_csv("original.csv", encoding='cp949')
 
arHello = csv.loc[:, '가 치']
arBye = csv.loc[:, '시간']
 
print(csv)
print(type(csv))
print(arHello)
 
print(type(csv.loc[:, '시간']))
 
plt.plot(arBye, arHello)
plt.show()