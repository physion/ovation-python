from nose.tools import istest, assert_equals
from ovation.testing import TestBase

from ovation.core import DateTime
from ovation.conversion import asclass

class TestCast(TestBase):

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
    def should_cast_experiment_from_procedure_element(self):
        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)
        assert_equals(self.expt.getUuid().toString(),
                      asclass("Experiment", epoch.getParent()).getUuid().toString())

    @istest
    def should_cast_experiment_from_procedure_element_via_explicit_cast(self):
        epoch = self.expt.insertEpoch(DateTime(), DateTime(), self.protocol, None, None)
        assert_equals(self.expt.getUuid().toString(),
                      asclass("us.physion.ovation.domain.Experiment", epoch.getParent()).getUuid().toString())

    @istest
    def should_cast_none(self):
        assert_equals(None, asclass("Experiment", None))
