import json
import os
import numpy as np
import pdal
import matplotlib.pyplot as plt


def get_socs(filename):
    # Convert LAS/LAZ point cloud from UTM to SOCS system:
    #   (1) UTM to ECEF, (2) Inverse POP, (3) Inverse SOP
    #   Note: SOP is hardcoded here for ATLAS_South-201908

    root, ext = os.path.splitext(filename)
    outfilename = root + "-SOCS" + ext

    pdal_pipe = [
        "{}".format(filename),
        {
            "type":"filters.reprojection",
            "in_srs":"EPSG:32624",
            "out_srs":"EPSG:7789"
        },
        {
            "type":"filters.transformation",
            "matrix":"0.61830666 -0.720011854 0.315086978 2015337.3934507162 0.78593694 0.566442551 -0.247882962 -1585491.7479251158 0.0 0.400906182 0.916119115 5820390.8039255987 0.0 0.0 0.0 1.0",
            "invert":"true"
        },
        {
            "type":"filters.transformation",
            "matrix":"0.4560212389547335 -0.8899688924677321 -0.0000078707114301 830.9795317677513 0.8899669318671532 0.4560202157410177 0.0021030973542710 -3931.5277531064141 -0.0018681020196080 -0.0009660617340401 0.9999977884573395 512.8759432302256 0.0 0.0 0.0 1.0",
            "invert":"true"
        }
    ]
    p = pdal.Pipeline(json.dumps(pdal_pipe))
    p.validate()
    p.execute()
    arrays = p.arrays
    view = arrays[0]

    t = view('GpsTime')
    x = view['X']
    y = view['y']
    z = view['z']

    return t, x, y, z


def get_incl(filename):
    # Read in text file of RXP inclination data (time, roll, pitch)
    incl = np.loadtxt(filename, delimiter=",", skiprows=1)
    # Remove garbage
    incl = incl[incl[:,0] > 0]
    incl = incl[~np.isnan(incl[:,0])]
    t = incl[:,0]
    roll = incl[:,1]
    pitch = incl[:,2]
    return t, roll, pitch


def filter_incl(incl, kernel_length=101)
    # Blackman window kernel
    kernel = np.blackman(kernel_length)
    kernel = kernel / np.sum(kernel)
    # Pad roll and pitch signals
    pad_width = np.int(kernel_length/2)
    padded_incl = np.pad(incl, pad_width, 'reflect')
    # Filter
    filtered_incl = np.convolve(padded_incl, kernel, mode='valid')

    return filtered_incl


def apply_incl(pt, x, y, z, it, roll, pitch):
    




pnts_filename = "/mnt/e/ATLAS/south_200501-200515/laz/200501_072310.laz"
incl_filename = "/mnt/e/ATLAS/south_200501-200515/rxp/mta/200501_072310-incl.txt"

pt, x, y, z = get_socs(pnts_filename)
it, roll, pitch = get_incl(incl_filename)

filt_roll = filtered_incl(roll, 101)
filt_pitch = filtered_incl(pitch, 101)



