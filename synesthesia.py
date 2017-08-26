import alsaaudio as aa
import fft
import time
import random
import copy
from neopixel import Adafruit_NeoPixel
from neopixel import Color
from populate_coldict import popcol

LED_NUMBER=30
STARTING_VAL = 13
BIN_SIZE = 0.06
STEP_MODIFIER = 0.002
SAMPLE_RATE = 44100
CHUNK_SIZE = 192
LOWER_FREQ = 0
HIGHER_FREQ = 16000

light_types = ["volume","waterfall","frequency"]

strip = Adafruit_NeoPixel(LED_NUMBER,18,800000, 5, False, 100)
strip.begin()
silence=False
highest = 0

modifier = 0
prev_highest = 0
prev_list = [0,0,0,0,0,0,0,0,0,0,0,0,0]

bin_dict = {}
# Creates a threshold for every led, once threshold is surpassed the led is lit
for i in range(0,LED_NUMBER):
    STARTING_VAL += BIN_SIZE
    bin_dict[i] = STARTING_VAL

waterfall_dict = {}
for i in range(0,LED_NUMBER):
    waterfall_dict[i] = [0,0,0]

ticket_dict = {}
for i in range(0,LED_NUMBER):
    ticket_dict[i] = 0



"""looks at difference between current highest sound and previous highest sound
the bigger the difference the brighter the colour, this colour is then set as
the first led in the waterfall dict and all colours are carried forward by one,
such that anytime a beat occurs it appears to travel along the led strip"""
def update_lights_waterfall(matrix,coldict):
    global prev_highest
    cur_sound = max(matrix)
    cur_val = cur_sound - prev_highest
    if cur_val > 0.5:
        cur_val = 0.5
    if cur_val < 0:
        cur_val = 0
    maxled = int(cur_val*(LED_NUMBER-1)*2)
    pulse_colour = coldict[maxled]
    waterfall_dict[0] = pulse_colour
    for x in range(LED_NUMBER,0,-1):
        waterfall_dict[x] = waterfall_dict[x-1]
    for x in range(LED_NUMBER,0,-1):
        strip.setPixelColor(x,Color(waterfall_dict[x][0],waterfall_dict[x][1],waterfall_dict[x][2]))
    strip.show()
    prev_highest = cur_sound
   


# updates lights based on frequency, each time it's called it's looks at the most common led number in 
#prev_list and lights that led, this is done to help reduce noise.
def update_lights_frequency(matrix,coldict,prev_list):
    maxval = max(matrix)
    
    #if highest sound is below this value then decay everything and return
    if maxval < 9.25:
        for i in range(0,LED_NUMBER):
            rolling_col_dict[i][0] -= 8#r_decay
            rolling_col_dict[i][1] -= 8#g_decay
            rolling_col_dict[i][2] -= 8#b_decay
            if rolling_col_dict[i][0] < 0:
                rolling_col_dict[i][0] = 0
            if rolling_col_dict[i][1] < 0:
                rolling_col_dict[i][1] = 0
            if rolling_col_dict[i][2] < 0:
                rolling_col_dict[i][2] = 0
        for i in range(0,LED_NUMBER):
            strip.setPixelColor(i,Color(rolling_col_dict[i][0],rolling_col_dict[i][1],rolling_col_dict[i][2]))
        strip.show()
        return None
    
    # find the highest led, add it to prev list and move everything in prev list back by one
    for i in range(0,LED_NUMBER):
        if matrix[i] == maxval:
            for z in range(11,-1,-1):
                prev_list[z] = prev_list[z+1]
            prev_list[-1] = i
            
    #get the most common led in prev_list        
    mode = max(set(prev_list), key=prev_list.count)

    #ticket dict is used to allow each led to have multiple tickets, only when an led's ticket count gets to zero does
    #it's light begin to fade, without this the leds come on/off too quickly leading to a jarring effect
    if ticket_dict[mode] < 5:
        ticket_dict[mode] += 1
    for i in range(0,LED_NUMBER):
        if ticket_dict[i] == 0:
            rolling_col_dict[i][0] -= 8#r_decay
            rolling_col_dict[i][1] -= 8#g_decay
            rolling_col_dict[i][2] -= 8#b_decay
            
            if rolling_col_dict[i][0] < 0:
                rolling_col_dict[i][0] = 0
            if rolling_col_dict[i][1] < 0:
                rolling_col_dict[i][1] = 0
            if rolling_col_dict[i][2] < 0:
                rolling_col_dict[i][2] = 0
        else:    
            ticket_dict[i] -= 1
            r = int(coldict[i][0])
            g = int(coldict[i][1])
            b = int(coldict[i][2])
            rolling_col_dict[i] = [r,g,b]
    for i in range(0,LED_NUMBER):
        strip.setPixelColor(i,Color(rolling_col_dict[i][0],rolling_col_dict[i][1],rolling_col_dict[i][2]))
    strip.show()


