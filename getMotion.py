import cv2
import os
import sys
import numpy
import warnings
import math

warnings.filterwarnings('error', category=RuntimeWarning)
# check if directory exists for extracted motion detection fields
# this is only required for inspection frame by frame of motion analysis
if not os.path.isdir(os.path.join(os.getcwd(), 'monkeyFrames')):
    os.mkdir("monkeyFrames")
else:
    print('stored motion detection will be overwritten.\n')

capture = cv2.VideoCapture('monkeyVid.mov')
if not capture.isOpened():
    print('video clip failed to open....Exiting.')
    sys.exit(1)

num_of_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
# pad size sufficiently large for expanding searh radius
# ensure dims are multiples of kernel size
pad_height = 14*14
pad_width = 12*14

# to hold coordinates for 5 body parts
# 0 = R_arm, 1 = L_arm, 2 = Torso, 3 = R_leg, 4 = L_leg
limb_coords = numpy.zeros((5, num_of_frames, 2))
# number of blocks to match per area of interest
num_blocks = 9
init_coords = numpy.zeros((5, num_blocks, 2))


def insert_padding(img, pad_h, pad_w):
    """
    This method was adapted from week 2 lab solution
    :param img: image to pad
    :return: paddded image
    """
    global frame_height, frame_width
    padding_3_dims = ((pad_h, pad_h), (pad_w, pad_w), (0, 0))
    # apply padding in the above dimensions with values 0
    padded_img = numpy.pad(img, padding_3_dims, 'constant', constant_values=0)
    return padded_img


def segment_red(img, yellow_thresh, red_thresh):
    """segments given image by given thresholds
    :param img image to process
    :param yellow_thresh max green channel value
    :param red_thresh minimum red channel value
    :return segmented image"""
    # 255 is white, Red, Green, Blue
    # where green and yellow exists strongly set to 0
    yellow_filter = (img[:, :, 1] < yellow_thresh)*numpy.ones((img.shape[0], img.shape[1]))
    # where red and yellow doesnt exist set to 0
    red_filter = (img[:, :, 2] > red_thresh)*numpy.ones((img.shape[0], img.shape[1]))
    # TAKE THE INTERSECTION of SET A and B
    total_filter = numpy.multiply(yellow_filter, red_filter)
    img[:, :, 0] = 0
    img[:, :, 1] = numpy.multiply(total_filter, img[:, :, 1])
    img[:, :, 2] = numpy.multiply(total_filter, img[:, :, 2])
    cv2.imwrite('segmented.png', img)
    return img


def remove_artifacts(img):
    """ performs cleaning on image to remove small artifacts
    :param img image to process"""
    h = 14
    w = 10
    mask = numpy.zeros((h, w, 2))
    mask[0, :, :] = 1
    mask[h-1, :, :] = 1
    mask[:, 0, :] = 1
    mask[:, w-1, :] = 1

    y = 0
    while y < frame_height - h:
        x = 0
        while x < frame_width - w:
            mask_applied = mask*img[y:y+h, x:x+w, 1:3] > 0 + numpy.zeros((h, w, 2))
            if numpy.sum(mask_applied) < (2*h-1 + 2*w-1)*0.25:
                img[y+1:y+h-1, x+1:x+w-1, 1:3] = 0
            x += 1
        y += 1


def erode(img, kernel_h, kernel_w):
    """ erodes a provided image with a kernel of specified size
    :param img image to process
    :param kernel_h height of kernel
    :param kernel_w width of kernel"""
    # kernel_w and kernel_h chosen to get 4 clear markers in first frame to set initial limb coordinates.
    """ if majority of kernel is blue, else erase"""
    y = 0
    print(frame_height)
    while y < frame_height - kernel_h:
        x = 0
        while x < frame_width - kernel_w:
            # where Red exist
            kernel = img[y:y+kernel_h, x:x+kernel_w, 2] > 0 + numpy.zeros((kernel_h, kernel_w))

            if numpy.all(kernel == 0):
                pass
            elif numpy.sum(kernel) < (kernel_w*kernel_h)*0.85:
                img[y:y+kernel_h, x:x+kernel_w, 1:3] = 0
            else:
                img[y:y+kernel_h, x:x+kernel_w, 2] = 255

            x += kernel_w
        y += kernel_h


