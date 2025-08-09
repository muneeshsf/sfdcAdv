# === CONFIGURATION ===
#$folderPath = "$PSScriptRoot"         # Uses current script directory
$outputCSV = "$PSScriptRoot\Approver_Report.csv"


$folderPath = "C:\Muneesh\ApprovalProcesses\unpackaged\approvalProcesses"
#$outputCSV = "C:\Muneesh\Approval_Approvers_Report.csv"

# === INIT ===
$results = @()

# === PROCESS FILES ===
Get-ChildItem -Path $folderPath -Filter *.approvalProcess | ForEach-Object {
    $file = $_
    Write-Host "🔍 Processing: $($file.Name)"

    try {
        [xml]$xml = Get-Content $file.FullName
        $nsmgr = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
        $nsmgr.AddNamespace("sf", "http://soap.sforce.com/2006/04/metadata")

        # Correct XPath for <name> inside <approver>
        $nameNodes = $xml.SelectNodes("//sf:assignedApprover/sf:approver/sf:name", $nsmgr)

        $nameList = @()
        foreach ($node in $nameNodes) {
            if ($node -ne $null -and $node.InnerText.Trim() -ne "") {
                $nameList += $node.InnerText.Trim()
            }
        }

        $finalApprovers = if ($nameList.Count -gt 0) { $nameList -join "; " } else { "Not Found" }

        $results += [PSCustomObject]@{
            ApprovalProcessName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
            AssignedApprover    = $finalApprovers
        }
    }
    catch {
        Write-Host "❌ Error in $($file.Name): $($_.Exception.Message)"
    }
}

# === OUTPUT TO CSV ===
if ($results.Count -gt 0) {
    $results | Export-Csv -Path $outputCSV -NoTypeInformation -Encoding UTF8
    Write-Host ""
    Write-Host "✅ Extraction complete! Results saved to: $outputCSV"
} else {
    Write-Host ""
    Write-Host "⚠️ No approvers found in the XML files."
}
