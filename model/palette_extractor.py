import numpy as np
import pandas as pd
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import whiten


class PaletteExtractor:

    def __init__(self, palette_size):
        self.cluster_centers = None
        self.stds = None
        self.palette_size = palette_size

    def fit(self, image):
        df = pd.DataFrame()
        df['r'] = pd.Series(image[:, :, 0].flatten())
        df['g'] = pd.Series(image[:, :, 1].flatten())
        df['b'] = pd.Series(image[:, :, 2].flatten())
        df['r_whiten'] = whiten(df['r'])
        df['g_whiten'] = whiten(df['g'])
        df['b_whiten'] = whiten(df['b'])
        self.cluster_centers, _ = kmeans(df[['r_whiten', 'g_whiten', 'b_whiten']], int(self.palette_size))
        self.stds = df[['r', 'g', 'b']].std()

    def get_colors(self):
        colors = []
        r_std, g_std, b_std = self.stds
        for color in self.cluster_centers:
            cluster_r, cluster_g, cluster_b = color
            r, g, b = int(cluster_r * r_std), int(cluster_g * g_std), int(cluster_b * b_std)
            colors.append([r, g, b])
        return colors

    def get_hexes(self):
        hexes = []
        r_std, g_std, b_std = self.stds
        for color in self.cluster_centers:
            cluster_r, cluster_g, cluster_b = color
            r, g, b = int(cluster_r * r_std), int(cluster_g * g_std), int(cluster_b * b_std)
            hexes.append('#{:02x}{:02x}{:02x}'.format(r, g, b))
        return hexes

    def get_rals(self):
        df = pd.read_csv("data/ral_code.csv")
        rals = []
        r_std, g_std, b_std = self.stds
        for color in self.cluster_centers:
            cluster_r, cluster_g, cluster_b = color
            r, g, b = int(cluster_r * r_std), int(cluster_g * g_std), int(cluster_b * b_std)
            min_dist = 1e9
            best_ral = -1
            best_ral_name = None
            for _, row in df.iterrows():
                dist = np.sqrt((r - row["r"]) ** 2 + (g - row["g"]) ** 2 + (b - row["b"]) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    best_ral = row["id"]
                    best_ral_name = row["name"]
            rals.append((best_ral, best_ral_name))
        return rals

    def get_ncs(self):
        df = pd.read_csv("data/ncs_code.csv")
        ncs = []
        r_std, g_std, b_std = self.stds
        for color in self.cluster_centers:
            cluster_r, cluster_g, cluster_b = color
            r, g, b = int(cluster_r * r_std), int(cluster_g * g_std), int(cluster_b * b_std)
            min_dist = 1e9
            best_ral = -1
            for _, row in df.iterrows():
                dist = np.sqrt((r - row["r"]) ** 2 + (g - row["g"]) ** 2 + (b - row["b"]) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    best_ral = row["id"]
            ncs.append(best_ral)
        return ncs
