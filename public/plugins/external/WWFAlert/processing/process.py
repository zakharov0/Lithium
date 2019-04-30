# process.py <inputFile> <xmin> <xmax> <ymin> <ymax> <dateBase> <outputFile>

import sys
import os
from datetime import datetime,timedelta

from scipy import ndimage
from scipy import misc
import numpy as np

# import matplotlib.pyplot as plt

MIN_SIZE = 10
SECONDS_IN_DAY = 24*3600

img = misc.imread(sys.argv[1])

xmin = float(sys.argv[2])
xmax = float(sys.argv[3])
ymin = float(sys.argv[4])
ymax = float(sys.argv[5])

dateBase = datetime.utcfromtimestamp(float(sys.argv[6]))

xstep = (xmax - xmin)/img.shape[0]
ystep = (ymax - ymin)/img.shape[1]

needHeader = not os.path.isfile(sys.argv[7])

outFile = open(sys.argv[7], "a+")

if needHeader:
    outFile.write('Lat;Lng;Size;Date\n')

dateImg = img[:, :, 0].astype(np.uint16) + ((img[:, :, 1]&0xf).astype(np.uint16) << 8) # extract date information

print 'Date plane size', dateImg.shape

s = [[1,1,1],
     [1,1,1],
     [1,1,1]]

dateHist = ndimage.measurements.histogram(dateImg, 0, 400, 401);
for d in range(1, len(dateHist)):
    if dateHist[d] > 0:
        mask = dateImg == d
        label_im, nb_labels = ndimage.label(mask, structure=s)
        print d, nb_labels

        # filter out small elements
        sizes = ndimage.sum(mask, label_im, range(1, nb_labels + 1))
        centroids = ndimage.measurements.center_of_mass(mask, label_im, range(1, nb_labels + 1))

        for p in range(len(centroids)):
            if sizes[p] >= MIN_SIZE:
                outFile.write('{0};{1};{2:.0f};{3}\n'.format(
                    ymax - centroids[p][0]*ystep, 
                    xmin + centroids[p][1]*xstep, 
                    sizes[p], 
                    (dateBase + timedelta(d-1)).strftime('%Y.%m.%d')
                ))

outFile.close()

# plt.imshow(img)
# imgplot = plt.imshow(label_im, cmap=plt.cm.spectral)
# imgplot = plt.imshow(mask)
# imgplot.set_interpolation('nearest')
# plt.show()