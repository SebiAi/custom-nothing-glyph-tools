@echo off
title Create Custom Glyph
setlocal
:start

:: check if python is installed
@(
    (
        python --version >nul 2>&1
    ) || (
        cls
        call :PrintWarning "Python is not installed."
        call :PrintInfo "Consider running the Install-Dependencies.bat first."
        echo.
        goto :runInstallDependencies
    )
)

:: check if ffmpeg is installed
@(
    (
        ffmpeg -version >nul 2>&1
    ) || (
        cls
        call :PrintWarning "ffmpeg is not installed."
        call :PrintInfo "Consider running the Install-Dependencies.bat first."
        echo.
        goto :runInstallDependencies
    )
)

goto :checkIfToolsDirectoryExists

:: create a goto label for the case that either python or ffmpeg is not installed and the user wants to run the Install-Dependencies.bat
:runInstallDependencies
:: ask if the user wants to run the Install-Dependencies.bat now
echo Press y to run the Install-Dependencies.bat or any other key to cancel.
set /p "runInstallDependencies="
if /i "%runInstallDependencies%"=="y" (
    cls
    call :PrintInfo "Running the Install-Dependencies.bat."
    echo.
    echo Press any key to continue.
    pause >nul
    call Install-Dependencies.bat
    goto :start
) else (
    cls
    call :PrintWarning "Python is not installed. Please install it manually."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :eof
)

:checkIfToolsDirectoryExists
:: check if the GlyphTranslator.py and GlyphModder.py files exist
if not exist GlyphTranslator.py (
    cls
    call :PrintWarning "The file GlyphTranslator.py does not exist."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :eof
)

if not exist GlyphModder.py (
    cls
    call :PrintWarning "The file GlyphModder.py does not exist."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :eof
)

:: get current directory and save it to a variable
set "toolsDirectory=%cd%"

:: ask for a name for the new glyph
:askForGlyphName
cls
set /p glyphName="Enter a title for the new glyph: "
if "%glyphName%"=="" goto :askForGlyphName

:: create a new folder for the custom glyph and change to it
set "glyphFolder=%~dp0%glyphName%"
if not exist "%glyphFolder%" (
    md "%glyphFolder%"
    call :PrintInfo "created new Directory %cd%. Please add the files for the new glyph to this folder."
    goto :getToGlyphFolder
)

cls
:: ask if the user wants to continue if the folder already exists
call :PrintWarning "The folder %glyphFolder% already exists."
echo.
set /p continue="Press y to continue or any other key to cancel. "
echo "%continue%"=="y"
pause
if /i not "%continue%"=="y" goto :eof
call :PrintInfo "opened Directory %cd%. Please add the files for the new glyph to this folder."

:getToGlyphFolder
cd /d "%glyphFolder%"
:: open the new folder in the file explorer
explorer "%glyphFolder%"
echo.
echo Press any key to continue.
pause >nul

:: check if the folder is empty
:checkFolderEmpty
set "folderEmpty=true"
for /f "delims=" %%i in ('dir /b /a-d') do set "folderEmpty=false"
if "%folderEmpty%"=="true" (
    cls
    call :PrintWarning "The folder %cd% is empty. Please add the files."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :checkFolderEmpty
)

:: check if the folder contains 1 .txt file
:checkFolderContainsOneTxtFile
set "txtFileName="
for /f "delims=" %%i in ('dir /b /a-d *.txt') do set "txtFileName=%%i"
if "%txtFileName%"=="" (
    cls
    call :PrintWarning "The folder %cd% does not seem to contain a labels file. Please add a labels file."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :checkFolderContainsOneTxtFile
)

:: ask if the user wants to disable compatibility mode
cls

set /p disableCompatibilityMode="Press y to disable compatibility mode or any other key to continue with compatibility mode. "
if /i "%disableCompatibilityMode%"=="y" (
    cls
    call :PrintInfo "Compatibility mode disabled."
    echo.
    echo Press any key to continue.
    pause >nul
    set "disableCompatibilityMode=--disableCompatibility"
) else (
    set "disableCompatibilityMode="
)

cls
echo.
:: take the filename of the .txt file and use it as parameter for GlyphTranslator
@(
    (
        python %toolsDirectory%/GlyphTranslator.py "%txtFileName%" %disableCompatibilityMode%
    ) || (
        cls
        call :PrintError "The file %txtFileName% does not seem to be a valid labels file. Please add a valid labels file."
        echo.
        echo Press any key to continue.
        pause >nul
        goto :checkFolderContainsOneTxtFile
    )
)

timeout /t 3

:: check if the folder contains 1 .glypha file and add the filename to a variable
:checkFolderContainsOneGlyphaFile
set "glyphaFileName="
for /f "delims=" %%i in ('dir /b /a-d *.glypha') do set "glyphaFileName=%%i"
if "%glyphaFileName%"=="" (
    cls
    call :PrintWarning "The folder %cd% does not seem to contain a valid glypha file. Please add a valid glypha file."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :checkFolderContainsOneGlyphaFile
)

:: check if the folder contains 1 .glyphc1 file and add the filename to a variable
:checkFolderContainsOneGlyphc1File
set "glyphc1FileName="
for /f "delims=" %%i in ('dir /b /a-d *.glyphc1') do set "glyphc1FileName=%%i"
if "%glyphc1FileName%"=="" (
    cls
    call :PrintWarning "The folder %cd% does not seem to contain a valid glyphc1 file. Please add a valid glyphc1 file."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :checkFolderContainsOneGlyphc1File
)

:: check if the folder contains 1 .ogg file and add the filename to a variable
:checkFolderContainsOneOggFile
set "oggFileName="
for /f "delims=" %%i in ('dir /b /a-d *.ogg') do set "oggFileName=%%i"
if "%oggFileName%"=="" (
    cls
    call :PrintWarning "The folder %cd% does not seem to contain a valid sound file. Please add a valid sound file."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :checkFolderContainsOneOggFile
)

echo.
:: run the GlyphModder with the filename of the .glypha, .glyphc1 and .ogg file as parameter the CustomTitle will be the folder name
python %toolsDirectory%/GlyphModder.py -t "%glyphName%" -w "%glyphaFileName%" "%glyphc1FileName%" "%oggFileName%"

:: check if the command was successful
if not "%errorlevel%"=="0" (
    cls
    call :PrintError "At least one of these files (%glyphaFileName%, %glyphc1FileName%, %oggFileName%) does not seem to be a valid file."
    echo.
    echo Press any key to continue.
    pause >nul
    goto :checkFolderContainsOneGlyphaFile
)
echo.
pause

:: ask if the user wants to delete the folder
cls
call :PrintInfo "The glyph %glyphName% was created successfully."
echo.
echo Press y to delete the folder %glyphFolder% or any other key to keep the folder.
set /p "deleteFolder="
if /i "%deleteFolder%"=="y" (
    cls
    call :PrintWarning "The folder %glyphFolder% will be deleted."
    echo.
    echo Press any key to continue.
    pause >nul
    cd /d %toolsDirectory%
    rd /s /q "%glyphFolder%"
) else (
    cls
    call :PrintInfo "The folder %glyphFolder% will be kept."
    echo.
    echo Press any key to continue.
    pause >nul
)


:PrintError
powershell Write-Host -ForegroundColor Red '[ERROR] %*'
exit /b 0

:PrintWarning
powershell Write-Host -ForegroundColor Yellow '[WARNING] %*'
exit /b 0

:PrintInfo
powershell Write-Host -ForegroundColor DarkCyan '[INFO] %*'
exit /b 0