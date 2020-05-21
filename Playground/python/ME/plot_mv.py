import numpy as np
import matplotlib.pyplot as plt
from imageio import imwrite
from colorsys import hsv_to_rgb
import math

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in hsv_to_rgb(h,s,v))

def plot_vector_field(mv_field, block_size, out_path, method='vector_field'):
    if method == 'vector_field':
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
    elif method == 'intensity':
        output_intensity = np.copy(mv_field)
        max_intensity = 0
        for i in range(output_intensity.shape[0]):
            for j in range(output_intensity.shape[1]):
                intensity = float(output_intensity[i,j,0]) ** 2.0 + float(output_intensity[i,j,1]) ** 2.0
                if intensity > max_intensity:
                    max_intensity = intensity
                output_intensity[i,j,:] = [intensity, intensity, intensity]
        output_intensity = 255 - (output_intensity * (255.0 / float(max_intensity)))
        imwrite(out_path, output_intensity)
    elif method == 'colour_dir':
        # convert vector direction to hue, then hsv to rbg
        output = np.copy(mv_field)
        for row in range(output.shape[0]):
            for col in range(output.shape[1]):
                degrees = math.atan2(output[row,col,0], output[row,col,1]) / (2 * math.pi)
                rgb = hsv2rgb(degrees, 1.0, 1.0)
                output[row, col, 0] = rgb[0]
                output[row, col, 1] = rgb[1]
                output[row, col, 2] = rgb[2]
        imwrite(out_path, output)
    else:
        raise Exception('Can only print using \'vector_field\' or \'intensity\' methods.')