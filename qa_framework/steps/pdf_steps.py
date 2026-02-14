from behave import then, when
import os
import time
from pypdf import PdfReader

from qa_framework.utils.driver import get_downloads_dir

DOWNLOADS_DIR = get_downloads_dir()

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
def step_verify_pdf_content_keyword(context, count, filename, keyword):
    filepath = getattr(context, 'last_downloaded_file', os.path.join(DOWNLOADS_DIR, filename))
    reader = PdfReader(filepath)
    found = False
    for i in range(min(count, len(reader.pages))):
        text = reader.pages[i].extract_text().lower()
        if keyword.lower() in text:
            found = True
            break
    assert found, f"Keyword '{keyword}' not found in first {count} pages of {filename}"

@then('I verify the content of the first {page_count:d} pages of "{filename}"')
def step_verify_pdf_content_non_empty(context, page_count, filename):
    """Verify that the first N pages of the PDF are not empty."""
    filepath = getattr(context, 'last_downloaded_file', os.path.join(DOWNLOADS_DIR, filename))
    
    # Simple wait for file if not already in context
    if not os.path.exists(filepath):
        for _ in range(5):
            if os.path.exists(filepath):
                break
            time.sleep(1)
            
    assert os.path.exists(filepath), f"File {filename} not found in {DOWNLOADS_DIR}"
    
    reader = PdfReader(filepath)
    actual_pages = len(reader.pages)
    assert actual_pages >= page_count, f"PDF has {actual_pages} pages, expected at least {page_count}"
    
    for i in range(page_count):
        page_text = reader.pages[i].extract_text()
        assert page_text.strip(), f"Page {i+1} of {filename} is empty or could not be read."


@then('a downloaded file with prefix "{prefix}" and timestamp format "{fmt}" should exist')
def step_verify_downloaded_file_with_timestamp(context, prefix, fmt):
    """
    Verify existence of a downloaded file with a specific prefix and timestamp format.
    Checks both local and UTC time.
    
    Example:
        Then a downloaded file with prefix "REPORT_" and timestamp format "%Y-%m-%d" should exist
    """
    from datetime import datetime
    import shutil
    
    local_ts = datetime.now().strftime(fmt)
    utc_ts = datetime.utcnow().strftime(fmt)
    
    possible_filenames = [
        f"{prefix}{local_ts}.pdf", # Assumes .pdf default for now, could be parameterized
        f"{prefix}{utc_ts}.pdf",
        f"{prefix}{local_ts}.csv",
        f"{prefix}{utc_ts}.csv"
    ]
    
    downloads_dir = DOWNLOADS_DIR
    system_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    filepath = None
    
    # Wait loop
    for _ in range(30):
        for filename in possible_filenames:
            # Check project dir
            temp_path = os.path.join(downloads_dir, filename)
            if os.path.exists(temp_path):
                filepath = temp_path
                break
                
            # Check system dir
            sys_path = os.path.join(system_downloads, filename)
            if os.path.exists(sys_path):
                # Auto-move
                try:
                    if not os.path.exists(downloads_dir):
                        os.makedirs(downloads_dir)
                    shutil.move(sys_path, temp_path)
                    filepath = temp_path
                except Exception:
                    filepath = sys_path
                break
        
        if filepath:
            break
        time.sleep(1)
        
    assert filepath, f"File with prefix '{prefix}' and format '{fmt}' not found in downloads."
    context.last_downloaded_file = filepath
