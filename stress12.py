# Proof of Concept of Interactive Stress Tracker Dashboard
# Mike Komadina, June 2020
# Stanford Python Data Visualization class

# Combine Tkinter, Matplotlib and Seaborn to create a dashboard where the
# user can track both their stress level and various activities that
# may improve stress

# This is proof of concept for class working with many new concepts

# This code needs to be improved and refactored, but is intended to demonstrate capabilities
# and learn how to combine various aspects of data Visualization.

# Some sources of information:
# https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
# https://stackoverflow.com/questions/30774281/update-matplotlib-plot-in-tkinter-gui
# https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
# https://stackoverflow.com/questions/30490740/move-legend-outside-figure-in-seaborn-tsplot
# https://www.delftstack.com/howto/python-tkinter/how-to-pass-arguments-to-tkinter-button-command/
# https://stackoverflow.com/questions/20716842/python-download-images-from-google-image-search
# https://nickcharlton.net/posts/drawing-animating-shapes-matplotlib.html
# https://stackoverflow.com/questions/27533244/how-to-make-a-flashing-text-box-in-tkinter

import tkinter as tk
import os.path
from os import path
from subprocess import call
import datetime
import webbrowser
from urllib.request import urlopen
import json as simplejson
from io import StringIO
from PIL import ImageTk, Image
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.font_manager import FontProperties
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import statistics
import seaborn as sns
import subprocess
import numpy as np


time = 1        # each stress record is a time sequence; why not 0? not sure why I started with 1
actions = []    # records the actions (e.g. meditation) in between stress records
lastStress = 0  # the prior stress reading, used to track changes in stress from activities

plt.rcParams['legend.title_fontsize'] = 'xx-small'

# launches other python program to do breathing practice simulation
pyprog = 'breathe1.py'
def callpy(): os.system("python3 breathe1.py")

