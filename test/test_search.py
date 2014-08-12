from nose.tools import istest
from ovation.core import DateTime
from ovation.search import search
from ovation.testing import TestBase

UNUSED_STRING = "UNUSED"


class TestSearch(TestBase):

    @istest
    def should_run_search(self):
        ctx = self.get_dsc().getContext()
        project = ctx.insertProject(UNUSED_STRING, UNUSED_STRING, DateTime())
        experiment = project.insertExperiment(UNUSED_STRING, DateTime())

        tag = 'tag'
        project.addTag(tag)
        experiment.addTag(tag)

        actual = list(search(ctx, "tag:" + '"tag"'))

        actual_uris = [e.getURI().toString() for e in actual]

        self.assertItemsEqual(actual_uris, (project.getURI().toString(), experiment.getURI().toString()))

