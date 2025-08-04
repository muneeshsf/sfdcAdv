@echo off

:: Navigate to the project directory
cd C:\Muneesh\SFDXSetup\MBMeta

:: Set SFDX path and org alias
set sf_path=C:\Program Files\sf\bin\sf.cmd
set username_alias=metaprod
set input_folder=C:\Muneesh\CustomSettings
set output_file=C:\Muneesh\CSetting_Report.xlsx

:: Retrieve Custom Settings
echo Retrieving Custom Settings...

call "%sf_path%" force:source:retrieve -m CustomSetting --target-org %username_alias%
xcopy /y /s "C:\Muneesh\SFDXSetup\MBMeta\force-app\main\default\CustomSetting\*" "%input_folder%\"

pause 
pause
:: Run the Python script
if exist C:\tools\fb-python\fb-python312\python.exe (
    echo Python executable found.
   # C:\tools\fb-python\fb-python312\python.exe  c:\Muneesh\ActiveApprovers8thJuneWithPara.py "%input_folder%" "%output_file%"
) else (
    echo Python executable not found.
)
pause

echo Done!


