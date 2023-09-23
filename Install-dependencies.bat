@echo off
setlocal

title Install dependencies for Custom Glyphs

:: Run the PowerShell command and save the output to a variable
for /f %%i in ('powershell -command "[System.Environment]::OSVersion.Version.Build"') do (
    set "build=%%i"
)

:: Check if the build version is greater than or equal to 16299
set "threshold=16299"
if %build% geq %threshold% (
    echo Windows build is supported.
) else (
    :: Inform the user that the build version is not supported and exit
    powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('This Windows build (%build%) is not supported.' + [Environment]::NewLine + [Environment]::NewLine + 'Please update your Windows installation to build %threshold% or higher!', 'Windows build not supported', [System.Windows.MessageBoxButton]::OK, [System.Windows.MessageBoxImage]::ERROR);"
    exit
)

:: ---------------------------check for admin rights-----------------------------------------------------
@(
    (
        net session >nul 2>&1
    ) || (
        :: elevate the script to admin
        powershell Start-Process -FilePath '%0' -Verb RunAs
        goto :EOF
    )
)

:: check if the folder ".tmp" exists and create it if it doesn't
if exist "%~dp0/.tmp" (
  echo The folder ".tmp" exists.
) else (
  mkdir "%~dp0/.tmp"
  attrib +h "%~dp0/.tmp" /s /d
)
cls

:: ---------------------------check for winget-----------------------------------------------------------
:tryWinget
winget
if %errorlevel%==0 goto :install
cls
:: ---------------------------automated WinGet install--------------------------------------------------
echo Downloading WinGet and its dependencies...

:: Download the latest version of WinGet and save it to the .tmp folder as WinGet.msixbundle
powershell -Command "Invoke-WebRequest -Uri "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle" -OutFile "%~dp0/.tmp/WinGet.msixbundle""

:: get hash of WinGet.msixbundle and save it to the .tmp folder as file_hash.txt
CertUtil -hashfile "%~dp0/.tmp/WinGet.msixbundle" SHA256 > %~dp0/.tmp/file_hash.txt

:: get hash of the latest version of WinGet from web and save it to the .tmp folder as hash.txt
powershell -Command "Invoke-WebRequest -Uri "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.txt" -OutFile "%~dp0/.tmp/hash.txt""

:: get the hash value from the hash.txt file
(for /L %%i in (1,1,1) do set /P "hash=") < "%~dp0/.tmp/hash.txt"
echo The file hash is: %hash%

:: get the hash value from the file_hash.txt file
(for /L %%i in (1,1,2) do set /P "file_hash=") < "%~dp0/.tmp/file_hash.txt"
echo The file hash is: %file_hash%

:: Compare the hash values
if "%file_hash%"=="%hash%" (
    echo The hashes match!
) else (
    echo The hashes do not match.
    goto :manualInstall
)
cls

:: Download winget dependencies (Microsoft.VCLibs, Microsoft.UI.Xaml) and save them to the .tmp folder (https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget-on-windows-sandbox)
powershell -Command "Invoke-WebRequest -Uri "https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx" -OutFile "%~dp0/.tmp/Microsoft.VCLibs.x64.14.00.Desktop.appx""
powershell -Command "Invoke-WebRequest -Uri "https://github.com/microsoft/microsoft-ui-xaml/releases/download/v2.7.3/Microsoft.UI.Xaml.2.7.x64.appx" -OutFile "%~dp0/.tmp/Microsoft.UI.Xaml.2.7.x64.appx""

:: Install WinGet
powershell -Command "Add-AppxPackage "%~dp0/.tmp/WinGet.msixbundle" -DependencyPath "%~dp0/.tmp/Microsoft.VCLibs.x64.14.00.Desktop.appx, %~dp0/.tmp/Microsoft.UI.Xaml.2.7.x64.appx""
:: if the installation doesn't fail, try if winget works now
if %errorlevel%==0 goto :tryWinget
cls
echo Automatic installation failed.
:: if the installation fails, try to install it from the Microsoft Store manually
:manualInstall
echo Please install/update AppInstaller from the Microsoft Store.
::open the Microsoft Store page for AppInstaller
start ms-windows-store://pdp/?ProductId=9nblggh4nns1
echo.
pause
goto :tryWinget

:install
cls
:: ask the user if they want to install Audacity or not which is Optional
set /p "install=Do you want to install Audacity? (y/n): "
if /i "%install%"=="y" goto :fullInstall
if /i "%install%"=="n" goto :basicInstall
else goto :install

:fullInstall
:: install Audacity
winget install Audacity.Audacity
echo.
call :basicInstall
goto :refrenv

:basicInstall
:: install the rest of the programs
winget install Gyan.FFmpeg
echo.
winget install Python.Python.3.11
echo.
goto :refrenv

:installPythonStuff
cls
:: install the python packages
pip install -r %~dp0/requirements.txt
echo.

:end
powershell write-host -fore Green "Success!"
pause
:: delete the .tmp folder and exit
rd /S /Q "%~dp0/.tmp"
exit

:refrenv
powershell -Command "Invoke-WebRequest -Uri "https://raw.githubusercontent.com/badrelmers/RefrEnv/main/refrenv.bat" -OutFile "%~dp0/.tmp/refrenv.bat""

call %~dp0/.tmp/refrenv.bat
goto :installPythonStuff