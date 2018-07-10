# clevfix.py
#
# This 'fixes' the contour levels to UoE preferences:
# Increment = 1.2
# Number of levels = 20
#
# The script reads in current contour levels, and recalculates them as appropriate
# It stores the new levels and reads in the dataset again to refresh the display 
# 
# Author: Will Kew
# Email:  will.kew@gmail.com
# Date:   2017/12/07 
#
#
#
# Version: v1.0 TopSpin3.5

# Adding current directory to Python path, as otherwise the module cannot be found
def getAbsPath(path):
    ls = path.split("/")
    ls.pop()
    return "/".join(ls)
a= getAbsPath(sys.argv[0])
sys.path.append(a)

XCMD(".ls") 

[name, expno, procno, disk] = CURDATA()    # topspin 3
clevpath = disk +"/"+ name+"/"+expno+"/pdata/"+procno+ "/clevels"


#clevpath = "F:/NMR/Man-PS_Glucose/6/pdata/1"+"/clevels"

with open(clevpath) as f:
	content = f.readlines()

        
levelsidx = content.index("##$LEVELS= (0..255)\n")

levsignidx = 0
levsignval = 1
while levsignidx == 0:
    try:
        levsignidx = content.index('##$LEVSIGN= '+str(levsignval)+'\n')
    except:
        levsignval += 1

NEGBASE = float(content[levsignidx+3][12:-1])
negvalues = [NEGBASE]
for x in range(20)[1:]:
    negvalues.append(negvalues[-1] * 1.2)
    
POSBASE = float(content[levsignidx+5][12:-1])    
posvalues = [POSBASE]
for x in range(20)[1:]:
    posvalues.append(posvalues[-1] * 1.2)

negvalues.extend(posvalues)
negvalues.sort()
negvalues.extend([0]*(128-len(negvalues)))

values  = ' '.join(str(e) for e in negvalues)

content[levsignidx+1] = "##$MAXLEV= 20\n"
content[levsignidx+4] = "##$NEGINCR= 1.2\n"
content[levsignidx+6] = "##$POSINCR= 1.2\n"

dellevs = list(range(levelsidx+1, levsignidx))

newcontent = content[:levelsidx+1]
newcontent.append(values)
newcontent.extend(content[levsignidx:])

fwa = open(clevpath, "w")
for item in newcontent:
  fwa.write("%s" % item)
fwa.close()

RE_PATH(disk +"/"+ name+"/"+str(expno)+"/pdata/"+str(procno))