def get_start_positions(img_in):
    """ algorithm for locating starting coordinates
    :param img_in image to process"""

    def initialize_coordinates(kernel_h, kernel_w):
        """ locates positions of interest by traversing eroded image and
        saves 9 points on each area of interest to global matrix
        :param kernel_h height of kernel used for harsh erosion
        :param kernel_w width of kernel used for harsh erosion"""
        global init_coords

        count = 0
        y = 0
        while y < frame_height - kernel_h:
            x = 0
            while x < frame_width - kernel_w:
                locator = img[y:y+kernel_h, x:x+kernel_w, 2] > 0 + numpy.zeros((kernel_h, kernel_w))
                if numpy.any(locator):
                    if count == 0:
                        init_coords[count][0][0] = y - 2
                        init_coords[count][0][1] = x + 2
                    elif count == 1:
                        init_coords[count][0][0] = y + 2
                        init_coords[count][0][1] = x + 2
                    elif count == 2:
                        init_coords[count][0][0] = y + 2
                        init_coords[count][0][1] = x + 2
                    elif count == 3:
                        init_coords[count][0][0] = y - 3
                        init_coords[count][0][1] = x + 2
                    elif count == 4:
                        init_coords[count][0][0] = y + 3
                        init_coords[count][0][1] = x - 5
                    count += 1
                    break
                x += kernel_w
            y += kernel_h

        # store 8 more points for each body part
        f = 1.5
        for count in range(5):
            init_coords[count][1][1] = init_coords[count][0][1] + 3*f
            init_coords[count][1][0] = init_coords[count][0][0] + 0
            init_coords[count][2][1] = init_coords[count][0][1] + 6*f
            init_coords[count][2][0] = init_coords[count][0][0] + 0
            init_coords[count][3][1] = init_coords[count][0][1] + 0
            init_coords[count][3][0] = init_coords[count][0][0] + 3*f
            init_coords[count][4][1] = init_coords[count][0][1] + 3*f
            init_coords[count][4][0] = init_coords[count][0][0] + 3*f
            init_coords[count][5][1] = init_coords[count][0][1] + 6*f
            init_coords[count][5][0] = init_coords[count][0][0] + 3*f
            init_coords[count][6][1] = init_coords[count][0][1] + 0
            init_coords[count][6][0] = init_coords[count][0][0] + 6*f
            init_coords[count][7][1] = init_coords[count][0][1] + 3*f
            init_coords[count][7][0] = init_coords[count][0][0] + 6*f
            init_coords[count][8][1] = init_coords[count][0][1] + 6*f
            init_coords[count][8][0] = init_coords[count][0][0] + 6*f

        limb_coords[0][0][0] = init_coords[0][5][0]
        limb_coords[0][0][1] = init_coords[0][5][1]
        limb_coords[1][0][0] = init_coords[1][5][0]
        limb_coords[1][0][1] = init_coords[1][5][1]
        limb_coords[2][0][0] = init_coords[2][5][0]
        limb_coords[2][0][1] = init_coords[2][5][1]
        limb_coords[3][0][0] = init_coords[3][5][0]
        limb_coords[3][0][1] = init_coords[3][5][1]
        limb_coords[4][0][0] = init_coords[4][5][0]
        limb_coords[4][0][1] = init_coords[4][5][1]

    img = img_in.copy()
    img = segment_red(img, 205, 135)
    erode(img, 14, 12)
    initialize_coordinates(14, 12)


