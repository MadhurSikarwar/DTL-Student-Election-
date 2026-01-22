@echo off
echo ======================================
echo Pushing Updates to GitHub
echo ======================================

echo.
echo Adding changed files...
git add templates/login.html
git add requirements.txt

echo.
echo Creating commit...
git commit -m "Add premium forgot password UI with gradients and enhanced modal"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ======================================
echo Done! Your changes are now on GitHub.
echo Render will auto-deploy shortly.
echo ======================================
pause
