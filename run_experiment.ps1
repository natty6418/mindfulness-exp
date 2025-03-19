# Prompt user for participant ID
$participantID = Read-Host "Enter Participant ID"

# Define log file paths
$videoLogOut = "./data/participant_${participantID}_video_out.log"
$videoLogErr = "./data/participant_${participantID}_video_err.log"
$ppgLogOut = "./data/participant_${participantID}_ppg_out.log"
$ppgLogErr = "./data/participant_${participantID}_ppg_err.log"
$triggerLogOut = "./data/participant_${participantID}_trigger_out.log"
$triggerLogErr = "./data/participant_${participantID}_trigger_err.log"

Write-Output "Starting experiment for Participant $participantID..."

# Video
$videoProcess = Start-Process `
    -FilePath "python" `
    -ArgumentList "recordVideo.py $participantID" `
    -RedirectStandardOutput $videoLogOut `
    -RedirectStandardError $videoLogErr `
    -PassThru

# PPG
$ppgProcess = Start-Process `
    -FilePath "python" `
    -ArgumentList "ppg.py $participantID" `
    -RedirectStandardOutput $ppgLogOut `
    -RedirectStandardError $ppgLogErr `
    -PassThru

# Trigger
$triggerProcess = Start-Process `
    -FilePath "python" `
    -ArgumentList "remote_trigger_.py $participantID" `
    -RedirectStandardOutput $triggerLogOut `
    -RedirectStandardError $triggerLogErr `
    -PassThru

# Check if processes started successfully
if (!$videoProcess) { Write-Error "Error: Failed to start recordVideo.py" }
if (!$ppgProcess) { Write-Error "Error: Failed to start ppg.py" }
if (!$triggerProcess) { Write-Error "Error: Failed to start remote_trigger_.py" }

Write-Output "Processes started. Logs are being written."

# Wait for user to stop experiment
Write-Host "Press any key to stop the experiment..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop running processes
if ($videoProcess -and $videoProcess.Id) {
    Stop-Process -Id $videoProcess.Id -Force
}
if ($ppgProcess -and $ppgProcess.Id) {
    Stop-Process -Id $ppgProcess.Id -Force
}
if ($triggerProcess -and $triggerProcess.Id) {
    Stop-Process -Id $triggerProcess.Id -Force
}

Write-Output "Experiment stopped. Data saved as:"
Write-Output " - Video: participant_${participantID}_video.avi"
Write-Output " - PPG Data: participant_${participantID}_ppg_data.txt"
Write-Output " - Logs: $videoLogOut, $videoLogErr, $ppgLogOut, $ppgLogErr, $triggerLogOut, $triggerLogErr"
