$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m pip install pyinstaller==6.16.0
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller installation failed' }
if (!(Test-Path tools/ffmpeg.exe) -or !(Test-Path tools/ffprobe.exe)) {
  throw 'Place FFmpeg and FFprobe Windows executables in tools before building.'
}
if (Test-Path dist/LoopMaker) { Remove-Item dist/LoopMaker -Recurse -Force }
python -m PyInstaller --noconfirm --clean --onedir --windowed --name LoopMaker loopmaker.py
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
Copy-Item tools/ffmpeg.exe,tools/ffprobe.exe dist/LoopMaker/
Copy-Item README.md dist/LoopMaker/
if (Test-Path tools/licenses) { Copy-Item tools/licenses dist/LoopMaker/licenses -Recurse -Force }
Compress-Archive -Path dist/LoopMaker -DestinationPath LoopMaker-Windows.zip -Force
