from pynput.mouse import Button, Controller
from pynput.keyboard import Key
from pynput import keyboard
import time
from PIL import ImageGrab
from pynput import keyboard
import time

speedMultiplier = 1.5
hr = True
running = True

#figuring out the code will be left as an excersise for the reader

#parsing the .osu fule
song_path = r"the\path\to\the\.osu\file\here"
normalnotes = open("%s" % song_path, encoding = "utf8")
targetpoints = open("%s" % song_path, encoding = "utf8") #probably don't need to open it twice, but oh well

targetpoints = targetpoints.read().splitlines()

#weird tech with reading files; once a line is read, it won't be read again. Therefore, we read until the hitcircle, and then read the rest into a list
while True:
    line = normalnotes.readline()
    if("SliderMultiplier" in line):
        line = line.split(":")
        preslidervelocity = float(line[1].strip("\n")) #getting the slider velocity
    if("[HitObjects]" in line): #checking if we have read to the hit circles
        break

timingpoints = []

#a very jank way to get the timing points
reading = False
for i in targetpoints:
    if("[Colours]" in i):
        break

    if(reading == True):
        if(i == ""):
            break
        timingpoints.append(i.split(","))

    if("[TimingPoints]" in i):
        reading = True

#function to detect keystrokes; press esc to stop the program
def on_press(key):
    pass

def on_release(key):
    global running
    if key == keyboard.Key.esc:
        # Stop the loop
        running = False

#thread to detect key presses
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()


#setting up the mouse to be pushed around
mouse = Controller()

#getting the notes
normalnotes = normalnotes.read().splitlines()
normalnotes = [i.split(",") for i in normalnotes]
timing = int(normalnotes[0][2])

#formatting the note list
notes = [[int(i[0]), int(i[1]), int(i[2]) - timing, int(i[3])] for i in normalnotes]

#time.sleep is wildly inaccurate so im using this instead
def accuratewait(howlong):
    targettime = time.perf_counter() + howlong
    while(time.perf_counter() < targettime):
        pass
    return

#this is to reliably start the program at the same time every time. It clicks the reset button
accuratewait(2)
mouse.click(Button.left, 1)

#function for checking the color wheel to see if it's still green. This is to detect when the maps starts, since it seems to be randomized.
def isgreen(rgb):
    return(rgb[0] > rgb[2] * 1.5 and rgb[1] > rgb[2] * 1.5)

mouse = Controller()

#giving time for the loading animation
accuratewait(1)

prepos = [notes[0][0] / 614.4 * 1280 + 100, 1024 - (notes[0][1] / 460.8 * 1024 + 50) if hr else (notes[0][1] / 460.8 * 1024 + 100)]
mouse.position = prepos[0], prepos[1]

#waiting until the map fully starts
while True:
    screen = ImageGrab.grab()

    pixel = list(screen.getpixel((354, 67)))

    if(not isgreen(pixel)):
        break

#maps with skips are more janky so im using this EXTREMELY janky code to counterbalance
if(int(normalnotes[0][2]) > 600):
    accuratewait(int(normalnotes[0][2])/160000)

#getting when the beatmap started
starttime = time.perf_counter() * 1000

#assigning some variables for the sliders
bpm = float(timingpoints[0][1])
slidervelocity = preslidervelocity if hr else preslidervelocity

