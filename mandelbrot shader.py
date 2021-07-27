import glfw, timeit
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

file1 = open("MyFile.txt", "w")
file1.close()
# viewer parameters
xmax, ymax = 1920.0, 1060.0  # Width and height (respectively) of display window
center_xt, center_yt, zoomt = -0.5, 0.0, 1.01  # Target center and target zoom
center_x, center_y, zoom = center_xt, center_yt, zoomt  # Actual center and actual zoom
wx = 4  # Width of complex plane displayed
wy = wx * ymax / xmax  # Height of complex plane displayed
newpos = [0, 0]  # Mouse pixel coordinate
zoomin, zoomout, moveup, movedown, moveleft, moveright = False, False, False, False, False, False


# making all the glfw callback functions for keyboard and mouse inputs
def mouse_button_clb(window, button, action, mode):
    global center_xt, center_yt, newpos
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        center_xt += (newpos[0] / xmax - 0.5) * wx / zoom
        center_yt -= (newpos[1] / ymax - 0.5) * wy / zoom


def cursor_pos_clb(window, xpos, ypos):
    mouse_coord(xpos, ypos)


def scroll_clb(window, xoffset, yoffset):
    global zoomin, zoomout
    pass
    # if int(yoffset) > 0.5:
    #     zoomin = True
    # elif int(yoffset) < -0.5:
    #     zoomout = True


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


# making all the keyboard and mouse actions
def kbcamera():
    """
    keyboard controls for camera, sets the zoom levels by q and e keys for zooming in and out respectively
    :return:
    """
    global center_x, center_y, zoom, zoomin, zoomout, moveup, movedown, moveleft, moveright
    if zoomin:
        zoom *= 1.02
        # zoomin = False
    if zoomout:
        zoom *= 1 / 1.02
        # zoomout = False
    # if moveup:
    #     center_yt += move_size
    #     # moveup = False
    # if movedown:
    #     center_yt -= move_size
    #     # movedown = False
    # if moveright:
    #     center_xt += move_size
    #     # moveright = False
    # if moveleft:
    #     center_xt -= move_size
    #     # moveleft = False


def mouse_coord(xpos, ypos):
    """
    setting the mouse coordinates every frame
    :param xpos:
    :param ypos:
    :return:
    """
    global newpos
    newpos = [xpos, ypos + 16]


def mscamera():
    """
    mouse controls for camera, moving the center of the window to where user clicks on the window
    :return:
    """
    global center_x, center_y, zoomt, zoom, zoomin, zoomout

    dx = center_xt - center_x
    dy = center_yt - center_y

    center_x += dx * 0.08
    center_y += dy * 0.08
    # if zoomin:
    #     zoomt *= 1.2
    #     # zoomin = False
    # elif zoomout:
    #     zoomt *= 1/1.2
    #     # zoomout = False
    #
    # dz = zoomt - zoom
    # print(dz, zoomt)
    # zoom += dz * 0.01
    # if dz < (0.1 * zoomt):
    #     zoomt = zoom


# glsl code for vertex shader, the vertex shader is responsible for setting the vertex properties on screen,
# and for passing the out data to the fragment shader
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

# glsl code for fragment shader, the fragment shader is responsible for colouring each and every pixel on the window
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
    float color = 1.0*itr/itr_limit*int(itr<temp_threshold)+converged*int(itr>itr_limit);


    if (xy.x > 959 && xy.x < 961)
    {   
        if (xy.y > 529 && xy.y < 551)
        {
            out_color = vec4(1.0, 0.0, 0.0, 1.0);
        } else
        {
        out_color = vec4(0.2*color, 0.4*color, 0.8*color, 1.0);
        }
    } else if (xy.y > 539 && xy.y < 541)
    {   
        if (xy.x > 949 && xy.x < 971)
        {
            out_color = vec4(1.0, 0.0, 0.0, 1.0);
        } else
        {
        out_color = vec4(0.2*color, 0.4*color, 0.8*color, 1.0);
        }
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

# set window's position on screen
glfw.set_window_pos(window, 0, 34)
glfw.make_context_current(window)

# set Vsync to be zero so frame time can go lower than 16.66ms
glfw.swap_interval(0)

# setting all glfw input callbacks
glfw.set_key_callback(window, key_input_clb)
glfw.set_cursor_pos_callback(window, cursor_pos_clb)
glfw.set_mouse_button_callback(window, mouse_button_clb)
glfw.set_scroll_callback(window, scroll_clb)

# compiling and using shader programs
shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
glUseProgram(shader)

# frame time variables
frame_times = [0, 0]

# the main application loop
while not glfw.window_should_close(window):
    # move_size = wy/zoom * 0.005

    tic = timeit.default_timer()  # frame timer start

    # setting shader inputs
    shader_inputs = [-1.0, 1.0, 0.0,  # vertex 1 position
                     1111111111.0, 1.0, 0.0,  # vertex 2 position
                     -1.0, -1111111111.0, 0.0,  # vertex 3 position
                     xmax, ymax,  # width and height of glfw window
                     center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                     wx, wy]  # width and height of complex plane

    shader_inputs = np.array(shader_inputs, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, shader_inputs.nbytes, shader_inputs, GL_STATIC_DRAW)

    # instructions to opengl what the input parameters are
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

    # running the camera functions to facilitate camera movement
    kbcamera()
    mscamera()

    glClear(GL_COLOR_BUFFER_BIT)

    # drawing on the window
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glfw.swap_buffers(window)

    toc = timeit.default_timer()  # frame timer end

    # calculate frame time
    frame_times[0] += toc - tic
    frame_times[1] += 1

    # printing frame time averaged over 50 frames
    if frame_times[1] >= 50:
        print(f'frame time = {round(frame_times[0] / frame_times[1] * 1000, 2)}ms')
        frame_times[0], frame_times[1] = 0, 0

# terminate glfw, free up allocated resources
glfw.terminate()