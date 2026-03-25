<<comment
Step 2: Make the Script Executable (One-time setup)
Unlike Windows, Mac doesn't automatically trust script files just because you double-click them. They need to tell their Mac that this file is safe to run.

They should open their Mac Terminal and navigate to the project folder.

Run this single command to grant execution permissions:

Bash
chmod +x build_mac.sh
(They only ever have to do this once. The file will remember it has permission forever).

Step 3: How to use it
Whenever they update the code and want to generate a fresh Mac executable, they can just open their terminal to the project folder and run:

Bash
./build_mac.sh
It will execute the exact same 4-step process as your Windows batch file, and output a fresh, native SCEMAS executable into their dist folder!
comment


#!/bin/bash

echo "=========================================="
echo "       SCEMAS Auto-Build Script (Mac)"
echo "=========================================="
echo ""

echo "[1/4] Building React Frontend..."
cd frontend || exit
npm run build
cd ..

echo ""
echo "[2/4] Cleaning old build files..."
rm -rf build dist SCEMAS.spec

echo ""
echo "[3/4] Packaging Application into Executable..."
# Note the colon (:) instead of a semicolon (;) for Mac paths!
python3 -m PyInstaller --name SCEMAS --onefile --add-data "frontend/dist:dist" app.py

echo ""
echo "=========================================="
echo "[4/4] Build Complete!"
echo "Check the 'dist' folder for the 'SCEMAS' executable file."
echo "=========================================="