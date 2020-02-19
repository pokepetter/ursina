"""Test Ursina."""


def main():
    try:
        import pytest
    except ImportError:
        err = lambda msg: print(f"Error: {msg}")
        err("You need to install pytest! O:")
    else:
        pytest.main()


if __name__ == "__main__":
    main()
