#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


# given x and y of height and width, x * w + y is the index of pixel in 1D array
def get_pixel(image, x, y):
    return image['pixels'][ x * image['width'] + y ]

def set_pixel(image, x, y, c):
    image['pixels'][ x * image['width'] + y ] = c


def apply_per_pixel(image, func):
    # define new image object with same dimensions and zero-ed out pixels array of same length
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*(image['height']*image['width']),
    }
    # iterate through every row and column, apply func to pixel, save new pixel value into new image object
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def extend(image, k):
    """
    given an image and a kernel side length, extends the image for the kernel side length. 
    Returns separate image, not modified in place.
    """
    extended = {
        'height': image['height'] + k-1,
        'width': image['width'] + k-1,
        'pixels': []
    }
    # add top border padding , doesn't include any original pxs
    for i in range(k//2):
        row_1 = image['pixels'][:image['width']]
        extended['pixels'] += [row_1[0]] * (k//2 + 1) + row_1[1:-1] + [row_1[-1]] * (k//2 + 1)
    # add left-right padded for all the original img rows
    for i in range(image['height']):
        row_i = image['pixels'][i*image['width'] : (i+1)*image['width']]
        extended['pixels'] += [row_i[0]] * (k//2 + 1) + row_i[1:-1] + [row_i[-1]] * (k//2 + 1)
    # add bottom border padding , doesn't include any original pxs
    for i in range(k//2):
        row_h = image['pixels'][-image['width']:]
        extended['pixels'] += [row_h[0]] * (k//2 + 1) + row_h[1:-1] + [row_h[-1]] * (k//2 + 1)
    return extended

def element_mult(A, B):
    """
    given two nonempty 2D arrays of the same size, return a scalar that is the sum of 
    the element-wise multiplications of the 2 arrays.
    """
    s = 0
    for r in range(len(A)):
        for c in range(len(A[0])):
            s += A[r][c] * B[r][c]
    return s

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    kernel: 2D array, list of rows which are themselves lists of vals for each column, e.g.
    [[1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]]
    values accessed by kernel[r][c]
    """
    # create new image obj
    correlated = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    k = len(kernel)
    extended = extend(image, k)
    # loop through all original pixels of image (no padding)
    for r in range(k//2, k//2 + extended['height'] - k + 1):
        for c in range(k//2, k//2 + extended['width'] - k + 1):
            im_block = []
            first_row = r-k//2
            # for each original pixel, find the 2D array of relevant (extended) pixels around the original pixel
            for i in range(k):
                e_row = first_row + i
                row_l_i = extended['width'] * e_row + c - k//2
                im_block += [extended['pixels'][row_l_i: row_l_i + k]]
            # add the dot product of relevant pixel block and kernel to new image object's pixels
            correlated['pixels'] += [element_mult(im_block, kernel)]
    return correlated


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    # create new image obj
    rced = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    #round and clip pixels in old image obj to add to new image obj
    for x in image['pixels']:
        end = round(x)
        if end > 255: end = 255
        if end < 0: end = 0
        rced['pixels'] += [end]
    return rced


# FILTERS

def get_kernel(n):
    return [[1/n**2] * n] * n

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = get_kernel(n)

    # then compute the correlation of the input image with that kernel
    correlated = correlate(image, kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(correlated)

def sharpened(image, n):
    """
    Returns a sharpened image by subtraction of blurred (without r&c) with kernel
    size n from original.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # make kernel, blur image without rounding and clipping yet
    kernel = get_kernel(n)
    blurred = correlate(image, kernel)
    # make new image obj to be returned at end
    sharpened = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    # loop through image & blurred pixels to do subtraction
    for i in range(len(image['pixels'])):
        sharpened['pixels'] += [2 * image['pixels'][i] - blurred['pixels'][i]]
    return round_and_clip_image(sharpened)

def edges(image):
    """
    Returns an image with detected edges using the Sobel operator filter.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    k_x = [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ]
    k_y = [
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ]
    # find x, y outputs by correlation with respective kernels
    O_x = correlate(image, k_x)
    O_y = correlate(image, k_y)
    # define new output object
    O = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    # loop though pixels in O_x and O_y to get pixel values for total output
    for p in range(len(image['pixels'])):
        O['pixels'] += [round(math.sqrt( O_x['pixels'][p] ** 2 + O_y['pixels'][p] ** 2 ))]
    return round_and_clip_image(O)

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    # # inverting bluegill image
    # bluegill = load_image('./test_images/bluegill.png')
    # save_image(inverted(bluegill), './test_results/bluegillinverted.png')

    # #convoluting pigbird image
    # pigbird = load_image('./test_images/pigbird.png')
    # kernel = [
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # ]
    # save_image(round_and_clip_image(correlate(pigbird, kernel)), './test_results/pigbird_convoluted.png')

    # # blurring cat image
    # cat = load_image('./test_images/cat.png')
    # save_image(blurred(cat, 5), './test_results/cat_blurred.png')

    # # sharpening python image
    # python = load_image('./test_images/python.png')
    # save_image(sharpened(python, 11), './test_results/python_sharpened.png')

    # detecting edges in construct image
    construct = load_image('./test_images/construct.png')
    save_image(edges(construct), './test_results/construct_edges.png')


