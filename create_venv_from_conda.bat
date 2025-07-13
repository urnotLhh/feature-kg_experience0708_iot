@echo off
echo ========================================
echo 从Conda环境创建Python venv环境
echo ========================================

echo.
echo 正在检查Python版本...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo.
echo 正在创建虚拟环境...
python -m venv venv_from_conda
if errorlevel 1 (
    echo 错误: 创建虚拟环境失败
    pause
    exit /b 1
)

echo.
echo 正在激活虚拟环境...
call venv_from_conda\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

echo.
echo 正在升级pip...
python -m pip install --upgrade pip

echo.
echo 正在安装依赖包...
echo 请选择要使用的requirements文件:
echo 1. requirements_from_conda.txt (推荐)
echo 2. requirements_pip.txt
echo 3. 手动指定文件路径
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" (
    if exist requirements_from_conda.txt (
        pip install -r requirements_from_conda.txt
    ) else (
        echo 错误: requirements_from_conda.txt 文件不存在
        pause
        exit /b 1
    )
) else if "%choice%"=="2" (
    if exist requirements_pip.txt (
        pip install -r requirements_pip.txt
    ) else (
        echo 错误: requirements_pip.txt 文件不存在
        pause
        exit /b 1
    )
) else if "%choice%"=="3" (
    set /p filepath="请输入文件路径: "
    if exist "%filepath%" (
        pip install -r "%filepath%"
    ) else (
        echo 错误: 文件不存在
        pause
        exit /b 1
    )
) else (
    echo 无效选择
    pause
    exit /b 1
)

echo.
echo ========================================
echo 环境创建完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 激活环境: venv_from_conda\Scripts\activate.bat
echo 2. 退出环境: deactivate
echo.
echo 注意: 某些conda特定的包可能需要手动安装
echo ========================================

pause 