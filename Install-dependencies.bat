@echo off
REM Maybe add a Windows Version check here?

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

:: ---------------------------check for winget-----------------------------------------------------------
:tryWinget
winget
if %errorlevel%==0 goto :install
cls
:: ---------------------------automated WinGet install--------------------------------------------------
setlocal
:: check if the folder ".tmp" exists and create it if it doesn't
if exist "%~dp0/.tmp" (
  echo The folder ".tmp" exists.
) else (
  mkdir "%~dp0/.tmp"
  attrib +h "%~dp0/.tmp" /s /d
)
cls
echo Downloading WinGet

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

endlocal

:: Install WinGet
powershell -Command "Add-AppxPackage "%~dp0/.tmp/WinGet.msixbundle"
:: if the installation doesn't fail, try if winget works now
if %errorlevel%==0 goto :tryWinget

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
goto :restartScript

:basicInstall
:: install the rest of the programs
winget install Gyan.FFmpeg
echo.
winget install Python.Python.3.11
echo.

:: try if python command is working
:restartScript
python --version
:: if the python command is working, go to the next step
if %errorlevel%==0 goto :installPythonStuff
cls
:: if the python command is not working, try to refresh the environment
goto :refrenv
pause

:installPythonStuff
cls
:: install the python packages
pip install -r requirements.txt
echo.

:end
powershell write-host -fore Green "Success!"
pause
:: delete the .tmp folder and exit
rd /S /Q "%~dp0/.tmp"
exit
:: ----------------------------------------------------------------------------------------------------
:: refresh environment variables with the RefrEnv script

REM refrenv.bat script by @badrelmers https://github.com/badrelmers
REM Source: https://github.com/badrelmers/RefrEnv
:refrenv
<!-- : Begin batch script
@echo off

if "%debugme%"=="yes" (
    echo RefrEnv - Refresh the Environment for CMD - ^(Debug enabled^)
) else (
    echo RefrEnv - Refresh the Environment for CMD
)

set "TEMPDir=%TEMP%\refrenv"
IF NOT EXIST "%TEMPDir%" mkdir "%TEMPDir%"
set "outputfile=%TEMPDir%\_NewEnv.cmd"

set "DelayedExpansionState=IsDisabled"
IF "^!" == "^!^" (
    set "DelayedExpansionState=IsEnabled"
)

cscript //nologo "%~f0?.wsf" "%outputfile%" %DelayedExpansionState%

For /f delims^=^ eol^= %%a in (%outputfile%) do set %%a

if "%debugme%"=="yes" (
    explorer "%TEMPDir%"
) else (
    rmdir /Q /S "%TEMPDir%"
)

set "TEMPDir="
set "outputfile="
set "DelayedExpansionState="
set "debugme="

goto :installPythonStuff

----- Begin wsf script --->
<job><script language="VBScript">

Const ForReading = 1 
Const ForWriting = 2
Const ForAppending = 8 

Set WshShell = WScript.CreateObject("WScript.Shell")
filename=WScript.Arguments.Item(0)
DelayedExpansionState=WScript.Arguments.Item(1)

TMPfilename=filename & "_temp_.cmd"
Set fso = CreateObject("Scripting.fileSystemObject")
Set tmpF = fso.CreateTextFile(TMPfilename, TRUE)


set oEnvS=WshShell.Environment("System")
for each sitem in oEnvS
    tmpF.WriteLine(sitem)
next
SystemPath = oEnvS("PATH")

set oEnvU=WshShell.Environment("User")
for each sitem in oEnvU
    tmpF.WriteLine(sitem)
next
UserPath = oEnvU("PATH")

set oEnvV=WshShell.Environment("Volatile")
for each sitem in oEnvV
    tmpF.WriteLine(sitem)
next
VolatilePath = oEnvV("PATH")

set oEnvP=WshShell.Environment("Process")

ProcessPath = oEnvP("PATH")

NewPath = SystemPath & ";" & UserPath & ";" & VolatilePath & ";" & ProcessPath

Function remove_duplicates(list)
	arr = Split(list,";")
	Set dict = CreateObject("Scripting.Dictionary")
    dict.CompareMode = 1

	For i = 0 To UBound(arr)
		If dict.Exists(arr(i)) = False Then
			dict.Add arr(i),""
		End If
	Next
	For Each key In dict.Keys
		tmp = tmp & key & ";"
	Next
	remove_duplicates = Left(tmp,Len(tmp)-1)
End Function

NewPath = WshShell.ExpandEnvironmentStrings(NewPath)
NewPath=remove_duplicates(NewPath)

If Right(NewPath, 1) = ";" Then 
    NewPath = Left(NewPath, Len(NewPath) - 1) 
End If
  
tmpF.WriteLine("PATH=" & NewPath)
tmpF.Close

arrBlackList = Array("ALLUSERSPROFILE=", "APPDATA=", "CommonProgramFiles=", "CommonProgramFiles(x86)=", "CommonProgramW6432=", "COMPUTERNAME=", "ComSpec=", "HOMEDRIVE=", "HOMEPATH=", "LOCALAPPDATA=", "LOGONSERVER=", "NUMBER_OF_PROCESSORS=", "OS=", "PATHEXT=", "PROCESSOR_ARCHITECTURE=", "PROCESSOR_ARCHITEW6432=", "PROCESSOR_IDENTIFIER=", "PROCESSOR_LEVEL=", "PROCESSOR_REVISION=", "ProgramData=", "ProgramFiles=", "ProgramFiles(x86)=", "ProgramW6432=", "PUBLIC=", "SystemDrive=", "SystemRoot=", "TEMP=", "TMP=", "USERDOMAIN=", "USERDOMAIN_ROAMINGPROFILE=", "USERNAME=", "USERPROFILE=", "windir=", "SESSIONNAME=")

Set objFS = CreateObject("Scripting.FileSystemObject")
Set objTS = objFS.OpenTextFile(TMPfilename, ForReading)
strContents = objTS.ReadAll
objTS.Close

TMPfilename2= filename & "_temp2_.cmd"
arrLines = Split(strContents, vbNewLine)
Set objTS = objFS.OpenTextFile(TMPfilename2, ForWriting, True)

For Each strLine In arrLines
    bypassThisLine=False
    For Each BlackWord In arrBlackList
        If Left(UCase(LTrim(strLine)),Len(BlackWord)) = UCase(BlackWord) Then
            bypassThisLine=True
        End If
    Next
    If bypassThisLine=False Then
        objTS.WriteLine strLine
    End If
Next

set f=fso.OpenTextFile(TMPfilename2,ForReading)
set fW=fso.OpenTextFile(filename,ForWriting,True)
Do Until f.AtEndOfStream
    LineContent = f.ReadLine
    LineContent = WshShell.ExpandEnvironmentStrings(LineContent)
    
    If DelayedExpansionState="IsEnabled" Then
        If InStr(LineContent, "!") > 0 Then
            LineContent=Replace(LineContent,"^","^^")
            LineContent=Replace(LineContent,"!","^!")
        End If
    End If
    
    fW.WriteLine(LineContent)
Loop

f.Close
fW.Close

</script></job>