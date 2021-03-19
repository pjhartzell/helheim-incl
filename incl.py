import json
import numpy as np
from scipy import optimize
import pdal


def get_pnts(filename):
    pdal_pipe = [
        filename,
        {
            "type":"filters.sort",
            "dimension":"GpsTime"
        }
    ]
    p = pdal.Pipeline(json.dumps(pdal_pipe))
    p.validate()
    p.execute()
    arrays = p.arrays
    array = arrays[0]

    return array


def get_incl(filename):
    # Read in text file of RXP inclination data (time, roll, pitch)
    incl = np.loadtxt(filename, delimiter=",", skiprows=1)
    # Remove garbage
    incl = incl[incl[:,0] > 0]
    incl = incl[~np.isnan(incl[:,0])]
    # Remove duplicates
    garbage, idx = np.unique(incl[:,0], return_index=True)
    incl = incl[idx]

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
    start_pad = incl[0:pad_width]
    start_pad = np.flip(start_pad)
    start_pad = 2 * np.mean(start_pad[-10:]) - start_pad
    end_pad = incl[-pad_width:]
    end_pad = np.flip(end_pad)
    end_pad = 2 * np.mean(end_pad[0:10]) - end_pad
    padded_incl = np.hstack((start_pad, incl, end_pad))

    # Filter
    filtered_incl = np.convolve(padded_incl, kernel, mode='valid')

    return filtered_incl


def warp_cloud(pt, x, y, z, it, roll, pitch):
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
        # Apply inclination rotation
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


def save_utm(filename, array):
    pdal_pipe = [
        {
            "type":"filters.reprojection",
            "in_srs":"EPSG:7789",
            "out_srs":"EPSG:32624"
        },
        {
            "type":"writers.las",
            "filename":filename
        }
    ]
    p = pdal.Pipeline(json=json.dumps(pdal_pipe), arrays=[array,])
    p.validate()
    p.execute()


def get_phi(it, pt, x, y):
    # Near field points cause odd phi solutions
    mask = np.sqrt(x**2 + y**2) > 100
    pt = pt[mask]
    x = x[mask]
    y = y[mask]

    # Indices of closest points in time to the inclination reading times
    idx = np.searchsorted(pt, it)

    # Handle any out of bound indices on the high side
    idx[idx >= len(pt)] -= 1

    # Angle in xy plane
    phi = np.arctan2(y[idx], x[idx])

    return np.asarray(phi)


def model(phi, a, c, d):
    return a * np.sin(phi + c) + d


def fit_model(phi, incl):
    # These initial values don't seem to matter much
    a0 = 0
    c0 = 0
    d0 = 0

    params, params_cov = optimize.curve_fit(model, phi, incl, p0=[a0,c0,d0])

    return params


def remove_reg_trend_incl(phi, roll, pitch, roll_params, pitch_params):
    # Modeled registration roll and pitch at phi values
    roll_modeled = model(phi, roll_params[0], roll_params[1], roll_params[2])
    pitch_modeled = model(phi, pitch_params[0], pitch_params[1], pitch_params[2])

    # Remove modeled trend
    roll -= roll_modeled
    pitch -= pitch_modeled

    return roll, pitch


def sop_pop_cloud(x, y, z, mat_file):
    mat = np.loadtxt(mat_file, delimiter=" ")
    xyz1 = np.vstack((x, y, z, np.ones(len(x))))
    xyz_rot = (mat @ xyz1).T

    x_rot = xyz_rot[:,0]
    y_rot = xyz_rot[:,1]
    z_rot = xyz_rot[:,2]

    return x_rot, y_rot, z_rot


def save_incl(t, roll, pitch, data_dir, root, ext):
    outfilename = data_dir + "/" + root + ext
    np.savetxt(
        outfilename,
        np.column_stack((t, roll, pitch)),
        "%0.4f",
        delimiter=',',
        header="Time,Roll,Pitch"
    )


def tr_warp_adj(array, it, roll, pitch,
                msa_roll_params, msa_pitch_params,
                sop_file, pop_file, data_dir, basename):
    # Compute scan phi (horizontal) angle
    phi = get_phi(it, array["GpsTime"], array["X"], array["Y"])

    # Remove MSA registration scan inclination cyclical trends
    tr_roll, tr_pitch = remove_reg_trend_incl(phi, roll, pitch,
                                              msa_roll_params, msa_pitch_params)

    # Noise filter
    filtered_tr_roll = filter_incl(tr_roll)
    filtered_tr_pitch = filter_incl(tr_pitch)

    # Apply inclination
    xw, yw, zw = warp_cloud(
        array["GpsTime"], array["X"], array["Y"], array["Z"],
        it, filtered_tr_roll, filtered_tr_pitch
    )
    
    # Save warped points
    x, y, z = sop_pop_cloud(xw, yw, zw, sop_file)
    x, y, z = sop_pop_cloud(x, y, z, pop_file)

    array["X"] = x
    array["Y"] = y
    array["Z"] = z

    outfilename = data_dir + "/" + basename + "-msatrendrem-warped-utm.laz"
    save_utm(outfilename, array)
 
    # Save detrended and filtered detrended inclination
    ext = "-incl-msatrendrem.txt"
    save_incl(it, tr_roll, tr_pitch, data_dir, basename, ext)
    ext = "-incl-msatrendrem-filtered.txt"
    save_incl(it, filtered_tr_roll, filtered_tr_pitch, data_dir, basename, ext)


def no_adj(array, sop_file, pop_file, data_dir, basename):
    # Save points in UTM
    x, y, z = sop_pop_cloud(array["X"], array["Y"], array["Z"], sop_file)
    x, y, z = sop_pop_cloud(x, y, z, pop_file)

    array["X"] = x
    array["Y"] = y
    array["Z"] = z

    outfilename = data_dir + "/" + basename + "-utm.laz"
    save_utm(outfilename, array)
