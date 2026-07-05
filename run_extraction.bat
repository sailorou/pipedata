@echo off
REM run_extraction.bat - 执行 PDF 提取脚本
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ====================================
echo PDF 管道图纸材料表提取
echo ====================================
echo.

REM 设置 Tesseract 路径
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

REM 源 PDF 文件
set SOURCE_PDF="PP12EXP-P109-G__-MDA-07895_Rev.0C_pkg Isometric drawings for WTP&ETP - 副本 - 副本.pdf"

REM 输出文件（桌面）
set OUTPUT_CSV="%USERPROFILE%\Desktop\piping_materials.csv"
set OUTPUT_XLSX="%USERPROFILE%\Desktop\piping_materials.xlsx"

echo [信息] 源文件：%SOURCE_PDF%
echo [信息] 输出位置：%USERPROFILE%\Desktop\
echo.

REM 检查源文件是否存在
if not exist %SOURCE_PDF% (
    echo [错误] 找不到源 PDF 文件：%SOURCE_PDF%
    echo.
    echo 请确保：
    echo 1. 当前目录包含 PDF 文件
    echo 2. 在仓库根目录运行此脚本
    echo.
    pause
    exit /b 1
)

echo [开始] 提取材料表信息...
echo 这可能需要几分钟（取决于 PDF 页数）
echo.

python parse_piping_pdfs.py %SOURCE_PDF% %OUTPUT_CSV%

if %errorlevel% equ 0 (
    echo.
    echo [成功] 提取完成！
    echo.
    echo [输出文件]
    echo   CSV:  %OUTPUT_CSV%
    if exist %OUTPUT_XLSX% (
        echo   XLSX: %OUTPUT_XLSX%
    )
    echo.
    echo 按任意键打开输出文件夹...
    pause >nul
    explorer %USERPROFILE%\Desktop\
) else (
    echo.
    echo [错误] 提取失败
    echo.
    echo 常见原因：
    echo 1. Tesseract OCR 未安装 - 运行 setup_windows.bat
    echo 2. Python 依赖缺失 - 运行 setup_windows.bat
    echo 3. PDF 文件路径或名称不对
    echo.
    pause
    exit /b 1
)
