import numpy as np
import matplotlib.pyplot as plt

def plot_vector_field(mv_field, block_size, out_path):
    Down_sampled_MV= mv_field[::int(block_size),::int(block_size),:]
    X, Y = np.meshgrid(np.linspace(0, Down_sampled_MV.shape[1], Down_sampled_MV.shape[1]), \
                        np.linspace(0, Down_sampled_MV.shape[0], Down_sampled_MV.shape[0]))

    U = np.flip(Down_sampled_MV[:,:,0], axis=0)
    V = np.flip(Down_sampled_MV[:,:,1], axis=0)

    #Z=np.add(np.square(U),np.square(V))
    #plt.contourf(X,Y,Z)

    M = np.hypot(U, V)
    plt.quiver(X, Y, U, V, M, units='x', pivot='tip', width=0.15,
            scale=1 / 0.15)
    plt.savefig(out_path, dpi=1000)