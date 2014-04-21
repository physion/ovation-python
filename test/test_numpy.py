import numpy as np
import quantities as pq
from nose.tools import istest, assert_equals, assert_true

from ovation.conversion import to_map
from ovation.data import as_data_frame, insert_numeric_measurement, insert_numeric_analysis_artifact
from ovation.testing import TestBase
from ovation.core import DateTime


def assert_data_frame_equals(expected, actual):
    for (key, expected_array) in expected.iteritems():
        actual_array = actual[key]
        assert_true(np.all(expected_array == actual_array))
        assert_equals(expected_array.dimensionality.string, actual_array.dimensionality.string)


class TestNumPy(TestBase):

    @classmethod
    def make_experiment_fixture(cls):
        ctx = cls.dsc.getContext()
        project = ctx.insertProject("name", "description", DateTime())
        expt = project.insertExperiment("purpose", DateTime())
        protocol = ctx.insertProtocol("protocol", "description")
        return ctx, expt, protocol

    @classmethod
    def setup_class(cls):
        TestBase.setup_class()

        cls.ctx, cls.expt, cls.protocol = cls.make_experiment_fixture()

    def setup(self):
        self.ctx = self.__class__.ctx
        self.expt = self.__class__.expt
        self.protocol = self.__class__.protocol

    @istest
    def should_round_trip_1D_floating_point(self):
        (expected,actual) = _round_trip(self.expt, self.protocol)

        assert_data_frame_equals(expected, actual)

    @istest
    def should_round_trip_labels(self):
        (expected,actual) = _round_trip(self.expt, self.protocol)

        for k in expected.keys():
            ex = expected[k]
            v = actual[k]

            assert_equals(ex.labels, v.labels)

    @istest
    def should_round_trip_sampling_rate(self):
        (expected,actual) = _round_trip(self.expt, self.protocol)

        for k in expected.keys():
            ex = expected[k]
            v = actual[k]

            assert_equals(tuple(ex.sampling_rates), v.sampling_rates)

    @istest
    def should_round_trip_units(self):
        (expected,actual) = _round_trip(self.expt, self.protocol)
        for k in expected.keys():
            ex = expected[k]
            v = actual[k]

            assert_equals(ex.units, v.units)


    @istest
    def should_round_trip_2D_floating_point(self):
       arr = np.random.randn(10,10) * pq.s
       arr.labels = [u'volts', u'other']
       arr.name = u'name'
       arr.sampling_rates = [1.0 * pq.Hz, 10.0 * pq.Hz]
       (expected, actual) = _round_trip_array(arr, self.expt, self.protocol)

       assert_data_frame_equals(expected, actual)

    @istest
    def should_round_trip_2D_floating_point_analysis_artifact(self):
        arr = np.random.randn(10,10) * pq.s
        arr.labels = [u'volts', u'other']
        arr.name = u'name'
        arr.sampling_rates = [1.0 * pq.Hz, 10.0 * pq.Hz]

        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)

        ar = epoch.addAnalysisRecord("record", to_map({}), self.protocol, to_map({}))

        result_name = 'result'
        expected = {result_name: arr}
        record_name = "record-name"
        artifact = insert_numeric_analysis_artifact(ar, record_name, expected)

        assert artifact is not None

        actual = None
        while actual is None:
            try:
                actual = as_data_frame(artifact)
            except:
                artifact.refresh()

        assert_data_frame_equals(expected, actual)

    @istest
    def should_round_trip_multi_element_data_frame(self):
        arr1 = np.random.randn(10,10) * pq.s
        arr1.labels = [u'volts', u'other']
        arr1.name = u'name'
        arr1.sampling_rates = [1.0 * pq.Hz, 10.0 * pq.Hz]

        arr2 = np.random.randn(10,10) * pq.V
        arr2.labels = [u'volts', u'other']
        arr2.name = u'name'
        arr2.sampling_rates = [1.0 * pq.Hz, 10.0 * pq.Hz]

        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)

        ar = epoch.addAnalysisRecord("record", to_map({}), self.protocol, to_map({}))

        result_name1 = 'result'
        result_name2 = 'other-result'
        expected = {result_name1: arr1,
                    result_name2: arr2}
        record_name = "record-name"
        artifact = insert_numeric_analysis_artifact(ar, record_name, expected)

        assert artifact is not None

        actual = None
        while actual is None:
            try:
                actual = as_data_frame(artifact)
            except:
                artifact.refresh()

        assert_data_frame_equals(expected, actual)
        
    @istest
    def should_allow_dimensionless_sampling_rates(self):
        arr = np.random.randn(10) * pq.s
        arr.name = u'name'
        arr.sampling_rates = [1.0 * pq.dimensionless]
        arr.labels = ['time']
        
        (expected,actual) = _round_trip_array(arr, self.expt, self.protocol)

        assert_data_frame_equals(expected, actual)

        for k in expected.keys():
            ex = expected[k]
            v = actual[k]

            assert_equals(tuple(ex.sampling_rates), v.sampling_rates)



def _round_trip_array(arr, experiment, protocol):
    epoch = experiment.insertEpoch(DateTime(), DateTime(), protocol, None, None)
    trace_name = 'trace1'
    expected = { trace_name: arr }

    sourceName = 'source'
    s = epoch.getDataContext().insertSource('source-name', 'source-id')
    epoch.addInputSource(sourceName, s)

    m = insert_numeric_measurement(epoch, set([sourceName]), set(['amp']), trace_name, expected)

    actual = None
    while actual is None:
        try:
            actual = as_data_frame(m)
        except:
            m.refresh();

    return (expected, actual)


def _round_trip(experiment, protocol):
    arr = np.random.randn(10) * pq.s
    arr.name = u'name'
    arr.sampling_rates = [1.0 * pq.Hz]
    arr.labels = ['time']

    return _round_trip_array(arr, experiment, protocol)


