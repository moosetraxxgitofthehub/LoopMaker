# Build and validation status

Implemented: lightweight Tkinter GUI, background processing, broad FFmpeg input support,
exact 0.5x–1.5x speed choices, 10-second input validation, forward/reverse concatenation,
silent H.264/yuv420p MP4, original-file protection, collision-safe naming, automatic temporary
cleanup, portable dependency discovery, error handling, Windows build script and CI workflow.

Passed on Linux with FFmpeg: MP4, MOV, WebM/VP9, MKV and AVI; speeds 0.5x/1.0x/1.5x;
frame-by-frame comparison with speed-adjusted input; forward/reverse symmetry; retained
160x120 resolution and 12fps; stripped audio; filenames and paths with spaces; source hashes
unchanged; duplicate export preservation; corrupt/missing input handling; exactly 10-second
input producing a 40-second output at 0.5x; rejection of 10.1-second input.

Not yet validated: Windows GUI launch, executable without Python installed, Windows bundled
FFmpeg/FFprobe, actual disconnected Windows execution, and the Nitro 5 test. No Windows
runner or repository is connected to this environment, so the configured workflow could not
be triggered. The workflow now validates the downloaded dependency checksum, extracted ZIP
contents, bundled tool execution and packaged GUI launch before uploading the artifact. No Windows EXE has been produced. Runtime code has no network calls.

The next required build operation is to run .github/workflows/windows.yml in a connected
GitHub repository. That workflow produces LoopMaker-Windows.zip including LoopMaker.exe,
its runtime, FFmpeg, FFprobe and licensing notices.
