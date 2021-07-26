import glfw, timeit
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

# viewer parameters
xmax, ymax = 1920.0, 1060.0

center_xt, center_yt, zoom = -0.5, 0.0, 1.01
center_x, center_y = center_xt, center_yt
wx = 4
wy = wx * ymax / xmax
zoomin, zoomout, moveup, movedown, moveleft, moveright = False, False, False, False, False, False
newpos = [0, 0]
windowc = [xmax / 2, ymax / 2]


def mouse_coord(xpos, ypos):
    global newpos
    newpos = [xpos, ypos + 16]


def mouse_button_clb(window, button, action, mode):
    global center_xt, center_yt, newpos, windowc
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        center_xt += (newpos[0] / xmax - 0.5) * wx / zoom
        center_yt -= (newpos[1] / ymax - 0.5) * wy / zoom
        print(newpos)


def cursor_pos_clb(window, xpos, ypos):
    mouse_coord(xpos, ypos)


def mscamera(x, y):
    windowc = [xmax / 2, ymax / 2]


def key_input_clb(window, key, scancode, action, mode):
    global zoomin, zoomout, moveup, movedown, moveleft, moveright
    # zoomin, zoomout, moveup, movedown, moveleft, moveright = False, False, False, False, False, False
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    if key == glfw.KEY_E and action == glfw.PRESS:
        zoomin = True
    if key == glfw.KEY_E and action == glfw.RELEASE:
        zoomin = False

    if key == glfw.KEY_Q and action == glfw.PRESS:
        zoomout = True
    if key == glfw.KEY_Q and action == glfw.RELEASE:
        zoomout = False

    # if key == glfw.KEY_W and action == glfw.PRESS:
    #     moveup = True
    # if key == glfw.KEY_W and action == glfw.RELEASE:
    #     moveup = False
    #
    # if key == glfw.KEY_A and action == glfw.PRESS:
    #     moveleft = True
    # if key == glfw.KEY_A and action == glfw.RELEASE:
    #     moveleft = False
    #
    # if key == glfw.KEY_S and action == glfw.PRESS:
    #     movedown = True
    # if key == glfw.KEY_S and action == glfw.RELEASE:
    #     movedown = False
    #
    # if key == glfw.KEY_D and action == glfw.PRESS:
    #     moveright = True
    # if key == glfw.KEY_D and action == glfw.RELEASE:
    #     moveright = False


def kbcamera():
    global center_x, center_y, zoom, zoomin, zoomout, moveup, movedown, moveleft, moveright
    if zoomin:
        zoom *= 1.1
        # zoomin = False
    if zoomout:
        zoom *= 1 / 1.1
        # zoomout = False
    if moveup:
        center_yt += move_size
        # moveup = False
    if movedown:
        center_yt -= move_size
        # movedown = False
    if moveright:
        center_xt += move_size
        # moveright = False
    if moveleft:
        center_xt -= move_size
        # moveleft = False


def mscamera():
    global center_x, center_y

    dx = center_xt - center_x
    dy = center_yt - center_y

    center_x += dx * 0.02
    center_y += dy * 0.02


vertex_src = """
# version 400
in vec3 a_position;
in vec2 a_dims;
in vec3 a_center_n_zoom;
in vec2 wx_wy;
out vec2 scr_dim;
out vec3 center_n_zoom;
out vec2 wx_wy2;
void main()
{
    gl_Position = vec4(a_position, 1.0);
    scr_dim = a_dims;
    center_n_zoom = a_center_n_zoom;
    wx_wy2 = wx_wy;
}
"""

fragment_src = """
# version 400
in vec2 scr_dim;
in vec3 center_n_zoom;
in vec2 wx_wy2;
out vec4 out_color;
void main()
{   
    int itr = 0;
    int itr_limit = 256;
    float abs = 0.0;
    float abs_lim = 5.0;
    float converged = 0;

    float zoom = center_n_zoom.z;
    vec2 center = vec2(center_n_zoom.x, center_n_zoom.y);
    vec2 xy = vec2(gl_FragCoord.x, gl_FragCoord.y);
    vec2 z = vec2(0.0, 0.0);
    vec2 zt = vec2(0.0, 0.0);

    for(int aae=0; aae<4; aae++)
    {   
        for(int bae=0; bae<4; bae++)
        {   
            vec2 aa = vec2(aae, bae);
            vec2 c = ((xy-0.25+aa*0.125)/scr_dim-0.5)*wx_wy2/zoom+center;

            while (itr<itr_limit && abs<abs_lim)
            {   
                zt = z;
                z = vec2(zt.x* zt.x - zt.y*zt.y + c.x, 
                         2* zt.x*zt.y + c.y);

                abs = z.x*z.x + z.y*z.y;
                itr++;
            }
            converged = converged + int(abs<abs_lim);
        }
    }
    int temp_threshold = itr_limit*18;
    converged = converged/4.0;
    float color = 0.8*itr/itr_limit*int(itr<temp_threshold)+converged*int(itr>itr_limit);


    if (xy.x > 959 && xy.x < 961)
    {
        out_color = vec4(1.0, 0.0, 0.0, 1.0);
    } else if (xy.y > 539 && xy.y < 541)
    {
        out_color = vec4(1.0, 0.0, 0.0, 1.0);
    } else 
    {
        out_color = vec4(0.2*color, 0.4*color, 0.8*color, 1.0);
    }

}
"""

# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(int(xmax), int(ymax), "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 0, 34)
glfw.make_context_current(window)
glfw.swap_interval(0)

glfw.set_key_callback(window, key_input_clb)
glfw.set_cursor_pos_callback(window, cursor_pos_clb)
glfw.set_mouse_button_callback(window, mouse_button_clb)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

glUseProgram(shader)

frame_times = [0, 0]
# the main application loop
while not glfw.window_should_close(window):
    move_size = wy / zoom * 0.005

    tic = timeit.default_timer()

    # setting shader parameters and objects
    vertices = [-1.0, 1.0, 0.0,
                11111111.0, 1.0, 0.0,
                -1.0, -11111111.0, 0.0,
                xmax, ymax,  # width and height of glfw window
                center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                wx, wy]  # width and height of complex plane

    vertices = np.array(vertices, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    position = glGetAttribLocation(shader, "a_position")
    glEnableVertexAttribArray(position)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    scr_dims = glGetAttribLocation(shader, "a_dims")
    glEnableVertexAttribArray(scr_dims)
    glVertexAttribPointer(scr_dims, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(36))

    center_n_zoom = glGetAttribLocation(shader, "a_center_n_zoom")
    glVertexAttribPointer(center_n_zoom, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(44))
    glEnableVertexAttribArray(center_n_zoom)

    wx_wy = glGetAttribLocation(shader, "wx_wy")
    glVertexAttribPointer(wx_wy, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(56))
    glEnableVertexAttribArray(wx_wy)

    # game loop
    glfw.poll_events()

    kbcamera()
    mscamera()

    glClear(GL_COLOR_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glfw.swap_buffers(window)

    toc = timeit.default_timer()

    # Calculate frame time
    frame_times[0] += toc - tic
    frame_times[1] += 1

    if frame_times[1] >= 50:
        print(f'frame time = {round(frame_times[0] / frame_times[1] * 1000, 2)}ms')
        frame_times[0], frame_times[1] = 0, 0

# terminate glfw, free up allocated resources
glfw.terminate()