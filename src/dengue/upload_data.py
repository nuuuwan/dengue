"""Uploaded data to nuuuwan/dengue:data branch."""

import os


def upload_data():
    """Upload data."""
    os.system('echo "test data" > /tmp/dengue.test.txt')
    os.system('echo "# dengue" > /tmp/README.md')


if __name__ == '__main__':
    upload_data()
