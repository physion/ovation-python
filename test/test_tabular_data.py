import numpy as np
import pandas as pd
from nose.tools import istest, assert_equals, assert_true

from ovation.conversion import to_map, to_set, asclass
from ovation.data import as_numeric_data_frame, insert_numeric_measurement, add_numeric_analysis_artifact, insert_tabular_measurement, as_data_frame, add_tabular_analysis_artifact
from ovation.testing import TestBase
from ovation.core import DateTime


class TestTabularData(TestBase):

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


    @istest
    def should_round_trip_pandas_data_frame(self):

        expected = pd.DataFrame({'ColA' : np.random.randn(10),
                                 'ColB' : np.random.randn(10)})

        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)

        m = insert_tabular_measurement(epoch, set(), set(), 'tabular', expected)

        while(m.getDataContext().getFileService().hasPendingUploads()):
            pass

        m = asclass('Measurement', m.refresh())

        actual = as_data_frame(m, index_col=0)

        assert_equals(expected, actual)

    @istest
    def should_round_trip_pandas_data_frame_artifact(self):
        expected = pd.DataFrame({'ColA' : np.random.randn(10),
                                 'ColB' : np.random.randn(10)})

        project = list(self.expt.getProjects())[0]
        record = project.addAnalysisRecord('name', to_map({}), None, to_map({}))

        m = add_tabular_analysis_artifact(record, 'tabular', expected)

        while(m.getDataContext().getFileService().hasPendingUploads()):
            pass

        m = asclass('Measurement', m.refresh())

        actual = as_data_frame(m, index_col=0)

        assert_equals(expected, actual)
