# createEthanolShape.py
#
# Computes coupling between CH3 and CH2, and uses that information to generate a shape
# for supression. Also computes SPdB23. Shape name is: EthanolShape
# 
# Author: Boris Mitrovic
# Email:  boris.mitrovic@gmail.com
# Date:   2012/9/6 15:47:04
#
#
#
# Version: v1.1 TopSpin3.1

# Adding current directory to Python path, as otherwise the module cannot be found
def getAbsPath(path):
    ls = path.split("/")
    ls.pop()
    return "/".join(ls)
a= getAbsPath(sys.argv[0])
sys.path.append(a)

#from selectRanges import selectRanges
from time import sleep

XCMD("rpar whisky_satellites_2 all")
XCMD("getprosol")
#print("1")
if len(sys.argv)==2:
    #print("2")
    if sys.argv[1] == "acq":
        #print("3")
        XCMD("zgwait")
        EFP()
        #XCMD("apk0f")
        #APK0()
XCMD("apk0f")
expnoP1 = "10"	# experiment where computed P1 is saved

[name, expno, procno, disk] = CURDATA()
RE([name, expnoP1, procno, disk])
P1 = GETPAR("P 1")
RE([name, expno, procno, disk])
PUTPAR("P 1", P1)

#userpick = False
#if len(sys.argv)==2:
#    userpick = eval(sys.argv[1])


# maybe add input dialog?

# standard parameters for peak picking optimised for finding very intense peaks only
MI = -100000000     # has to be negative infinity because of negative peaks (TS3.1)
MAXI = 100000000    # increase if biggest peaks undetected
PC = 50             # detection sensitivity - decrease if peaks undetected
PSIGN = "both"         # 'both' - positive and negative peaks detected
PSCAL = "global"         # 'global'
CY = "-3"


PUTPAR("CY",str(CY))
PUTPAR("MI",str(MI))
PUTPAR("MAXI",str(MAXI))
PUTPAR("PC",str(PC))
PUTPAR("PSIGN",PSIGN)
PUTPAR("PSCAL",PSCAL)

#if userpick:
#    MSG("Please select ranges")
#    rangeVec = selectRanges()
#    print rangeVec
#else:

#Here we can check if the temperature has been raised
TE = float(GETPAR("1s TE"))
if TE > 301:
    rangeVec = [3.80, 3.69, 3.6,3.5, 1.32,1.25,1.17,1.07] #these values OK for 70% EtOH at 308 K
else: #these values ok at 298-300K.
    rangeVec = [3.70,3.58,3.49,3.40,1.27,1.12,1.04,0.85]    #[2.97, 2.83, 2.73, 2.57, 0.50, 0.36, 0.29, 0.15] #[3,1.5,1,0] - acetone [3.67,3.57,3.44,3.20,1.20,1.10,0.99,0.89] 



# from ppm values
ev = [n for (i,n) in zip(range(len(rangeVec)),rangeVec) if i%2==0]

# to ppm values
odd = [n for (i,n) in zip(range(len(rangeVec)),rangeVec) if i%2==1]

ranges = zip(ev,odd)

[name, expno, procno, disk] = CURDATA()
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

if len(peaks) < 14:
    MSG("Too few peaks found (14 required): \nnPeaks=" + str(len(peaks))+"\n\n Check the parameters for peak picking in this script (confirm regions where peaks are picked, try reducing PC)"+"\n\nProgram will terminate...")
    EXIT()
printmsg=False
if len(peaks) > 14:
    print ("WARNING: found more than 14 peaks, precisely: " + str(len(peaks)))
    printmsg = True

# assuming 14 most intense peaks in the selected region are CH3 and CH2 peaks

peaks.sort(key=lambda peak: abs(peak.getIntensity()), reverse=True)
peaks = peaks[:10]
peaks.sort(key=lambda peak: peak.getPositions()[0], reverse=True)
"""
print ("used peaks: "+  str(map(lambda peak: peak.getPositions()[0],peaks)))
if printmsg:
    print ("used peaks: "+  str(map(lambda peak: peak.getPositions()[0],peaks)))
"""
SFO = float(GETPAR("SFO1"))

cl4 = (peaks[0].getPositions()[0]+peaks[1].getPositions()[0])/2
cr4 = (peaks[2].getPositions()[0]+peaks[3].getPositions()[0])/2

cl3 = peaks[5].getPositions()[0]
cr3 = peaks[8].getPositions()[0]

ch2isotopeShift = 1.53 / SFO # ppm
ch3isotopeShift = 1.11 / SFO # ppm

c4 = (cl4 + cr4) / 2 + ch2isotopeShift 
c3 = (cl3 + cr3) / 2 + ch3isotopeShift

c = abs(c4-c3)
#print ("value of c4-c3= " + str(c))
#in Hz
ch = c*SFO
time = 100/ch *1000000 # [usec]

#We have to make sure that the decoupling time is a multiple of the minimum IPSO unit of time, 0.025us. 
#Ironicially, TopSpin is only precise to 2dp for decoupling time, so only values ending in .?0 or .?5 will work. .?25 or 0.?75 fail as TopSpin rounds these to 0.03 or 0.08.
#This section now rounds the pulse to the nearest 100us. The PPM difference in a pulse of 50100us and 50000us is -0.00492
otime = time
#time = int(time)

npoints = 1000
timeA = float(time) / float(npoints)
timeB = timeA/0.025
timeA = int(timeB)*0.025*1000
time = timeA
"""
timeA=time
timeB= int(timeA/25)+(timeA % 25 > 12.5)
time = timeB*25
""" 
P1 = float(GETPAR("P 1"))
PL1 = float(GETPAR("PLdB 1"))
#print ("value of time=" + str(time))
#MSG("c4: " + str(c4) + "ppm\nc3: " + str(c3)+ "ppm\n\nDistance is: " + str(ch)+"Hz\n\nComputed pulse length based on this distance is: "+str(time) + "usec")

# Create shape with these parameters
XCMD("st generate Rectangle 1000 100 filename=EthanolShape")

XCMD("pulse180_whiskey " + str(time) + "us")    # computes and stores SPdB23
print ("below is the distance in hertz")
print (ch)
XCMD("st manipulate EthanolShape offs m " + str(time) + " 2 0 " + str(-ch))


PUTPAR("O3P", str(c4))
PUTPAR("SPNAM 23","EthanolShape")
PUTPAR("P 23", str(time))

[name, expno, procno, disk] = CURDATA()    # topspin 3
debugf = disk +"/"+ name+"/"+expno+"/pdata/"+procno+ "/debugfile"

fwa = open(debugf, "wb")

# write variables to output file, useful for debuggin
fwa.write("""#Variables from experiment run \r\n
#2015-07-09  w.kew@sms.ed.ac.uk \r\n
#O3P \t C4-C3Hz \t OriginalTime \t NewTime \r\n
""")
print>>fwa, '\r\n'
print>>fwa, "  " + str(c4) + " \t " + str(ch) + " \t " + str(otime) + " \t " + str(time)

fwa.close()
