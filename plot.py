import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg    


def plotScatter(flatData):
    """
    Plots a scatter plot from the list of resale flat data.
    """
    flatData.plot(kind="scatter", x="longitude", y="latitude",
    label="population",
    c="min_distance_to_dorm_in_km", cmap=plt.get_cmap("jet"),
    colorbar=True, alpha=0.4, figsize=(15,7))

    plt.ylabel("Latitude", fontsize=14)
    plt.xlabel("Longitude", fontsize=14)
    plt.legend(fontsize=16)
    plt.show()


def plotData(flatData):
    """
    Plots a scatter plot with a heatmap from the list of resale flat data.
    """
    singapore_img = mpimg.imread('./image/singapore.png')

    ax = flatData.plot(kind="scatter", x="longitude", y="latitude", figsize=(10,7),
                        label="Resale Flats", c="Mininum distance of resale flat to the nearest dormitory (in km)", cmap=plt.get_cmap("jet_r"),
                        colorbar=True, alpha=0.4)

    # extent = [left, right, down, up]
    # original extent = [103.67, 104.00, 1.26, 1.47]
    # 103.64, 104.02, 1.22, 1.49
    plt.imshow(singapore_img, extent=[103.64, 104.02, 1.22, 1.49], alpha=0.5)
    plt.ylabel("Latitude", fontsize=14)
    plt.xlabel("Longitude", fontsize=14)
    plt.legend(fontsize=16)
    plt.show()


def main():
    flatData = pd.read_csv('./output/output-for-plot-edited-heading.csv')  
    plotData(flatData)


if __name__ == "__main__":
    main()
