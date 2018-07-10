# acqWhiskey.py
#
# final whiskey data acquisition
# copies all the relevant parameters and computes a few parameters before acq spectrum
# assumes existance of parameters from efindwater_ethanol, createEthanolShape and createCarbonShape in experiments 10, 11 and 12 respectively
# 
# Author: Boris Mitrovic
# Email:  boris.mitrovic@gmail.com
# Date:   2012/9/6 15:47:04
#
#
#
# Version: v1.1 TopSpin3.1
# 
from time import sleep
[name, expno, procno, disk] = CURDATA()


expnoEFindWaterEthanol = "10"
expnoCreateEthanolShape = "11"
expnoCreateCarbonShape = "12"

RE([name, expnoEFindWaterEthanol, procno, disk])
P1 = GETPAR("P 1")
O3P = GETPAR("O1P")
PL22 = GETPAR("PLdB 22")

RE([name, expnoCreateEthanolShape, procno, disk])
P23 = GETPAR("P 23")
SP23 = GETPAR("SPdB 23")
#SPNAM23 = GETPAR("SPNAM 23")
O1P = GETPAR("O3P")

RE([name, expnoCreateCarbonShape, procno, disk])
O2P = GETPAR("O2P")
#SPNAM24 = GETPAR("SPNAM 24")
P24 = GETPAR("P 24")


RE([name, expno, procno, disk])
PUTPAR("P 1", P1)
PUTPAR("P 0", P1)
PUTPAR("P 23", P23)
PUTPAR("SPdB 23", SP23)
#PUTPAR("SPNAM 23", SPNAM23)
PUTPAR("O1P", O1P)
PUTPAR("O3P",O3P)
PUTPAR("PLdB 22", PL22)

PUTPAR("O2P",O2P)
#PUTPAR("SPNAM 24", SPNAM24)
PUTPAR("P 24", P24)
PUTPAR("PCPD 2", P24)


strength = "12.5KHZ"
XCMD("pulse_whiskey " + strength)   # sp30 pulse computation
XCMD("pulsec180_whiskey " + P24 + "us")    # computes and stores SPdB24

SP24 = GETPAR("SPdB 24")

# Safety checks
if float(SP24) < 10:
    MSG("WARNING: SPdB24 <10, SPdB24 is: " + SP24 + "\n\nProgram will terminate...")    
    EXIT()
if float(SP23) < 50:
    MSG("WARNING: SPdB23 <50, SPdB23 is: " + SP23 + "\n\nProgram will terminate...")    
    EXIT()

#MSG("Acquisition starting...")
XCMD("zgwait")
FP()
XCMD("apk0f")
#APK0()

