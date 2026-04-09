#!/usr/bin/env node

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function testViewer() {
  let browser;
  try {
    console.log('🚀 Starting Playwright test of snapshot viewer...\n');
    
    // Try to launch browser
    console.log('📌 Launching Chromium browser...');
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    // Collect console messages
    const consoleMessages = [];
    const pageErrors = [];
    
    page.on('console', msg => {
      const level = msg.type().toUpperCase();
      const text = msg.text();
      consoleMessages.push({ level, text });
      console.log(`  [${level}] ${text.substring(0, 100)}`);
    });
    
    page.on('pageerror', err => {
      pageErrors.push(err.toString());
      console.error(`  ❌ PAGE ERROR: ${err}`);
    });
    
    // Navigate to viewer
    console.log('\n📄 Loading snapshot viewer...');
    try {
      await page.goto('http://localhost:8000/snapshot_viewer.html', { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });
      console.log('  ✓ Page loaded');
    } catch (e) {
      console.error(`  ✗ Failed to load page: ${e.message}`);
      throw e;
    }
    
    // Wait for bundles
    console.log('\n⏳ Waiting for bundles to load...');
    try {
      await page.waitForFunction(() => {
        const select = document.getElementById('bundleSelect');
        return select && select.options.length > 1;
      }, { timeout: 15000 });
      console.log('  ✓ Bundles loaded');
    } catch (e) {
      console.error(`  ✗ Bundles didn't load: ${e.message}`);
      throw e;
    }
    
    // Check available bundles
    const bundles = await page.$$eval('#bundleSelect option', opts => 
      opts.map(o => o.value).filter(v => v)
    );
    console.log(`  Found bundles: ${bundles.join(', ')}`);
    
    if (!bundles.includes('SamusPlushie_body')) {
      throw new Error('SamusPlushie_body not found in bundles');
    }
    
    // Select Samus
    console.log('\n🎮 Selecting SamusPlushie_body...');
    await page.selectOption('#bundleSelect', 'SamusPlushie_body');
    console.log('  ✓ Selected');
    
    // Wait for rendering
    console.log('\n🎨 Waiting for meshes to render...');
    await page.waitForTimeout(4000);
    
    // Check scene state
    console.log('\n📊 Checking scene state...');
    const sceneState = await page.evaluate(() => {
      return {
        hasScene: typeof window.scene !== 'undefined',
        sceneChildren: window.scene?.children?.length || 0,
        currentMeshCount: window.currentMeshes?.length || 0,
        materialRegistrySize: Object.keys(window.materialRegistry || {}).length,
        materialKeys: Object.keys(window.materialRegistry || {}).slice(0, 5)
      };
    });
    
    console.log(`  Scene children: ${sceneState.sceneChildren}`);
    console.log(`  Current meshes: ${sceneState.currentMeshCount}`);
    console.log(`  Materials in registry: ${sceneState.materialRegistrySize}`);
    if (sceneState.materialKeys.length > 0) {
      console.log(`  Sample material IDs: ${sceneState.materialKeys.join(', ')}`);
    }
    
    // Analyze console for specific issues
    console.log('\n📋 Console Analysis:');
    const errors = consoleMessages.filter(m => m.level === 'ERROR');
    const warnings = consoleMessages.filter(m => m.level === 'WARNING');
    const logs = consoleMessages.filter(m => m.level === 'LOG');
    
    console.log(`  Errors: ${errors.length}`);
    console.log(`  Warnings: ${warnings.length}`);
    console.log(`  Logs: ${logs.length}`);
    
    if (errors.length > 0) {
      console.log('\n  ⚠️ Error messages:');
      errors.slice(0, 5).forEach(e => {
        console.log(`    - ${e.text}`);
      });
    }
    
    // Check for specific issues
    console.log('\n🔍 Checking for known issues:');
    
    const materialLookupFailed = errors.some(e => 
      e.text.includes('Material NOT found') || e.text.includes('material registry')
    );
    if (!materialLookupFailed) {
      console.log('  ✓ No material lookup failures');
    } else {
      console.log('  ✗ Material lookup failures detected');
    }
    
    const textureLoadFailed = errors.some(e => 
      e.text.includes('Texture failed') || e.text.includes('404')
    );
    if (!textureLoadFailed) {
      console.log('  ✓ No texture loading failures');
    } else {
      console.log('  ✗ Texture loading failures detected');
    }
    
    const meshesRendered = sceneState.currentMeshCount > 0;
    if (meshesRendered) {
      console.log(`  ✓ Meshes rendered: ${sceneState.currentMeshCount}`);
    } else {
      console.log('  ✗ No meshes rendered');
    }
    
    // Take screenshot
    console.log('\n📸 Taking screenshot...');
    await page.screenshot({ path: 'test_screenshot.png' });
    console.log('  Screenshot saved to test_screenshot.png');
    
    // Report overall status
    console.log('\n' + '='.repeat(50));
    if (sceneState.currentMeshCount > 0 && !textureLoadFailed && !materialLookupFailed) {
      console.log('✅ TEST PASSED: Viewer loaded and rendered successfully');
      return 0;
    } else {
      console.log('⚠️ TEST WARNINGS: See issues above');
      return 1;
    }
    
  } catch (error) {
    console.error('\n❌ TEST FAILED:');
    console.error(`  ${error.message}`);
    console.error(error.stack);
    return 1;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run test
testViewer().then(code => {
  process.exit(code);
}).catch(err => {
  console.error('Unhandled error:', err);
  process.exit(1);
});
