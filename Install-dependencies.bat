@echo off
:: Maybe add a Windows Version check here?

:tryWinget
winget
if %errorlevel%==0 goto :install
cls
echo Please install/update AppInstaller from the Microsoft Store.
start ms-windows-store://pdp/?ProductId=9nblggh4nns1
echo.
pause
goto :tryWinget

:install
cls
set /p "install=Do you want to install Audacity? (y/n): "
if /i "%install%"=="y" goto :fullInstall
if /i "%install%"=="n" goto :basicInstall
else goto :install

:fullInstall
call :basicInstall
winget install Audacity.Audacity
echo.
goto :restartScript

:basicInstall
cls
winget install Gyan.FFmpeg
echo.
winget install Python.Python.3.11
echo.

:restartScript
python --version
if %errorlevel%==0 goto :installPythonStuff
cls
goto :refrenv
pause

:installPythonStuff
pip install -r requirements.txt
echo.

:end
powershell write-host -fore Green "Success!"
pause
exit


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