import pytest
import os
from intern_hunter.core.resume_tailor import ResumeTailor

def test_resume_tailor_read_master():
    tailor = ResumeTailor()
    # It should not crash even if files are missing in test env
    content = tailor._read_master_resume()
    assert isinstance(content, str)
