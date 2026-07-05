@echo off
REM setup_windows.bat - Windows 环境安装脚本

echo ====================================
echo pipedata - Windows 环境安装
echo ====================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 未安装或未在 PATH 中
    echo 请从 https://www.python.org/downloads/ 安装 Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python 已安装

echo.
echo [步骤 1] 安装 Python 依赖包...
pip install pymupdf pdf2image pytesseract pillow pandas openpyxl regex
if %errorlevel% neq 0 (
    echo [ERROR] pip 安装失败
    pause
    exit /b 1
)
echo [OK] Python 依赖安装完成

echo.
echo [步骤 2] Tesseract OCR 安装说明
echo ====================================
echo Windows 需要手动安装 Tesseract OCR：
echo.
echo 1. 下载安装程序：
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo    推荐下载：tesseract-ocr-w64-setup-v5.x.exe
echo.
echo 2. 运行安装程序，记住安装路径（默认：C:\Program Files\Tesseract-OCR）
echo.
echo 3. 安装完成后，脚本会自动配置路径
echo.
pause

REM 尝试找到 Tesseract
for %%A in (
    "C:\Program Files\Tesseract-OCR\tesseract.exe"
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
) do (
    if exist %%A (
        echo [OK] 找到 Tesseract: %%A
        set TESSERACT_PATH=%%A
        goto tesseract_found
    )
)

echo [WARNING] 未找到 Tesseract，请手动配置
echo 安装 Tesseract 后，运行脚本时会使用默认路径

:tesseract_found
echo.
echo ====================================
echo 安装完成！
echo ====================================
echo.
echo 下一步：运行提取脚本
echo 命令：python parse_piping_pdfs.py "PP12EXP-P109-G__-MDA-07895_Rev.0C_pkg Isometric drawings for WTP&ETP - 副本 - 副本.pdf" "%USERPROFILE%\Desktop\output.csv"
echo.
pause
