"""Compute SDM driving functions.

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

    grid = sfs.util.xyz_grid([-2, 2], [-2, 2], 0, spacing=0.02)

    array = sfs.array.linear(32, 0.2, orientation=[0, -1, 0])

    def plot(d, selection, secondary_source):
        p = sfs.fd.synthesize(d, selection, array, secondary_source, grid=grid)
        sfs.plot2d.amplitude(p, grid)
        sfs.plot2d.loudspeakers(array.x, array.n, selection * array.a, size=0.15)

"""
import numpy as _np
from scipy.special import hankel2 as _hankel2

from . import secondary_source_line as _secondary_source_line
from . import secondary_source_point as _secondary_source_point
from .. import util as _util


def line_2d(omega, x0, n0, xs, *, c=None):
    r"""Driving function for 2-dimensional SDM for a virtual line source.

    Parameters
    ----------
    omega : float
        Angular frequency of line source.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    n0 : (N, 3) array_like
        Sequence of normal vectors of secondary sources.
    xs : (3,) array_like
        Position of line source.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing ``True`` or ``False`` depending on
        whether the corresponding secondary source is "active" or not.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    The secondary sources have to be located on the x-axis (y0=0).
    Derived from :cite:`Spors2009`, Eq.(9), Eq.(4).

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.sdm.line_2d(
            omega, array.x, array.n, xs)
        plot(d, selection, secondary_source)

    """
    x0 = _util.asarray_of_rows(x0)
    n0 = _util.asarray_of_rows(n0)
    xs = _util.asarray_1d(xs)
    k = _util.wavenumber(omega, c)
    ds = x0 - xs
    r = _np.linalg.norm(ds, axis=1)
    d = - 1j/2 * k * xs[1] / r * _hankel2(1, k * r)
    selection = _util.source_selection_all(len(x0))
    return d, selection, _secondary_source_line(omega, c)


def plane_2d(omega, x0, n0, n=[0, 1, 0], *, c=None):
    r"""Driving function for 2-dimensional SDM for a virtual plane wave.

    Parameters
    ----------
    omega : float
        Angular frequency of plane wave.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    n0 : (N, 3) array_like
        Sequence of normal vectors of secondary sources.
    n: (3,) array_like, optional
        Normal vector (traveling direction) of plane wave.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing ``True`` or ``False`` depending on
        whether the corresponding secondary source is "active" or not.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    The secondary sources have to be located on the x-axis (y0=0).
    Derived from :cite:`Ahrens2012`, Eq.(3.73), Eq.(C.5), Eq.(C.11):

    .. math::

        D(\x_0,k) = k_\text{pw,y} \e{-\i k_\text{pw,x} x}

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.sdm.plane_2d(
            omega, array.x, array.n, npw)
        plot(d, selection, secondary_source)

    """
    x0 = _util.asarray_of_rows(x0)
    n0 = _util.asarray_of_rows(n0)
    n = _util.normalize_vector(n)
    k = _util.wavenumber(omega, c)
    d = k * n[1] * _np.exp(-1j * k * n[0] * x0[:, 0])
    selection = _util.source_selection_all(len(x0))
    return d, selection, _secondary_source_line(omega, c)


def plane_25d(omega, x0, n0, n=[0, 1, 0], *, xref=[0, 0, 0], c=None):
    r"""Driving function for 2.5-dimensional SDM for a virtual plane wave.

    Parameters
    ----------
    omega : float
        Angular frequency of plane wave.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    n0 : (N, 3) array_like
        Sequence of normal vectors of secondary sources.
    n: (3,) array_like, optional
        Normal vector (traveling direction) of plane wave.
    xref : (3,) array_like, optional
        Reference point for synthesized sound field.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing ``True`` or ``False`` depending on
        whether the corresponding secondary source is "active" or not.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    The secondary sources have to be located on the x-axis (y0=0).
    Eq.(3.79) from :cite:`Ahrens2012`.

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.sdm.plane_25d(
            omega, array.x, array.n, npw, xref=[0, -1, 0])
        plot(d, selection, secondary_source)

    """
    x0 = _util.asarray_of_rows(x0)
    n0 = _util.asarray_of_rows(n0)
    n = _util.normalize_vector(n)
    xref = _util.asarray_1d(xref)
    k = _util.wavenumber(omega, c)
    d = 4j * _np.exp(-1j*k*n[1]*xref[1]) / _hankel2(0, k*n[1]*xref[1]) * \
        _np.exp(-1j*k*n[0]*x0[:, 0])
    selection = _util.source_selection_all(len(x0))
    return d, selection, _secondary_source_point(omega, c)


def point_25d(omega, x0, n0, xs, *, xref=[0, 0, 0], c=None):
    r"""Driving function for 2.5-dimensional SDM for a virtual point source.

    Parameters
    ----------
    omega : float
        Angular frequency of point source.
    x0 : (N, 3) array_like
        Sequence of secondary source positions.
    n0 : (N, 3) array_like
        Sequence of normal vectors of secondary sources.
    xs: (3,) array_like
        Position of virtual point source.
    xref : (3,) array_like, optional
        Reference point for synthesized sound field.
    c : float, optional
        Speed of sound.

    Returns
    -------
    d : (N,) numpy.ndarray
        Complex weights of secondary sources.
    selection : (N,) numpy.ndarray
        Boolean array containing ``True`` or ``False`` depending on
        whether the corresponding secondary source is "active" or not.
    secondary_source_function : callable
        A function that can be used to create the sound field of a
        single secondary source.  See `sfs.fd.synthesize()`.

    Notes
    -----
    The secondary sources have to be located on the x-axis (y0=0).
    Driving function from :cite:`Spors2010`, Eq.(24).

    Examples
    --------
    .. plot::
        :context: close-figs

        d, selection, secondary_source = sfs.fd.sdm.point_25d(
            omega, array.x, array.n, xs, xref=[0, -1, 0])
        plot(d, selection, secondary_source)

    """
    x0 = _util.asarray_of_rows(x0)
    n0 = _util.asarray_of_rows(n0)
    xs = _util.asarray_1d(xs)
    xref = _util.asarray_1d(xref)
    k = _util.wavenumber(omega, c)
    ds = x0 - xs
    r = _np.linalg.norm(ds, axis=1)
    d = 1/2 * 1j * k * _np.sqrt(xref[1] / (xref[1] - xs[1])) * \
        xs[1] / r * _hankel2(1, k * r)
    selection = _util.source_selection_all(len(x0))
    return d, selection, _secondary_source_point(omega, c)
