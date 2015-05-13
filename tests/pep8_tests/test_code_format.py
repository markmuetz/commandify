from glob import glob
import pep8


class TestCodeFormat(object):
    def __init__(self):
        self.pep8style = pep8.StyleGuide()

    def _test_conformance_in_files(self, filenames):
        assert len(filenames) != 0
        for filename in filenames:
            result = self.pep8style.check_files([filename])
            assert result.total_errors == 0, "Found code style errors (and warnings)."

    def test_1_commandify_pep8_conformance(self):
        """Test that commandify module conforms to PEP8."""
        filenames = glob('../commandify/*.py')
        filenames.append('../commandify/commandify_examples')
        self._test_conformance_in_files(filenames)
