@echo off
setlocal

REM +-----------------------------------------------------------------------------------------------------------------------+
REM / This script installs the necessary software and packages for the custom-nothing-glyph-tools - if not already present. /
REM /                                                                                                                       /
REM / ATTENTION:                                                                                                            /
REM /   Please do not execute this script standalone. Download AND EXTRACT the project and execute it from there.           /
REM +-----------------------------------------------------------------------------------------------------------------------+

title Install dependencies for Custom Glyphs

REM ----------------------------------Check for Windows build-------------------------------------------

REM Run the PowerShell command and save the output to a variable
for /f %%i in ('powershell -command "[System.Environment]::OSVersion.Version.Build"') do (
    set "build=%%i"
)

REM Check if the build version is greater than or equal to 16299 - also works for Windows 11 (has build 22000 or higher)
REM This is the minimal build where winget is supported
set "threshold=16299"
if %build% lss %threshold% (
    REM Inform the user that the build version is not supported and exit
    powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('This Windows build (%build%) is not supported.' + [Environment]::NewLine + [Environment]::NewLine + 'Please update your Windows installation to build %threshold% or higher!', 'Windows build not supported', [System.Windows.MessageBoxButton]::OK, [System.Windows.MessageBoxImage]::ERROR);"
    exit /b 1
)

REM ----------------------------------Check for required files-------------------------------------------

REM Check if the file "requirements.txt" exists
if not exist "%~dp0/requirements.txt" (
    REM Inform the user that the file "requirements.txt" is missing and exit
    powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('The file ''requirements.txt'' is missing.' + [Environment]::NewLine + [Environment]::NewLine + 'Please make sure that this script is in the root of the custom-nothing-glyph-tools directory.' + [Environment]::NewLine + [Environment]::NewLine + 'Also DO NOT execute any of the scripts from inside the zip file!', 'File ''requirements.txt'' missing', [System.Windows.MessageBoxButton]::OK, [System.Windows.MessageBoxImage]::ERROR);"
    exit /b 1
)

REM ----------------------------------Check for arguments-----------------------------------------------

REM Skip printing info if the user passed the --skip-info argument
if /i "%1"=="--skip-info" goto :checkForAdminRights

REM If we need more arguments in the future, we can maybe use this: https://stackoverflow.com/a/4871831/14622654

REM ----------------------------------Print info-------------------------------------------------------

echo This script installs the necessary software and packages for the custom-nothing-glyph-tools - if not already present.
echo It will install most of the dependencies with the open-source package manager WinGet.
echo.
echo You will need an active internet connection for this script to work. 
echo.
echo The following dependencies will be installed:
echo  * Audacity (optional)
echo  * ffmpeg
echo  * python
echo  * python packages needed (see requirements.txt)
echo.
echo The script will ask for administrator rights when you continue.

REM -----------------------Ask the user if he wants to continue running the script-----------------------

:askToContinue
set /p "continueRunning=Do you want to continue? [y/n]: "
if /i "%continueRunning%" equ "n" exit /b 0
if /i "%continueRunning%" neq "y" goto :askToContinue

REM ---------------------------Check for admin rights-----------------------------------------------------

:checkForAdminRights
@(
    (
        net session >nul 2>&1
    ) || (
        REM Elevate the script to admin
        powershell Start-Process -FilePath '%0' -Verb RunAs -ArgumentList '--skip-info %*'
        exit /b 0
    )
)

REM ---------------------------Check for .tmp folder------------------------------------------------------

REM Check if the folder ".tmp" exists and create it if it doesn't
if exist "%~dp0/.tmp" (
    call :PrintInfo "The folder "".tmp""" exists - using it."
) else (
    REM Create the folder ".tmp" and hide it
    mkdir "%~dp0/.tmp"
    attrib +h "%~dp0/.tmp" /s /d
)

REM ---------------------------Check for winget-----------------------------------------------------------

:tryWinget
@(
    (
        winget >nul 2>&1
    ) && (
        goto :install
    )
)

REM ---------------------------Manual WinGet install-----------------------------------------------------

:manualInstall
call :PrintInfo "Please install/update AppInstaller from the Microsoft Store."
REM Open the Microsoft Store page for AppInstaller
start ms-windows-store://pdp/?ProductId=9nblggh4nns1
echo.
pause
goto :tryWinget

REM ---------------------------Install dependencies-----------------------------------------------------

REM Update the winget sources before installing anything
:install
winget source update

REM Ask the user if they want to install Audacity or not which is optional
:audacityQuestion
set /p "install=Do you want to install Audacity? [y/n]: "
if /i "%install%"=="y" goto :fullInstall
if /i "%install%"=="n" goto :basicInstall
goto :audacityQuestion

:fullInstall
REM Install Audacity
winget install Audacity.Audacity
call :CheckWinGetResult %ERRORLEVEL% "Audacity"
echo.

