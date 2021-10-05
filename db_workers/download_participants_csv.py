# headless version of https://github.com/ftnext/connpass-ops-playbook/blob/main/examples/download_participants_csv.py

import argparse
import os

from connpass_ops_playbook.decorators import logged_in, using_firefox
from connpass_ops_playbook.playbooks import download_latest_participants_csv
from helium import kill_browser
from selenium.webdriver import FirefoxOptions

options = FirefoxOptions()
options.set_preference("intl.accept_languages", "ja")
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", os.getcwd())
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")


@using_firefox(options=options, headless=True)
@logged_in
def download(url):
    download_latest_participants_csv(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    download(args.url)

    print(f"CSV download from {args.url} done.")

    kill_browser()
