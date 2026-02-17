@echo off
echo Certificate Generator Example Usage
echo ===================================
echo.

REM Basic usage with default settings
echo Running basic example...
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --output output

REM Example with custom font size and color
echo.
echo Running example with custom font size and color...
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --output output_custom --font-size 80 --color blue

REM Example with custom position
echo.
echo Running example with custom text position...
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --output output_position --position 500 400

echo.
echo All examples completed. Check the output folders for generated certificates.
pause