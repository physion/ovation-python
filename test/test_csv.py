import numpy as np
import pandas as pd
from nose.tools import istest, assert_equals, assert_true

from ovation.conversion import to_map, asclass
from ovation.data import insert_tabular_measurement
from ovation.testing import TestBase
from ovation.core import DateTime


class TestCsv(TestBase):

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
    def should_round_trip_data_frame(self):
        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)

        df = pd.DataFrame({'col1': np.random.rand(10), 'col2': np.random.rand(10)})

        source_name = 'source'
        s = epoch.getDataContext().insertSource('source-name', 'source-id')
        epoch.addInputSource(source_name, s)

        name = 'data_name'
        m = insert_tabular_measurement(epoch, {source_name}, {'amp'}, name, df)

        actual = None
        while actual is None:
            m = asclass('Measurement', m.refresh())
            try:
                actual = pd.read_csv(m.getLocalDataPath().get(), index_col=0)
            except Exception as e:
                pass

        assert_true(((actual-df) < .001).all().all(), msg="Approximately equal")