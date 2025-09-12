param (
    [string]$Message = ""
)

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = Read-Host "Enter commit message"
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "$Message [$timestamp]"

Write-Host "Adding all changes..."
git add .

Write-Host "Committing with message: $commitMessage"
git commit -m "$commitMessage"

Write-Host "Pushing to remote..."
git push

Write-Host "✅ Done!"
