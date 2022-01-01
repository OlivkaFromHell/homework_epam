import pytest

from hw3.task02 import calculate_0_500


@pytest.mark.skip
def test_executing_time():
    result = calculate_0_500()
    assert result['time'] < 60
