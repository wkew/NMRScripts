# displayMDInt.py
# displays multiple datasets in a new window in multiple display mode
# This version is standalone
# 
# Author:  Will Kew
# Email:  will.kew@gmail.com
# Date:   2015/12/15 10:16:00
#
# Version: v2.0 

from TopCmds import RE, XCMD, NEWWIN

result = FIND_DIALOG()
NEWWIN()
RE_PATH(result[0])
XCMD(".md no_load")

for i in result[1:]:
	RE_PATH(i)
	

