Option Explicit 
   '* 
    Const ForWriting = 8
    
   '* 
    Dim strGFI, objFSO1, objOutputFile 
    Dim strOTF, MyString, objFileSystem 
    Dim strWSE, strWritePath, objFile 
    Dim strInput1, strInput2, cFOL, StrDirectory,strInput3,strInput4,strInput5,strInput6
	strInput1="BMG Sales"
	strInput2="BMG Partner"
	strInput3="BMG Tech Partner"
	strInput4="BMG_SALES"
	strInput5="BMG_PARTNER"
	strInput6="BMG_TECH_PARTNER"
   '* 
   cFOL = InputBox("Enter the path to search"& VbCrLf & "(e.g., C:\temp)")
  ' strInput = Inputbox("Enter the text1 you would like to search for.")
   
   MyString = "FileSearchResultLables"
   strWritePath = "C:\Muneesh\Lables\" & MyString & ".txt"
   strDirectory =  "C:\Muneesh\Lables\"
   
   Set objFSO1 = CreateObject("Scripting.FileSystemObject")

If objFSO1.FileExists(strWritePath) Then
	Wscript.Echo "The file Exists"
Else
	Set objFile = objFSO1.CreateTextFile(strDirectory & MyString & ".txt")
	objFile = ""

End If
   
Set objFileSystem = CreateObject("Scripting.fileSystemObject")
Set objOutputFile = objFileSystem.OpenTextFile("C:\Muneesh\Lables\" & MyString & ".txt", ForWriting)

If cFOL > "" Then
	If strInput1 > "" Then
	
    Dim objFSO 
    Set objFSO = CreateObject("Scripting.FileSystemObject") 
    Dim objGFO 
    Set objGFO = objFSO.GetFolder(cFOL) 
    Dim objGFI 
    Set objGFI = objGFO.Files 
    For Each strGFI in objGFI 
        Dim objOTF 
        Set objOTF = objFSO.OpenTextFile(cFOL & "\" & strGFI.Name,1) 
        Do While Not objOTF.AtEndOfStream 
            strOTF = objOTF.ReadAll() 
			
        Loop 
            objOTF.Close() 
        Set objOTF = Nothing 
       '* 
       ' If  InStr(LCase(strOTF), strInput) > 0 Then 
	   If  InStr(strOTF, strInput1) > 0  Then
            strWSE = strWSE & strGFI.Name & " contains " & strInput1  & vbCrLf
		End if	
				
        If  InStr(strOTF, strInput2) > 0 Then
            strWSE = strWSE & strGFI.Name & " contains " & strInput2 &  vbCrLf
		End if
		 If  InStr(strOTF, strInput3) > 0 Then
            strWSE = strWSE & strGFI.Name & " contains " & strInput3 &  vbCrLf
		End if
		 If  InStr(strOTF, strInput4) > 0 Then
            strWSE = strWSE & strGFI.Name & " contains " & strInput4 &  vbCrLf
		End if
		 If  InStr(strOTF, strInput5) > 0 Then
            strWSE = strWSE & strGFI.Name & " contains " & strInput5 &  vbCrLf
		End if
		 If  InStr(strOTF, strInput6) > 0 Then
            strWSE = strWSE & strGFI.Name & " contains " & strInput6 &  vbCrLf
		End if
		
    Next 
	objOutputFile.WriteLine(strWSE)
	objOutputFile.Close
	
   '* 
    Set objGFI = Nothing 
    Set objGFO = Nothing 
    Set objFSO = Nothing
	Set objFileSystem = Nothing
	Set objFSO1 = Nothing
	
   '* 
    WScript.Echo strWSE
	Wscript.Echo "Processing Over"
		Else
		Wscript.Echo "You Clicked Cancel or no search string was defined."
		End If
Else
Wscript.Echo "You Clicked Cancel or no search path was defined."
WScript.Quit
End If