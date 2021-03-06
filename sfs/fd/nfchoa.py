"""Compute NFC-HOA driving functions.

.. include:: math-definitions.rst

.. plot::
    :context: reset

    import matplotlib.pyplot as plt
    import numpy as np
    import sfs

    plt.rcParams['figure.figsize'] = 6, 6

    xs = -1.5, 1.5, 0
    # normal vector for plane wave:
    npw = sfs.util.direction_vector(np.radians(-45))
    f = 300  # Hz
    omega = 2 * np.pi * f
    R = 1.5  # Radius of circular loudspeaker array

    grid = sfs.util.xyz_grid([-2, 2], [-2, 2], 0, spacing=0.02)

    array = sfs.array.circular(N=32, R=R)

    def plot(d, selection, secondary_source):
        p = sfs.fd.synthesize(d, selection, array, secondary_source, grid=grid)
        sfs.plot2d.amplitude(p, grid)
        sfs.plot2d.loudspeakers(array.x, array.n, selection * array.a, size=0.15)

"""
import numpy as _np
from scipy.special import hankel2 as _hankel2

from . import secondary_source_point as _secondary_source_point
from .. import util as _util


def plane_2d(omega, x0, r0, n=[0, 1, 0], *, max_order=None, c=None):
    r"""Driving function for 2-dimensional NFC-HOA for a virtual plane wave.

    Parameters
    ----------
    omega : float
        Angular frequency of plane wave.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    r0 : float
        Radius of circular secondary source distribution.
    n : (3,) array_like, optional
        Normal vector (traveling direction) of plane wave.
    max_order : float, optional
        Maximum order of circular harmonics used for the calculation.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing only ``True`` indicating that
        all secondary source are "active" for NFC-HOA.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    .. math::

        D(\phi_0, \omega) =
        -\frac{2\i}{\pi r_0}
        \sum_{m=-M}^M
        \frac{\i^{-m}}{\Hankel{2}{m}{\wc r_0}}
        \e{\i m (\phi_0 - \phi_\text{pw})}

    See :sfs:`d_nfchoa/#equation-fd-nfchoa-plane-2d`

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.nfchoa.plane_2d(
            omega, array.x, R, npw)
        plot(d, selection, secondary_source)

    """
    if max_order is None:
        max_order = _util.max_order_circular_harmonics(len(x0))

    x0 = _util.asarray_of_rows(x0)
    k = _util.wavenumber(omega, c)
    n = _util.normalize_vector(n)
    phi, _, r = _util.cart2sph(*n)
    phi0 = _util.cart2sph(*x0.T)[0]
    d = 0
    for m in range(-max_order, max_order + 1):
        d += 1j**-m / _hankel2(m, k * r0) * _np.exp(1j * m * (phi0 - phi))
    selection = _util.source_selection_all(len(x0))
    return -2j / (_np.pi*r0) * d, selection, _secondary_source_point(omega, c)


def point_25d(omega, x0, r0, xs, *, max_order=None, c=None):
    r"""Driving function for 2.5-dimensional NFC-HOA for a virtual point source.

    Parameters
    ----------
    omega : float
        Angular frequency of point source.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    r0 : float
        Radius of circular secondary source distribution.
    xs : (3,) array_like
        Position of point source.
    max_order : float, optional
        Maximum order of circular harmonics used for the calculation.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing only ``True`` indicating that
        all secondary source are "active" for NFC-HOA.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    .. math::

        D(\phi_0, \omega) =
        \frac{1}{2 \pi r_0}
        \sum_{m=-M}^M
        \frac{\hankel{2}{|m|}{\wc r}}{\hankel{2}{|m|}{\wc r_0}}
        \e{\i m (\phi_0 - \phi)}

    See :sfs:`d_nfchoa/#equation-fd-nfchoa-point-25d`

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.nfchoa.point_25d(
            omega, array.x, R, xs)
        plot(d, selection, secondary_source)

    """
    if max_order is None:
        max_order = _util.max_order_circular_harmonics(len(x0))

    x0 = _util.asarray_of_rows(x0)
    k = _util.wavenumber(omega, c)
    xs = _util.asarray_1d(xs)
    phi, _, r = _util.cart2sph(*xs)
    phi0 = _util.cart2sph(*x0.T)[0]
    hr = _util.spherical_hn2(range(0, max_order + 1), k * r)
    hr0 = _util.spherical_hn2(range(0, max_order + 1), k * r0)
    d = 0
    for m in range(-max_order, max_order + 1):
        d += hr[abs(m)] / hr0[abs(m)] * _np.exp(1j * m * (phi0 - phi))
    selection = _util.source_selection_all(len(x0))
    return d / (2 * _np.pi * r0), selection, _secondary_source_point(omega, c)


def plane_25d(omega, x0, r0, n=[0, 1, 0], *, max_order=None, c=None):
    r"""Driving function for 2.5-dimensional NFC-HOA for a virtual plane wave.

    Parameters
    ----------
    omega : float
        Angular frequency of point source.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    r0 : float
        Radius of circular secondary source distribution.
    n : (3,) array_like, optional
        Normal vector (traveling direction) of plane wave.
    max_order : float, optional
        Maximum order of circular harmonics used for the calculation.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing only ``True`` indicating that
        all secondary source are "active" for NFC-HOA.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    .. math::

        D(\phi_0, \omega) =
        \frac{2\i}{r_0}
        \sum_{m=-M}^M
        \frac{\i^{-|m|}}{\wc \hankel{2}{|m|}{\wc r_0}}
        \e{\i m (\phi_0 - \phi_\text{pw})}

    See :sfs:`d_nfchoa/#equation-fd-nfchoa-plane-25d`

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.nfchoa.plane_25d(
            omega, array.x, R, npw)
        plot(d, selection, secondary_source)

    """
    if max_order is None:
        max_order = _util.max_order_circular_harmonics(len(x0))

    x0 = _util.asarray_of_rows(x0)
    k = _util.wavenumber(omega, c)
    n = _util.normalize_vector(n)
    phi, _, r = _util.cart2sph(*n)
    phi0 = _util.cart2sph(*x0.T)[0]
    d = 0
    hn2 = _util.spherical_hn2(range(0, max_order + 1), k * r0)
    for m in range(-max_order, max_order + 1):
        d += (-1j)**abs(m) / (k * hn2[abs(m)]) * _np.exp(1j * m * (phi0 - phi))
    selection = _util.source_selection_all(len(x0))
    return 2*1j / r0 * d, selection, _secondary_source_point(omega, c)
