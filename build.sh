python3 -m pip3 install -U pyinstaller

pyinstaller --onefile main.py -

echo "purging ./dist/"
rm -rf dist/

python -m PyInstaller --onefile --name "tictactoe" main.py

echo "executable at dist/tictactoe"
