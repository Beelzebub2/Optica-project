@echo off
call conda activate Optica_env
cd "C:\Users\ricar\OneDrive\Documents\GitHub\Optica-project"
pyinstaller --noconfirm --onedir --windowed --icon "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/icon.ico" --name "Optica" --upx-dir "C:/Users/ricar/upx-3.96-win64" --clean --add-data "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/Faces;Faces/" --add-data "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/Glasses;Glasses/" --add-data "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/Languages;Languages/" --add-data "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/Necessary files;Necessary files/" --add-data "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/Ready-images;Ready-images/" --collect-all "customtkinter" --distpath "C:\Users\ricar\OneDrive\Documents\GitHub\Optica-project\Output" "C:/Users/ricar/OneDrive/Documents/GitHub/Optica-project/main.py"
pause

