import pygame as pg
import numpy as np
import os,timeit, time
from multiprocessing import Process, current_process, Pool
# giteatest
pg.init()
pg.display.set_caption("Mandelbrot set")

xmax = 1080  # width of the window/map
ymax = 720  # height of the window/map
scr = pg.display.set_mode((xmax, ymax))

rf, gf, bf = 2, 3, 5  # the colour factors for rgb, these factors determine how much is added to each colour
# channel after 1 frame or 1 "game" loop. See function colour for how these var are used.

iteration_per_call = 6  # the number of times the code runs the mandelbrot iterative equation: z_n+1 = (z_n)**2 + c,
# for each frame or each game loop

zoom = 68  # level of zoom
center = -1.405, 1/zoom-0.002  # the coordinates for the centre of the window

C = np.mgrid[0:xmax, 0:ymax]
empty_arr = np.zeros((xmax, ymax))

itr = 0


def generate_complex_plane(x, y, grid, zoom):
    return (grid[0]-2*xmax/3)/(zoom*xmax/3)+x+(((grid[1]-ymax/2)/(zoom*ymax/2))-y)*1j


def iterator(z_0, c):
    # the mandelbrot set equation
    z = z_0
    for i in range(iteration_per_call):
        # z = abs(z.real)+abs(z.imag)*1j
        z = z*z + c
    return z


def colour(z, iter, lowest_iter):
    # the mandelbrot set definition (whether the number has or has not exploded, colouring step)
    y = np.absolute(z)
    # if y < 1+1/(zoom*1):
    if y < 16:
        iter += 1
        return 255, 255, 255, iter
    else:
        # r = min(255, 255 * max(0, 1.5 * (-math.cos(math.pi * iter*10))))
        # g = min(255, 255 * (1.5 * math.sin(math.pi * iter*10)))
        # b = min(255, 255 * max(0, 1.5 * math.cos(math.pi * iter/10)))
        multiplier = -210/(1+np.exp(iter/3.4-6))+210+0.003*iter**1.8
        # r, g = min(255, (iter-lowest_iter) * rf), min(255, (iter-lowest_iter) * gf)
        # b = min(255, (iter-lowest_iter) * bf)
        r, g = min(255, multiplier* rf), min(255, multiplier * gf)
        b = min(255, multiplier * bf)
        return r, g, b, iter


def vfunc1_mp(explody_arr, Z):
    start_time = time.time()
    p = Pool()
    result = p.map(vfunc1, (explody_arr, Z))

    p.close()
    p.join()

    end_time = time.time() - start_time
    print(f"{end_time} seconds using multiprocessing")

    return result


def vfunc2_mp(explody_arr, be, lowest_iter_array):
    start_time = time.time()
    p = Pool()
    result = p.map(vfunc2, (explody_arr, be, lowest_iter_array))

    p.close()
    p.join()

    end_time = time.time() - start_time
    print(f"{end_time} seconds using multiprocessing")

    return result


Z = generate_complex_plane(center[0], center[1], C, zoom)

vfunc1 = np.vectorize(iterator)
vfunc2 = np.vectorize(colour)
explody_arr = vfunc1(empty_arr, Z)

be = vfunc2(explody_arr, empty_arr, empty_arr)
lowest_iter_array = empty_arr+be[3].min()
# disp_arr = np.stack((be[0], be[1], be[2]), axis=-1)

# Main Loop!!
running = True
play = 1
while running:
    toc = timeit.default_timer()

    explody_arr = vfunc1(explody_arr, Z)
    be = vfunc2(explody_arr, be[3], lowest_iter_array)
    # explody_arr = vfunc1_mp(explody_arr, Z)
    # be = vfunc2_mp(explody_arr, be[3], lowest_iter_array)
    lowest_iter_array = empty_arr+be[3].min()

    disp_arr = np.stack((be[0], be[1], be[2]), axis=-1)  # the array of pixels to be displayed
    pg.surfarray.blit_array(scr, disp_arr)

    tic = timeit.default_timer()

    itr += 1
    print(itr, str(tic-toc))
    # if itr == 12:
    #     # Making a directory to put pictures in
    #     dir_name = str(xmax) + ' x ' + str(ymax) + ', ' + str(iteration_per_call) + ' iterations, ' + str(
    #         rf) + ' ' + str(gf) + ' ' + str(bf) + ', ' + str(center) + ', ' + str(zoom)
    #     current_directory = os.getcwd()
    #     final_directory = os.path.join(current_directory, dir_name)
    #     if not os.path.exists(final_directory):
    #         os.makedirs(final_directory)
    # if itr > 12 and itr % 3 == 0:
    #     if itr % 10 == 0:
    #         pg.image.save(scr, final_directory+'/'+str(timeit.default_timer()) + ".tiff")
    #     else:
    #         pg.image.save(scr, final_directory+'/'+str(timeit.default_timer()) + ".png")

    # quit event
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    if itr > 2100:
        running = False
    pg.display.flip()
pg.quit()
