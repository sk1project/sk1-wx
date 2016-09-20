Wscript.Echo "==="


strComputer = "."
Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")

Set colItems = objWMIService.ExecQuery("Select * from Win32_PrinterConfiguration",,48)
For Each objItem in colItems
    Wscript.Echo objItem.Name & "::" & objItem.Color
Next

Wscript.Echo "==="

Set colInstalledPrinters = objWMIService.ExecQuery ("Select * from Win32_Printer")
For Each objPrinter in colInstalledPrinters
    val = "False"
    IF objPrinter.Default THEN val = "True"
    Wscript.Echo objPrinter.Name & "::" & val
Next


Wscript.Echo "==="