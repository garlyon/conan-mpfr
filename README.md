# conan-mpfr

Development version

`conan create mpfr grif/dev`

Building process requires WSL on Windows

Cross-compillation is not supported

## What works:
Linux - x64 - gmp:static/shared - mpfr:static/shared

Windows - x86/x86_64 - gmp:shared - mpfr:shared

## What doesn't:
Linux - x86_64

Windows - x86/x86_64 - gmp:static - mpfr:static

Windows - x86/x86_64 - gmp:static - mpfr:shared

Windows - x86/x86_64 - gmp:shared - mpfr:static