:basicInstall
REM Install the rest of the programs
@(
    (
        ffmpeg -version >nul 2>&1
    ) && (
        call :PrintInfo "ffmpeg is already installed. Skipping..."
    ) || (
        REM ffmpeg is not installed, install it
        call :PrintInfo "Installing ffmpeg..."
        winget install Gyan.FFmpeg
        call :CheckWinGetResult %ERRORLEVEL% "FFmpeg"
    )
)
echo.
REM if Get-Package Python* is not throwing an error check if python is in the path and if it is, skip the installation
@(
    (
        powershell -Command "Get-Package 'Python 3*'" >nul 2>&1
    ) && (
        call :PrintInfo "python is already installed. Skipping..."
    ) || (
        REM python is not installed, install it
        call :PrintInfo "Installing python..."
        winget install Python.Python.3.11
        call :CheckWinGetResult %ERRORLEVEL% "Python 3.11"
        goto :refreshEnv
    )
)
setlocal enabledelayedexpansion
@(
    (
        python --version >nul 2>&1
    ) && (
        call :PrintInfo "python is already in PATH. Skipping..."
        REM No need to refresh environment variables if python is already working
        goto :python3Check
    ) || (
        REM python is not installed, install it
        call :PrintWarning "python is not in path."
        REM ask for user to uninstall current found package using powershell -Command "Get-Package Python*" and then install python using winget
        set /p "reInstall=Do you want to uninstall and reinstall python using winget? [y/N]: "
        if /i "!reInstall!"=="y" (
            echo.
            call :PrintInfo "Uninstalling python..."
            winget uninstall Python
            echo.
            call :PrintInfo "Installing python..."
            winget install Python.Python.3.11
            call :CheckWinGetResult %ERRORLEVEL% "Python 3.11"
            goto :refreshEnv
        )
        endlocal
        call :PrintError "Python is not in PATH! Please add python to the PATH manually. See here: https://docs.python.org/3/using/windows.html#excursus-setting-environment-variables"
        pause
        call :CleanUp
        exit /b 0
    )
)
endlocal

REM ---------------------------Refresh environment variables--------------------------------------------------
:refreshEnv
echo.
call :PrintInfo "Refreshing environment variables..."
@(
    (
        REM Download code from @badrelmers on GitHub to refresh environment variables.
        REM This downloaded code is part of badrelmers/RefrEnv (https://github.com/badrelmers/RefrEnv) which is released under the GPL-3.0 license.
        REM Go to https://github.com/badrelmers/RefrEnv/blob/main/LICENSE for full license details.
        powershell -Command "Invoke-WebRequest -Uri "https://raw.githubusercontent.com/badrelmers/RefrEnv/main/refrenv.bat" -OutFile '%~dp0/.tmp/refrenv.bat'"
    ) && (
        call "%~dp0/.tmp/refrenv.bat"
    ) || (
        REM Download failed - inform the user
        call :PrintWarning "Could not refresh environment. Please install the python packages manually: python -m pip install -r requirements.txt"
        pause
        call :CleanUp
        exit /b 0
    )
)

REM ---------------------------Link python to python3--------------------------------------------------

:python3Check
setlocal enabledelayedexpansion
@(
    (
        python3 --version >nul 2>&1
    ) && (
        endlocal
        call :PrintInfo "python3 is linked properly"
        REM No need to create a symlink if python3 is already working
        goto :installPythonStuff
    ) || (
        REM python3 symlink is not created - inform the user
        call :PrintWarning "python3 is not available to invoke python."
        REM ask the user if they want to create a symlink python3 pointing to python
        set /p "doLinking=Do you also want to invoke python via 'python3'? Press any key if unsure. (Y/n):: " 
        if /i "!doLinking!"=="n" (
            echo.
            endlocal
            call :PrintWarning "python3 is not linked! You will need to use 'python' to call the scripts."
            goto :installPythonStuff
        )
    )
)
endlocal
echo.
REM Get path to the python.exe in the system path
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do (
    set "pythonPath=%%i"
)

REM remove the python.exe from pythonPath variable
set "pythonPath=%pythonPath:python.exe=%"
set "pythonPath=%pythonPath:~0,-1%"

REM Set the path to the cwd for easier symlinking
pushd "%pythonPath%"

REM make symlink to the python.exe
mklink python3.exe python.exe

REM revert the path to the cwd
popd

REM ---------------------------Install python packages--------------------------------------------------

:installPythonStuff
echo.
REM Install the python packages
call :PrintInfo "Installing python packages..."
python -m pip install -r "%~dp0/requirements.txt"
echo.

REM ---------------------------Clean-up--------------------------------------------------

:end
powershell Write-Host -ForegroundColor Green 'Success!'
pause

REM delete the .tmp folder and exit
call :CleanUp

exit /b 0

REM ----------------------------------Convenience functions------------------------------------------------------

:CleanUp
rd /S /Q "%~dp0/.tmp"
exit /b 0

:PrintError
powershell Write-Host -ForegroundColor Red '[ERROR] %*'
exit /b 0

:PrintWarning
powershell Write-Host -ForegroundColor Yellow '[WARNING] %*'
exit /b 0

:PrintInfo
powershell Write-Host -ForegroundColor DarkCyan '[INFO] %*'
exit /b 0

:CheckWinGetResult
if %1 NEQ 0 (
    if %1 EQU -1978335212 (
        REM No packages found
        call :PrintError "%2 could not be found in the configured winget sources. Please try resetting the winget resources in an admin terminal with ""winget source reset --force""" or use the manual install method."
        pause
        call :CleanUp
        REM Exit, no script exit (/b)
        exit 1
    )    
    if %1 NEQ -1978335189 (
        REM All other errors
        REM -1978335189 means No applicable update found => We dont want to throw.
        call :PrintError "An unhandled error occurred with winget (%1). Please try the manual install method."
        pause
        call :CleanUp
        REM Exit, no script exit (/b)
        exit 1
    )
)
exit /b 0