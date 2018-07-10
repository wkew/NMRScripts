# createCarbonShape.py
#
# Computes coupling between carbons, and uses that information to generate a shape
# for supression. Shape name is: CarbonShape
# 
# Author: Boris Mitrovic
# Email:  boris.mitrovic@gmail.com
# Date:   2012/9/6 15:47:04
#
#
#
# Version: v1.1 TopSpin3.1

import time
from time import sleep

# Adding current directory to Python path, as otherwise the module cannot be found
def getAbsPath(path):
    ls = path.split("/")
    ls.pop()
    return "/".join(ls)
a= getAbsPath(sys.argv[0])
sys.path.append(a)

#from selectRanges import selectRanges


XCMD("rpar whisky_carbon all")
XCMD("getprosol")

if len(sys.argv)==2:
    if sys.argv[1] == "acq":
        XCMD("zgwait")
    	time.sleep(0.5)
        EFP()
        APK0()


# maybe add input dialog?

# standard parameters for peak picking optimised for finding very intense peaks only
MI = 1
MAXI = 100000000    # increase if biggest peaks undetected
PC = 30             # detection sensitivity - decrease if peaks undetected
PSIGN = "0"         # 'both' - positive and negative peaks detected
PSCAL = "0"         # 'global'
CY = "-3"


PUTPAR("CY",str(CY))
PUTPAR("MI",str(MI))
PUTPAR("MAXI",str(MAXI))
PUTPAR("PC",str(PC))
PUTPAR("PSIGN",PSIGN)
PUTPAR("PSCAL",PSCAL)

rangeVec = [65,55,24,14] # format from selectRanges.py



# from ppm values
ev = [n for (i,n) in zip(range(len(rangeVec)),rangeVec) if i%2==0]

# to ppm values
odd = [n for (i,n) in zip(range(len(rangeVec)),rangeVec) if i%2==1]

ranges = zip(ev,odd)

[name, expno, procno, disk] = CURDATA()    # topspin 3
peakrdir = disk +"/"+ name+"/"+expno+"/pdata/"+procno+ "/peakrng"

fw = open(peakrdir, "wb")

# write to peakrng file, which is used for peak picking
fw.write("""P    #regions in PPM
# 2012-08-27 11:17:37 +0100  bmitrovic@nmr-server.chem.ed.ac.uk
# low field   high field   mi   maxi
""")
for ran in ranges:
    (fppm,tppm) = ran
    print>>fw, "  " + str(fppm) + "  " + str(tppm) + "  " + str(MI) + "  " + str(MAXI)

fw.close()

# find peaks
XCMD("PPL")

peaks = GETPEAKSARRAY()

if peaks == None:
    MSG("no peaks file found, after performing ppl")
    EXIT()

peaks = peaks.tolist()

if len(peaks) < 2:
    MSG("Too few peaks found (2 required): \nnPeaks=" + str(len(peaks))+"\n\n Check the parameters for peak picking in this script (confirm regions where peaks are picked, try reducing PC)"+"\n\nProgram will terminate...")
    EXIT()
printmsg=False
if len(peaks) > 2:
    print ("WARNING: More than 2 peaks found (will pick strongest two), precisely: " + str(len(peaks)))
    printmsg = True


peaks.sort(key=lambda peak: abs(peak.getIntensity()), reverse=True)
peaks = peaks[:2]
peaks.sort(key=lambda peak: peak.getPositions()[0], reverse=True)

if printmsg:
    print ("used peaks: "+  str(map(lambda peak: peak.getPositions()[0],peaks)))

SFO = float(GETPAR("SFO1"))

left = peaks[0].getPositions()[0]
right = peaks[1].getPositions()[0]

c = abs(left-right)

# in Hz
ch = c*SFO
time = 15/ch *1000000 # [usec]
#We have to make sure that the decoupling time is a multiple of the minimum IPSO unit of time, 0.025us. 
#Ironicially, TopSpin is only precise to 2dp for decoupling time, so only values ending in .?0 or .?5 will work. .?25 or 0.?75 fail as TopSpin rounds these to 0.03 or 0.08.
otime= time
"""time = int(time)
time = int(time/0.05)
if time % 2 == 0:
    time = time * 0.05
else:
    time = (time-1) * 0.05
    
print ("value of time=" + str(time))
    
ch = int(ch/0.05)
if ch % 2 == 0:
    ch = ch * 0.05
else:
    ch = (ch-1) * 0.05
"""
P1 = float(GETPAR("P 1"))
PL1 = float(GETPAR("PLdB 1"))

#MSG("Distance is: " + str(ch)+"Hz\n\nComputed pulse length based on this distance is: "+str(time) + "usec")

#This section ensure that each "point" of the pulse is of a length that is divisible by 25ns, the resolution of the SGU.
#I hope. - WK 7/7/15
#It now will modify the time slightly (+- 1us in 0.025us increments) to find a number of points which works.
#Now it will round time up or down to the nearest whole us. The difference in PPM (13C) for a 2458 or 2459 us pulse is 0.01642. 
#The script then checks for a number of points for the shaped pulse between low and high which give points of lengths divisible by 0.025us.
#If none are found, it adds or removes 1 us from the pulse and tries again.
timeA = int(time/1)+(time%1>0.5)
time = timeA*1
x=float(time)
a = 0.025
low = 470
high = 550

def pointcalc(x,a,low,high):
    for i in range(low,high):
        y = x / i
        z = y / a 
        if z % 1 == 0:
            points = i
            return points
            break
        elif i == (high-1):
            return False
        else:
            i + 1 
    return 
    
points = pointcalc(x,a,low,high)
if points != False:
    time = int(x)    
elif points == False:
    x = x +1.0
    points = pointcalc(x,a,low,high)
    if points != False:
        time = int(x)
    else:
        x = x -2
        points = pointcalc(x,a,low,high)
        if points != False:
            time = int(x)
        else:
            points = 500
            time = int(x)

# Create shape with these parameters
XCMD("st generate Rectangle " + str(points) +" 100 filename=CarbonShape")

XCMD("st manipulate CarbonShape cosm2 " + str(time) +" " + str(abs(ch/2)))


PUTPAR("O2P", str(c/2+right))
PUTPAR("SPNAM 24","CarbonShape")
PUTPAR("P 24", str(time))

[name, expno, procno, disk] = CURDATA()    # topspin 3
debugf = disk +"/"+ name+"/"+expno+"/pdata/"+procno+ "/debugfile"

fwa = open(debugf, "wb")

# write variables to output file, useful for debuggin
fwa.write("""#Variables from experiment run \r\n
#2015-07-09  w.kew@sms.ed.ac.uk \r\n
#O2P \t OriginalTime \t NewTime \t Points \r\n
""")
print>>fwa, '\r\n'
print>>fwa, "  " + str(c/2+right) + " \t " + str(otime) + " \t " + str(time) + " \t \t " + str(points) 

fwa.close()
