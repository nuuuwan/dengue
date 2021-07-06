"""Uploaded data to nuuuwan/dengue:data branch."""

from dengue import epid


def upload_data():
    """Upload data."""
    epid._scrape_and_dump()


if __name__ == '__main__':
    upload_data()
