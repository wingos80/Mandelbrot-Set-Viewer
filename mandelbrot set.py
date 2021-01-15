import pygame as pg
import numpy as np
import math
import timeit

toc = timeit.default_timer()

pg.init()
pg.display.set_caption("Mandelbrot set")
pg.font.init()

xmax = 2140
ymax = 1206
scr = pg.display.set_mode((xmax, ymax))

black = (0, 0, 0)

C = np.mgrid[0:xmax, 0:ymax]
empty_arr = np.zeros((xmax, ymax))

itr = 0


def generate_complex_plane(x, y, grid, zoom):
    return (grid[0]-2*xmax/3)/(zoom*xmax/3)+x+(((grid[1]-ymax/2)/(zoom*ymax/2))-y)*1j


def iterator(z_0, c):
    # the mandelbrot set equation
    z = z_0
    for i in range(3):
        z = abs(z.real)+abs(z.imag)*1j
        z = z*z + c
    # if y > 1:
    #     # r = min(255, 255 * max(0, 1.5 * (-math.cos(math.pi * y/99999))))
    #     # g = min(255, 255 * (1.5 * math.sin(math.pi * y/99999)))
    #     # b = min(255, 255 * max(0, 1.5 * math.cos(math.pi * y/99999)))
    #     r = 0
    #     g = 0
    #     b = min(255, y/9999999999)
    return z


def colour(z, iter):
    # the mandelbrot set definition (whether the number has or has not exploded, colouring step
    y = np.absolute(z)
    # if y < 1+1/(zoom*1):
    if y < 2:
        iter += 1
        return 255, 255, 255, iter
    else:
        # r = min(255, 255 * max(0, 1.5 * (-math.cos(math.pi * iter*10))))
        # g = min(255, 255 * (1.5 * math.sin(math.pi * iter*10)))
        # b = min(255, 255 * max(0, 1.5 * math.cos(math.pi * iter/10)))
        # r, g = min(255, iter*10/(zoom/2.5)), min(255, iter*20/(zoom/2.5))
        # b = min(255, iter*30/(zoom/2.5))
        # return r, g, b, iter
        r, g = min(255, iter * 8), min(255, iter * 13)
        b = min(255, iter * 25)
        return r, g, b, iter
        # r, g = min(255, iter * 0.8), min(255, iter * 1.2)
        # b = min(255, iter * 3)
        # return r, g, b, iter
        # return 0, 10, 200, iter
    # else:
    #     return 0, 0, 255


# remember to implement zooming. Turns out zooming + panning will defo not work :(
# for i in range(xmax):
#     for j in range(ymax):
#         a, b, c = colour(i)
#         arr[i][j] = (a, b, c)

# Z is the complex number array
# Z = (C[0]-2*xmax/3)/(xmax/3)+(C[1]-ymax/2)*1j/(ymax/2)
center = -1.62, 0
zoom = 8
Z = generate_complex_plane(center[0], center[1], C, zoom)

vfunc1 = np.vectorize(iterator)
vfunc2 = np.vectorize(colour)
explody_arr = vfunc1(empty_arr, Z)

be = vfunc2(explody_arr, empty_arr)
disp_arr = np.stack((be[0], be[1], be[2]), axis=-1)

tic = timeit.default_timer()

print(tic - toc)
# new_center = 0

# Main Loop!!
running = True
play = 1
while running:
    # t = timeit.default_timer()
    #
    # circle_colour = (min(255, 255 * max(0, 1.5 * (-math.cos(math.pi * t / 5)))),
    #                  min(255, 255 * max(0,(1.5 * math.sin(math.pi * t / 5)))),
    #                  min(255, 255 * max(0, 1.5 * math.cos(math.pi * t / 5))))
    # if play == 1:
    #     explody_arr = vfunc1(explody_arr, Z)
    #     be = vfunc2(explody_arr, be[3])
    #     # circle_colour = (255, 255, 255)

    explody_arr = vfunc1(explody_arr, Z)
    be = vfunc2(explody_arr, be[3])

    dis_arr = np.stack((be[0], be[1], be[2]), axis=-1)
    pg.surfarray.blit_array(scr, dis_arr)

    # pg.draw.circle(surface=scr, color=circle_colour, center=(2 * xmax / 3, ymax / 2), radius=3)

    itr += 1
    print(itr)
    if itr > 9 and itr % 3 == 0:
        if itr % 10 == 0:
            pg.image.save(scr, str(timeit.default_timer()) + str(center) + str(zoom) + ".tiff")
        else:
            pg.image.save(scr, str(timeit.default_timer()) + str(center) + str(zoom) + ".jpeg")

    # quit event
    # event = pg.event.wait()
    # if event.type == pg.KEYDOWN:
    #     if event.type == pg.K_RIGHT:
    #         zoom += 10
    #         print("ere")
    #
    #         Z = generate_complex_plane(center[0], center[1], C, zoom)
    #         explody_arr = vfunc1(empty_arr, Z)
    #         be = vfunc2(explody_arr, empty_arr)
    #         disp_arr = np.stack((be[0], be[1], be[2]), axis=-1)
    #     if event.type == pg.K_LEFT:
    #         zoom -= 10
    #
    #         Z = generate_complex_plane(center[0], center[1], C, zoom)
    #         explody_arr = vfunc1(empty_arr, Z)
    #         be = vfunc2(explody_arr, empty_arr)
    #         disp_arr = np.stack((be[0], be[1], be[2]), axis=-1)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONUP:
            new_center = pg.mouse.get_pos()
            pg.image.save(scr, str(timeit.default_timer())+str(center)+str(zoom)+".jpeg")
            print("heh")

            # play = play * -1
            # center = (new_center[0]-2*xmax/3)/(xmax/3), -(new_center[1]-ymax/2)/(ymax/2)
            #
            # Z = generate_complex_plane(center[0], center[1], C, zoom)
            # explody_arr = vfunc1(empty_arr, Z)
            # be = vfunc2(explody_arr, empty_arr)
            # disp_arr = np.stack((be[0], be[1], be[2]), axis=-1)

        if event.type == pg.QUIT:
            running = False
    if itr > 2100:
        running = False
    pg.display.flip()
pg.quit()
