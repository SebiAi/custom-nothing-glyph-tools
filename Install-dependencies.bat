@echo off
setlocal

title Install dependencies for Custom Glyphs

:: ----------------------------------Check for Windows build-------------------------------------------

:: Run the PowerShell command and save the output to a variable
for /f %%i in ('powershell -command "[System.Environment]::OSVersion.Version.Build"') do (
    set "build=%%i"
)

:: Check if the build version is greater than or equal to 16299 - also works for Windows 11 (has build 22000 or higher)
:: This is the minimal build where winget is supported
set "threshold=16299"
if %build% lss %threshold% (
    :: Inform the user that the build version is not supported and exit
    powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('This Windows build (%build%) is not supported.' + [Environment]::NewLine + [Environment]::NewLine + 'Please update your Windows installation to build %threshold% or higher!', 'Windows build not supported', [System.Windows.MessageBoxButton]::OK, [System.Windows.MessageBoxImage]::ERROR);"
    exit /b 1
)

:: ----------------------------------Check for arguments-----------------------------------------------

:: Skip printing info if the user passed the --skip-info argument
if /i "%1"=="--skip-info" goto :checkForAdminRights

:: If we need more arguments in the future, we can maybe use this: https://stackoverflow.com/a/4871831/14622654

:: ----------------------------------Print info-------------------------------------------------------

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

:: -----------------------Ask the user if he wants to continue running the script-----------------------

:askToContinue
set /p "continueRunning=Do you want to continue? [y/n]: "
if /i "%continueRunning%" equ "n" exit /b 0
if /i "%continueRunning%" neq "y" goto :askToContinue

:: ---------------------------Check for admin rights-----------------------------------------------------

:checkForAdminRights
@(
    (
        net session >nul 2>&1
    ) || (
        :: Elevate the script to admin
        powershell Start-Process -FilePath '%0' -Verb RunAs -ArgumentList '--skip-info %*'
        exit /b 0
    )
)

:: ---------------------------Check for .tmp folder------------------------------------------------------

:: Check if the folder ".tmp" exists and create it if it doesn't
if exist "%~dp0/.tmp" (
    call :PrintInfo "The folder "".tmp""" exists - using it."
) else (
    :: Create the folder ".tmp" and hide it
    mkdir "%~dp0/.tmp"
    attrib +h "%~dp0/.tmp" /s /d
)

:: ---------------------------Check for winget-----------------------------------------------------------

:tryWinget
@(
    (
        winget >nul 2>&1
    ) && (
        goto :install
    )
)

:: ---------------------------Automated WinGet install--------------------------------------------------

call :PrintInfo "Downloading WinGet and its dependencies..."


@(
    (
        :: Download the latest version of WinGet and save it to the .tmp folder as WinGet.msixbundle
        powershell -Command "Invoke-WebRequest -Uri "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle" -OutFile "%~dp0/.tmp/WinGet.msixbundle""
        :: Get hash of the latest version of WinGet from web and save it to the .tmp folder as hash.txt
        powershell -Command "Invoke-WebRequest -Uri "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.txt" -OutFile "%~dp0/.tmp/hash.txt""

        :: Download winget dependencies (Microsoft.VCLibs, Microsoft.UI.Xaml) and save them to the .tmp folder (https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget-on-windows-sandbox)
        powershell -Command "Invoke-WebRequest -Uri "https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx" -OutFile "%~dp0/.tmp/Microsoft.VCLibs.x64.14.00.Desktop.appx""
        powershell -Command "Invoke-WebRequest -Uri "https://github.com/microsoft/microsoft-ui-xaml/releases/download/v2.7.3/Microsoft.UI.Xaml.2.7.x64.appx" -OutFile "%~dp0/.tmp/Microsoft.UI.Xaml.2.7.x64.appx""
    ) || (
        :: Error downloading
        call :PrintError "Could not download WinGet. Do you have a working internet connection?"
        goto :manualInstall
    )
)

:: Get hash of WinGet.msixbundle and save it to the .tmp folder as file_hash.txt
CertUtil -hashfile "%~dp0/.tmp/WinGet.msixbundle" SHA256 > %~dp0/.tmp/file_hash.txt

