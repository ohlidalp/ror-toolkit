@echo off
Echo.Rigs Of Rods Tool Kit By Lepes/tdev/max98
Echo.For Rigs of Rods 0.38.XXX
Echo.RoR Tool Kit Revision 2
Echo.------------------------------------------------------
Echo. Saving Logs 
Echo.  >>logs/start.bat.txt
Echo.=================== >>logs/log.start.bat.txt
echo.%Date% >>logs/log.start.bat.txt
echo.%Time% >>logs/log.start.bat.txt
Echo.Logs Saved
Echo.Starting Now


.\python26\python.exe .\rortoolkit.py
rem pause

Echo. Deleting inused files
start delclear.bat


