param (
    [Parameter(Mandatory = $true)]
    [string]$Experiment,

    [Parameter(Mandatory = $true)]
    [string]$ParticipantID
)

$remoteUser = "qtrobot"
$remoteHost = "192.168.1.34"
$remoteDir = "/home/qtrobot/robot/code/natty/test_qt_speech/src/data/$Experiment"
$remoteFile = "participant_${ParticipantID}_data.csv"
$remotePath = "$remoteDir/$remoteFile"
$localPath = "./data/$Experiment"

if (-not (Test-Path $localPath)) {
    New-Item -ItemType Directory -Path $localPath | Out-Null
}

Write-Output "📥 Downloading participant $ParticipantID data for $Experiment..."

# Use scp command with proper quoting
$scpCommand = "scp ${remoteUser}@${remoteHost}:$remotePath $localPath"
Invoke-Expression $scpCommand

if ($LASTEXITCODE -eq 0) {
    Write-Output "✅ Download complete: $localPath/$remoteFile"
}
else {
    Write-Output "❌ Download failed."
}
