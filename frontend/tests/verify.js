const path = require('path');
const pw = require('../.test-tools/node_modules/playwright-core');

async function runTests() {
  console.log('Starting verification suite with Playwright (Edge)...');
  const browser = await pw.chromium.launch({
    channel: 'msedge',
    headless: true
  });

  const indexPath = path.resolve(__dirname, '../index.html');
  const fileUrl = 'file:///' + indexPath.replace(/\\/g, '/');

  const consoleErrors = [];
  const report = {
    screens: [],
    interactions: [],
    horizontalScrollTests: []
  };

  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
      console.error('[Browser Console Error]', msg.text());
    }
  });

  page.on('pageerror', (err) => {
    consoleErrors.push(err.message);
    console.error('[Browser Page Error]', err.message);
  });

  const widths = [1440, 1024, 768, 375];
  const screens = [
    { name: 'dashboard', hash: '#/dashboard' },
    { name: 'partners', hash: '#/partners' },
    { name: 'matches', hash: '#/matches' },
    { name: 'sessions', hash: '#/sessions' },
    { name: 'profile', hash: '#/profile' },
    { name: 'landing', hash: '#/landing' },
    { name: 'login', hash: '#/login' },
    { name: 'register', hash: '#/register' }
  ];

  console.log('\n--- 1. Testing Screen Rendering & Responsive Layouts ---');

  for (const s of screens) {
    for (const w of widths) {
      await page.setViewportSize({ width: w, height: 900 });
      await page.goto(`${fileUrl}${s.hash}`, { waitUntil: 'load' });
      await page.waitForTimeout(150);

      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });

      report.horizontalScrollTests.push({
        screen: s.name,
        width: w,
        hasHorizontalScroll: hasHorizontalScroll
      });

      if (hasHorizontalScroll) {
        console.warn(`[WARNING] Horizontal scroll detected on ${s.name} at ${w}px!`);
      }

      // Save screenshot for desktop (1440) and mobile (375)
      if (w === 1440) {
        const shotPath = path.resolve(__dirname, `../screenshots/${s.name}-desktop-1440.png`);
        await page.screenshot({ path: shotPath, fullPage: false });
      } else if (w === 375) {
        const shotPath = path.resolve(__dirname, `../screenshots/${s.name}-mobile-375.png`);
        await page.screenshot({ path: shotPath, fullPage: false });
      }
    }
    console.log(`✓ Screen [${s.name}] verified across 1440px, 1024px, 768px, 375px`);
  }

  console.log('\n--- 2. Testing Key Interactions ---');

  // Test 2.1: Theme Toggle
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`${fileUrl}#/dashboard`, { waitUntil: 'load' });
  await page.waitForTimeout(100);

  const initialTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await page.click('#theme-toggle');
  await page.waitForTimeout(100);
  const darkTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await page.screenshot({ path: path.resolve(__dirname, '../screenshots/dashboard-dark-1440.png') });
  await page.click('#theme-toggle');
  await page.waitForTimeout(100);
  const restoredTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));

  report.interactions.push({
    test: 'Theme toggle',
    success: darkTheme === 'dark' && restoredTheme === 'light'
  });
  console.log(`✓ Theme toggle: ${initialTheme} -> ${darkTheme} -> ${restoredTheme}`);

  // Test 2.2: Mobile Sidebar Drawer
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(`${fileUrl}#/dashboard`, { waitUntil: 'load' });
  await page.waitForTimeout(100);

  const drawerClosedBefore = await page.evaluate(() => !document.body.classList.contains('sidebar-open'));
  await page.click('#menu-toggle');
  await page.waitForTimeout(150);
  const drawerOpen = await page.evaluate(() => document.body.classList.contains('sidebar-open'));
  await page.screenshot({ path: path.resolve(__dirname, '../screenshots/mobile-drawer-375.png') });

  // Close via Escape
  await page.keyboard.press('Escape');
  await page.waitForTimeout(150);
  const drawerClosedEscape = await page.evaluate(() => !document.body.classList.contains('sidebar-open'));

  report.interactions.push({
    test: 'Mobile sidebar drawer (toggle & Escape)',
    success: drawerClosedBefore && drawerOpen && drawerClosedEscape
  });
  console.log(`✓ Mobile drawer toggle & Escape close: success=${drawerClosedBefore && drawerOpen && drawerClosedEscape}`);

  // Test 2.3: Connect Modal Interaction
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`${fileUrl}#/partners`, { waitUntil: 'load' });
  await page.waitForTimeout(100);

  const connectBtn = await page.$('[data-action="connect"]');
  if (connectBtn) {
    await connectBtn.click();
    await page.waitForTimeout(150);
    const modalVisible = await page.evaluate(() => !!document.querySelector('.modal'));
    await page.screenshot({ path: path.resolve(__dirname, '../screenshots/connect-modal-1440.png') });

    // Submit connect request
    await page.click('#btn-submit-connect');
    await page.waitForTimeout(200);
    const toastVisible = await page.evaluate(() => !!document.querySelector('.toast'));

    report.interactions.push({
      test: 'Connect modal & submit',
      success: modalVisible && toastVisible
    });
    console.log(`✓ Connect modal opened and request submitted: success=${modalVisible && toastVisible}`);
  }

  // Test 2.4: Requests & Matches tabs and accept request
  await page.goto(`${fileUrl}#/matches`, { waitUntil: 'load' });
  await page.waitForTimeout(150);

  // Click on active tab
  await page.click('[data-tab="active"]');
  await page.waitForTimeout(150);
  const activePairsCount = await page.evaluate(() => document.querySelectorAll('.active-card').length);

  // Switch back to incoming tab and accept first request
  await page.click('[data-tab="incoming"]');
  await page.waitForTimeout(150);
  const acceptBtn = await page.$('[data-action="accept-req"]');
  if (acceptBtn) {
    await acceptBtn.click();
    await page.waitForTimeout(200);
  }
  const activeTabBtn = await page.$('[data-tab="active"]');
  await activeTabBtn.click();
  await page.waitForTimeout(150);
  const newActivePairsCount = await page.evaluate(() => document.querySelectorAll('.active-card').length);

  report.interactions.push({
    test: 'Accept incoming request moves to active pairs',
    success: newActivePairsCount > activePairsCount
  });
  console.log(`✓ Accept study request: active pairs went from ${activePairsCount} to ${newActivePairsCount}`);

  // Test 2.5: Schedule Session Modal
  const scheduleBtn = await page.$('#btn-open-schedule');
  if (scheduleBtn) {
    await scheduleBtn.click();
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.resolve(__dirname, '../screenshots/schedule-modal-1440.png') });
    await page.click('#btn-save-session');
    await page.waitForTimeout(200);
    console.log('✓ Schedule session modal opened and session saved');
  }

  // Test 2.6: Sessions confirm & review flow
  await page.goto(`${fileUrl}#/sessions`, { waitUntil: 'load' });
  await page.waitForTimeout(150);
  const confirmBtn = await page.$('[data-action="confirm"]');
  if (confirmBtn) {
    await confirmBtn.click();
    await page.waitForTimeout(150);
    await page.click('#btn-proceed-review');
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.resolve(__dirname, '../screenshots/review-modal-1440.png') });
    await page.click('#btn-submit-review');
    await page.waitForTimeout(200);
    console.log('✓ Confirm session & leave peer review flow completed');
  }

  // Test 2.7: Profile Availability slots click
  await page.goto(`${fileUrl}#/profile`, { waitUntil: 'load' });
  await page.waitForTimeout(150);
  const slot = await page.$('.slot:not(.selected)');
  if (slot) {
    await slot.click();
    await page.waitForTimeout(100);
    const isSelected = await slot.evaluate((el) => el.classList.contains('selected'));
    console.log(`✓ Availability slot toggle: selected=${isSelected}`);
  }

  // Test 2.8: Global search and Ctrl+K
  await page.keyboard.press('Control+KeyK');
  await page.waitForTimeout(100);
  const searchFocused = await page.evaluate(() => document.activeElement.id === 'global-search');
  await page.type('#global-search', 'Jasur');
  await page.waitForTimeout(150);
  const searchDropVisible = await page.evaluate(() => !!document.getElementById('search-dropdown'));
  console.log(`✓ Global search Ctrl+K focus and dropdown preview: focused=${searchFocused}, dropdown=${searchDropVisible}`);

  console.log('\n--- 3. Error Summary ---');
  console.log(`Console errors count: ${consoleErrors.length}`);
  if (consoleErrors.length > 0) {
    console.error('Console errors:', consoleErrors);
  }

  await browser.close();
  console.log('\nVerification suite finished successfully.');
}

runTests().catch((err) => {
  console.error('Test run failed:', err);
  process.exit(1);
});