""" Number of leds lit is based on current volume, very loud volume means entire strip is lit. Can't put hard frequency_limits
here as volume is very much dependent on song and output device, so a modifier is used to make it raise or lower the frequency_limits
if there is too much/too little activity"""
def update_lights_volume(matrix,coldict):
    global modifier
    maxled = 0
    cur_sound = max(matrix)
    for i in bin_dict:
        if cur_sound > (bin_dict[i]+modifier):
            maxled = i+1
    if maxled <= 3:
        modifier -= STEP_MODIFIER
    if maxled >= 25:
        modifier += STEP_MODIFIER
    if modifier > 4:
        modifier = 4
    if modifier < -3:
        modifier = -3
    for i in range(0,maxled):
        strip.setPixelColor(i,Color(coldict[i][0],coldict[i][1],coldict[i][2]))
    for i in range(maxled,LED_NUMBER):
        strip.setPixelColor(i,Color(0,0,0))
    strip.show()




chosen_type = random.choice(light_types)
def set_stream(higher_freq,lower_freq,sample_rate,chunk_size):
    non_linear_bin = 120
    total_bin = 600
    frequency_limits = []
    for i in range(0,LED_NUMBER):
        lower_limit = total_bin
        upper_limit = total_bin + non_linear_bin
        frequency_limits.append((lower_limit, upper_limit))
        total_bin = upper_limit
        non_linear_bin += 28
    stream = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL,device='sysdefault:CARD=Set')
    stream.setchannels(2)
    stream.setformat(aa.PCM_FORMAT_S16_LE) 
    stream.setrate(sample_rate)
    stream.setperiodsize(chunk_size)
    return (frequency_limits,stream)


lowcount = 0


chosen_type = random.choice(light_types)
if chosen_type == "volume":
    coldict = popcol(LED_NUMBER,"binned")
    frequency_limits,stream = set_stream(HIGHER_FREQ,LOWER_FREQ,SAMPLE_RATE,CHUNK_SIZE)
elif chosen_type == "waterfall":
    coldict = popcol(LED_NUMBER,"grad_increase")
    frequency_limits,stream = set_stream(HIGHER_FREQ,LOWER_FREQ,SAMPLE_RATE,CHUNK_SIZE)
elif chosen_type == "frequency":
    coldict = popcol(LED_NUMBER,"gradient")
    rolling_col_dict = copy.deepcopy(coldict)
    frequency_limits,stream = set_stream(HIGHER_FREQ,LOWER_FREQ,SAMPLE_RATE,CHUNK_SIZE)
    
    
    
    
""" Continously reads data from stream and passes it to update_lights,also detects if a song has ended and
changes the update lights function and coldict """
while True:
    data=stream.read()
    matrix = fft.calculate_levels(data[1], CHUNK_SIZE, SAMPLE_RATE, frequency_limits, 2)
    maxmatrix = max(matrix)
    if maxmatrix < 9:
        lowcount +=1
    else:
        lowcount = 0
        silence = False
    if lowcount > 10.0 and silence == False:
        silence = True
        chosen_type = random.choice(light_types)
        if chosen_type == "volume":
            coldict = popcol(LED_NUMBER,"binned")
            frequency_limits,stream = set_stream(HIGHER_FREQ,LOWER_FREQ,SAMPLE_RATE,CHUNK_SIZE)
        elif chosen_type == "waterfall":
            coldict = popcol(LED_NUMBER,"grad_increase")
            frequency_limits,stream = set_stream(HIGHER_FREQ,LOWER_FREQ,SAMPLE_RATE,CHUNK_SIZE)
        elif chosen_type == "frequency":
            coldict = popcol(LED_NUMBER,"gradient")
            rolling_col_dict = copy.deepcopy(coldict)
            frequency_limits,stream = set_stream(HIGHER_FREQ,LOWER_FREQ,SAMPLE_RATE,CHUNK_SIZE)
    if chosen_type == "volume":
        update_lights_volume(matrix,coldict)
    elif chosen_type == "waterfall":
        update_lights_waterfall(matrix,coldict)
    elif chosen_type == "frequency":
        update_lights_frequency(matrix,coldict,prev_list)

