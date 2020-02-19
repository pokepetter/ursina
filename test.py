"""Test Ursina."""

import logging
import textwrap

_log = logging.getLogger(__name__)


def main():
    """Run ursina unit tests using pytest.

    Pytest is not a requirement, so in the event that it is not already
    installed, instruct the user on running tests in an automated fashion
    using Python's included unittest package.
    """
    try:
        import pytest
    except ImportError:
        _log.error(textwrap.dedent(f"""\
            Pytest is the preferred method of running unit tests. Please run
            the following command, then re-run {__file__}.
                python -m pip install pytest

            Otherwise, run the following command from the repository root:
                python -m unittest discover -s test
        """))
    else:
        pytest.main()


if __name__ == "__main__":
    main()
