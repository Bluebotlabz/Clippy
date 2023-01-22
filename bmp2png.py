from PIL import Image, ImageChops
import os

os.makedirs('./Agent/Images', exist_ok=True)

for image in os.listdir('./Agent/bmp/'):
    im = Image.open(os.path.join('./Agent/bmp/', image))

    # Convert bitmap to RGB type
    im = im.convert("RGBA")

    # Split colour bands and convert to 1-bit images
    splitBands = im.split()
    red = splitBands[0].point(lambda i: i < 255 and 255, mode='1')
    green = splitBands[1].point(lambda i: i < 255 and 255, mode='1')
    blue = splitBands[2].point(lambda i: i < 255 and 255, mode='1')

    # Remove anything that isn't 255, 0, 255 (ok, this actually makes the inverse, idk)
    red = ImageChops.subtract(green, red)
    blue = ImageChops.subtract(green, blue)

    # Calculate alpha and invert bc idk
    alpha = ImageChops.logical_and(red, blue)
    alpha = ImageChops.invert(alpha)

    # Add alpha to the image
    im.putalpha(alpha)

    #im = im.resize((im.width*4, im.height*4), resample=Image.Resampling.NEAREST)

    im.save(os.path.join('./Agent/Images/', image.replace('.bmp', '.png')))