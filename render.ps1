$env:QUARTO_DENO_V8_OPTIONS = "--max-old-space-size=14336"
$quarto = "C:\Users\raban\AppData\Local\Programs\Positron\resources\app\quarto\bin\quarto.exe"
$log = "render.log"

Write-Host "Starting Quarto render of 680 pages..." -ForegroundColor Cyan
Write-Host "This will take approximately 30 minutes." -ForegroundColor Yellow
Write-Host "Progress is logged to $log" -ForegroundColor DarkGray
Write-Host ""

$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $quarto render --to html 2>&1 | Tee-Object -FilePath $log
$sw.Stop()

$mins = [math]::Round($sw.Elapsed.TotalMinutes, 1)
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nRender complete in $mins minutes! Open docs\index.html to view." -ForegroundColor Green
} else {
    Write-Host "`nRender failed with exit code $LASTEXITCODE after $mins minutes." -ForegroundColor Red
    Write-Host "Check $log for details." -ForegroundColor Yellow
}
