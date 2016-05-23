from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import numpy as np


def surf(signal, *argv):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    X = np.arange(0, signal.shape[1])
    Y = np.arange(0, signal.shape[0])
    X, Y = np.meshgrid(X, Y)
    # Additional Arguments
    if argv:
        X = argv[0]
        Y = argv[1]
        X, Y = np.meshgrid(X, Y)
        Y = Y.T
        X = X.T
    R = np.sqrt(X ** 2 + Y ** 2)
    Z = signal
    # Remove Not numbers
    nan_ind = np.isnan(Z)
    inf_ind = np.isinf(Z)
    Z[nan_ind] = 0
    Z[inf_ind] = 0
    norm = matplotlib.colors.Normalize(vmin=np.min(Z), vmax=np.max(Z), clip=False)
    surf = ax.plot_surface(X, Y, Z, rstride=1, norm=norm, cstride=1, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()
