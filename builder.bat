call conda activate countdowner
pyinstaller manage.spec --noconfirm
pyinstaller main.spec --noconfirm
pyinstaller console.spec --noconfirm
move dist\manage.exe dist\main\

