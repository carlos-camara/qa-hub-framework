from behave import then, when
import os
import time
from pypdf import PdfReader

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

@when('I wait for {seconds:d} seconds for the download to complete')
def step_wait_for_download(context, seconds):
    time.sleep(seconds)

@then('the downloaded file "{filename}" should exist')
def step_verify_file_exists(context, filename):
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    found = False
    for _ in range(3):
        if os.path.exists(filepath):
            found = True
            break
        time.sleep(1)
    assert found, f"File {filename} not found in {DOWNLOADS_DIR}"
    assert os.path.getsize(filepath) > 0, f"File {filename} is empty"
    context.last_downloaded_file = filepath

@then('the PDF "{filename}" should have at least {page_count:d} pages')
def step_verify_pdf_pages(context, filename, page_count):
    filepath = getattr(context, 'last_downloaded_file', os.path.join(DOWNLOADS_DIR, filename))
    reader = PdfReader(filepath)
    actual_pages = len(reader.pages)
    assert actual_pages >= page_count, f"Expected {page_count}, found {actual_pages}"

@then('I verify the content of the first {count:d} pages of "{filename}" contains "{keyword}"')
def step_verify_pdf_content(context, count, filename, keyword):
    filepath = getattr(context, 'last_downloaded_file', os.path.join(DOWNLOADS_DIR, filename))
    reader = PdfReader(filepath)
    found = False
    for i in range(min(count, len(reader.pages))):
        text = reader.pages[i].extract_text().lower()
        if keyword.lower() in text:
            found = True
            break
    assert found, f"Keyword '{keyword}' not found in first {count} pages of {filename}"
