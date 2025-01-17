# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 02:30:45 2023

@author: anshbharadwaj
"""



import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter




'''IMPORT STATEMENTS: Used to import position data from excel into Python, depending on how it has been stored'''




df1 = pd.read_excel('C:/Users/ANSH/Desktop/Eye Datasets-Saccade course/d4/Assignment_dataset.xlsx', header=None, sheet_name='EyeX')
df2 = pd.read_excel('C:/Users/ANSH/Desktop/Eye Datasets-Saccade course/d4/Assignment_dataset.xlsx', header=None, sheet_name='EyeY')
#df = pd.read_excel('C:/Users/ANSH/Desktop/simple.xlsx',header=None) #name of the Excel file I was using.

big_amplist = []
big_vellist = []
big_durlist = []


for row_num in range(30):



    temp_x=df1.iloc[row_num] #Reads first row of the Excel spreadsheet
    eye_x=temp_x.to_numpy() #Position data along x-axis stored in Numpy array eye_x
    temp_y=df2.iloc[row_num] #Reads second row of the Excel spreadsheet
    eye_y=temp_y.to_numpy() #Position data along y-axis stored in Numpy array eye_y
    #print(eye_x.size, eye_y.size) #Prints lengths of each array
    
    
    
    
    
    '''PLOTTING RAW POSITION DATA AGAINST TIME'''
    '''
    f=plt.figure(1)
    f.set_figheight(10) #Setting the dimensions (length & width) of the figure to be generated
    f.set_figwidth(20)  
    time_axis = np.arange(1,(eye_x.size+1)) #Specifying the time axis
    plt.plot(time_axis, eye_x, 'ro', label='Eye position along x axis') #Plotting eye x-coordinates
    plt.plot(time_axis, eye_y, 'bo', label='Eye position along y axis') #Plotting eye y-coordinates
    plt.legend(loc="upper left", fontsize = "16") #Specifying legend... 
    plt.xlabel("Time (ms)", fontsize = "20") #...and axis labels
    plt.ylabel("Eye position (degrees)", fontsize = "20")
    '''
    
    
    
    
    '''CHECKING FOR & REMOVING NaN VALUES'''
    
    #Checking where the first NaN value occurs for y-position data
    for i_y in range(eye_y.size):
        if np.isnan(eye_y[i_y])==True:
           # print(i_y)
            break
    
    #Checking where the first NaN value occurs for x-position data
    for i_x in range(eye_x.size):
        if np.isnan(eye_x[i_x])==True:
           # print(i_x)
            break
        
    #Checking total length of y and x arrays with all NaNs removed. 
    nan_y = eye_y[~np.isnan(eye_y)]
    y_size = nan_y.size
    nan_x = eye_x[~np.isnan(eye_x)]
    x_size = nan_x.size
    
    #If both measures are equal, all NaNs are at the end of the array, and are removed.
    if i_x == x_size and i_y == y_size:
        eye_x = eye_x[:x_size]
        eye_y = eye_y[:y_size]
    else:
        print("All NaNs not at the end")
    
    
    
    
    
    '''PASSING THROUGH FILTER: SAVITSKY-GOLAY WITH STEP-SIZE 45, DEGREE 3'''
    
    x_clean = savgol_filter(eye_x, 45, 3)
    y_clean = savgol_filter(eye_y, 45, 3)
    
    
    
    
    
    '''PLOTTING SMOOTHENED POSITION DATA AGAINST TIME'''
    '''
    f=plt.figure(2)
    f.set_figheight(10)
    f.set_figwidth(20)
    time_axis = np.arange(1,(x_clean.size+1))
    plt.plot(time_axis, x_clean, 'ro', label='Eye position along x axis')
    plt.plot(time_axis, y_clean, 'bo', label='Eye position along y axis')
    plt.legend(loc="upper left", fontsize = "16")
    plt.xlabel("Time (ms)", fontsize = "20")
    plt.ylabel("Eye position (degrees)", fontsize = "20")
    '''
    
    
    
    '''CALCULATING VELOCITY DATA FROM POSITION DATA'''
    
    vel_x = np.diff(x_clean) # Obtaining velocity along x-axis by numerical differentiation of x-position array
    vel_y = np.diff(y_clean) # Obtaining velocity along y-axis by numerical differentiation of y-position array
    vel = np.sqrt(np.square(vel_x)+np.square(vel_y)) # Calculating magnitude of resultant velocity
    vel *= 1000 # Converting velocity from deg/ms to deg/s
    #print(vel.size) #Checking size of velocity array: should be one element smaller than position arrays
    
    
    
    
    
    '''BLINK DETECTION'''
    
    bfring = 100 # Setting width of blink fringe
    bthresh = 1500 # Setting blink velocity threshold
    blinks = np.nonzero(vel>bthresh) # Checking indices where eye velocity exceeds blink threshold
    blinks=(np.array(blinks)).flatten() # Indices of all such points stored in an array
    blinklist = [] # Empty list created to store blinks
    for i in blinks:
        b = list(range((i-bfring),(i+bfring))) # Adding fringes on either side of points exceeding blink threshold...
        blinklist += b #...and adding indices of all these points to the list of blinks
    for i in range(len(blinklist)): # Removing portions of fringes that might have dropped below zero
        if blinklist[i]<0:
            blinklist[i]=0
    final_blinks = np.unique(np.array(blinklist)) # Storing final blink indices in an array, keeping only unique values
    
    
    
    
    
    '''PLOTTING BLINKS'''
    '''
    f=plt.figure(3)
    f.set_figheight(10)
    f.set_figwidth(20)
    time_axis = np.arange(1,(x_clean.size+1))
    plt.plot(time_axis, x_clean, 'ro', label='Eye position along x axis')
    plt.plot(time_axis, y_clean, 'bo', label='Eye position along y axis')
    plt.vlines(final_blinks,ymin = min(x_clean), ymax = max(y_clean), colors = 'gray')
    plt.legend(loc="upper left", fontsize = "16")
    plt.xlabel("Time (ms)", fontsize = "20")
    plt.ylabel("Eye position (degrees)", fontsize = "20")
    '''
    
        
    
    
    
    '''DETECTING POTENTIAL SACCADE ONSET POINTS'''
    
    vel_thresh = 30 # Saccade velocity threshold
    candidates = np.nonzero(vel>vel_thresh) # Finding all points where eye velocity exceeds saccade threshold
    candidates=(np.array(candidates)).flatten() # Indices of all such points stored in "candidates" array
    
    diffcand = np.diff(candidates) # subtracting nth element from (n+1)th element in "candidates"
    
    # Difference between indices of successive pts in "candidates", stored in "diffcand"
    # Wherever difference between indices of successive pts >2, there is a break in pts above velocity threshold
    # We use a difference of 2 instead of 1, so that criteria for saccade onsets & ends are matched.
    # So a saccade onset is only detected when 2 successive points immediately preceding it have velocity < threshold
    # Could mark the end of a potential saccade
    # The next point in "candidates" would then mark the onset of the next potential saccade
    
    sac_b = [candidates[0]] #List created to store potential onset pts, 1st element = 1st element of "candidates"
    for i in range(diffcand.size):
        if diffcand[i]>2: # Finding pt where the difference in indices > 2
            if (candidates[i+1] in final_blinks) == False: # Checking if the next point in "candidates" falls within a blink
                sac_b.append(candidates[i+1]) # If not, adding it to list of potential saccade onset pts.
            
    
    
    
    
    
    '''PLOTTING POTENTIAL SACCADE ONSET POINTS'''
    '''
    f=plt.figure(4)
    f.set_figheight(10)
    f.set_figwidth(20)
    time_axis = np.arange(1,(x_clean.size+1))
    plt.plot(time_axis, x_clean, 'ro', label='Eye position along x axis')
    plt.plot(time_axis, y_clean, 'bo', label='Eye position along y axis')
    plt.vlines(sac_b,ymin = min(x_clean), ymax = max(y_clean), colors = 'green', label='Potential saccade onset points')
    plt.vlines(final_blinks,ymin = min(x_clean), ymax = max(y_clean), colors = 'gray')
    plt.legend(loc="upper left", fontsize = "16")
    plt.xlabel("Time (ms)", fontsize = "20")
    plt.ylabel("Eye position (degrees)", fontsize = "20")
    '''
    
    
    #print(sac_b) #Printing list of potential saccade onsets 
    
    
    
    
    
    
    '''DETECTING POTENTIAL SACCADE END-POINTS'''
    
    sac_e = [] # Creating empty list to eventually store endpoints of each potential saccade
    incomp = 0 # Variable to check whether last saccade is incomplete; initialized with value 0.
    
    for ii in sac_b: # For each potential saccade onset pt...
        jj = ii+1
        while True:
            if jj>=(vel.size-1): #If dataset ends before a suitable endpoint has been detected, breaking off the loop
                incomp = 1 # Changing value of "incomp" to 1, indicating data collection ended before saccade was completed
                break
            if vel[jj]<30 and vel[jj+1]<30: # Locating the next instance of 2 successive points with velocity below threshold
                break
            jj+=1
        sac_e.append(jj) # Storing the first of the 2 points with velocity < threshold as the end of that potential saccade
        
    if incomp == 1: # If the last saccade was incomplete...
        del sac_b[-1] # Removing last saccade from list of potential saccades
        del sac_e[-1]
        
    #print(sac_b)
    #print(sac_e) #Printing list of potential saccade ends
    
    
    
    
    
    '''PLOTTING ONSETS AND ENDS OF POTENTIAL SACCADES TOGETHER'''
    '''
    f=plt.figure(5)
    f.set_figheight(10)
    f.set_figwidth(20)
    time_axis = np.arange(1,(x_clean.size+1))
    plt.plot(time_axis, x_clean, 'ro', label='Eye position along x axis')
    plt.plot(time_axis, y_clean, 'bo', label='Eye position along y axis')
    plt.vlines(sac_b,ymin = min(x_clean), ymax = max(y_clean), colors = 'green', label='Potential saccade onset points')
    plt.vlines(sac_e,ymin = min(x_clean), ymax = max(y_clean), colors = 'magenta', label='Potential saccade end points')     
    plt.vlines(final_blinks,ymin = min(x_clean), ymax = max(y_clean), colors = 'gray')
    plt.legend(loc="upper left", fontsize = "16")
    plt.xlabel("Time (ms)", fontsize = "20")
    plt.ylabel("Eye position (degrees)", fontsize = "20")      
    '''
    
    
    
    
    
    '''ELIMINATING UNWANTED EYE MOVEMENTS'''
    
    amp_thresh = 1 # Amplitude threshold below which a potential saccade is considered a microsaccade
    
    #Initializing empty lists to eventually store beginnings and ends of microsaccades and valid saccades
    micro_b = []
    micro_e = []
    saccade_begin = []
    saccade_end = []
    amplitudes = []
    
    
    for i in range(len(sac_b)): #For each detected potential saccade... 
        inv = 0 # Error variable, detects if saccade falls within a blink. Initialized with value 0.
        p1 = sac_b[i] # Storing index of onset point
        p2 = sac_e[i] # Storing index of end-point
        
        #BLINK CHECK
        for j in range(p1,p2+1):
            if (j in final_blinks) == True: # Checking if any portion of the potential saccade falls within a blink
                inv = 1 # If yes, value of error variable changed, saccade will not be considered valid
                break
            
        #MICROSACCADE CHECK
        if inv == 0: # If  potential saccade has passed blink check...
           xamp = x_clean[p2] - x_clean[p1] # Computing change in x-coordinate over the course of the saccade
           yamp = y_clean[p2] - y_clean[p1] # Computing change in y-coordinate over the course of the saccade
           ampchk = math.sqrt(math.pow(xamp,2)+math.pow(yamp,2)) # Computing amplitude of the saccade
           if ampchk<amp_thresh: # If amplitude is lower than microsaccade threshold, store as microsaccade...
               micro_b.append(p1)
               micro_e.append(p2)
           else:
               saccade_begin.append(p1) # Otherwise, store as a valid saccade
               saccade_end.append(p2)
               amplitudes.append(ampchk)
    
                
    
    #PRINTING FINAL LISTS OF SACCADE ONSETS AND ENDS
    print(saccade_begin)         
    print(saccade_end)   
               
    if saccade_begin[0] == 0 or saccade_begin[0] == 1:
        del saccade_begin[0]
        del saccade_end[0]
        del amplitudes[0]
    
    
    
    '''PLOTTING ONSETS AND ENDS OF FINAL, VALID SACCADES'''
    
    f=plt.figure(row_num+1)
    f.set_figheight(10)
    f.set_figwidth(20)
    time_axis = np.arange(1,(x_clean.size+1))
    plt.plot(time_axis, x_clean, 'ro', label='Eye position along x axis')
    plt.plot(time_axis, y_clean, 'bo', label='Eye position along y axis')
    plt.vlines(saccade_begin,ymin = min(x_clean), ymax = max(y_clean), colors = 'green', label='Saccade onset points')
    plt.vlines(saccade_end,ymin = min(x_clean), ymax = max(y_clean), colors = 'magenta', label='Saccade end points')     
    plt.vlines(final_blinks,ymin = min(x_clean), ymax = max(y_clean), colors = 'gray')
    plt.legend(loc="upper left", fontsize = "16")
    plt.xlabel("Time (ms)", fontsize = "20")
    plt.ylabel("Eye position (degrees)", fontsize = "20")   
    
    '''if sacc[0]==0 or sacconset2[0]==1:
        sacconset2.remove(0)
        
    else:
        a  = sacconset2[0]-1
        b = sacconset2[0]-2
        
        if res_velList[a]>30 or res_velList[b]>30:
            sacconset2.remove(0)'''  
    
     
    
        
    
    
    pk_vel = []
    durlist = []
    for i in range(len(saccade_begin)):
        v = vel[saccade_begin[i]:saccade_end[i]].max()
        dur = saccade_end[i] - saccade_begin[i]
        pk_vel.append(v)
        durlist.append(dur)
        
    
    big_amplist += amplitudes
    big_vellist += pk_vel
    big_durlist += durlist
    

print("a", big_amplist)    
print("v", big_vellist)

f=plt.figure(31)
#f.set_figheight(10) #Setting the dimensions (length & width) of the figure to be generated
#f.set_figwidth(20)  
#time_axis = np.arange(1,(eye_x.size+1)) #Specifying the time axis
plt.plot(big_amplist, big_vellist, 'ro', label='Eye position along x axis') #Plotting eye x-coordinates
#plt.plot(time_axis, eye_y, 'bo', label='Eye position along y axis') #Plotting eye y-coordinates
#plt.legend(loc="upper left", fontsize = "16") #Specifying legend... 
#plt.xlabel("Time (ms)", fontsize = "20") #...and axis labels
#plt.ylabel("Eye position (degrees)", fontsize = "20")


f=plt.figure(32)
plt.plot(big_amplist, big_durlist, 'ro', label='Eye position along x axis')

f=plt.figure(33)
plt.hist(big_amplist)

f=plt.figure(34)
plt.hist(big_vellist)

f=plt.figure(35)
plt.hist(big_durlist)
    
    
    
       
    
     




