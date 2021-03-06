del ".\docker\raw\dockerdist\*.py" /s /f /q
xcopy "*.py" ".\docker\raw\dockerdist" /Y /F
xcopy "samples\*.*" ".\docker\raw\dockerdist\samples\" /Y /F
xcopy "conf\*.*" ".\docker\raw\dockerdist\conf\" /Y /F
xcopy "runtime_data" ".\docker\raw\dockerdist\runtime_data\" /Y /E
xcopy "source\*.*" ".\docker\raw\dockerdist\source\" /Y /F
python "crawlerunittest.py" "192.168.0.10" "nimir" "@soleil1"
if %errorlevel% neq 0 exit /b %errorlevel%
cd docker
docker-compose.exe -f .\croustibatch.yml up -d --build