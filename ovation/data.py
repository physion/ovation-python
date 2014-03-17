from contextlib import contextmanager
import json
import tempfile
import quantities as pq

from scipy.io import netcdf

from ovation.conversion import to_java_set
from ovation.core import NumericDataElements, File

__author__ = 'barry'
__copyright__= 'Copyright (c) 2013. Physion Consulting. All rights reserved.'


def as_data_frame(numeric_data_element):
    """Converts a numeric Ovation numeric `DataElement` to a dictionary of `Quantities` (NumPy) arrays.
    This dictionary can be used to create a Pandas `DataFrame`, though as of Pandas 0.11.0, Quantities' units
    information will be lost.

    Parameters
    ----------
    numeric_data_element : us.physion.ovation.domain.mixin.DataElement
        Numeric `DataElement` instance to convert to a dictionary of`quantities` arrays

    Returns
    -------
    data_frame : dict
        Dict of `Quantity` arrays with additional dimension `labels`, `sampling_rates` properties
    """

    if not NumericDataElements.isNumeric(numeric_data_element):
        raise NumericMeasurementException("Attempted to convert a non-numeric measurement to a data frame")

    data_path = numeric_data_element.getLocalDataPath().get()
    numeric_data = NumericDataElements.getNumericData(numeric_data_element).get()

    with _netcdf_file_context(data_path, 'r') as ncf:
        result = {}

        #data_elements = to_dict(numeric_data.getData())
        for k in numeric_data.getData().keySet().toArray(): #(name,element) in data_elements.iteritems():
            element = numeric_data.getData().get(k)

            units = pq.Quantity(1, element.units)
            sampling_rates = element.samplingRates
            sampling_rate_units = element.samplingRateUnits
            dimension_labels = element.dimensionLabels

            # NetCDF/Java replaces ' ' with '_' when naming varibles. scipy.io.netcdf seems to remove them
            arr = ncf.variables[element.name.replace('_', ' ')].data * units

            arr.sampling_rates = tuple(pq.Quantity(rate, unit) for (rate, unit) in zip(sampling_rates, sampling_rate_units))

            arr.labels = dimension_labels

            result[k] = arr

        return result


@contextmanager
def _netcdf_file_context(path, mode='r', mmap=None, version=1):
    ncf = netcdf.netcdf_file(path, mode=mode, mmap=mmap, version=version)
    yield ncf

    ncf.close()


class NumericMeasurementException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def insert_numeric_analysis_artifact(analysis_record, name, data_frame):
    """Inserts a `dict` of Quantities (NumPy) arrays as a numeric output on the given `AnalysisRecord`

    Parameters
    ----------
    analysis_record : us.physion.ovation.domain.AnalysisRecord
    name : string
        Output name
    data_frame : dict of pq.Quantity
        Quantity (NumPy) array with `labels` and `sampling_rate` properties

    Returns
    -------
    output : us.physion.ovation.domain.mixin.DataElement
         Numeric `Measurement` instance containing the given data frame
    """

    tmp = _make_temp_numeric_file(data_frame, name)

    return analysis_record.addOutput(name,
                                     File(tmp.name).toURI().toURL(),
                                     NumericDataElements.NUMERIC_MEASUREMENT_CONTENT_TYPE)


def _make_temp_numeric_file(data_frame, name):
    tmp = tempfile.NamedTemporaryFile(
        prefix=name,
        suffix=".nc",
        delete=False)
    with _netcdf_file_context(tmp.name, 'w') as ncf:
        for array_name, arr in data_frame.iteritems():
            _create_variable(ncf,
                             array_name,
                             arr,
                             arr.labels,
                             units=arr.dimensionality.string,
                             samplingRates=[r.item() for r in arr.sampling_rates],
                             samplingRateUnits=json.dumps([r.dimensionality.string for r in arr.sampling_rates]))
    return tmp


def insert_numeric_measurement(epoch, sources, devices, name, data_frame):
    """Inserts a `dict` of Quantities (NumPy) arrays as a numeric `Measurement` on the given `Epoch`

    Parameters
    ----------
    epoch : us.physion.ovation.domain.Epoch
    sources : set
        `Source` names in the `Epoch`
    devices : set
        Device names in the `Epoch's` containing experiment
    name : string
        `Measurement` name
    data_frame : dict of pq.Quantity
        Quantity (NumPy) array with `labels` and `sampling_rate` properties

    Returns
    -------
    measurement : us.physion.ovation.domain.Measurement
         Numeric `Measurement` instance containing the given data frame
    """

    tmp = _make_temp_numeric_file(data_frame, name)

    return epoch.insertMeasurement(name,
                                   to_java_set(sources),
                                   to_java_set(devices),
                                   File(tmp.name).toURI().toURL(),
                                   NumericDataElements.NUMERIC_MEASUREMENT_CONTENT_TYPE)


def variable_dimension_name(dim, name):
    return name + "_" + dim


def _create_variable(ncf, name, data, dimensions, **attributes):
    for (sz,dim) in zip(data.shape, dimensions):
        if not dim in ncf.dimensions:
            ncf.createDimension(variable_dimension_name(dim, name), sz)

    shape = tuple([ncf.dimensions[variable_dimension_name(dim, name)] for dim in dimensions])

    typecode, size = data.dtype.char, data.dtype.itemsize
    if (typecode, size) not in netcdf.REVERSE:
        raise ValueError("NetCDF 3 does not support type {}".format(data.dtype))

    if data.dtype == data.dtype.newbyteorder('B'): #Always big-endian for NetCDF
        data_array = data
    else:
        data_array = data.byteswap()

    ncf.variables[name] = netcdf.netcdf_variable(data_array,
                                                 typecode,
                                                 size,
                                                 shape,
                                                 [variable_dimension_name(dim,name) for dim in dimensions],
                                                 attributes=attributes)
    return ncf.variables[name]
