pyinstaller --onefile --noconsole --icon=icons\3d.ico mainwindow.py
rename %cd%\dist\mainwindow.exe BlockGenerator.exe
move %cd%\dist\BlockGenerator.exe %cd%
rd /s /Q %cd%\dist
rd /s /Q %cd%\build