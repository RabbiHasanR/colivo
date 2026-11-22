/**
 * Screenshots of every built page, to compare by eye with colivo-design/web
 * (specs/testing.md → "Layout is not test-driven, but it is not optional").
 *
 *   make web-screens            →  web/screens/<page>-<width>.png
 *
 * Starts the web app on its own port and answers its API calls with sample
 * data, so no backend is needed. Each phase adds its pages to PAGES and the
 * data they read to API.
 */
import { spawn } from 'node:child_process';
import { get } from 'node:http';
import { mkdir } from 'node:fs/promises';
import { chromium } from '@playwright/test';

const PORT = 4399;
const BASE = `http://localhost:${PORT}`;
const OUT = 'screens';
const WIDTHS = [390, 1440];

const home = {
  id: 'h1',
  code: 'OF-4827',
  name: 'Our Flat',
  area: 'Mirpur',
  first_month: '2026-11-01',
};

const owner = {
  person: { phone: '+8801712345678' },
  membership: {
    id: 'm1',
    name: 'Rabbi Hasan',
    role: 'owner',
    status: 'active',
    joined_on: '2026-11-01',
    added_by_name: null,
    details_checked: true,
  },
  home,
};

function member(id, name, role, status, joinedOn) {
  return {
    id,
    name,
    phone: `+88017000000${id.slice(1)}`,
    email: null,
    role,
    status,
    joined_on: joinedOn,
  };
}

/** What the API answers, by path under /api/v1/. */
const API = {
  me: owner,
  'home/setup': {
    steps: [
      { key: 'home_created', done: true },
      { key: 'members', done: false },
      { key: 'rooms', done: false },
      { key: 'rules', done: false },
      { key: 'bills', done: false },
    ],
  },
  members: [
    member('m1', 'Rabbi Hasan', 'owner', 'active', '2026-11-01'),
    member('m2', 'Hijam Shusil', 'manager', 'active', '2026-11-05'),
    member('m3', 'Maruf', 'member', 'active', '2026-11-21'),
    member('m4', 'Nafis Islam', 'member', 'inactive', '2026-09-01'),
  ],
};

/** Each page: its name, its URL, and whether someone is logged in. */
const PAGES = [
  { name: 'log-in', path: '/log-in', loggedIn: false },
  { name: 'home', path: '/', loggedIn: true },
  { name: 'members', path: '/members', loggedIn: true },
];

function json(status, body) {
  return {
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  };
}

/** Answer the app's API calls from API; /me is 401 when nobody is logged in. */
async function answerApi(page, loggedIn) {
  await page.route('**/api/v1/**', (route) => {
    const path = new URL(route.request().url()).pathname.replace(
      '/api/v1/',
      '',
    );
    if (path === 'me' && !loggedIn) {
      return route.fulfill(
        json(401, { success: false, message: 'Log in first.', errors: [] }),
      );
    }
    if (!(path in API)) {
      return route.fulfill(
        json(404, { success: false, message: `No sample for ${path}` }),
      );
    }
    return route.fulfill(
      json(200, { success: true, message: 'ok', data: API[path] }),
    );
  });
}

/** Whether the web app answers yet. */
function isUp() {
  return new Promise((resolve) => {
    get(BASE, (response) => {
      response.resume();
      resolve(true);
    }).on('error', () => resolve(false));
  });
}

async function waitForServer() {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    if (await isUp()) return;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`The web app did not start on ${BASE}`);
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const server = spawn(
    'pnpm',
    ['exec', 'vite', '--port', String(PORT), '--strictPort'],
    {
      stdio: 'ignore',
      detached: true,
    },
  );
  const browser = await chromium.launch();
  try {
    await waitForServer();
    for (const { name, path, loggedIn } of PAGES) {
      for (const width of WIDTHS) {
        const page = await browser.newPage({
          viewport: { width, height: 900 },
        });
        await answerApi(page, loggedIn);
        await page.goto(`${BASE}${path}`, { waitUntil: 'networkidle' });
        const file = `${OUT}/${name}-${width}.png`;
        await page.screenshot({ path: file, fullPage: true });
        console.log(file);
        await page.close();
      }
    }
  } finally {
    await browser.close();
    process.kill(-server.pid);
  }
}

await main();