def get_motion(frame1k, frame2k, frame_count):
    """ runs motion detection algorithm
    :param frame1k z
    :param frame2k z+1
    :param z"""
    frame1 = frame1k.copy()
    frame2 = frame2k.copy()

    global limb_coords, init_coords, num_blocks
    cv2.imwrite("thisImageAnalyse.png", frame2)
    block_size = 3
    block_rad = int(block_size/2)

    def get_SSD():
        """ applies SSD formula to search area
        :return SSD value"""
        dist = 0
        # traversal of pixels in potential Bi+1 block
        # compare corresponding pixel positions with source block in f1 and neighbour block in f2
        y1 = center_y1 - block_rad      # start pos.
        for y2 in range(center_y2 - block_rad, (center_y2 - block_rad + block_size)):
            x1 = center_x1 - block_rad      # start pos
            for x2 in range(center_x2 - block_rad, (center_x2 - block_rad + block_size)):
                try:
                    # displacement formula for RGB channels of each pixel in block
                    dist = dist + (frame1[y1][x1][0] - frame2[y2][x2][0])**2 + (frame1[y1][x1][1] - frame2[y2][x2][1])**2 + (frame1[y1][x1][2] - frame2[y2][x2][2])**2
                except RuntimeWarning:
                    pass
                x1 += 1
            y1 += 1
        return math.sqrt(dist)

    # for each body part
    b = 0
    while b < 5:
        avg_x = 0.0
        avg_y = 0.0
        new_x = 0.0
        new_y = 0.0
        a = 0
        # for each block on body part (9 total)
        while a < num_blocks:
            found = False
            search_rad = 5
            while found is False:
                center_y1 = int(init_coords[b][a][0])
                center_x1 = int(init_coords[b][a][1])
                min_SSD = 999999
                # for pythagoras to ensure closest block gets picked when equality occurs of SSD value
                min_d = 999999
                # this finds the center of the block to compare
                for factor_y in range(-search_rad, search_rad + 1):
                    center_y2 = center_y1 + block_size*factor_y
                    y_dist = center_y1 - abs(center_y2)
                    for factor_x in range(-search_rad, search_rad + 1):
                        center_x2 = center_x1 + block_size*factor_x
                        x_dist = center_x1 - abs(center_x2)
                        # pythagoras
                        d = math.sqrt((y_dist**2 + x_dist**2))
                        if d < min_d:
                            min_d = d

                        SSD = get_SSD()
                        if frame2[center_y2][center_x2][1] != 0 and frame2[center_y2][center_x2][2] != 0:
                            found = True
                            if SSD < min_SSD:
                                min_SSD = SSD
                                new_y = center_y2
                                new_x = center_x2
                            elif SSD == min_SSD and d < min_d:
                                new_y = center_y2
                                new_x = center_x2
                if found is False:
                    # if no block is found repeat the search, increasing the search size by 1
                    search_rad += 1
            # draw extracted vectors
            cv2.arrowedLine(frame1k, (int(center_x1), int(center_y1)), (int(new_x), int(new_y)), (150, 200, 30), 1, 4, 0, 0.3)
            avg_x += new_x
            avg_y += new_y
            init_coords[b][a][0] = new_y
            init_coords[b][a][1] = new_x
            a += 1
        cv2.imwrite('monkeyFrames/contrast_enhanced%d.png' % frame_count, frame1k)
        limb_coords[b][frame_count][0] = int(avg_y/num_blocks)
        limb_coords[b][frame_count][1] = int(avg_x/num_blocks)
        b += 1


def enhance_contrast(img):
    """ adds blue to areas high in yellow in an increasing scale
    along the x-axis. Unused for final data extraction
    :param image to process"""
    for y in range(frame_height):
        for x in range(frame_width):
            if img[y, x, 1] > 100:
                # range of blues to limit of puppet motion 255/(frame_width - 150)
                img[y][x][0] = x*0.4
            if img[y, x, 1] <= 100:
                img[y][x][2] = img[y][x][2]*0.5
    cv2.imwrite("contrasted.png", img)


def motion_extraction():
    """ algorithm to process images"""
    # iterate through frames
    global frame_height, frame_width
    global limb_coords, init_coords
    frame_count = 0
    has_frames, frame = capture.read()

    while has_frames:
        img_out = frame.copy()
        img_out = insert_padding(img_out, 14*14, 12*14)

        if frame_count == 0:
            # change global values of height and width
            frame_height = frame_height + 14*14*2
            frame_width = frame_width + 12*14*2
            get_start_positions(img_out)
        img_out2 = segment_red(img_out, 200, 130)
        #erode(img_out2, 4, 6)
        remove_artifacts(img_out2)
        #enhance_contrast(img_out2)

        if frame_count > 0:
            get_motion(prev_frame, img_out2, frame_count)

        prev_frame = img_out2.copy()
        frame_count += 1
        has_frames, frame = capture.read()


def run():
    """To be called from top level module if needed.
    runs the algorithm and stores the data points in text files."""
    motion_extraction()
    file_buff = open("right_arm.txt", "w")
    for frame_coord in limb_coords[0]:
        file_buff.write("%d %d\n" % (frame_coord[1], frame_coord[0]))
    file_buff.close()
    file_buff2 = open("left_arm.txt", "w")
    for frame_coord in limb_coords[1]:
        file_buff2.write("%d %d\n" % (frame_coord[1], frame_coord[0]))
    file_buff2.close()
    file_buff3 = open("body.txt", "w")
    for frame_coord in limb_coords[2]:
        file_buff3.write("%d %d\n" % (frame_coord[1], frame_coord[0]))
    file_buff3.close()
    file_buff4 = open("right_leg.txt", "w")
    for frame_coord in limb_coords[3]:
        file_buff4.write("%d %d\n" % (frame_coord[1], frame_coord[0]))
    file_buff4.close()
    file_buff5 = open("left_leg.txt", "w")
    for frame_coord in limb_coords[4]:
        file_buff5.write("%d %d\n" % (frame_coord[1], frame_coord[0]))
    file_buff5.close()


