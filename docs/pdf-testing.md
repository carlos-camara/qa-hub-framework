<div align="center">
  <h1>📄 Intelligent PDF Audit</h1>
  <p><i>Automated integrity and content validation for mission-critical documents.</i></p>
</div>

---

Specialized testing for generated reports and downloaded documents. The framework includes steps to verify the integrity and content of PDF files.

## 📥 Handling Downloads

Before verifying a PDF, you must ensure it has been fully downloaded to the system.

```gherkin
When I wait for 5 seconds for the download to complete
Then the downloaded file "executive-summary.pdf" should exist
```

## 🔍 Document Verification

### Structure Check
Verify that the document contains at least the expected number of pages:
```gherkin
Then the PDF "executive-summary.pdf" should have at least 2 pages
```

### Content Validation
Verify that specific keywords exist within the document text. This step automatically extracts text from the PDF pages.

```gherkin
Then I verify the content of the first 2 pages of "executive-summary.pdf" contains "QA HUB"
```

!!! warning "Search Sensitivity"
    PDF text extraction can be sensitive to layout. Always use simple, unique keywords for verification to avoid brittle tests.
