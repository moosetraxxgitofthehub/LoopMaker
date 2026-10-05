# Windows packaging

Put the CONTENTS of this LoopMaker folder at the repository root. The workflow must
be at .github/workflows/windows.yml, not LoopMaker/.github/workflows/windows.yml.

The workflow runs on pushes to main/master, or manually via Actions → Build portable
Windows LoopMaker → Run workflow. No repository secrets are required. GitHub Actions
must be enabled and the account must have Windows runner capacity available.

It downloads and checks FFmpeg, runs the existing processing tests on Windows,
builds a portable PyInstaller folder, checks the packaged runtime and launches the
packaged GUI from another working directory, then publishes the LoopMaker-Windows
artifact. The artifact contains LoopMaker-Windows.zip; extract that ZIP completely
and open LoopMaker/LoopMaker.exe. Artifacts are retained for thirty days.

Configured but not executed yet: no GitHub repository or account is connected to
this session. Connecting GitHub and providing a writable repository is the remaining
requirement. The app source and features are unchanged.
