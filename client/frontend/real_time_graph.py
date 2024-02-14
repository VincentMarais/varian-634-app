import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class RealTimeGraphApp:
    def __init__(self, root, csv_file_path, physical_datas, update_interval=1000):
        self.root = root
        self.csv_file_path = csv_file_path
        self.update_interval = update_interval

        # Configuration de la fenêtre
        self.root.title("Affichage Dynamique des Données avec Curseur")
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.button_quit = tk.Button(master=root, text="Quit", command=self._quit)
        self.button_quit.pack(side=tk.BOTTOM)
        # Configuration du graphique
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill=tk.BOTH, expand=True)

        # Ajout de la barre d'outils de navigation
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack()
        self.physical_datas = physical_datas

        # Lancement de la mise à jour du graphique
        self.update_graph()

    def read_data(self):
        if os.path.exists(self.csv_file_path):
            return pd.read_csv(self.csv_file_path)
        else:
            return pd.DataFrame(columns=[self.physical_datas[0], self.physical_datas[1]])

    def update_graph(self):        
        if self.root.winfo_exists():  # Vérifie si la fenêtre principale existe
            df = self.read_data()
            self.ax.clear()        
            if not df.empty:
                self.line, = self.ax.plot(df[self.physical_datas[0]], df[self.physical_datas[1]], picker=5)  # 5 points tolerance
                self.ax.set_title("Longueur d'onde vs Absorbance")
                self.ax.set_xlabel("Longueur d'onde (nm)")
                self.ax.set_ylabel("Absorbance")
                self.ax.grid(True)

            self.canvas.draw()
            self.root.after(self.update_interval, self.update_graph)
    
    def on_mouse_move(self, event):
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            # Affichage des coordonnées dans le titre du graphique pour l'exemple
            self.ax.set_title(f"Longueur d'onde: {x:.2f} nm, Absorbance: {y:.2f}")
            self.canvas.draw_idle()

    def _quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate



if __name__ == "__main__":
    root = tk.Tk()
    PHYSICAL_DATAS = ["Longueur d'onde (nm)", "Tension photodiode 1 (Volt)"]
    CHEMIN = "C:\\Users\\vimarais\\Documents\\GitHub\\varian-634-app\\client\\raw_data\\raw_data_14_02_2024.csv"
    app = RealTimeGraphApp(root, CHEMIN, PHYSICAL_DATAS)
    root.mainloop()