#running over the entire song
while(len(notes) > 0) and running:

    currenttime = round((time.perf_counter() * 1000 - starttime - 10)*speedMultiplier)

    #timing points suck
    try:
        if(float(timingpoints[0][0]) - timing <= currenttime):
            if(float(timingpoints[0][1]) < 0):
                slidervelocity = preslidervelocity * (100/(float(timingpoints[0][1]) * -1)) if hr else preslidervelocity * (100/(float(timingpoints[0][1]) * -1))
            else:
                bpm = float(timingpoints[0][1])
            timingpoints.pop(0)
    except:
        pass

    #checking if the time the note appears in is the same time as the time since the song started
    if(notes[0][2] <= currenttime):

        #type 12 is a spinner
        if(notes[0][3] == 12):
            mouse.press(Button.left)
            while(currenttime < float(normalnotes[0][5]) - timing):
                currenttime = round((time.perf_counter() * 1000 - starttime - 10)*speedMultiplier)

                #the triangle spin???? not clickbait???
                mouse.position = 640, 480
                accuratewait(0.003)
                mouse.position = 600, 540
                accuratewait(0.003)
                mouse.position = 680, 540
                accuratewait(0.003)

            mouse.release(Button.left)
            mouse.position = notes[1][0] / 614.4 * 1280 + 100, 1024 - (notes[1][1] / 460.8 * 1024 + 50) if hr else (notes[1][1] / 460.8 * 1024 + 100)

        #slider!!!!!! EW
        elif(notes[0][3] == 6 or notes[0][3] == 2):
            #how long the slider is
            slidertime = (float(normalnotes[0][7]))/(slidervelocity * 100) * bpm/1000

            prepos = [notes[0][0] / 614.4 * 1280 + 100, 1024 - (notes[0][1] / 460.8 * 1024 + 50) if hr else (notes[0][1] / 460.8 * 1024 + 100)]
            slideranchors = normalnotes[0][5].split("|")
            lastnote = slideranchors[-1].split(":")

            targetpos = [int(lastnote[0]) / 614.4 * 1280 + 100, 1024 - (int(lastnote[1]) / 460.8 * 1024 + 50) if hr else (int(lastnote[1]) / 460.8 * 1024 + 100)]
            mouse.position = prepos[0], prepos[1]
            distance = [targetpos[0] - prepos[0], targetpos[1] - prepos[1]]

            targetpos, prepos = prepos, targetpos
            #interpolation stuff
            for j in range(int(normalnotes[0][6])):
                targetpos, prepos = prepos, targetpos
                distance = [targetpos[0] - prepos[0], targetpos[1] - prepos[1]]
                mouse.position = prepos[0], prepos[1]

                for i in range(10):
                    accuratewait(slidertime/10/speedMultiplier)
                    mouse.move(distance[0]/10, distance[1]/10)

            mouse.press(Button.left)
            newtargetpos = [notes[1][0] / 614.4 * 1280 + 100, 1024 - (notes[1][1] / 460.8 * 1024 + 50) if hr else (notes[1][1] / 460.8 * 1024 + 100)]
            distance = [newtargetpos[0] - targetpos[0], newtargetpos[1] - targetpos[1]]

            #Interpolating from a slider
            timebetween = (notes[1][2] - notes[0][2])/1000
            for i in range(10):
                accuratewait((timebetween - slidertime * int(normalnotes[0][6]))/15/speedMultiplier)
                mouse.move(distance[0]/10, distance[1]/10)

            mouse.position = (notes[1][0] / 614.4 * 1280 + 100, 1024 - (notes[1][1] / 460.8 * 1024 + 50) if hr else (notes[1][1] / 460.8 * 1024 + 100))

            mouse.release(Button.left)

        else: #This are the normal hitcircles
            prepos = [notes[0][0] / 614.4 * 1280 + 100, 1024 - (notes[0][1] / 460.8 * 1024 + 50) if hr else (notes[0][1] / 460.8 * 1024 + 100)]
            mouse.position = prepos[0], prepos[1]
            targetpos = [notes[1][0] / 614.4 * 1280 + 100, 1024 - (notes[1][1] / 460.8 * 1024 + 50) if hr else (notes[1][1] / 460.8 * 1024 + 100)]
            timebetween = (notes[1][2] - notes[0][2])/1000
            distance = [targetpos[0] - prepos[0], targetpos[1] - prepos[1]]

            #interpolation between the circles. 
            for i in range(10):
                accuratewait(timebetween/15/speedMultiplier)
                mouse.move(distance[0]/10, distance[1]/10)
            mouse.click(Button.left, 1)

        notes.pop(0)
        normalnotes.pop(0)
