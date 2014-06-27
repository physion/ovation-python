import numpy as np
import pandas as pd

from nose.tools import istest,assert_equals
from ovation.conversion import asclass
from ovation.data import insert_tabular_measurement, datapath
from ovation.testing import TestBase
from ovation.core import DateTime


class TestDataPath(TestBase):

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
    def should_give_data_path(self):

        df = pd.DataFrame({'ColA' : np.random.randn(10),
                                 'ColB' : np.random.randn(10)})

        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)

        m = insert_tabular_measurement(epoch, set(), set(), 'tabular', df)

        while(m.getDataContext().getFileService().hasPendingUploads()):
            pass

        m = asclass('Measurement', m.refresh())

        expected = m.getLocalDataPath().get()
        actual = datapath(m)

        assert_equals(expected, actual)


