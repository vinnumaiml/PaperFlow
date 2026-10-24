import { test, expect } from "@playwright/test";

test.describe("PaperFlow End-to-End Suite", () => {
  test("Homepage loads with correct visual hierarchy and sections", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");

    // 1. Navigation Header
    await expect(page.locator("header")).toBeVisible();
    await expect(page.locator("header")).toContainText("PaperFlow");
    await expect(page.locator("header")).toContainText("PDF Studio");

    // 2. Hero Section
    const heroHeadline = page.locator("h1");
    await expect(heroHeadline).toContainText("Everything you need to work with PDFs.");

    // 3. Popular Tools (8 high-frequency tools)
    const popularSection = page.locator("section:has-text('Popular Tools')");
    await expect(popularSection).toBeVisible();
    await expect(popularSection).toContainText("Merge PDF");
    await expect(popularSection).toContainText("Compress PDF");
    await expect(popularSection).toContainText("Split PDF");
    await expect(popularSection).toContainText("PDF to Word");
    await expect(popularSection).toContainText("Word to PDF");
    await expect(popularSection).toContainText("JPG to PDF");
    await expect(popularSection).toContainText("Organize PDF");
    await expect(popularSection).toContainText("Sign PDF");

    // 4. Browse by Task
    const browseSection = page.locator("section:has-text('Browse by Task')");
    await expect(browseSection).toBeVisible();
    await expect(browseSection).toContainText("Organize PDF");
    await expect(browseSection).toContainText("Compress, Repair and OCR");
    await expect(browseSection).toContainText("Convert PDF");
    await expect(browseSection).toContainText("Edit PDF");
    await expect(browseSection).toContainText("Secure and Sign");
    await expect(browseSection).toContainText("Extract and Understand");

    // 5. Security Explainer
    const securitySection = page.locator("section:has-text('Security & Data Protection Architecture')");
    await expect(securitySection).toBeVisible();

    // 6. Footer
    const footer = page.locator("footer");
    await expect(footer).toBeVisible();
    await expect(footer).toContainText("PaperFlow");
  });

  test("Homepage live search filters tools and navigates", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    const searchInput = page.locator("input[placeholder*='Search all 40 PDF tools']");
    await expect(searchInput).toBeVisible();
    await searchInput.fill("compress");

    // Wait for search dropdown results
    const resultItem = page.locator("a:has-text('Compress PDF')").first();
    await expect(resultItem).toBeVisible();
    await resultItem.click();

    await expect(page).toHaveURL(/\/tools\/compress-pdf/);
    await expect(page.locator("h1:has-text('Compress PDF')")).toBeVisible();
  });

  test("All Tools discovery page (/tools) displays 40 tools and category filters", async ({ page }) => {
    await page.goto("/tools");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    // Header count
    await expect(page.locator("h1")).toContainText("All PDF & Document Tools");
    await expect(page.locator("body")).toContainText("Showing 40 of 40 tools");

    // Category filter pills
    const allCategoriesBtn = page.locator("button:has-text('All Categories')");
    await expect(allCategoriesBtn).toBeVisible();

    // Filter by 'Edit PDF'
    const editFilterBtn = page.locator("button:has-text('Edit PDF')").first();
    await editFilterBtn.click();
    await expect(page.locator("body")).toContainText("Showing 8 of 40 tools");

    // Filter by search text
    const searchInput = page.locator("input[placeholder*='Search tools']");
    await searchInput.fill("metadata");
    await expect(page.locator("h3:has-text('PDF Metadata Editor')")).toBeVisible();
    await expect(page.locator("body")).toContainText("Showing 1 of 40 tools");

    // Reset filter
    await allCategoriesBtn.click();
    await searchInput.fill("");
    await expect(page.locator("body")).toContainText("Showing 40 of 40 tools");
  });

  test("New tool: Resize PDF settings and controls", async ({ page }) => {
    await page.goto("/tools/resize-pdf");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    await expect(page.locator("h1")).toContainText("Resize PDF Pages");
    await expect(page.locator("text=Page Geometry & Sizing Options")).toBeVisible();

    // Select standard size
    const sizeSelect = page.locator("select");
    await expect(sizeSelect).toBeVisible();
    await sizeSelect.selectOption("Letter");
    await expect(sizeSelect).toHaveValue("Letter");

    // Orientation toggle
    const landscapeBtn = page.locator("button:has-text('Landscape')");
    await landscapeBtn.click();
    await expect(landscapeBtn).toHaveClass(/border-\[#5146D8\]/);

    // Margins input
    const marginInput = page.locator("input[type='number']");
    await marginInput.fill("15");
    await expect(marginInput).toHaveValue("15");
  });

  test("New tool: PDF Metadata Viewer & Editor settings", async ({ page }) => {
    await page.goto("/tools/pdf-metadata");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    await expect(page.locator("h1")).toContainText("PDF Metadata Editor");
    await expect(page.locator("text=Document Metadata Properties")).toBeVisible();

    const titleInput = page.locator("input[placeholder*='Annual Financial Statement']");
    await titleInput.fill("Q4 2026 Audit Report");
    await expect(titleInput).toHaveValue("Q4 2026 Audit Report");

    const authorInput = page.locator("input[placeholder*='Acme Corporation']");
    await authorInput.fill("PaperFlow QA Team");
    await expect(authorInput).toHaveValue("PaperFlow QA Team");
  });

  test("New tool: Remove Blank Pages settings", async ({ page }) => {
    await page.goto("/tools/remove-blank-pages");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    await expect(page.locator("h1")).toContainText("Remove Blank Pages");
    await expect(page.locator("text=Blank Page Detection Heuristics")).toBeVisible();

    const slider = page.locator("input[type='range']");
    await expect(slider).toBeVisible();
    await expect(page.locator("span.font-bold:has-text('99.2%')")).toBeVisible();
  });

  test("New tool: Clean and Deskew Scans settings", async ({ page }) => {
    await page.goto("/tools/deskew-pdf");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    await expect(page.locator("h1")).toContainText("Clean and Deskew Scans");
    await expect(page.locator("text=Scan Cleaning & Deskew Configuration")).toBeVisible();

    const deskewCheckbox = page.locator("input[type='checkbox']").first();
    await expect(deskewCheckbox).toBeChecked();
  });

  test("New tool: Extract Text settings", async ({ page }) => {
    await page.goto("/tools/extract-text");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    await expect(page.locator("h1")).toContainText("Extract Text");
    await expect(page.locator("text=Text Extraction Settings")).toBeVisible();

    const pageInput = page.locator("input[placeholder*='all, or 1-3, 5']");
    await expect(pageInput).toHaveValue("all");
  });

  test("Dark mode toggle toggles html theme class", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(600);

    const themeToggle = page.locator("button[aria-label='Toggle theme']");
    await expect(themeToggle).toBeVisible();

    const initialIsDark = await page.evaluate(() =>
      document.documentElement.classList.contains("dark")
    );

    await themeToggle.click();

    const toggledIsDark = await page.evaluate(() =>
      document.documentElement.classList.contains("dark")
    );

    expect(toggledIsDark).toBe(!initialIsDark);
  });

  test("End-to-End File Processing: Upload, Resize PDF, Complete & Download", async ({ page }) => {
    await page.goto("/tools/resize-pdf");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(800);

    // Minimal valid 1-page PDF
    const minimalPdf = `%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 35 >> stream
BT /F1 12 Tf 72 712 Td (Hello World) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer << /Root 1 0 R /Size 5 >>
startxref
299
%%EOF`;

    // Upload file to file input
    const fileInput = page.locator("input[type='file']").first();
    await fileInput.setInputFiles({
      name: "sample-document.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from(minimalPdf),
    });

    // File should appear in FileList
    await expect(page.locator("text=sample-document.pdf")).toBeVisible();

    // Select Letter size
    const sizeSelect = page.locator("select");
    await sizeSelect.selectOption("Letter");

    // Click submit button (actionButtonText is "Resize Pages")
    const submitBtn = page.locator("button:has-text('Resize Pages')");
    await expect(submitBtn).toBeEnabled();
    await submitBtn.click();

    // Wait for completion card
    await expect(page.locator("h3:has-text('Task Completed!')")).toBeVisible({ timeout: 25000 });

    // Verify download link is present and valid
    const downloadLink = page.locator("a:has-text('Download')");
    await expect(downloadLink).toBeVisible();
    const href = await downloadLink.getAttribute("href");
    expect(href).toContain("/api/jobs/");
    expect(href).toContain("/download");
  });
});
