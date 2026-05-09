$env:QUARTO_DENO_V8_OPTIONS = "--max-old-space-size=14336"
$quarto = "C:\Users\raban\AppData\Local\Programs\Positron\resources\app\quarto\bin\quarto.exe"
Set-Location "C:\Users\raban\Documents\GitHub\methods-in-r"
& $quarto render --to html *> "C:\Users\raban\Documents\GitHub\methods-in-r\render.log"
if ($LASTEXITCODE -eq 0) {
    "SUCCESS" | Out-File "C:\Users\raban\Documents\GitHub\methods-in-r\render.status" -Encoding utf8
} else {
    "FAILED:$LASTEXITCODE" | Out-File "C:\Users\raban\Documents\GitHub\methods-in-r\render.status" -Encoding utf8
}
