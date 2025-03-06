'''
This script is taken from DOI: 10.1002/mrc.4444
A new approach to the optimisation of non-uniform sampling schedules for use in the rapid acquisition of 2D NMR spectra of small molecules
By Phil Sidebottom, MagResChem, 2016, Vol 54, Issue 8, Pages 689-694

Adapted to work for different FnMODE data

'''

#cutomized python program for getting full path
#to be called by the program has to be in ....<topspin version>/exp/stan/nmr/py/usr

#from GetPathDirs import *
import os
import shutil

#read the nuslist file and export the content
def rlistfile(listfilepath):
	list=[]
	f=open(listfilepath, 'r')
	list = f.readlines()
	f.close()
	return list

#check of status parameter fntype
if GETPAR("2s FnTYPE") <> "0":
	MSG('Data NOT acquired using FnTYPE=traditional(planes).\n Plese open uniformly sampled data.')
	EXIT()
	
#Check what acquisition mode was used
fnmode = int(GETPAR("1s FnMODE"))
# FnMODEs
#0 - undef
#1 - QF
#2 - QSEQ
#3 - TPPI
#4 - States
#5 - States-TPPI
#6 - Echo-Antiecho
	
curdat = CURDATA()
#check if exp to create already exist. If it already exists, it will be icremented by 1000 and checked again
nexp=int(curdat[1])+1000
while os.path.exists(str(curdat[3])+"/"+str(curdat[0])+"/"+str(nexp))==True:
	nexp=nexp+1
	
#Dialog box to define the parameter
result = INPUT_DIALOG("NUSsim",
					"Simulation of NUS from uniformly sampled data",
					["Experiment to create", "Percent of spares sampling",
					"NUS list name", "NUS mode", "CS algorithm", "NUST2",
					"TopspsinInstallPath"],
					[str(nexp), "25", "automatic", "cs", "irls", "1","C:/Bruker/TopSpin4.4.1/"], ["","%","","cs or mdd","irls or ist", "seconds","Path"],
					["1", "1","1","1","1","1","1"])
					
nuslistname=result[2] #name of the nuslist file create in <topspin version>/exp/stan/nmr/list/vc
topspinpath = result[6] # path of topspin installer 
nussamplerapp_path = topspinpath+"prog/bin/nussampler.exe"
#define listfilepath calling external function (GetPathDirs) 
vclistpath = topspinpath+"exp/stan/nmr/lists/vc/"
#listfilepath=GetVclistPath(nuslistname)
listfilepath = vclistpath+str(result[2])

XCMD("wrpa %s" % str(nexp))
XCMD("re %s" % str(nexp))

tdat=CURDATA() #target data

os.remove(tdat[3] + '/' + tdat[0] + '/' + tdat[1] + '/ser') #delete raw data

PUTPAR("NUSLIST", result[2])
PUTPAR("FnTYPE", "non-uniform_sampling") #define fntype required by Mdd_mod (not "s fntype"!!)
XCMD('2s FnTYPE non-uniform_sampling') #required by xfb
PUTPAR("NusAMOUNT", result[1])
PUTPAR("Mdd_mod", result[3])
XCMD("1 NUST2 %s" % result[5]) #it is not working??

if result[3]=="mdd":
	XCMD("1 MddCEXP TRUE") #to use recorsive mdd
	
XCMD("2 Mdd_CsALG %s" % result[4])

nustd=GETPAR("1 TD")

nusamount=result[1]
td=GETPAR("1s TD")

nuspoints=int((int(td))*(float(nusamount)/100))

XCMD('1s NUSTD %s' % td)
PUTPAR("1s TD", str(int(nuspoints)))
#XCMD("mddparam setup")
XCMD("nusdisp")
fidnum=str(9119) #maybe should be better a check of the expno



#call rlistfile function defined at the very top
nuslist=rlistfile(listfilepath)

#loop to create the new NUS exp relative to the nuslist values
if fnmode >=2: #states, tppi, states tppi, or echoantiecho
	for i in range (len(nuslist)):
		XCMD('re %s' % curdat[1])
		XCMD('rser %s %s' % (str(int(nuslist[i])*2+1), fidnum))
		#print('reading real fid number ' + str(int(nuslist[i])*2+1))
		XCMD('wser %s %s' % (str(i*2+1), str(nexp)))
		#print('writing real fid in ' + str(i*2+1))
		XCMD('re %s' % curdat[1])
		XCMD('rser %s %s' % (str(int(nuslist[i])*2+2), fidnum))
		#print('reading img. fid number ' + str(int(nuslist[i])*2+2))
		XCMD('wser %s %s' % (str(i*2+2), str(nexp)))
		#print('writing img. fid in ' + str(i*2+2))
		#to delete the processed data from starting exp
	os.remove(curdat[3]+'/'+curdat[0]+'/'+str(nexp)+'/pdata'+'/1'+'/2rr')
	os.remove(curdat[3]+'/'+curdat[0]+'/'+str(nexp)+'/pdata'+'/1'+'/2ri')
	os.remove(curdat[3]+'/'+curdat[0]+'/'+str(nexp)+'/pdata'+'/1'+'/2ir')
	os.remove(curdat[3]+'/'+curdat[0]+'/'+str(nexp)+'/pdata'+'/1'+'/2ii')
elif fnmode == 1: #qf
	for i in range (len(nuslist)):
		XCMD('re %s' % curdat[1])
		XCMD('rser %s %s' % (str(int(nuslist[i])+1), fidnum))
		#print('reading real fid number ' + str(int(nuslist[i])*2+1))
		XCMD('wser %s %s' % (str(i+1), str(nexp)))
		#print('writing real fid in ' + str(i*2+1))
		#XCMD('re %s' % curdat[1])
	os.remove(curdat[3]+'/'+curdat[0]+'/'+str(nexp)+'/pdata'+'/1'+'/2rr')
		
shutil.copyfile(listfilepath, curdat[3]+'/'+curdat[0]+'/'+str(nexp)+'/nuslist')

#shutil.rmtree(curdat[3]+'/'+curdat[0]+'/'+str(fidnum), ignore_errors=True) #to delete the 9999 temp file

MSG('NUSsim program finished.\n Original experiment: %s\n NUS experimens: %s\n NUS experiment is not processed yet.\n Process it using xfb'
%
(curdat[1], str(nexp)))
XCMD('re %s' % str(nexp))
XCMD('settitle NUS=%s, NUSLIST = %s' % (str(result[1]), str(nuslistname)))