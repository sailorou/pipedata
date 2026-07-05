# pipedata - Windows 安装和使用指南

## 快速开始（3步）

### 步骤 1：安装系统依赖 - Tesseract OCR

1. **下载安装程序**
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载 `tesseract-ocr-w64-setup-v5.x.exe`（最新版本）

2. **运行安装**
   - 双击安装程序
   - 默认安装路径：`C:\Program Files\Tesseract-OCR`
   - 完成安装

### 步骤 2：安装 Python 依赖

在命令行中运行：

```bash
pip install pymupdf pdf2image pytesseract pillow pandas openpyxl regex
```

或者双击运行 `setup_windows.bat` 脚本（自动安装）

### 步骤 3：运行提取脚本

在命令行中执行：

```bash
python parse_piping_pdfs.py "PP12EXP-P109-G__-MDA-07895_Rev.0C_pkg Isometric drawings for WTP&ETP - 副本 - 副本.pdf" "%USERPROFILE%\Desktop\output.csv"
```

或者双击运行 `run_extraction.bat` 脚本

---

## 详细说明

### 环境要求

- **Python 3.8+** （如未安装，从 https://www.python.org/downloads/ 下载）
- **Tesseract OCR** （见步骤 1）

### 输出文件

脚本运行完成后，桌面上会生成：

- `piping_materials.csv` - CSV 格式结果
- `piping_materials.xlsx` - Excel 格式结果

### 输出格式说明

| 列名 | 说明 |
|------|------|
| `pdf_file` | PDF 文件名 |
| `page_number` | 页码 |
| `pipeline_numbers` | 提取的管线号（多个用 `;` 分隔） |
| `materials` | 提取的材质信息（多个用 `;` 分隔） |
| `text_snippet` | 页面文本摘要（前 300 字符） |
| `ocr_used` | 是否使用了 OCR（True/False） |

### 示例结果

```
pdf_file,page_number,pipeline_numbers,materials,text_snippet,ocr_used
PP12EXP-P109-G__-MDA-07895_Rev.0C_pkg...pdf,1,A-101; L-201,SS316; 碳钢,管线号: A-101 材质: SS316...,False
```

---

## 故障排除

### 问题 1：`ModuleNotFoundError: No module named 'fitz'`

**解决**：重新安装 PyMuPDF
```bash
pip install --upgrade pymupdf
```

### 问题 2：`pytesseract.TesseractNotFoundError`

**解决**：Tesseract OCR 未正确安装或路径不对

1. 检查 Tesseract 是否安装在 `C:\Program Files\Tesseract-OCR`
2. 如果安装在其他位置，编辑 `run_extraction.bat`，修改第 7-8 行：
   ```batch
   set TESSDATA_PREFIX=您的安装路径\tessdata
   set PATH=%PATH%;您的安装路径
   ```

### 问题 3：PDF 无法提取文本（OCR_used 全为 True）

**原因**：PDF 是扫描件（图片形式）

**解决**：确保 Tesseract 已正确安装并配置（见问题 2）

### 问题 4：无法识别中文字符

**原因**：Tesseract 语言包不完整

**解决**：
1. 在 Tesseract 安装过程中勾选 "Chinese Simplified"
2. 或手动下载语言包到 `C:\Program Files\Tesseract-OCR\tessdata`

---

## 自定义提取规则

如需修改提取规则以适应特定的标签格式，编辑 `parse_piping_pdfs.py` 文件：

### 修改管线号识别（约 40-49 行）

```python
PIPE_PATTERNS = [
    # 添加您的自定义模式
    re.compile(r'您的标签格式', re.IGNORECASE),
]
```

### 修改材质识别（约 51-59 行）

```python
MATERIAL_PATTERNS = [
    # 添加您的自定义模式
    re.compile(r'您的标签格式', re.IGNORECASE),
]
```

示例：如果图纸使用 "SPEC:" 标签，添加：
```python
re.compile(r'SPEC[:：]?\s*([A-Za-z0-9\-\s/]+)', re.IGNORECASE),
```

---

## 获取帮助

- 查看脚本源代码：`parse_piping_pdfs.py`
- GitHub 仓库：https://github.com/sailorou/pipedata
