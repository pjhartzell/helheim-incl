import json
import glob
import os
import numpy as np
import pdal


def get_socs(filename):
    # Convert LAS/LAZ point cloud from UTM to SOCS system:
    #   (1) UTM to ECEF, (2) Inverse POP, (3) Inverse SOP
    #   Note: SOP is hardcoded here for ATLAS_South-201908
    root, ext = os.path.splitext(filename)
    outfilename = root + "-socs" + ext
    pdal_pipe = [
        filename,
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
        },
        outfilename
    ]
    p = pdal.Pipeline(json.dumps(pdal_pipe))
    p.validate()
    p.execute()
    arrays = p.arrays
    view = arrays[0]

    t = view['GpsTime']
    x = view['X']
    y = view['Y']
    z = view['Z']

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


def filter_incl(incl, kernel_length=101):
    # Blackman window kernel. Default kernel length based on prior work
    # published in Journal of Glaciology.
    kernel = np.blackman(kernel_length)
    kernel = kernel / np.sum(kernel)
    # Pad roll and pitch signals
    pad_width = np.int(kernel_length/2)
    padded_incl = np.pad(incl, pad_width, 'reflect')
    # Filter
    filtered_incl = np.convolve(padded_incl, kernel, mode='valid')

    return filtered_incl


def apply_incl(pt, x, y, z, it, roll, pitch):
    # Inclination time midpoints for masking
    it_mid = (it[1:] + it[:-1]) / 2

    # Rotate points according to closes inclination time
    xyz_rot = np.zeros((len(x), 3))
    for i in range(0, len(it)):
        # Mask for points closest to current inclination time
        if i == 0:
            mask = pt <= it_mid[i]
        elif i == (len(it) - 1):
            mask = pt > it_mid[i-1]
        else:
            mask = np.logical_and(pt > it_mid[i-1], pt <= it_mid[i])
        # Apply inclination rotations
        R_roll = np.array([
            [1, 0, 0],
            [0, np.cos(np.deg2rad(roll[i])), -np.sin(np.deg2rad(roll[i]))],
            [0, np.sin(np.deg2rad(roll[i])), np.cos(np.deg2rad(roll[i]))]
        ])
        R_pitch = np.array([
            [np.cos(np.deg2rad(pitch[i])), 0, np.sin(np.deg2rad(pitch[i]))],
            [0, 1, 0],
            [-np.sin(np.deg2rad(pitch[i])), 0, np.cos(np.deg2rad(pitch[i]))],
        ])
        xyz_rot[mask,0:3] = (R_pitch @ R_roll @ np.vstack((x[mask], y[mask], z[mask]))).T

    x_rot = xyz_rot[:,0]
    y_rot = xyz_rot[:,1]
    z_rot = xyz_rot[:,2]

    return x_rot, y_rot, z_rot


def save_socs(filename, t, x, y, z):
    out_type = np.dtype([('GpsTime', t.dtype), ('X', x.dtype), ('Y', y.dtype), ('Z', z.dtype)])
    out = np.empty(len(t), dtype=out_type)
    out['GpsTime'] = t
    out['X'] = x
    out['Y'] = y
    out['Z'] = z

    pdal_pipe = [
        {
            "type":"writers.las",
            "filename":filename
        }
    ]

    p = pdal.Pipeline(json=json.dumps(pdal_pipe), arrays=[out,])
    p.validate()
    p.execute()

