import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const baseUrl = process.env.ARTIFACT_URL || "http://localhost:4173";
const outputDir = fileURLToPath(new URL("../docs/images/", import.meta.url));

const shots = [
  { name: "release-command-center.png", tab: "Release Command Center" },
  { name: "backlog-acceptance-lab.png", tab: "Backlog and Acceptance Lab" },
  { name: "deployment-adoption-board.png", tab: "Deployment and Adoption Board" },
];

await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 980 }, deviceScaleFactor: 1 });
await page.goto(baseUrl, { waitUntil: "networkidle" });

for (const shot of shots) {
  await page.getByRole("button", { name: shot.tab }).click();
  await page.waitForTimeout(250);
  await page.screenshot({ path: `${outputDir}${shot.name}`, fullPage: true });
}

await browser.close();
console.log(`Captured ${shots.length} screenshots from ${baseUrl}.`);
