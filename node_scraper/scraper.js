const puppeteer = require('puppeteer');
const cheerio = require('cheerio');

/**
 * Supplementary Node.js puppeteer scraper for Scapper
 * Usage: node scraper.js <URL> [waitForSelector]
 */
async function run() {
  const url = process.argv[2];
  const waitForSelector = process.argv[3];

  if (!url) {
    console.error(JSON.stringify({ error: 'URL argument is required' }));
    process.exit(1);
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    );

    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

    if (waitForSelector) {
      await page.waitForSelector(waitForSelector, { timeout: 5000 }).catch(() => {});
    }

    const html = await page.content();
    await browser.close();

    const $ = cheerio.load(html);
    $('script, style, noscript, svg, footer, nav').remove();
    const cleanedText = $('body').text().replace(/\s+/g, ' ').trim();

    console.log(JSON.stringify({
      raw_html: html,
      cleaned_text: cleanedText,
      mode_used: 'node_puppeteer'
    }));
  } catch (err) {
    if (browser) await browser.close();
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  }
}

run();
