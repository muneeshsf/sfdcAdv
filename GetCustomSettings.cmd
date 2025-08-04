@echo off

:: Specify the output directory
set OUTPUT_DIR=C:\Muneesh\CustomSettings\output
set INPUT_DIR=C:\Muneesh\CustomSettings

:: Create the output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: Read SOQL queries from file
for /f "tokens=*" %%a in (%INPUT_DIR%\customSettingsSoql.txt) do (
  :: Extract the custom setting name from the SOQL query
  for /f "tokens=2 delims=FROM" %%b in ("%%a") do (
    for /f "tokens=1" %%c in ("%%b") do (
      sfdx force:data:soql:query -q "%%a" --result-format csv > "%OUTPUT_DIR%\%%c.csv"
    )
  )
)