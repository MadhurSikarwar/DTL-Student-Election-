@echo off
echo ======================================
echo Git Push to GitHub
echo ======================================

echo.
echo Step 1: Checking Git status...
git status

echo.
echo Step 2: Initializing Git repository (if needed)...
git init

echo.
echo Step 3: Adding all files...
git add .

echo.
echo Step 4: Creating commit...
git commit -m "Prepare for Render deployment - Add configuration files"

echo.
echo Step 5: Adding remote repository...
git remote add origin https://github.com/MadhurSikarwar/DTL-Student-Election-.git

echo.
echo Step 6: Setting branch to main...
git branch -M main

echo.
echo Step 7: Pushing to GitHub...
git push -u origin main

echo.
echo ======================================
echo Done! Check output above for any errors.
echo ======================================
pause
