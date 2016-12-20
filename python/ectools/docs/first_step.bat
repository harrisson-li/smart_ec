@ECHO OFF

:: run this script to generate rst file at the beginning.
:: you do not have to run it again and again.

cd %~dp0
sphinx-apidoc -F -o source ../ectools
