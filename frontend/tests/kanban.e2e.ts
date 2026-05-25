import { test, expect } from "@playwright/test";

test("add card and persistence", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Kanban Studio/i })).toBeVisible();

  // pick first column
  const firstColumn = page.locator('section[data-testid^="column-"]').first();
    await expect(firstColumn).toBeVisible(); // Ensure the first column is visible

  // open new card form
    await firstColumn.getByRole("button", { name: /Add a card/i }).click();
    await firstColumn.locator('input[placeholder="Card title"]').fill("E2E Test Card");
    await firstColumn.locator('textarea[placeholder="Details"]').fill("persist details");
    await firstColumn.getByRole("button", { name: /Add card/i }).click();

  // card should appear
  await expect(page.getByText("E2E Test Card")).toBeVisible();

  // reload and verify persistence
  await page.reload();
  await expect(page.getByText("E2E Test Card")).toBeVisible();
});
