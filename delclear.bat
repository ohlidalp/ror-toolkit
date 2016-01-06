@echo off
Echo.Rigs Of Rods Tool Kit 
Echo.For Rigs of Rods tool Kit 0.38
Echo.------------------------------------------------------
Echo. Saving Logs 
Echo.  >>logs/del.bat.txt
Echo.=================== >>logs/log.del.bat.txt
echo.%Date% >>logs/log.del.bat.txt
echo.%Time% >>logs/log.del.bat.txt
Echo.Clearing Now
echo Clearing cache
del /s /q *.pyc 

Echo.Logs Saved
Echo.Exiting
.
.
.
exit
