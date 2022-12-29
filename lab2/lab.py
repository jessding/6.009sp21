#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


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


# VARIOUS FILTERS

# split colored image to three separate images for each color channel
def rgb_split(im):
    r = {
        'height': im['height'],
        'width': im['width'],
        'pixels': [x[0] for x in im['pixels']]
    }
    g = {
        'height': im['height'],
        'width': im['width'],
        'pixels': [x[1] for x in im['pixels']]
    }
    b = {
        'height': im['height'],
        'width': im['width'],
        'pixels': [x[2] for x in im['pixels']]
    }
    return (r, g, b)

# given three color-channel versions of the same image, combine all channels together for one colored image
def rgb_combine(r, g, b):
    im = {
        'height': r['height'],
        'width': r['width'],
        'pixels': [(r['pixels'][i], g['pixels'][i], b['pixels'][i]) for i in range(len(r['pixels']))]
    }
    return im

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def filter_color(color_im):
        r, g, b = rgb_split(color_im)
        return rgb_combine(filt(r), filt(g), filt(b))
    return filter_color

# makes a blur filter function with only image arg
def make_blur_filter(n):
    def blur(im):
        return blurred(im, n)
    return blur

# makes a sharpen filter function with only image arg
def make_sharpen_filter(n):
    def sharpen(im):
        return sharpened(im, n)
    return sharpen

# makes a single filter that is the sum of consequently applying all filters in given list
def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter_stack(im):
        for f in filters:
            im = f(im)
        return im
    return filter_stack


def threshold(t):
    """
    Given a color image and a threshold t, changes each pixel channel value to 0 if < threshold and 255 if >= threshold.
    """
    def threshold_t(im):
        returned = {
            'height': im['height'],
            'width': im['width'],
            'pixels': []
        }
        for p in im['pixels']:
            new_p = (0 if p[0] < t else 255, 0 if p[1] < t else 255, 0 if p[2] < t else 255)
            returned['pixels'] += [new_p]
        return returned
    return threshold_t

# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    for i in range(ncols):
        gray = greyscale_image_from_color_image(image)
        energy = compute_energy(gray)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        image = image_without_seam(image, seam)
    return image


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    gray = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [round(0.299*p[0] + 0.587*p[1] + 0.114* p[2]) for p in image['pixels']]
    }
    return gray


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    # create new image/energy map object
    w = energy['width']
    h = energy['height']
    cumu_energy = {
        'height': h,
        'width': w,
        'pixels': energy['pixels'][:w]
    }
    # iterate through the rows top-down and get the top adjacent 3 pixels, substituting inf if on edge.
    # use the adjacent pixels to calculate value for cumulative energy map
    for r in range(1, h):
        for p in range(r*w, (r+1)*w):
            top_left_p = cumu_energy['pixels'][p-w-1] if p != r*w else float('inf')
            top_center_p = cumu_energy['pixels'][p-w]
            top_right_p = cumu_energy['pixels'][p-w+1] if p != (r+1)*w-1 else float('inf')
            cumu_energy['pixels'] += [energy['pixels'][p] + min(top_left_p, top_center_p, top_right_p)]
    return cumu_energy

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    h = cem['height']
    w = cem['width']
    # add minimum index of last row of cem to seam
    last_row = cem['pixels'][(h-1)*w : h*w]
    min_i = last_row.index(min(last_row)) + (h-1)*w
    seam = [ min_i ]

    # iterate through the rows bottom-up and get a list length 3 of top adjacent pixels, substituting inf if on edge.
    # use the minimum index of the 3-list to calculate index of next pixel in seam
    for r in range(h-2, -1, -1):
        top_left_p = cem['pixels'][min_i - w - 1] if min_i != (r+1)*w else float('inf')
        top_center_p = cem['pixels'][min_i - w]
        top_right_p = cem['pixels'][min_i - w + 1] if min_i != (r+2)*w-1 else float('inf')
        row_above = [top_left_p, top_center_p, top_right_p]
        min_top = row_above.index(min(row_above))
        min_i = min_i - w - 1 + min_top
        seam += [ min_i ]

    return seam


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    new_im = []
    for i in range(len(image['pixels'])):
        if i not in seam:
            new_im += [image['pixels'][i]]
    ret = {
        'height': image['height'],
        'width': image['width']-1,
        'pixels': new_im
    }
    return ret

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
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


def save_greyscale_image(image, filename, mode='PNG'):
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

    # color_cat = load_color_image('./test_images/cat.png')
    # color_invert = color_filter_from_greyscale_filter(inverted)
    # save_color_image(color_invert(color_cat), './test_results/catcolorinverted.png')

    # python = load_color_image('./test_images/python.png')
    # blur_f = make_blur_filter(9)
    # color_blur = color_filter_from_greyscale_filter(blur_f)
    # save_color_image(color_blur(python), './test_results/pythoncolorblurred.png')

    # schick = load_color_image('./test_images/sparrowchick.png')
    # sharp_f = make_sharpen_filter(7)
    # color_sharp = color_filter_from_greyscale_filter(sharp_f)
    # save_color_image(color_sharp(schick), './test_results/sparrowchicksharpened.png')


    # frog = load_color_image('./test_images/frog.png')
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # save_color_image(filt(frog), './test_results/frogchainfiltered.png')


    # image = load_color_image('./test_images/pattern.png')
    # gray = greyscale_image_from_color_image(image)
    # print("gray: ", gray)
    # energy = compute_energy(gray)
    # print("energy: ", energy)
    # cem = cumulative_energy_map(energy)
    # print("cumulative energy map: ", cem)
    # seam = minimum_energy_seam(cem)
    # print("seam: ", seam)
    # image = image_without_seam(image, seam)
    # print("seam carved: ", image)
    # save_color_image(image, './test_results/pattern_seam_carved.png')


    # twocats = load_color_image('./test_images/twocats.png')
    # save_color_image(seam_carving(twocats, 100), './test_results/seam_carved_two_cats.png')

    frog = load_color_image('./test_images/frog.png')
    threshold_150 = threshold(150)
    save_color_image(threshold_150(frog), './test_results/thresholded_frog.png')
