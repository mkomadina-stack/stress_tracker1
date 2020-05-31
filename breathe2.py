# adapted from: https://nickcharlton.net/posts/drawing-animating-shapes-matplotlib.html

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import ffmpeg

# build a rectangle in axes coords
left, width = .2, .5
bottom, height = .5, .5
right = left + width
top = bottom + height


fig = plt.figure()
fig.set_dpi(100)
fig.set_size_inches(7, 6.5)


ax = plt.axes(xlim=(0, 10), ylim=(0, 10))
patch = plt.Circle((6, 6), 0.75, fc='cyan')
patch2 = plt.Circle((6, 6), 0.75, fc='limegreen')
time_text2 = ax.text(left, bottom, '',
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax.transAxes, fontsize = 20)

#plt.axhline(y = 2, alpha = 0.5, linestyle = '--')  #horizontal line
plt.hlines(6, 0.0, 5.0, linestyles = 'dashed', colors = 'lightblue')
#plt.axhline(y = 6, alpha = 0.5, linestyle = '--', xmin=0.0, xmax=5.0)  #horizontal line
plt.axvline(x = 5, alpha = 0.5, linestyle = '--')  #horizontal line
#plt.axvline(X_POSITION, ...)  #vertical line

def init():
    patch.center = (4, 1)
    ax.add_patch(patch)
    time_text2.set_text('')
    return patch, time_text2

def animate(i):

    x, y = patch.center
    x = 5 + 3 * np.sin(np.radians(i+200))
    y = 5 + 3 * np.cos(np.radians(i+200))

    patch.center = (x, y)

    if (x > 5):
        time_text2.set_text('Breathe out BAD data\npandas.DataFrame.dropna()')
        #patch.set_facecolor('gray')
        patch.set_facecolor([0,i/360,0])
    else:
        if (y < 6):
            time_text2.set_text('Breathe in GOOD data\npandas.read_csv()')
            #patch.set_facecolor('limegreen')
            patch.set_facecolor([.1,.8,.2])
        else:
            time_text2.set_text("Hold the data\ndf.describe()")
            patch.set_facecolor([.1,.9,.2])

    if (i < 180):
        patch.set_facecolor([0, 1-(i/360), 0])
    else:
        patch.set_facecolor([0, i/360, 0])

    return patch, time_text2

anim = animation.FuncAnimation(fig, animate,
                               init_func=init,
                               frames=360,
                               interval=30,
                               blit=True)

#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=20, metadata=dict(artist='Me'), bitrate=1800)
#anim.save('animation.mp4', writer=writer)

anim.save('animation2.mp4', fps=30, 
          extra_args=['-vcodec', 'h264',
                      '-pix_fmt', 'yuv420p'])

#anim.save('animation.mp4', fps=30)

plt.show()