# log the stress levels and associated actions taken during that time period
def writeLog(x):
    global time, actions, lastStress
    f=open("stress.txt", "a+")
    f.write(str(time) + "," + x + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
    f.close()
    time += 1

    # write out impact of actions
    g=open("action.txt", "a+")
    for action in actions:
        #print(time)
        #print(action)
        g.write(str(time) + ",1," + action + "," + str(int(x) - lastStress) + "\n")
    g.close()

    lastStress = int(x)             # save the last stress level
    actions = []                    # clear the actions as we have associated them with the time period
    entryRecent.delete(0,"end")     # clear the recent actions entry field
    entryRecent.insert(0, "")

    recentString.set("Recent Activities: ")    # reset the recent activities list to just the label
    update(1)


# In hindsight it's probably wiser to just have the action call a lambda with value, but oh well.
def button_0():
    writeLog("0")

def button_1():
    writeLog("1")

def button_2():
    writeLog("2")

def button_3():
    writeLog("3")

def button_4():
    writeLog("4")

def button_5():
    writeLog("5")

def button_6():
    writeLog("6")

def button_7():
    writeLog("7")

def button_8():
    writeLog("8")

def button_9():
    writeLog("9")

def button_10():
    writeLog("10")

def meditate():
    action("meditate")

def iceCream():
    action("eat ice cream")

def coffee():
    action("coffee")

def journaling():
    action("journaling")

def running():
    action("runnning")

def stretching():
    action("stretching")

def breathing():
    action("breathing")

def netflix():
    action("netflix")


# allow the user to enter a customized value that is added to the list and stored
def customActivity():
    custom = entryRecent.get()
    action(custom)
    entryRecent.delete(0,"end")
    entryRecent.insert(0, custom + " added")

# record the added action
def action(actionStr):
    global actions
    actions.append(actionStr)
    recentString.set(recentString.get() + actionStr + ", ")

# used to launch to a web page
def OpenUrl(url):
    webbrowser.open_new(url)

# again, there is probably a better way to do this with lambda functions,
# but this maps the stress buttons to functions
mapping = {
  "button_0": button_0,
  "button_1": button_1,
  "button_2": button_2,
  "button_3": button_3,
  "button_4": button_4,
  "button_5": button_5,
  "button_6": button_6,
  "button_7": button_7,
  "button_8": button_8,
  "button_9": button_9,
  "button_10": button_10,
}


# find the max time count in the file
count = 1 # build up

# open the stress file and get the maximum value as starting point for count
if (path.exists('stress.txt')):
    stress_data = open('stress.txt','r').read()
    lines = stress_data.split('\n')
    for line in lines:
        if len(line) > 1:
            timex, y, timestamp = line.split(',')
            #print("time: " + timex)
            if (int(timex) > time):
                time = int(timex)

print("max count: ", time)

# set style for charts
style.use('fivethirtyeight')
fig = Figure(figsize=(8, 8), dpi=100)

# not having as much luck doing padding as I'd like
# TODO - figure out how to make this work better
fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

# Add two subplots - one for stress and one for tracking activities
t = np.arange(0, 3, .01)
ax1 = fig.add_subplot(2,1,1)
ax1.set_yticks(range(0,11))
ax2 = fig.add_subplot(2,1,2)

# TODO - work on this so it eventually shows the activity values sorted
def boxplot_sorted(df, by, column):
  df2 = pd.DataFrame({col:vals[column] for col, vals in df.groupby(by)})
  meds = df2.median().sort_values()
  df2[meds.index].boxplot(rot=90)

# Main loop which changes the charts triggered by events
# TODO - A lot can be optimized in this loop; too much is being created inside
# for a repeating function.
def update(i):
    global ax1, fig, lastStress

    graph_data = open('stress.txt','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []

    global count

    # grab the last 30 values to show
    numLines = len(lines)
    if (numLines > 30):
        lines = lines[numLines-30::]

    # read through values
    for line in lines:
        if len(line) > 1:
            x, y, timestamp = line.split(',')
            # convert to datetime to get values for labels
            datetime_object = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            # Show either by Date/Time or just by the number of events captured
            # depending on the toggle menu
            if (tkvar.get() == "By Dates and Times"):
                xs.append(datetime_object)
            else:
                xs.append(float(x))
            ys.append(float(y))

    # some formatting stuff, TODO - need to tighten
    plt.subplots_adjust(hspace=100)
    ax1.clear()
    ax1.set_yticks(range(0,11))

    fig = plt.gcf()
    fig.autofmt_xdate()

    # set the datetime font smaller to read
    # TODO - find better ways to adapt the display
    # The trick is some sampling may be days apart, some very frequent
    SMALL_SIZE = 4
    if (tkvar.get() == "By Dates and Times"):
        #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %I%p'))
        plt.rc('axes', labelsize=SMALL_SIZE)    # fontsize of the x and y labels
        for label in ax1.get_xticklabels():
            #label.set_rotation(40)
            #label.set_horizontalalignment('right')
            label.set_size(8)
        #ax1.xaxis.set_style

    ax1.plot(xs, ys)

    fontP = FontProperties()
    fontP.set_size('large')

    ax1.set_title("Stress Level")
    ax1.set_ylabel = "hi"

    # Show a Savitzky–Golay filter if there is enough data
    if (numLines > 30):
        yhat = savgol_filter(ys, 29, 3)
        if (statistics.median(yhat) > 7):
            #sns.lineplot(x="count", y="effect", data=df, ax=ax1)
            ax1.plot(xs, yhat, color='red') # show red if it's trending higher stress
        else:
            ax1.plot(xs, yhat, color='green')
    #   ax2.plot()
    count = count + 1

    ax2.clear()
    #ax2.set_title("Activity Impact on Stress")
    ax2.set_title("")
    df = pd.DataFrame(columns = {'period', 'count', 'action', 'effect'})
    graph_data = open('action.txt','r').read()
    lines = graph_data.split('\n')

    # read the data for the effect of each activity on stress level
    # it measures the delta between one stress reading and the next

    for line in lines:
        if len(line) > 1:
            x, y, a, e = line.split(',')
            #print(x, y, a, e)
            df = df.append(
                {
                    'period': int(x),
                    'count': int(y),
                    'action': a,
                    'effect': int(e)
                }, ignore_index = True
            )

    print(df)

    fontP = FontProperties()
    sns.set_style("darkgrid")  # was evaluting for a future one on ax3
    if (df.empty == False):
        ax3 = sns.boxplot(x="count", y="effect", hue = "action",data=df)
        plt.ylabel('Change in Stress', fontsize = 25)

    # TODO - work more on the grouping so it can show low to high
    grouped = df.groupby(["action"])

    df2 = pd.DataFrame({col:vals['effect'] for col,vals in grouped})

    meds = df2.median(axis = 0)
    meds.sort_values(ascending=True, inplace=True)
    print(meds)
    df4 = df2

    grouped = df.groupby('action').median

    ax2.legend(bbox_to_anchor=(3.1, 3.05))
    #boxplot_sorted(df, by=["count", "action"], column="effect")
    if (df.empty == False):
        # Check which is the most useful stress Activity
        best_activity = list(meds.keys())[0]
        best_activity_value = meds[best_activity]

        bestResult.delete("1.0", "end")
        bestResult.insert("1.0", best_activity.capitalize() + " has the best stress reduction with a median of " + str(best_activity_value))

        print("making boxplot")
        b = sns.boxplot(x="count", y="effect", hue = "action",data=df, ax=ax2)
        b.set_ylabel('Impact on Stress')
        b.set_xlabel('Type of Activity')
    # sns.boxplot(data=df, ax=ax2)

    # show different image depending on stress level
    if (lastStress > 8):
        path = "corgi2.jpg"
    elif (lastStress > 4):
        path = "kitten1.jpg"
    else:
        path = "water1.jpg"

    img2 = ImageTk.PhotoImage(Image.open(path))
    panel2.configure(image=img2)
    panel2.image = img2

    canvas.draw()



###### boxplot
# TODO - combine with earlier code. this is oddly broken up by Update() in between


root = tk.Tk()
root.wm_title("Stress Tracking")
button = []
button2 = []

entryRecent = tk.Entry(root, width=40)

recentString = tk.StringVar(root)

stressLabel = tk.Label(root,
                    textvariable = recentString, font = "Helvetica 14 bold italic")
stressLabel.grid(column=1, row=9, ipadx=5, pady=0, sticky=tk.W+tk.N, columnspan = 15)
recentString.set("Recent Activities: ")

entryRecent.grid(column=1, row=10, padx=10, pady=0, sticky=tk.NW+tk.N, columnspan = 10)
entryRecent.insert(0, "")

labelName= tk.Label(root,
                    text = "Mike Komadina, 2020", font = "Helvetica 12 italic")
labelName.grid(column=10, row=11, ipadx=5, pady=0, sticky=tk.W+tk.N, columnspan = 2)

#r = range(11)
#for i in r:
#    button2.append(tk.Button(master=root, text=str(i*10), fg="red"))
#    button2[i].pack(side = tk.BOTTOM)

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
#stressLabel.grid(column=0, row=0, ipadx=5, pady=5, sticky=tk.W+tk.N)
canvas.get_tk_widget().grid(column = 0, row = 1, columnspan=1,  rowspan=10)
#canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
#canvas.get_tk_widget().grid(column=1, row=1)


#toolbar = NavigationToolbar2Tk(canvas, root)
#toolbar.update()
#canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def track(i):
    print(i)

def change_color():
    current_color = stressLabel.cget("background")
    next_color = "green" if current_color == "cyan" else "cyan"
    stressLabel.config(background=next_color)
    root.after(1000, change_color)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)

def process_scroll(event):
    print("scrolling")

canvas.mpl_connect('scroll_event', process_scroll)

#canvas.mpl_connect("key_press_event", on_key_press)

# TODO - put in quit button
def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


# on change dropdown filter by date or samples
def change_dropdown(*args):
    print( tkvar.get() )
    update(1)

# on change dropdown value - TODO add time duration choice
def change_duration(*args):
    print( tkvar2.get() )
    update(1)


# Generate the stress buttons
# TODO - Move the function definitions and main code

r = range(11)
for i in r:
    func_name = 'button_' + str(i)
    button.append(tk.Button(master=root, text=str(i), height=2, width=3, command = mapping[func_name]))
    button[i].grid(column= 1+i, row = 2, sticky=tk.NW)

stressLabel = tk.Label(master=root,
               text = "Please record your Stress Level (0=Low, 10=High)", font = "Helvetica 20 bold")
stressLabel.grid(column = 1, row = 1, columnspan=10, sticky=tk.W)

bestResult = tk.Text(root, height=3, width=60)
bestResult.configure(font=("Helvetica", 25, "bold"))
S = tk.Scrollbar(root)
bestResult.config(yscrollcommand=S.set)
quote = ""
bestResult.insert(tk.END, quote)
bestResult.grid(column = 0, row =15, columnspan = 2, sticky=tk.N)


# Fun buttons for stress interventions
url = 'https://www.tylervigen.com/spurious-correlations'
bDataChill = tk.Button(root, text="Spurious Correlations", command=lambda aurl=url:OpenUrl(aurl))
bDataChill.grid(column = 1, row = 4, columnspan = 2, sticky=tk.NW)

bBreathe = tk.Button(root, text="Breathe in Data", command = callpy)
bBreathe.grid(column = 3, row = 4, columnspan = 2, sticky=tk.NW)

url2 = 'https://www.google.com/search?q=pretty+pie+charts&source=lnms&tbm=isch'
bPie = tk.Button(root, text="Pretty Pie Charts", command=lambda aurl=url:OpenUrl(url2))
bPie.grid(column = 5, row = 4, columnspan = 2, sticky=tk.NW)


# add action buttons
stressLabel2 = tk.Label(master=root,
               text = "Please record any actions you took that may impact stress", font = "Helvetica 20 bold")
stressLabel2.grid(column = 1, row = 5, columnspan = 10, sticky=tk.W)

bIceCream = tk.Button(master=root, text="ice cream", width = 10, command = iceCream)
bIceCream.grid(column = 1, row = 6, columnspan = 2, sticky=tk.NW)
bMeditation = tk.Button(master=root, text="meditation", width = 10, command = meditate)
bMeditation.grid(column = 3, row = 6, columnspan = 2, sticky=tk.NW)
bcoffee = tk.Button(master=root, text="coffee", width = 10, command = coffee)
bcoffee.grid(column = 5, row = 6, columnspan = 2, sticky=tk.NW)
bJournaling = tk.Button(master=root, text="journaling", width = 10, command = journaling)
bJournaling.grid(column = 7, row = 6, columnspan = 2, sticky=tk.NW)


bBreathing = tk.Button(master=root, text="breathing", width = 10, command = breathing)
bBreathing.grid(column = 1, row = 7, columnspan = 2, sticky=tk.NW)
bNetflix = tk.Button(master=root, text="Netflix", width = 10, command = netflix)
bNetflix.grid(column = 3, row = 7, columnspan = 2, sticky=tk.NW)
bRunning = tk.Button(master=root, text="running", width = 10, command = running)
bRunning.grid(column = 5, row = 7, columnspan = 2, sticky=tk.NW)
bStretching = tk.Button(master=root, text="stretching", width = 10, command = stretching)
bStretching.grid(column = 7, row = 7, columnspan = 2, sticky=tk.NW)


# Allow user to type a custom Activity
# TODO - generate a button to match
bCustomActivity = tk.Button(master=root, text="Type and save a custom activity", command = customActivity)
bCustomActivity.grid(column = 7, row = 10, columnspan = 5, sticky=tk.NW)

## CHOICE OF DATE OR SERIES
# Create a tk variable
tkvar = tk.StringVar(root)

# Dictionary with options
choices = { 'By Dates and Times', "By Measurement"}
tkvar.set('By Dates and Times') # set the default option
# link function to change dropdown
tkvar.trace('w', change_dropdown)
popupMenu = tk.OptionMenu(root, tkvar, *choices)
#labelDates = tk.Label(root, font = "Helvetica 14 bold", text="Choose a dish").grid(row = 0, column = 1)
popupMenu.grid(row = 0, column =0)
popupMenu.config(width=20, font=('Helvetica', 12))

# Add the color bar to go along with stress buttons
path = "colors.png"
img = ImageTk.PhotoImage(Image.open(path).resize((750, 8)))
panel = tk.Label(root, image = img)
panel.grid(row=2, column = 1, columnspan = 11, sticky=tk.W)

# image for calm water
path = "water1.jpg"

img2 = ImageTk.PhotoImage(Image.open(path))
panel2 = tk.Label(root, image = img2)
panel2.grid(row=3, column = 1, columnspan = 11, sticky=tk.NW)

#redbutton = tk.Button(master=root, text="Red", fg="red")
#redbutton.pack( side = tk.LEFT)
#quitButton.grid(column = 0, row = 1, pady = 1, sticky=tk.W)
#change_color()

# This was needed to avoid a known bug between Tkinter and Matplotlib
# where scrolling causes crashing
while True:
    try:
        tk.mainloop()
        break
    except UnicodeDecodeError:
        pass

#tk.mainloop()

# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
