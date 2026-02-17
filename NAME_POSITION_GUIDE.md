# Name Position Guide for Certificate Generator

## Understanding the Position Parameter

The `--position` parameter in the certificate generator script controls where the name text appears on your certificate. It takes two values:

```
--position X Y
```

Where:
- **X**: Horizontal position (from left to right)
- **Y**: Vertical position (from top to bottom)

## Default Position

The default position is set to `400 300`, which means:
- 400 pixels from the left edge
- 300 pixels from the top edge

## Finding the Optimal Position

I've created a position finder tool that generates test images with sample text at different positions. To use it:

```
python position_finder.py "Blue and Gold Simple Certificate.png" --output position_test
```

This will create several test images in the `position_test` folder:

1. `grid_overlay.png` - Shows a grid with coordinate markers
2. `position_test_X_Y.png` - Sample images with text at different positions

## Certificate Dimensions

Your certificate template dimensions are **2000×1414 pixels**.

The position finder has generated test images with text at these positions:
- Center: (1000, 707)
- Upper center: (1000, 471)
- Lower center: (1000, 942)
- Center left: (666, 707)
- Center right: (1333, 707)
- Default position: (400, 300)

## How to Choose the Best Position

1. Open the test images in the `position_test` folder
2. Find the image where the text is positioned best for your certificate
3. Note the X and Y coordinates from the filename (`position_test_X_Y.png`)
4. Use those coordinates with the certificate generator:

```
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --position X Y
```

For example, if you prefer the center position:

```
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --position 1000 707
```

## Fine-Tuning

If none of the test positions are exactly right, you can adjust the X and Y values to fine-tune the position. For example:

```
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --position 1000 600
```

This would place the text at the horizontal center but slightly higher than the vertical center.