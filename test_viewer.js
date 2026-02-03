const { test, expect } = require('@playwright/test');

test('Snapshot Viewer - Load and render Samus', async ({ page, context }) => {
  // Set a longer timeout for loading large assets
  test.setTimeout(60000);
  
  // Navigate to viewer
  console.log('Navigating to viewer...');
  await page.goto('http://localhost:8000/snapshot_viewer.html', { waitUntil: 'networkidle' });
  
  // Wait for bundles to load
  console.log('Waiting for bundles to load...');
  await page.waitForSelector('#bundleSelect option', { timeout: 10000 });
  
  // Check that SamusPlushie_body is available
  const options = await page.$$eval('#bundleSelect option', opts => 
    opts.map(o => o.textContent)
  );
  console.log('Available bundles:', options);
  expect(options).toContain('SamusPlushie_body');
  
  // Select Samus
  console.log('Selecting SamusPlushie_body...');
  await page.selectOption('#bundleSelect', 'SamusPlushie_body');
  
  // Wait for meshes to render
  console.log('Waiting for meshes to render...');
  await page.waitForTimeout(3000);
  
  // Check console for errors
  const consoleMessages = [];
  page.on('console', msg => {
    console.log(`[${msg.type()}] ${msg.text()}`);
    consoleMessages.push({ type: msg.type(), text: msg.text() });
  });
  
  page.on('pageerror', err => {
    console.error('Page error:', err);
  });
  
  // Wait for meshes to be added to scene
  await page.waitForTimeout(5000);
  
  // Get scene info
  const sceneInfo = await page.evaluate(() => {
    return {
      sceneChildren: window.__TEST?.scene?.children?.length || 'N/A',
      meshCount: window.__TEST?.currentMeshes?.length || 'N/A',
      materialRegistry: Object.keys(window.__TEST?.materialRegistry || {})
    };
  });
  
  console.log('Scene info:', sceneInfo);
  
  // Check for specific error patterns
  const errorMessages = consoleMessages.filter(m => m.type === 'error');
  const warningMessages = consoleMessages.filter(m => m.type === 'warning');
  
  console.log(`\n=== CONSOLE SUMMARY ===`);
  console.log(`Errors: ${errorMessages.length}`);
  console.log(`Warnings: ${warningMessages.length}`);
  
  if (errorMessages.length > 0) {
    console.log('\nErrors found:');
    errorMessages.forEach(e => console.log(`  - ${e.text}`));
  }
  
  if (warningMessages.length > 0) {
    console.log('\nWarnings found:');
    warningMessages.slice(0, 5).forEach(w => console.log(`  - ${w.text}`));
  }
  
  // Screenshot for visual inspection
  await page.screenshot({ path: 'samus_test_screenshot.png' });
  console.log('\nScreenshot saved to samus_test_screenshot.png');
});
