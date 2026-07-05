@echo off
REM run_extraction.bat - 执行 PDF 提取脚本

setlocal enabledelayedexpansion

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
    echo [ERROR] 找不到源 PDF 文件：%SOURCE_PDF%
    echo 请确保在当前目录中运行此脚本
    pause
    exit /b 1
)

echo [开始] 提取材料表信息...
echo.

python parse_piping_pdfs.py %SOURCE_PDF% %OUTPUT_CSV%

if %errorlevel% equ 0 (
    echo.
    echo [成功] 提取完成！
    echo [输出] CSV: %OUTPUT_CSV%
    if exist %OUTPUT_XLSX% (
        echo [输出] XLSX: %OUTPUT_XLSX%
    )
    echo.
    echo 按任意键打开输出文件夹...
    pause
    explorer %USERPROFILE%\Desktop\
) else (
    echo.
    echo [ERROR] 提取失败，错误代码：%errorlevel%
    pause
    exit /b 1
)
