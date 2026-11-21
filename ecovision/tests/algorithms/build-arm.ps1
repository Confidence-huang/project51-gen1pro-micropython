$ErrorActionPreference='Stop'
Set-Location (Join-Path $PSScriptRoot '../..')
New-Item -ItemType Directory -Force tests/algorithms/build | Out-Null
$cc='D:\k51\ARM\ARMCLANG\bin\armclang.exe'
& $cc --version
if($LASTEXITCODE -ne 0){throw 'AC6 unavailable'}
& $cc --target=arm-arm-none-eabi -mcpu=cortex-m4 -mthumb -std=c99 -Oz -Wall -Wextra -Werror -I algorithms -c algorithms/ecovision_algorithm.c -o tests/algorithms/build/ecovision_algorithm.arm.o
if($LASTEXITCODE -ne 0){throw 'ARM object compilation failed'}
python tests/algorithms/arm_resources.py
if($LASTEXITCODE -ne 0){throw 'ARM object inspection failed'}