:: Get the hash value from the hash.txt file
(for /L %%i in (1,1,1) do set /P "hash=") < "%~dp0/.tmp/hash.txt"
call :PrintInfo "The file hash should be: %hash%"

:: Get the hash value from the file_hash.txt file
(for /L %%i in (1,1,2) do set /P "file_hash=") < "%~dp0/.tmp/file_hash.txt"
call :PrintInfo "The file hash is:        %file_hash%"

:: Compare the hash values
if "%file_hash%"=="%hash%" (
    call :PrintInfo "The hashes match!"
) else (
    call :PrintInfo "The hashes do not match."
    goto :manualInstall
)

:: If the installation doesn't fail, try if winget works now
@(
    (
        powershell -Command "Add-AppxPackage "%~dp0/.tmp/WinGet.msixbundle" -DependencyPath "%~dp0/.tmp/Microsoft.VCLibs.x64.14.00.Desktop.appx, %~dp0/.tmp/Microsoft.UI.Xaml.2.7.x64.appx""
    ) && (
        goto :tryWinget
    )
)

call :PrintWarning "Automatic installation failed."

:: ---------------------------Manual WinGet install-----------------------------------------------------

:manualInstall
call :PrintInfo "Please install/update AppInstaller from the Microsoft Store."
:: Open the Microsoft Store page for AppInstaller
start ms-windows-store://pdp/?ProductId=9nblggh4nns1
echo.
pause
goto :tryWinget

:: ---------------------------Install dependencies-----------------------------------------------------

:install
:: Ask the user if they want to install Audacity or not which is optional
set /p "install=Do you want to install Audacity? [y/n]: "
if /i "%install%"=="y" goto :fullInstall
if /i "%install%"=="n" goto :basicInstall
else goto :install

:fullInstall
:: Install Audacity
winget install Audacity.Audacity
echo.

:basicInstall
:: Install the rest of the programs
@(
    (
        ffmpeg -version >nul 2>&1
    ) && (
        call :PrintInfo "ffmpeg is already installed. Skipping..."
    ) || (
        :: ffmpeg is not installed, install it
        call :PrintInfo "Installing ffmpeg..."
        winget install Gyan.FFmpeg
    )
)
echo.
@(
    (
        python --version >nul 2>&1
    ) && (
        call :PrintInfo "python is already installed. Skipping..."
        :: No need to refresh environment variables if python is already working
        goto :installPythonStuff
    ) || (
        :: python is not installed, install it
        call :PrintInfo "Installing python..."
        winget install Python.Python.3.11
    )
)
echo.

:: ---------------------------Refresh environment variables--------------------------------------------------

call :PrintInfo "Refreshing environment variables..."
@(
    (
        :: Download code from @badrelmers on GitHub to refresh environment variables.
        :: This downloaded code is part of badrelmers/RefrEnv (https://github.com/badrelmers/RefrEnv) which is released under the GPL-3.0 license.
        :: Go to https://github.com/badrelmers/RefrEnv/blob/main/LICENSE for full license details.
        powershell -Command "Invoke-WebRequest -Uri "https://raw.githubusercontent.com/badrelmers/RefrEnv/main/refrenv.bat" -OutFile "%~dp0/.tmp/refrenv.bat""
    ) && (
        call %~dp0/.tmp/refrenv.bat
    ) || (
        :: Download failed - inform the user
        call :PrintWarning "Could not refresh environment. Please install the python packages manually: python -m pip install -r requirements.txt"
        pause
        call :CleanUp
        exit /b 0
    )
)

:: ---------------------------Install python packages--------------------------------------------------

:installPythonStuff
:: Install the python packages
call :PrintInfo "Installing python packages..."
python -m pip install -r %~dp0/requirements.txt
echo.

:: ---------------------------Clean-up--------------------------------------------------

:end
powershell Write-Host -ForegroundColor Green 'Success!'
pause

:: delete the .tmp folder and exit
call :CleanUp

exit /b 0

:: ----------------------------------Convenience functions------------------------------------------------------

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