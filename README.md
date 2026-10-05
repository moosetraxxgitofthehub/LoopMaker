# LoopMaker v1

Windows portable build: extract the complete ZIP, then double-click LoopMaker.exe.
Choose a video (10 seconds maximum), choose speed, and click MAKE LOOP.
The output is a silent H.264 MP4 in “LoopMaker Output” beside the input video.
Existing files are preserved; repeated exports receive a numbered suffix.
No connection, account, Python install or separate FFmpeg install is needed to run the packaged app.

## Rebuild
Run the included GitHub Actions Windows workflow. It tests the processing, bundles
FFmpeg/FFprobe with the Python/Tk runtime, and publishes LoopMaker-Windows.zip.
Alternatively, on Windows with Python 3.12, place Windows FFmpeg/FFprobe in tools,
then run build_windows.ps1. This development step needs internet for dependencies.
FFmpeg licenses are included by the workflow. FFmpeg with libx264 uses GPL licensing;
retain the supplied license notices and fulfill its source-distribution requirements when redistributing.

## Troubleshooting
Extract the entire folder, not just the EXE. Put the input video in a writable folder.
A local diagnostic log is kept at %LOCALAPPDATA%\LoopMaker\loopmaker.log.
Odd source dimensions are rounded down by one pixel for H.264 compatibility.

