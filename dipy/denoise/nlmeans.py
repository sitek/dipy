from __future__ import division, print_function

import numpy as np
from dipy.denoise.denspeed import nlmeans_3d
from dipy.denoise.nlmeans_block import nlmeans_block
from dipy.denoise.noise_estimate import estimate_sigma


def nlmeans(arr, sigma, mask=None, patch_radius=1, block_radius=5,
            rician=True, num_threads=None,type='voxelwise'):

    """ Non-local means for denoising 3D and 4D images

    Parameters
    ----------
    arr : 3D or 4D ndarray
        The array to be denoised
    mask : 3D ndarray
    sigma : float or 3D array
        standard deviation of the noise estimated from the data
    patch_radius : int
        patch size is ``2 x patch_radius + 1``. Default is 1.
    block_radius : int
        block size is ``2 x block_radius + 1``. Default is 5.
    rician : boolean
        If True the noise is estimated as Rician, otherwise Gaussian noise
        is assumed.
    num_threads : int
        Number of threads. If None (default) then all available threads
        will be used (all CPU cores).
    type : string
        Denotes the type of nlmeans approach followed, we have two options
        the 'voxelwise' averaging which is the default and the 'blockwise'
        averaging.

    Returns
    -------
    denoised_arr : ndarray
        the denoised ``arr`` which has the same shape as ``arr``.
    """

    if arr.ndim == 3:

        if type == 'blockwise':
            sigma = estimate_sigma(arr, N=4)
            return np.array(nlmeans_block(np.double(arr), patch_radius, block_radius, sigma[0], rician))
        else:    
            sigma = np.ones(arr.shape, dtype=np.float64) * sigma
            return nlmeans_3d(arr, mask, sigma,
                          patch_radius, block_radius,
                          rician, num_threads).astype(arr.dtype)


    elif arr.ndim == 4:
        denoised_arr = np.zeros_like(arr)
        if type == 'blockwise':
            for i in range(arr.shape[-1]):
                sigma = estimate_sigma(arr[..., i], N=4)
                denoised_arr[..., i] = np.array(nlmeans_block(np.double(arr[..., i]),patch_radius,block_radius,sigma[0]))

            return denoised_arr    
        else:
            if isinstance(sigma, np.ndarray) and sigma.ndim == 3:
                sigma = (np.ones(arr.shape, dtype=np.float64) *
                         sigma[..., np.newaxis])
            else:
                sigma = np.ones(arr.shape, dtype=np.float64) * sigma

            for i in range(arr.shape[-1]):
                denoised_arr[..., i] = nlmeans_3d(arr[..., i],
                                                  mask,
                                                  sigma[..., i],
                                                  patch_radius,
                                                  block_radius,
                                                  rician,
                                                  num_threads).astype(arr.dtype)

            return denoised_arr

    else:
        raise ValueError("Only 3D or 4D array are supported!", arr.shape)