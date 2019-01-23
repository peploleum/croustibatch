del ".\docker\raw\dockerdist\*.py" /s /f /q
xcopy "*.py" ".\docker\raw\dockerdist" /Y /F
xcopy "samples\*.*" ".\docker\raw\dockerdist\samples\" /Y /F
xcopy "conf\*.*" ".\docker\raw\dockerdist\conf\" /Y /F
xcopy "runtime_data" ".\docker\raw\dockerdist\runtime_data\" /Y /E