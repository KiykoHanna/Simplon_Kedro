from pathlib import Path

from kedro.framework.startup import bootstrap_project
from kedro.framework.project import pipelines


def test_data_processing_pipeline_registered():
    bootstrap_project(Path.cwd())

    assert "data_processing" in pipelines
    assert len(pipelines["data_processing"].nodes) == 3
