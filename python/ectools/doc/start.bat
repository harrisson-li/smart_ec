@ECHO OFF
cd %~dp0
sphinx-apidoc -f -o build ../ectools
