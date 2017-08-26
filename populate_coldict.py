import random


def popcol(led_num, dict_type):
    all_colours = {"red":[255,0,0],"lime":[0,255,0],"blue":[0,0,255],"yellow":[255,255,0],"cyan":[0,255,255],"magnenta":[255,0,255],"silver":[192,192,192],
                   "crimson":[225,40,90],"tomato":[255,99,71],"orangered":[255,69,0],"gold":[255,215,0],"goldenrod":[218,165,32],"lawngreen":[124,252,0],
                   "springgreen":[0,250,154],"deepskyblue":[0,191,255],"blueviolet":[138,43,226],"deeppink":[255,20,147],"aquamarine":[127,255,212]}
    coldict = {}
    if dict_type == "gradient":
        starting_colour = all_colours[random.choice(all_colours.keys())]
        ending_colour = all_colours[random.choice(all_colours.keys())]
        
        r_step = (ending_colour[0]-starting_colour[0])/led_num
        g_step = (ending_colour[1]-starting_colour[1])/led_num
        b_step = (ending_colour[2]-starting_colour[2])/led_num
    
        coldict[0] = starting_colour    
        for i in range(1,led_num):
            temp_dict = {"r":coldict[i-1][0] + r_step,
                         "g":coldict[i-1][1] + g_step,
                         "b":coldict[i-1][2] + b_step}
            for key in temp_dict:
                if temp_dict[key] > 255:
                    temp_dict[key] = 255
                elif temp_dict[key] < 0:
                    temp_dict[key] = 0
                
            coldict[i] = [temp_dict["r"],temp_dict["g"],temp_dict["b"]]
            
    elif dict_type == "grad_increase":        
        starting_colour = [0,0,0]
        ending_colour = all_colours[random.choice(all_colours.keys())]
        
        r_step = (ending_colour[0]-starting_colour[0])/led_num
        g_step = (ending_colour[1]-starting_colour[1])/led_num
        b_step = (ending_colour[2]-starting_colour[2])/led_num
    
        coldict[0] = starting_colour    
        for i in range(1,led_num):
            temp_dict = {"r":coldict[i-1][0] + r_step,
                         "g":coldict[i-1][1] + g_step,
                         "b":coldict[i-1][2] + b_step}
            for key in temp_dict:
                if temp_dict[key] > 255:
                    temp_dict[key] = 255
                elif temp_dict[key] < 0:
                    temp_dict[key] = 0
                
            coldict[i] = [temp_dict["r"],temp_dict["g"],temp_dict["b"]]
    
    elif dict_type == "random":
        for i in range(0,led_num):
            coldict[i] = all_colours[random.choice(all_colours.keys())]
            
    elif dict_type == "binned":
        for i in range(0,led_num,10):
            rancol = all_colours[random.choice(all_colours.keys())]
            for x in range(i,i+10):
                coldict[x] = rancol

    return coldict
        
