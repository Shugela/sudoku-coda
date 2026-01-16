import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_brute = pd.read_csv("Backend/app/data/statistiques_sudoku.csv")
df_ok = df_brute

df_ok["datetime"] = pd.to_datetime(df_brute["datetime"],format='%Y-%m-%d %H:%M').dt.strftime('%Y-%m-%d')

df_connexion = df_ok.groupby(["datetime"]).count()
x = np.arange(len(df_connexion['level']))
y = df_connexion['level']

width = 0.35
fig, ax1 = plt.subplots(figsize=(10, 6))

bars_total = ax1.bar(
    x,
    y,
    width,
    color="steelblue",
    label="Nombre de connexion"
)
ax1.set_xlabel("Date")
ax1.set_ylabel("Nombre de connexion")

# Axe X
ax1.set_xticks(x)
ax1.set_xticklabels(df_connexion.index, rotation=45)

# Titre
plt.title("Nombre de connexion par jour")
plt.tight_layout()


df_niveau = df_ok.drop(['datetime','name','completed'],axis=1)

df_niveau = df_niveau.groupby(['level']).mean()
print(df_niveau['guesses'])

plt.figure("tentative moyen par niveau")
df_niveau['guesses'].plot()

plt.title("nombre de tentative moyen par niveau")
plt.xlabel("niveau")
plt.ylabel("Nombre de tentative moyen")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()

plt.show()