"use strict";

const TOKEN = window.ANYPS5_TOKEN;
const ICONS = {
  play: '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>',
  install: '<svg viewBox="0 0 24 24"><path d="M12 3v12m0 0l-4-4m4 4l4-4M4 17v3h16v-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  audit: '<svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h10M4 18h7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M15 17l2 2 4-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  log: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M7 9l3 3-3 3M12 15h5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  pad: '<svg viewBox="0 0 24 24"><path d="M6 8h12a4 4 0 0 1 4 4v3a3 3 0 0 1-5.4 1.8L15 15H9l-1.6 1.8A3 3 0 0 1 2 15v-3a4 4 0 0 1 4-4z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 11v3M6.5 12.5h3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="16" cy="11.5" r="1" fill="currentColor"/><circle cx="18" cy="13.5" r="1" fill="currentColor"/></svg>',
  save: '<svg viewBox="0 0 24 24"><path d="M5 3h11l3 3v15H5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M8 3v5h7V3M8 21v-7h8v7" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
  folder: '<svg viewBox="0 0 24 24"><path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
  gpu: '<svg viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15 10h4M15 14h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  cache: '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="8" ry="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  debug: '<svg viewBox="0 0 24 24"><path d="M9 7a3 3 0 0 1 6 0v1H9zM7 11h10v5a5 5 0 0 1-10 0zM3 13h4M17 13h4M4 19l3-2M20 19l-3-2M5 8l3 2M19 8l-3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  docs: '<svg viewBox="0 0 24 24"><path d="M4 4h9l5 5v11H4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M13 4v5h5M8 13h8M8 17h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  info: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 11v6M12 7.5v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  grid: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5" fill="currentColor"/><rect x="14" y="3" width="7" height="7" rx="1.5" fill="currentColor"/><rect x="3" y="14" width="7" height="7" rx="1.5" fill="currentColor"/><rect x="14" y="14" width="7" height="7" rx="1.5" fill="currentColor"/></svg>',
  plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
  wrench: '<svg viewBox="0 0 24 24"><path d="M14.7 6.3a4 4 0 0 0 5 5l-9 9a2.1 2.1 0 0 1-3-3l9-9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M15 3.5a5 5 0 0 1 5.5 5.5L18 7.5 16.5 6z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
  home: '<svg viewBox="0 0 24 24"><path d="M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
  bell: '<svg viewBox="0 0 24 24"><path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4zM10 20a2 2 0 0 0 4 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
  sound: '<svg viewBox="0 0 24 24"><path d="M4 9v6h4l5 4V5L8 9zM16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>',
  power: '<svg viewBox="0 0 24 24"><path d="M12 3v9M6.3 7.3a8 8 0 1 0 11.4 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  user: '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 21a8 8 0 0 1 16 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  stop: '<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/></svg>',
  trash: '<svg viewBox="0 0 24 24"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  settings: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  refresh: '<svg viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.3-5.7M20 4v5h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  fullscreen: '<svg viewBox="0 0 24 24"><path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="M5 12l5 5L20 7" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  search: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
};

const state = {
  data: null,
  screen: "home",
  history: [],
  focus: null,
  focusMemory: {},
  selectedTile: null,
  settingsSection: "paths",
  libraryFilter: "all",
  installer: { source: "", inspect: null, options: {}, job: null },
  consoleJob: null,
  consoleGame: null,
  gameSettingsId: null,
  seenNotifications: new Set(),
  gamepads: {},
  audio: null,
  firstLoad: true,
  lastArt: "",
  artFlip: false,
  docs: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const el = (tag, attrs = {}, children = []) => {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key === "text") node.textContent = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (value === true) node.setAttribute(key, "");
    else if (value !== false && value != null) node.setAttribute(key, value);
  }
  for (const child of [].concat(children)) if (child != null) node.append(child);
  return node;
};
const escapeHtml = (text) => String(text).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function api(path, body) {
  const options = { headers: { "X-AnyPS5-Token": TOKEN } };
  if (body !== undefined) {
    options.method = "POST";
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(`/api/${path}`, options);
  const data = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

const THEMES = {
  ps5: { label: "PS5", desc: "Key art, glass cards and the soft menu tones of the PlayStation 5.", wave: "sine", gap: 0.05, sounds: { nav: [[1250, 0.03, 0.05]], select: [[900, 0.04, 0.06], [1400, 0.04, 0.08]], back: [[700, 0.05, 0.07]], open: [[500, 0.06, 0.12], [1000, 0.05, 0.1]], error: [[220, 0.1, 0.18]] } },
  ps4: { label: "PS4", desc: "Deep blue dynamic menu with drifting light and square tiles.", wave: "triangle", gap: 0.04, sounds: { nav: [[1800, 0.03, 0.025]], select: [[1500, 0.04, 0.03], [2100, 0.04, 0.05]], back: [[1100, 0.04, 0.05, 700]], open: [[900, 0.05, 0.14, 500]], error: [[200, 0.08, 0.2]] } },
  ps3: { label: "PS3 · XMB", desc: "The XrossMediaBar ribbon, glowing text and a colour that follows the month.", wave: "sine", gap: 0.04, sounds: { nav: [[2600, 0.03, 0.02]], select: [[1300, 0.05, 0.04, 650]], back: [[880, 0.05, 0.07, 440]], open: [[1760, 0.05, 0.09, 880]], error: [[300, 0.08, 0.2]] } },
  ps1: { label: "PS1", desc: "Bevelled grey panels, orange highlights, scanlines and chiptune bleeps.", wave: "square", gap: 0.07, sounds: { nav: [[1046, 0.015, 0.035]], select: [[523, 0.02, 0.06], [659, 0.02, 0.06], [784, 0.02, 0.09]], back: [[659, 0.02, 0.06], [440, 0.02, 0.08]], open: [[262, 0.02, 0.08, 523], [784, 0.02, 0.1]], error: [[110, 0.03, 0.25]] } },
};

function currentTheme() {
  const name = state.data && state.data.settings.theme;
  return THEMES[name] ? name : "ps5";
}

function sound(kind) {
  if (!state.data || !state.data.settings.ui_sounds) return;
  try {
    state.audio = state.audio || new (window.AudioContext || window.webkitAudioContext)();
    const context = state.audio;
    if (context.state === "suspended") context.resume();
    const now = context.currentTime;
    const theme = THEMES[currentTheme()];
    const notes = theme.sounds[kind] || [];
    notes.forEach(([frequency, volume, length, sweep], index) => {
      const start = now + index * theme.gap;
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = theme.wave;
      oscillator.frequency.setValueAtTime(frequency, start);
      if (sweep) oscillator.frequency.exponentialRampToValueAtTime(sweep, start + length);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(volume, start + 0.004);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + length);
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(start);
      oscillator.stop(start + length + 0.02);
    });
  } catch (error) { state.audio = null; }
}

function applyTheme() {
  const name = currentTheme();
  if (document.documentElement.dataset.theme === name && $("#bgTheme").childElementCount) return;
  document.documentElement.dataset.theme = name;
  const layer = $("#bgTheme");
  layer.innerHTML = "";
  if (name === "ps4") {
    for (let index = 0; index < 4; index += 1) layer.append(el("div", { class: "ps4-streak", style: `left:${index * 24}vw; animation-delay:${-index * 7}s; width:${12 + index * 5}vw` }));
    for (let index = 0; index < 14; index += 1) layer.append(el("div", { class: "ps4-dot", style: `left:${(index * 37) % 100}vw; top:${(index * 53) % 100}vh; animation-delay:${-index * 1.3}s; animation-duration:${12 + (index % 5) * 3}s; width:${3 + (index % 3) * 2}px; height:${3 + (index % 3) * 2}px` }));
  } else if (name === "ps3") {
    document.documentElement.style.setProperty("--xmb-hue", String([210, 45, 120, 320, 95, 180, 200, 25, 265, 30, 35, 0][new Date().getMonth()]));
    const paths = ["M-50 520 C 300 380, 600 700, 900 520 S 1500 360, 1900 540", "M-50 560 C 350 440, 650 720, 1000 560 S 1550 420, 1900 580", "M-50 600 C 400 480, 700 760, 1100 600 S 1600 460, 1900 620"];
    layer.innerHTML = `<svg viewBox="0 0 1850 900" preserveAspectRatio="none">${paths.map((d, index) => `<path class="xmb-wave ${["a", "b", "c"][index]}" d="${d}"/>`).join("")}</svg>`;
    for (let index = 0; index < 18; index += 1) layer.append(el("div", { class: "xmb-spark", style: `left:${(index * 41) % 100}vw; top:${45 + (index * 29) % 40}vh; animation-delay:${-index * 0.9}s; animation-duration:${7 + (index % 4) * 2}s` }));
  } else if (name === "ps1") {
    layer.append(el("div", { class: "ps1-diamond" }));
  }
}

async function setTheme(name) {
  if (!THEMES[name]) return;
  await api("settings", { theme: name });
  await refresh({ quiet: true });
  applyTheme();
  sound("open");
  toast("Theme", THEMES[name].label);
}

function chooseTheme() {
  const current = currentTheme();
  dialog({ title: "Theme", text: "Changes the look and the menu sounds.", options: Object.entries(THEMES).map(([value, theme]) => ({ label: theme.label, sub: theme.desc, value, active: value === current })), buttons: [{ label: "Cancel", value: undefined }] }).then((value) => { if (value && value !== current) setTheme(value); });
}

function cycleTheme() {
  const names = Object.keys(THEMES);
  setTheme(names[(names.indexOf(currentTheme()) + 1) % names.length]);
}

function topLayer() {
  if (!$("#dialogLayer").hidden) return $("#dialogLayer");
  if (!$("#controlCenter").hidden) return $("#controlCenter");
  if (!$("#sidemenu").hidden) return $("#sidemenu");
  return document.body;
}

function focusables() {
  const layer = topLayer();
  return $$("[data-focus]", layer).filter((node) => {
    if (layer === document.body && node.closest(".screen") && !node.closest(".screen.active")) return false;
    if (node.closest("[hidden]")) return false;
    const rect = node.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  });
}

function setFocus(node, options = {}) {
  if (!node) return;
  if (state.focus && state.focus !== node) state.focus.classList.remove("focused");
  state.focus = node;
  node.classList.add("focused");
  if (!options.silent) sound("nav");
  if (node.scrollIntoView) node.scrollIntoView({ block: "nearest", inline: "nearest", behavior: options.instant ? "instant" : "smooth" });
  if (node.tagName === "TEXTAREA" || node.tagName === "INPUT") node.focus({ preventScroll: true });
  else if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
  if (node.classList.contains("tile")) selectTile(node);
  node.dispatchEvent(new CustomEvent("focused"));
}

function defaultFocus(name) {
  if (name === "home") return $(`[data-key="tile:${CSS.escape(state.selectedTile || "")}"]`) || $("#tiles .tile");
  return $(".screen.active [data-focus]");
}

function shortenPath(text) {
  const value = String(text || "");
  if (value.length <= 44) return value;
  const parts = value.split(/[\\/]/).filter(Boolean);
  return parts.length > 2 ? `…/${parts.slice(-2).join("/")}` : value;
}

function focusFirst(preferred) {
  const list = focusables();
  const target = (preferred && list.includes(preferred)) ? preferred : list[0];
  if (target) setFocus(target, { silent: true, instant: true });
}

function move(direction) {
  const current = state.focus;
  const list = focusables();
  if (!current || !list.includes(current)) { focusFirst(); return; }
  const r = current.getBoundingClientRect();
  const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
  let best = null, bestScore = Infinity;
  for (const node of list) {
    if (node === current) continue;
    const b = node.getBoundingClientRect();
    const bx = (b.left + b.right) / 2, by = (b.top + b.bottom) / 2;
    let primary, secondary;
    if (direction === "left") { if (b.right > r.left + 4 && bx >= cx) continue; primary = Math.max(0, r.left - b.right); secondary = gap(r.top, r.bottom, b.top, b.bottom); }
    else if (direction === "right") { if (b.left < r.right - 4 && bx <= cx) continue; primary = Math.max(0, b.left - r.right); secondary = gap(r.top, r.bottom, b.top, b.bottom); }
    else if (direction === "up") { if (b.bottom > r.top + 4 && by >= cy) continue; primary = Math.max(0, r.top - b.bottom); secondary = gap(r.left, r.right, b.left, b.right); }
    else { if (b.top < r.bottom - 4 && by <= cy) continue; primary = Math.max(0, b.top - r.bottom); secondary = gap(r.left, r.right, b.left, b.right); }
    const axis = (direction === "left" || direction === "right") ? Math.abs(by - cy) : Math.abs(bx - cx);
    const score = primary + secondary * 3 + axis * 0.15;
    if (score < bestScore) { bestScore = score; best = node; }
  }
  if (best) setFocus(best);
}

function gap(a1, a2, b1, b2) {
  if (b2 >= a1 && b1 <= a2) return 0;
  return b1 > a2 ? b1 - a2 : a1 - b2;
}

function activate() {
  const node = state.focus;
  if (!node) return;
  sound("select");
  node.click();
}

function showScreen(name, options = {}) {
  if (!options.replace && state.screen !== name) {
    state.focusMemory[state.screen] = state.focus;
    state.history.push(state.screen);
  }
  state.screen = name;
  $$(".screen").forEach((section) => section.classList.toggle("active", section.dataset.screen === name));
  $$(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === name || (name === "home" && tab.dataset.tab === "home")));
  if (name !== "home" && name !== "homebrew") $$(".tab").forEach((tab) => tab.classList.remove("active"));
  renderScreen(name);
  updateHints();
  requestAnimationFrame(() => focusFirst(options.focus || state.focusMemory[name] || defaultFocus(name)));
}

function goBack() {
  if (!$("#dialogLayer").hidden) { closeDialog(null); return; }
  if (!$("#controlCenter").hidden) { closeControlCenter(); return; }
  if (!$("#sidemenu").hidden) { closeSideMenu(); return; }
  if (document.activeElement && document.activeElement.tagName === "TEXTAREA") { document.activeElement.blur(); return; }
  const previous = state.history.pop();
  sound("back");
  if (previous) showScreen(previous, { replace: true });
  else if (state.screen !== "home") showScreen("home", { replace: true });
}

function updateHints() {
  const left = $("#hintsLeft");
  left.innerHTML = "";
  const running = state.data && state.data.running;
  if (running) {
    const game = state.data.games.find((item) => item.id === running.id);
    left.append(el("span", { class: "running-banner", html: `<span class="dot"></span>Running: ${escapeHtml(game ? game.title : running.id)}` }));
  }
  const host = state.data && state.data.host;
  if (host && !host.relinker) left.append(el("span", { class: "pill bad", text: "relinker not found" }));
  if (host && !host.libs) left.append(el("span", { class: "pill bad", text: "system libraries not found" }));
}

function tickClock() {
  const now = new Date();
  const text = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit", hour12: !(state.data && state.data.settings.clock_24h) });
  $("#clock").textContent = text;
  $("#ccClock").textContent = text;
}

async function refresh(options = {}) {
  try {
    const data = await api("state");
    state.data = data;
    applyTheme();
    $("#avatar").textContent = (data.settings.profile_name || "P").trim().charAt(0).toUpperCase() || "P";
    $("#ccAvatar").textContent = $("#avatar").textContent;
    $("#ccName").textContent = data.settings.profile_name || "Player";
    for (const item of data.notifications) {
      if (!state.seenNotifications.has(item.id)) {
        state.seenNotifications.add(item.id);
        if (!state.firstLoad) toast(item.title, item.text);
      }
    }
    if (state.firstLoad) {
      state.firstLoad = false;
      renderScreen(state.screen);
      setTimeout(() => { $("#splash").classList.add("hide"); $("#app").classList.remove("booting"); focusFirst(defaultFocus(state.screen)); }, 900);
    } else if (!options.quiet) {
      renderScreen(state.screen, { keepFocus: true });
    } else {
      renderHomeIfChanged();
    }
    updateHints();
    tickClock();
  } catch (error) {
    if (!state.data) bootProblem(`Cannot reach the launcher: ${error.message}. Keep the terminal window open and reload this page (F5).`);
  }
}

function renderHomeIfChanged() {
  const signature = JSON.stringify(state.data.games.map((game) => [game.id, game.status, game.last_played, game.audit && game.audit.unique_by_class]));
  if (signature !== state.homeSignature) { state.homeSignature = signature; renderScreen(state.screen, { keepFocus: true }); }
  updateHints();
}

function renderScreen(name, options = {}) {
  const focusId = options.keepFocus && state.focus ? state.focus.dataset.key : null;
  if (name === "home") renderHome();
  else if (name === "homebrew") renderHomebrew();
  else if (name === "library") renderLibrary();
  else if (name === "settings") renderSettings();
  else if (name === "installer") renderInstaller();
  else if (name === "gamesettings") renderGameSettings();
  else if (name === "docs") renderDocs();
  if (focusId) {
    const again = focusables().find((node) => node.dataset.key === focusId);
    if (again) setFocus(again, { silent: true, instant: true });
    else if (!focusables().includes(state.focus)) focusFirst();
  }
}

function tileNode(game, extra = {}) {
  const tile = el("div", { class: `tile ${extra.class || ""}`, "data-focus": true, "data-key": `tile:${game.id}` });
  if (game.icon) tile.style.backgroundImage = `url(/api/icon?id=${encodeURIComponent(game.id)}&t=${TOKEN})`;
  else tile.append(el("div", { class: "tile-initials", text: initials(game.title), style: `background: ${gradientFor(game.title)}` }));
  if (!extra.noLabel) tile.append(el("div", { class: "tile-label", text: game.title }));
  const badge = game.status === "running" ? ["run", "▶"] : game.installed ? ["", "✓"] : game.status === "blocked" ? ["bad", "!"] : ["warn", "↓"];
  if (!extra.noBadge) tile.append(el("div", { class: `tile-badge ${badge[0]}`, text: badge[1] }));
  return tile;
}

function initials(title) {
  return (title || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((word) => word[0].toUpperCase()).join("") || "?";
}

function gradientFor(text) {
  let hash = 0;
  for (const char of text || "") hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  const hue = hash % 360;
  return `linear-gradient(145deg, hsl(${hue} 55% 42%), hsl(${(hue + 50) % 360} 60% 22%))`;
}

function specialTile(key, icon, label) {
  const tile = el("div", { class: "tile special", "data-focus": true, "data-key": `tile:${key}`, html: ICONS[icon], title: label });
  tile.dataset.special = key;
  return tile;
}

function renderHome() {
  const tiles = $("#tiles");
  tiles.innerHTML = "";
  const games = state.data.games;
  for (const game of games) {
    const tile = tileNode(game, { noLabel: true });
    tile.dataset.game = game.id;
    tile.addEventListener("click", () => primaryAction(game));
    tiles.append(tile);
  }
  const library = specialTile("library", "grid", "Game Library");
  library.addEventListener("click", () => showScreen("library"));
  const install = specialTile("install", "plus", "Install Package");
  install.addEventListener("click", () => showScreen("installer"));
  const homebrew = specialTile("homebrew", "wrench", "Homebrew");
  homebrew.addEventListener("click", () => showScreen("homebrew"));
  tiles.append(library, install, homebrew);
  const wanted = state.selectedTile && $(`[data-key="tile:${CSS.escape(state.selectedTile)}"]`, tiles);
  selectTile(wanted || tiles.firstElementChild);
}

function selectTile(tile) {
  if (!tile) return;
  state.selectedTile = tile.dataset.game || tile.dataset.special;
  const game = tile.dataset.game ? state.data.games.find((item) => item.id === tile.dataset.game) : null;
  renderHub(game, tile.dataset.special);
  setBackground(game);
}

function setBackground(game) {
  const url = game ? (game.art ? `/api/art?id=${encodeURIComponent(game.id)}&t=${TOKEN}` : game.icon ? `/api/icon?id=${encodeURIComponent(game.id)}&t=${TOKEN}` : "") : "";
  if (url === state.lastArt) return;
  state.lastArt = url;
  const incoming = $(state.artFlip ? "#bgArtA" : "#bgArtB");
  const outgoing = $(state.artFlip ? "#bgArtB" : "#bgArtA");
  state.artFlip = !state.artFlip;
  incoming.style.backgroundImage = url ? `url(${url})` : "";
  incoming.classList.toggle("blur", !!(game && !game.art));
  incoming.classList.toggle("active", !!url);
  outgoing.classList.remove("active");
}

function statusPill(game) {
  if (game.status === "running") return el("span", { class: "pill run", html: '<span class="dot"></span>Running' });
  if (game.installed) return el("span", { class: "pill ok", html: '<span class="dot"></span>Installed' });
  if (game.status === "blocked") return el("span", { class: "pill bad", html: '<span class="dot"></span>Cannot convert' });
  return el("span", { class: "pill warn", html: '<span class="dot"></span>Not installed' });
}

function verifiedText(game) {
  const notes = game.compatibility_notes || {};
  const own = (notes[state.data.host.platform] || "").trim();
  if (own && own !== "?") return `Verified on ${state.data.host.platform}: ${own}`;
  const other = state.data.host.platform === "windows" ? "linux" : "windows";
  const text = (notes[other] || "").trim();
  if (text && text !== "?") return `Verified on ${other}: ${text}`;
  return "";
}

function compatibilityText(game) {
  const audit = game.audit && game.audit.unique_by_class;
  const listed = verifiedText(game);
  const parts = [];
  if (listed) parts.push(listed);
  if (audit) {
    const absent = audit.absent || 0, stub = audit.stub || 0, implemented = audit.implemented || 0;
    parts.push(absent ? `${absent} missing system functions` : stub ? `${stub} stubbed functions may throw` : `${implemented} imports provided`);
  }
  return parts.join(" · ") || "Untested on this build";
}

function compatibilityClass(game) {
  const audit = game.audit && game.audit.unique_by_class;
  if (audit && audit.absent) return "bad";
  if (audit && audit.stub) return "warn";
  if (/playable|in game/i.test(verifiedText(game))) return "ok";
  if (audit) return "ok";
  return "";
}

function renderHub(game, special) {
  const hub = $("#hub");
  hub.innerHTML = "";
  if (!game) {
    const copy = {
      library: ["Game Library", "Every title found in your games folder and every installed build, with filters for what is installed or still needs conversion."],
      install: ["Install Package", "Convert a title dump with the relinker. The result is a native executable that runs on this PC without an emulator."],
      homebrew: ["Homebrew", "Import audit, logs, controller mapping, save data, shader cache, GPU selection and debug switches."],
    }[special] || ["AnyPS5", ""];
    hub.append(el("div", { class: "hub-title", text: copy[0] }), el("div", { class: "hub-empty", text: copy[1] }));
    if (!state.data.games.length) {
      hub.append(el("div", { class: "hub-empty", html: `No games yet. Put each title dump in its own folder under <strong>${escapeHtml(state.data.settings.games_dir)}</strong> and press <strong>Install Package</strong>, or change the folder in Settings › Paths.` }));
    }
    return;
  }
  hub.append(el("div", { class: "hub-title", text: game.title }));
  const meta = el("div", { class: "hub-meta" });
  meta.append(statusPill(game));
  if (game.title_id) meta.append(el("span", { text: game.title_id }));
  if (game.version) meta.append(el("span", { text: `v${game.version}` }));
  if (game.last_played) meta.append(el("span", { text: `Last played ${game.last_played_text}` }));
  if (game.play_seconds) meta.append(el("span", { text: `${formatDuration(game.play_seconds)} played` }));
  hub.append(meta);
  const actions = el("div", { class: "hub-actions" });
  if (game.status === "running") actions.append(button("Close Game", "stop", () => stopGame(), "primary"));
  else if (game.installed) actions.append(button("Play", "cross", () => launch(game), "primary"));
  if (game.valid && !game.installed && game.status !== "running") actions.append(button("Install", "install", () => installGame(game), game.installed ? "" : "primary"));
  if (game.valid && game.installed) actions.append(button("Reinstall", "install", () => installGame(game)));
  actions.append(button("Options", "triangle", () => openGameMenu(game)));
  hub.append(actions);
  const cards = el("div", { class: "hub-cards" });
  cards.append(card("Compatibility", compatibilityText(game), game.installed ? "Press to run the import audit" : (game.problems || []).join(". ") || "Install to audit imports", () => game.installed ? runAudit(game) : showScreen("installer"), `comp:${game.id}`, compatibilityClass(game)));
  cards.append(card("Last session", game.last_exit == null ? "Never launched" : game.last_exit === 0 ? "Exited normally" : game.last_exit < 0 ? "Closed by the launcher" : `Exit code ${game.last_exit}`, game.last_error || (game.launches ? `${game.launches} launches` : "Logs appear here after the first run"), () => showLog(game), `log:${game.id}`, game.last_exit > 0 ? "bad" : ""));
  cards.append(card("Controls", game.has_input ? "Custom keyboard mapping" : "Built-in mapping", "DualSense, Xbox and keyboard bindings", () => showInputEditor(game), `input:${game.id}`));
  cards.append(card("Save data", game.has_save ? "Save data present" : "No save data yet", game.has_save ? "Back up or open the _sd folder" : "Created on first save", () => openGameMenu(game), `save:${game.id}`));
  hub.append(cards);
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600), minutes = Math.floor((seconds % 3600) / 60);
  return hours ? `${hours} h ${minutes} min` : `${minutes || 1} min`;
}

function button(label, icon, handler, variant = "") {
  const glyph = ["cross", "circle", "triangle", "square"].includes(icon) ? `<i class="glyph ${icon}"></i>` : (ICONS[icon] ? `<span class="glyph" style="border:0">${ICONS[icon]}</span>` : "");
  const node = el("button", { class: `btn ${variant}`, "data-focus": true, "data-key": `btn:${label}`, html: `${glyph}<span>${escapeHtml(label)}</span>` });
  node.addEventListener("click", handler);
  return node;
}

function card(kicker, title, text, handler, key, tone = "") {
  const node = el("div", { class: "card", "data-focus": true, "data-key": key }, [
    el("div", { class: "card-kicker", text: kicker }),
    el("div", { class: `card-title ${tone}`, text: title }),
    el("div", { class: "card-text", text: text }),
  ]);
  if (tone) node.querySelector(".card-title").style.color = { ok: "#8ff3b9", warn: "#ffd978", bad: "#ff9c9c" }[tone] || "";
  node.addEventListener("click", handler);
  return node;
}

function primaryAction(game) {
  if (game.status === "running") return openGameMenu(game);
  if (game.installed) return launch(game);
  if (game.valid) return installGame(game);
  return dialog({ title: "Cannot convert this title", text: (game.problems || []).join("\n") || "The dump is incomplete.", buttons: [{ label: "OK" }] });
}

async function launch(game) {
  if (!game.installed) return;
  try {
    await api("launch", { id: game.id });
    toast("Launching", game.title);
    sound("open");
    await refresh({ quiet: true });
    renderScreen(state.screen, { keepFocus: true });
  } catch (error) {
    sound("error");
    dialog({ title: "Cannot start the game", text: error.message, buttons: [{ label: "OK" }] });
  }
}

async function stopGame() {
  try {
    await api("stop", {});
    await refresh({ quiet: true });
    renderScreen(state.screen, { keepFocus: true });
  } catch (error) { dialog({ title: "Error", text: error.message, buttons: [{ label: "OK" }] }); }
}

function installGame(game) {
  state.installer.source = game.source;
  state.installer.inspect = null;
  showScreen("installer");
}

async function runAudit(game) {
  try {
    const result = await api("audit", { id: game.id });
    openConsole({ title: `Import audit · ${game.title}`, job: result.job, game, kind: "audit" });
  } catch (error) { dialog({ title: "Audit unavailable", text: error.message, buttons: [{ label: "OK" }] }); }
}

function showLog(game) {
  openConsole({ title: `Log · ${game.title}`, game, kind: "log" });
}

function openGameMenu(game) {
  const menu = $("#sidemenu");
  const head = $("#sidemenuHead");
  head.innerHTML = "";
  const tile = tileNode(game, { noLabel: true, noBadge: true });
  tile.removeAttribute("data-focus");
  head.append(tile, el("div", {}, [el("div", { class: "name", text: game.title }), el("div", { class: "sub", text: [game.title_id, game.installed ? "Installed" : "Not installed"].filter(Boolean).join(" · ") })]));
  const list = $("#sidemenuList");
  list.innerHTML = "";
  const items = [];
  if (game.status === "running") items.push(["Close game", "stop", () => { closeSideMenu(); stopGame(); }]);
  else if (game.installed) items.push(["Play", "play", () => { closeSideMenu(); launch(game); }]);
  if (game.valid) items.push([game.installed ? "Reinstall (convert again)" : "Install", "install", () => { closeSideMenu(); installGame(game); }]);
  if (game.installed) items.push(["Check compatibility (import audit)", "audit", () => { closeSideMenu(); runAudit(game); }]);
  items.push(["View log", "log", () => { closeSideMenu(); showLog(game); }]);
  if (game.installed) items.push(["Controller & keyboard mapping", "pad", () => { closeSideMenu(); showInputEditor(game); }]);
  if (game.installed) items.push(["Game settings", "settings", () => { closeSideMenu(); state.gameSettingsId = game.id; showScreen("gamesettings"); }]);
  if (game.has_save) items.push(["Back up save data", "save", async () => { closeSideMenu(); try { const result = await api("save-backup", { id: game.id }); toast("Save data backed up", result.archive); } catch (error) { dialog({ title: "Backup failed", text: error.message, buttons: [{ label: "OK" }] }); } }]);
  if (game.has_save) items.push(["Open save data folder", "folder", () => openFolder(game.id, "save")]);
  if (game.installed) items.push(["Open installed folder", "folder", () => openFolder(game.id, "run")]);
  if (game.source) items.push(["Open dump folder", "folder", () => openFolder(game.id, "source")]);
  if (game.installed) items.push(["Remove installed build", "trash", () => { closeSideMenu(); removeGame(game); }, "danger"]);
  for (const [label, icon, handler, cls] of items) {
    const node = el("button", { class: `menuitem ${cls || ""}`, "data-focus": true, "data-key": `menu:${label}`, html: `${ICONS[icon]}<span>${escapeHtml(label)}</span>` });
    node.addEventListener("click", handler);
    list.append(node);
  }
  menu.hidden = false;
  sound("open");
  updateHints();
  requestAnimationFrame(() => focusFirst());
}

function closeSideMenu() {
  if ($("#sidemenu").hidden) return;
  $("#sidemenu").hidden = true;
  focusFirst(state.focusMemory[state.screen] || $(`[data-key="tile:${CSS.escape(state.selectedTile || "")}"]`));
}

async function openFolder(id, what) {
  closeSideMenu();
  try { await api("open", { id, what }); } catch (error) { dialog({ title: "Cannot open folder", text: error.message, buttons: [{ label: "OK" }] }); }
}

async function removeGame(game) {
  const choice = await dialog({ title: `Remove ${game.title}?`, text: "The converted executable, linked resources, logs and save data in the installed folder are deleted. The original dump is kept.", buttons: [{ label: "Cancel", value: null }, { label: "Remove", value: true, variant: "danger" }] });
  if (!choice) return;
  try { await api("remove", { id: game.id }); await refresh(); } catch (error) { dialog({ title: "Remove failed", text: error.message, buttons: [{ label: "OK" }] }); }
}

function renderHomebrew() {
  const grid = $("#homebrewGrid");
  grid.innerHTML = "";
  const host = state.data.host;
  const tools = [
    ["Package Installer", "install", "Convert a dump folder into a native build with the relinker.", () => showScreen("installer")],
    ["Import Audit", "audit", "Lists every system function a title imports and whether this build provides it, before you launch.", () => pickGame("Audit which title?", (game) => runAudit(game), (game) => game.installed)],
    ["Game Logs", "log", "Console output of the last run, with the throw message that stopped the game.", () => pickGame("Show the log of which title?", (game) => showLog(game))],
    ["Controller Mapper", "pad", "Edit anyps5-input.ini per title: keyboard and mouse bindings for every pad action.", () => pickGame("Map controls for which title?", (game) => showInputEditor(game), (game) => game.installed)],
    ["Save Data Manager", "save", "Back up save data to a zip or open the _sd folder of a title.", () => pickGame("Which title?", (game) => openGameMenu(game), (game) => game.installed)],
    ["Shader Cache", "cache", "Clear the SPIR-V shader cache of every installed title and the custom cache folder.", clearShaderCache],
    ["Themes", "home", `Switch between the PS5, PS4, PS3 and PS1 looks. Current: ${THEMES[currentTheme()].label}.`, chooseTheme],
    ["GPU Selector", "gpu", "Pick which Vulkan device runs the games (ANYPS5_GPU).", () => openSettings("graphics")],
    ["Debug Settings", "debug", "Deprecated relinker flags, syscall checks and binding modes. Unstable, for investigation only.", () => openSettings("debug")],
    ["Game Library", "grid", "Everything in the games folder and the installed folder.", () => showScreen("library")],
    ["Documentation", "docs", "Usage, input mapping and the verified compatibility list bundled with this build.", () => showScreen("docs")],
    ["System Information", "info", `${host.os} · ${host.cpu_vendor.toUpperCase()} CPU · ${host.libs_count} system libraries`, () => openSettings("system")],
    ["Rescan Games", "refresh", "Look for new dumps in the games folder.", async () => { await api("scan", {}); await refresh(); toast("Library rescanned", `${state.data.games.length} titles`); }],
  ];
  for (const [name, icon, text, handler] of tools) {
    const node = el("div", { class: "tool", "data-focus": true, "data-key": `tool:${name}`, html: `${ICONS[icon]}<div class="tool-name">${escapeHtml(name)}</div><div class="tool-desc">${escapeHtml(text)}</div>` });
    node.addEventListener("click", handler);
    grid.append(node);
  }
}

function openSettings(section) {
  state.settingsSection = section;
  showScreen("settings");
}

async function clearShaderCache() {
  const choice = await dialog({ title: "Clear shader cache?", text: "Games recompile their shaders on the next run, so the first minutes are slower.", buttons: [{ label: "Cancel", value: null }, { label: "Clear", value: true }] });
  if (!choice) return;
  try { const result = await api("clear-shader-cache", {}); toast("Shader cache cleared", `${result.count} folder(s)`); } catch (error) { dialog({ title: "Error", text: error.message, buttons: [{ label: "OK" }] }); }
}

function pickGame(title, handler, filter = () => true) {
  const games = state.data.games.filter(filter);
  if (!games.length) return dialog({ title, text: "No matching title. Install a game first.", buttons: [{ label: "OK" }] });
  dialog({ title, options: games.map((game) => ({ label: game.title, sub: game.title_id, value: game })), buttons: [{ label: "Cancel", value: null }] }).then((game) => { if (game) handler(game); });
}

function renderLibrary() {
  const chips = $("#libraryChips");
  chips.innerHTML = "";
  for (const [key, label] of [["all", "All"], ["installed", "Installed"], ["pending", "Not installed"], ["blocked", "Needs attention"]]) {
    const chip = el("button", { class: `chip ${state.libraryFilter === key ? "active" : ""}`, "data-focus": true, "data-key": `chip:${key}`, text: label });
    chip.addEventListener("click", () => { state.libraryFilter = key; renderLibrary(); focusFirst($(`[data-key="chip:${key}"]`)); });
    chips.append(chip);
  }
  const grid = $("#libraryGrid");
  grid.innerHTML = "";
  const games = state.data.games.filter((game) => state.libraryFilter === "all" || (state.libraryFilter === "installed" && game.installed) || (state.libraryFilter === "pending" && !game.installed && game.valid) || (state.libraryFilter === "blocked" && !game.valid));
  if (!games.length) grid.append(el("div", { class: "hub-empty", text: "Nothing here yet." }));
  for (const game of games) {
    const tile = tileNode(game, { noLabel: true });
    tile.removeAttribute("data-focus");
    const item = el("div", { class: "libitem", "data-focus": true, "data-key": `lib:${game.id}` }, [tile, el("div", { class: "lib-name", text: game.title }), el("div", { class: "lib-sub", text: [game.title_id, game.installed ? "Installed" : game.valid ? "Not installed" : "Needs attention"].filter(Boolean).join(" · ") })]);
    item.addEventListener("click", () => { state.selectedTile = game.id; openGameMenu(game); });
    grid.append(item);
  }
}

const SETTINGS_SECTIONS = [
  ["paths", "Paths", "folder"], ["conversion", "Conversion", "install"], ["graphics", "Graphics", "gpu"], ["runtime", "Runtime", "settings"], ["debug", "Debug Settings", "debug"], ["interface", "Interface", "home"], ["system", "System", "info"],
];

function settingsRows(section) {
  const host = state.data.host;
  const settings = state.data.settings;
  const windowsOnly = host.platform === "windows";
  const rows = {
    paths: [
      { group: "Folders" },
      { key: "games_dir", label: "Games folder", help: "One sub-folder per title dump (executable, sce_sys/, sce_module/).", type: "folder" },
      { key: "install_dir", label: "Installed builds folder", help: "Converted executables, linked resources, logs and save data live here.", type: "folder" },
      { group: "Tools" },
      { key: "relinker", label: "relinker executable", help: host.relinker ? `Using ${host.relinker}` : "Not found. Build the package or point this at relinker.", type: "file", status: host.relinker ? "ok" : "bad" },
      { key: "libs", label: "System libraries (libs/)", help: host.libs ? `${host.libs_count} .prx in ${host.libs}` : "Not found. Build the libs target or point this at the libs folder.", type: "folder", status: host.libs ? "ok" : "bad" },
      { key: "fonts", label: "System fonts folder", help: "Linked as anyps5-fonts/ beside each game for sceFontOpenFontSet (SST or Noto fonts).", type: "folder" },
    ],
    conversion: [
      { group: "relinker options for new installs" },
      { key: "to_intel", label: "Convert AMD-only instructions (--to-intel)", help: `Auto uses the host CPU: ${host.cpu_vendor.toUpperCase()} detected.`, type: "select", options: [["auto", "Auto"], ["on", "Always"], ["off", "Never"]] },
      { key: "unused_filter", label: "Unused import filter", help: "0 keeps every import; 1 filters unused non-PLT imports; 2 is strict and compacts the PLT.", type: "select", options: [[0, "0 · Keep all"], [1, "1 · Filter"], [2, "2 · Strict"]] },
      { key: "windows_gui", label: "Windows GUI subsystem (--windows-gui)", help: "No console window behind the game.", type: "toggle", hidden: !windowsOnly },
      { key: "windows_diagnostics", label: "Startup dependency diagnostics", help: "Adds --windows-diagnostics to report missing DLLs at start.", type: "toggle", hidden: !windowsOnly },
      { key: "copy_resources", label: "Copy resources instead of linking", help: "Links keep the dump as the single copy; copying doubles disk use but works on any file system.", type: "toggle" },
      { key: "rpath", label: "Library search path (--rpath)", help: "Leave empty for $ORIGIN/libs.", type: "text" },
    ],
    graphics: [
      { group: "GPU" },
      { key: "gpu", label: "Vulkan device (ANYPS5_GPU)", help: "Part of a device name, case-insensitive. Empty picks the first discrete GPU.", type: "gpu" },
      { key: "shader_cache", label: "Shader disk cache", help: "Keeps compiled SPIR-V between runs.", type: "toggle" },
      { key: "shader_cache_dir", label: "Shader cache folder", help: "Empty uses shader_cache/ beside each game.", type: "folder" },
      { action: "Clear shader cache", handler: clearShaderCache },
    ],
    runtime: [
      { group: "Runtime environment" },
      { key: "entitlements", label: "Entitlements file (ANYPS5_ENTITLEMENTS)", help: "Optional file for NpEntitlementAccess.", type: "file" },
      { key: "require_vulkan", label: "Require Vulkan (ANYPS5_REQUIRE_VULKAN)", help: "Fail at start instead of running without a usable device.", type: "toggle" },
      { key: "require_display", label: "Require display (ANYPS5_REQUIRE_DISPLAY)", type: "toggle" },
    ],
    debug: [
      { group: "Deprecated relinker flags · the game will be extremely unstable" },
      { key: "skip_sce_module", label: "Skip bundled modules (--skip-sce-module)", type: "toggle" },
      { key: "exclude_modules", label: "Exclude bundled modules (--exclude-sce-module)", help: "Comma-separated file names.", type: "text" },
      { key: "skip_syscall_check", label: "Skip syscall check (--skip-syscall-check)", type: "toggle" },
      { key: "lazy_binding", label: "Lazy symbol binding (--lazy-binding)", help: "Incompatible with bundled modules.", type: "toggle" },
      { group: "Diagnostics" },
      { action: "Open config folder", handler: () => api("open", { path: host.config }).catch((error) => toast("Error", error.message)) },
      { action: "Rescan games folder", handler: async () => { await api("scan", {}); await refresh(); toast("Rescanned", `${state.data.games.length} titles`); } },
    ],
    interface: [
      { group: "Look & feel" },
      { key: "profile_name", label: "Profile name", type: "text" },
      { key: "theme", label: "Theme", help: "PS5, PS4, PS3 XrossMediaBar or PS1. Each has its own menu sounds.", type: "select", options: Object.entries(THEMES).map(([value, theme]) => [value, theme.label]) },
      { key: "ui_sounds", label: "UI sounds", type: "toggle" },
      { key: "clock_24h", label: "24-hour clock", type: "toggle" },
      { action: "Toggle fullscreen", handler: toggleFullscreen },
    ],
    system: [
      { group: "This PC" },
      { info: "Operating system", value: host.os },
      { info: "CPU", value: `${host.cpu} (${host.cpu_vendor})` },
      { info: "relinker", value: host.relinker || "not found" },
      { info: "System libraries", value: host.libs ? `${host.libs_count} in ${host.libs}` : "not found" },
      { info: "Package", value: host.package },
      { info: "Build commit", value: host.commit || "source tree" },
      { info: "Config", value: host.config },
      { info: "Python", value: host.python },
      { group: "Launcher" },
      { action: "Exit launcher", handler: quitLauncher, danger: true },
    ],
  };
  return (rows[section] || []).filter((row) => !row.hidden).map((row) => ({ ...row, value: row.key ? settings[row.key] : undefined }));
}

function renderSettings() {
  const nav = $("#settingsNav");
  nav.innerHTML = "";
  for (const [key, label, icon] of SETTINGS_SECTIONS) {
    const item = el("button", { class: `navitem ${state.settingsSection === key ? "active" : ""}`, "data-focus": true, "data-key": `nav:${key}`, html: `${ICONS[icon]}<span>${escapeHtml(label)}</span>` });
    item.addEventListener("click", () => { state.settingsSection = key; renderSettings(); setFocus(item, { silent: true }); });
    item.addEventListener("focused", () => { if (state.settingsSection !== key) { state.settingsSection = key; renderSettingsBody($("#settingsBody"), settingsRows(key), saveSetting); $$(".navitem").forEach((node) => node.classList.toggle("active", node.dataset.key === `nav:${key}`)); } });
    nav.append(item);
  }
  renderSettingsBody($("#settingsBody"), settingsRows(state.settingsSection), saveSetting);
}

async function saveSetting(key, value) {
  try {
    await api("settings", { [key]: value });
    await refresh({ quiet: true });
    renderScreen(state.screen, { keepFocus: true });
  } catch (error) { dialog({ title: "Cannot save", text: error.message, buttons: [{ label: "OK" }] }); }
}

function renderSettingsBody(body, rows, save) {
  body.innerHTML = "";
  for (const row of rows) {
    if (row.group) { body.append(el("div", { class: "group-title", text: row.group })); continue; }
    if (row.info) { body.append(el("div", { class: "status-line", html: `${escapeHtml(row.info)}: <b>${escapeHtml(row.value || "")}</b>` })); continue; }
    const node = el("div", { class: `row ${row.action ? "action" : ""} ${row.danger ? "danger" : ""}`, "data-focus": true, "data-key": `row:${row.key || row.action}` });
    const left = el("div", {}, [el("div", { class: "row-label", text: row.label || row.action })]);
    if (row.help) left.append(el("div", { class: "row-help", text: row.help }));
    node.append(left);
    const right = el("div", { class: "row-value" });
    node.append(right);
    if (row.action) {
      right.append(el("span", { class: "arrow", text: "›" }));
      node.addEventListener("click", row.handler);
    } else if (row.type === "toggle") {
      right.append(el("div", { class: `toggle ${row.value ? "on" : ""}` }));
      node.addEventListener("click", () => save(row.key, !row.value));
    } else if (row.type === "select") {
      const current = row.options.find(([value]) => String(value) === String(row.value)) || row.options[0];
      right.append(el("span", { text: current[1] }), el("span", { class: "arrow", text: "›" }));
      node.addEventListener("click", async () => {
        const choice = await dialog({ title: row.label, options: row.options.map(([value, label]) => ({ label, value, active: String(value) === String(row.value) })), buttons: [{ label: "Cancel", value: undefined }] });
        if (choice !== undefined && choice !== null) save(row.key, choice);
      });
    } else if (row.type === "gpu") {
      right.append(el("span", { text: row.value || "Automatic" }), el("span", { class: "arrow", text: "›" }));
      node.addEventListener("click", async () => {
        let gpus = [];
        try { gpus = (await api("gpus")).gpus; } catch (error) { gpus = []; }
        const options = [{ label: "Automatic (first discrete GPU)", value: "" }, ...gpus.map((name) => ({ label: name, value: name })), { label: "Type a name…", value: "__custom" }];
        const choice = await dialog({ title: "Vulkan device", text: gpus.length ? "" : "Run a game once or install vulkaninfo to list devices here.", options, buttons: [{ label: "Cancel", value: undefined }] });
        if (choice === "__custom") { const typed = await prompt("Vulkan device name", row.value || ""); if (typed !== null) save(row.key, typed); }
        else if (choice !== undefined) save(row.key, choice);
      });
    } else {
      right.append(el("span", { text: row.value ? shortenPath(row.value) : (row.type === "text" ? "—" : "Not set"), title: row.value || "" }), el("span", { class: "arrow", text: "›" }));
      node.addEventListener("click", async () => {
        if (row.type === "folder" || row.type === "file") {
          const choice = await dialog({ title: row.label, text: row.value || "Not set", buttons: [{ label: "Browse…", value: "browse" }, { label: "Type path", value: "type" }, { label: "Clear", value: "clear" }, { label: "Cancel", value: undefined }] });
          if (choice === "browse") {
            const picked = await api("pick-folder", { title: row.label }).catch(() => ({ path: "" }));
            if (picked.path) save(row.key, picked.path);
            else if (row.type === "file") { const typed = await prompt(row.label, row.value || ""); if (typed !== null) save(row.key, typed); }
          } else if (choice === "type") { const typed = await prompt(row.label, row.value || ""); if (typed !== null) save(row.key, typed); }
          else if (choice === "clear") save(row.key, "");
        } else {
          const typed = await prompt(row.label, row.value || "");
          if (typed !== null) save(row.key, typed);
        }
      });
    }
    body.append(node);
  }
}

function renderGameSettings() {
  const game = state.data.games.find((item) => item.id === state.gameSettingsId);
  const body = $("#gameSettingsBody");
  if (!game) { body.innerHTML = ""; return; }
  $("#gameSettingsTitle").textContent = `${game.title} · Settings`;
  const overrides = game.overrides || {};
  const rows = [
    { group: "Graphics" },
    { key: "gpu", label: "Vulkan device", help: "Overrides ANYPS5_GPU for this title.", type: "gpu", value: overrides.gpu || "" },
    { key: "shader_cache", label: "Shader disk cache", type: "toggle", value: overrides.shader_cache !== false },
    { group: "Runtime" },
    { key: "fonts", label: "System fonts folder", type: "folder", value: overrides.fonts || "" },
    { key: "entitlements", label: "Entitlements file", type: "file", value: overrides.entitlements || "" },
    { key: "require_vulkan", label: "Require Vulkan", type: "toggle", value: !!overrides.require_vulkan },
    { group: "Install" },
    { info: "Conversion command", value: (game.install && game.install.command || []).join(" ") || "not installed" },
    { info: "Installed", value: game.install && game.install.installed ? new Date(game.install.installed * 1000).toLocaleString() : "—" },
    { action: "Reset overrides", handler: () => saveGameSetting(game.id, null) },
  ];
  renderSettingsBody(body, rows, (key, value) => saveGameSetting(game.id, { ...overrides, [key]: value }));
}

async function saveGameSetting(id, overrides) {
  try {
    await api("game-settings", { id, overrides: overrides || {} });
    await refresh({ quiet: true });
    renderScreen("gamesettings", { keepFocus: true });
  } catch (error) { dialog({ title: "Cannot save", text: error.message, buttons: [{ label: "OK" }] }); }
}

function renderInstaller() {
  const root = $("#installer");
  root.innerHTML = "";
  const left = el("div", { class: "col" });
  const right = el("div", { class: "col" });
  root.append(left, right);
  const installer = state.installer;
  const host = state.data.host;
  const settings = state.data.settings;
  const options = installer.options;
  const rows = [
    { group: "Source" },
    { action: installer.source ? shortenPath(installer.source) : "Choose the dump folder…", handler: chooseSource, label: "Dump folder", help: installer.source || "" },
    { action: "Pick from the games folder", handler: () => pickGame("Which title?", (game) => { installer.source = game.source; installer.inspect = null; renderInstaller(); inspectSource(); }, (game) => game.valid) },
  ];
  renderSettingsBody(left, rows, () => {});
  const inspectBox = el("div", { id: "inspectBox" });
  left.append(inspectBox);
  renderInspect(inspectBox);
  const optionRows = [
    { group: "Options for this conversion" },
    { key: "to_intel", label: "Convert AMD-only instructions", help: `Default: ${settings.to_intel} (${host.cpu_vendor.toUpperCase()} CPU)`, type: "select", options: [["auto", "Auto"], ["on", "Always"], ["off", "Never"]], value: options.to_intel ?? settings.to_intel },
    { key: "unused_filter", label: "Unused import filter", type: "select", options: [[0, "0 · Keep all"], [1, "1 · Filter"], [2, "2 · Strict"]], value: options.unused_filter ?? settings.unused_filter },
    { key: "copy_resources", label: "Copy resources instead of linking", type: "toggle", value: options.copy_resources ?? settings.copy_resources },
    { key: "windows_gui", label: "Windows GUI subsystem", type: "toggle", value: options.windows_gui ?? settings.windows_gui, hidden: host.platform !== "windows" },
  ].filter((row) => !row.hidden);
  const optionBox = el("div");
  left.append(optionBox);
  renderSettingsBody(optionBox, optionRows, (key, value) => { options[key] = value; renderInstaller(); focusFirst($(`[data-key="row:${CSS.escape(key)}"]`)); });
  const actions = el("div", { class: "hub-actions", style: "margin: 18px 18px 30px" });
  const ready = installer.inspect && installer.inspect.valid && host.relinker && host.libs && !(installer.job && installer.job.status === "running");
  const convert = button(installer.job && installer.job.status === "running" ? "Converting…" : "Convert & Install", "install", startInstall, "primary");
  convert.disabled = !ready;
  if (!ready) convert.removeAttribute("data-focus");
  actions.append(convert);
  left.append(actions);
  const title = el("div", { class: "group-title", text: "relinker output" });
  const output = el("pre", { class: "console", id: "installLog" });
  right.append(title, output);
  renderInstallLog();
  if (installer.source && !installer.inspect) inspectSource();
}

function renderInspect(box) {
  box.innerHTML = "";
  const info = state.installer.inspect;
  if (!info) return;
  const tile = el("div", { class: "tile" });
  if (info.icon) tile.style.backgroundImage = `url(/api/icon?id=${encodeURIComponent(info.id)}&t=${TOKEN})`;
  else tile.append(el("div", { class: "tile-initials", text: initials(info.title), style: `background: ${gradientFor(info.title)}` }));
  const text = el("div", {}, [
    el("div", { class: "inspect-title", text: info.title || "Unknown title" }),
    el("div", { class: "inspect-meta", html: [info.title_id, info.content_id, info.version ? `v${info.version}` : "", info.module_dir ? `modules in ${info.module_dir}/` : "", info.executable ? `${info.executable.split(/[\\/]/).pop()} (${{ elf: "clean ELF", self: "SELF container", missing: "missing", unknown: "unknown format" }[info.executable_status] || info.executable_status})` : ""].filter(Boolean).map(escapeHtml).join(" · ") }),
  ]);
  for (const problem of info.problems || []) text.append(el("div", { class: "problem", text: problem }));
  if (info.valid) text.append(el("div", { class: "inspect-meta", html: `<span class="pill ok"><span class="dot"></span>Ready to convert</span>` }));
  box.append(el("div", { class: "inspect" }, [tile, text]));
}

async function chooseSource() {
  const choice = await dialog({ title: "Dump folder", text: state.installer.source || "Select the folder with the executable, sce_sys/ and sce_module/.", buttons: [{ label: "Browse…", value: "browse" }, { label: "Type path", value: "type" }, { label: "Cancel", value: undefined }] });
  let path = null;
  if (choice === "browse") { const picked = await api("pick-folder", { title: "Select the title dump folder" }).catch(() => ({ path: "" })); path = picked.path || await prompt("Dump folder", state.installer.source); }
  else if (choice === "type") path = await prompt("Dump folder", state.installer.source);
  if (path) { state.installer.source = path; state.installer.inspect = null; renderInstaller(); inspectSource(); }
}

async function inspectSource() {
  try {
    state.installer.inspect = await api(`inspect?source=${encodeURIComponent(state.installer.source)}`);
  } catch (error) {
    state.installer.inspect = { valid: false, problems: [error.message], title: state.installer.source };
  }
  if (state.screen === "installer") { renderInstaller(); if (!focusables().includes(state.focus)) focusFirst(); }
}

async function startInstall() {
  const installer = state.installer;
  try {
    const result = await api("install", { source: installer.source, options: installer.options });
    installer.job = { id: result.job, status: "running", log: [] };
    renderInstaller();
    focusFirst($('[data-key="btn:Converting…"]') || $('[data-key="row:Pick from the games folder"]'));
    pollJob(result.job, (job) => {
      installer.job = job;
      renderInstallLog();
      if (job.status !== "running") {
        refresh().then(() => { renderInstaller(); focusFirst(); });
        if (job.status === "done") { toast("Installed", installer.inspect.title); sound("open"); }
        else { sound("error"); toast("Conversion failed", job.error); }
      }
    });
  } catch (error) {
    sound("error");
    dialog({ title: "Cannot start", text: error.message, buttons: [{ label: "OK" }] });
  }
}

function renderInstallLog() {
  const output = $("#installLog");
  if (!output) return;
  const job = state.installer.job;
  output.innerHTML = job ? job.log.map((line) => `<span class="${/^FAIL|error|exited with/i.test(line) ? "err" : /^Installing|Output file|Package ready/.test(line) ? "ok" : ""}">${escapeHtml(line)}</span>`).join("\n") : "The relinker output appears here.";
  output.scrollTop = output.scrollHeight;
}

function pollJob(id, callback) {
  const timer = setInterval(async () => {
    try {
      const job = await api(`job?id=${id}`);
      callback(job);
      if (job.status !== "running") clearInterval(timer);
    } catch (error) { clearInterval(timer); }
  }, 500);
}

function openConsole({ title, job, game, kind }) {
  state.consoleJob = job || null;
  state.consoleGame = game || null;
  $("#consoleTitle").textContent = title;
  const out = $("#consoleOut");
  const summary = $("#consoleSummary");
  const tools = $("#consoleTools");
  summary.innerHTML = "";
  tools.innerHTML = "";
  out.textContent = "";
  tools.append(button("Copy", "log", () => navigator.clipboard && navigator.clipboard.writeText(out.textContent).then(() => toast("Copied", "Log copied to the clipboard")), "small"));
  if (game) tools.append(button("Open folder", "folder", () => api("open", { id: game.id, what: "run" }).catch((error) => toast("Error", error.message)), "small"));
  showScreen("console");
  if (kind === "log") {
    tools.append(button("Refresh", "refresh", () => loadLog(game), "small"));
    loadLog(game);
  } else if (job) {
    pollJob(job, (data) => {
      out.innerHTML = data.log.map((line) => `<span class="${/^FAIL|absent|not load/i.test(line) ? "err" : /Nothing blocks/.test(line) ? "ok" : ""}">${escapeHtml(line)}</span>`).join("\n");
      out.scrollTop = out.scrollHeight;
      if (data.status !== "running") {
        renderAuditSummary(summary, data.result);
        refresh({ quiet: true });
      }
    });
  }
}

async function loadLog(game) {
  const out = $("#consoleOut");
  try {
    const result = await api(`log?id=${encodeURIComponent(game.id)}`);
    out.innerHTML = result.lines.length ? result.lines.map((line) => `<span class="${/error|terminate|what\(\)|FAIL/i.test(line) ? "err" : ""}">${escapeHtml(line)}</span>`).join("\n") : "No log yet. Launch the game once.";
    out.scrollTop = out.scrollHeight;
  } catch (error) { out.textContent = error.message; }
}

function renderAuditSummary(summary, result) {
  summary.innerHTML = "";
  if (!result || !result.unique_by_class) return;
  const classes = result.unique_by_class;
  summary.append(stat("Implemented", classes.implemented || 0, "ok"), stat("Stubs", classes.stub || 0, classes.stub ? "warn" : ""), stat("Absent", classes.absent || 0, classes.absent ? "bad" : "ok"), stat("Title modules", classes.module || 0, ""), stat("Missing libraries", (result.missing_libraries || []).length, (result.missing_libraries || []).length ? "bad" : "ok"));
  const absent = (result.imports || []).filter((entry) => entry.class === "absent").slice(0, 40);
  if (absent.length) summary.append(el("div", { class: "hub-empty", style: "width:100%", html: `<strong>Absent imports:</strong> ${absent.map((entry) => escapeHtml(`${entry.library || ""}:${entry.name || entry.nid}`)).join(", ")}${result.unique_by_class.absent > absent.length ? " …" : ""}` }));
}

function stat(label, value, tone) {
  return el("div", { class: `stat ${tone}`, html: `<b>${escapeHtml(String(value))}</b><span>${escapeHtml(label)}</span>` });
}

async function showInputEditor(game) {
  state.inputGame = game;
  showScreen("input");
  const root = $("#inputEditor");
  root.innerHTML = "Loading…";
  $("#inputSub").textContent = `${game.title} · anyps5-input.ini beside the installed executable. Controllers are mapped automatically; these lines change keyboard and mouse bindings.`;
  let data;
  try { data = await api(`input?id=${encodeURIComponent(game.id)}`); } catch (error) { root.textContent = error.message; return; }
  root.innerHTML = "";
  const textarea = el("textarea", { "data-focus": true, "data-key": "input:text", spellcheck: "false", placeholder: "# Action = Type:Value\nCross = KEY:Space\nLeftStickUp = KEY:W\nSquare = MOUSE:Left" });
  textarea.value = data.text;
  const side = el("div", { class: "input-side" });
  side.append(el("div", { class: "hint-text", text: "Press ✕ on the editor to type, ○ to leave it. The first line for an action replaces its built-in binding; later lines add alternates." }));
  side.append(button("Save", "check", async () => { try { await api("input", { id: game.id, text: textarea.value }); toast("Saved", "anyps5-input.ini"); refresh({ quiet: true }); } catch (error) { dialog({ title: "Invalid mapping", text: error.message, buttons: [{ label: "OK" }] }); } }, "primary"));
  side.append(button("WASD preset", "pad", () => { textarea.value = "LeftStickUp = KEY:W\nLeftStickDown = KEY:S\nLeftStickLeft = KEY:A\nLeftStickRight = KEY:D\nCross = KEY:Space\nCircle = KEY:C\nSquare = KEY:F\nTriangle = KEY:E\nL1 = KEY:Q\nR1 = KEY:R\nL2 = MOUSE:Right\nR2 = MOUSE:Left\nOptions = KEY:Escape\nToggleMouse = KEY:Tab\nToggleFullscreen = KEY:F11\n"; }));
  side.append(button("Clear (built-in mapping)", "trash", () => { textarea.value = ""; }));
  side.append(el("div", { class: "hint-text", text: "Sources: KEY:<SDL key name>, MOUSE:Left|Middle|Right|X1|X2, WHEEL:Up|Down. Actions:" }));
  side.append(el("div", { class: "actions-list", html: data.actions.map((action) => `<code>${action}</code>`).join(" ") }));
  root.append(textarea, side);
  focusFirst($('[data-key="btn:Save"]'));
}

async function renderDocs() {
  const body = $("#docsBody");
  if (!state.docs) {
    body.innerHTML = "Loading…";
    try { state.docs = (await api("docs")).docs; } catch (error) { body.textContent = error.message; return; }
  }
  body.innerHTML = "";
  const nav = el("div", { class: "docs-nav" });
  const content = el("div", { class: "docs-body", tabindex: "-1" });
  body.append(nav, content);
  const show = (doc) => { content.innerHTML = markdown(doc.text); content.scrollTop = 0; $$(".navitem", nav).forEach((node) => node.classList.toggle("active", node.dataset.key === `doc:${doc.name}`)); };
  for (const doc of state.docs) {
    const item = el("button", { class: "navitem", "data-focus": true, "data-key": `doc:${doc.name}`, html: `${ICONS.docs}<span>${escapeHtml(doc.name.replace(/_/g, " "))}</span>` });
    item.addEventListener("focused", () => show(doc));
    item.addEventListener("click", () => show(doc));
    nav.append(item);
  }
  nav.append(el("div", { class: "hint-text", style: "margin-top:12px;font-size:13px;color:var(--muted)", text: "Scroll the page with the right stick, mouse wheel or Page Up/Down." }));
  if (state.docs[0]) show(state.docs[0]);
}

function markdown(text) {
  const lines = text.split("\n");
  let html = "", inCode = false, inTable = false, inList = false;
  const inline = (s) => escapeHtml(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  for (const line of lines) {
    if (line.startsWith("```")) { inCode = !inCode; html += inCode ? "<pre>" : "</pre>"; continue; }
    if (inCode) { html += escapeHtml(line) + "\n"; continue; }
    if (line.startsWith("|")) {
      const cells = line.split("|").slice(1, -1).map((cell) => cell.trim());
      if (cells.every((cell) => /^:?-+:?$/.test(cell))) continue;
      if (!inTable) { html += "<table>"; inTable = true; }
      html += "<tr>" + cells.map((cell) => `<td>${inline(cell)}</td>`).join("") + "</tr>";
      continue;
    } else if (inTable) { html += "</table>"; inTable = false; }
    if (/^\s*[-*] /.test(line)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inline(line.replace(/^\s*[-*] /, ""))}</li>`; continue; }
    else if (inList) { html += "</ul>"; inList = false; }
    const heading = line.match(/^(#{1,4}) (.*)/);
    if (heading) { html += `<h${heading[1].length + 1}>${inline(heading[2])}</h${heading[1].length + 1}>`; continue; }
    if (line.trim()) html += `<p>${inline(line)}</p>`;
  }
  if (inTable) html += "</table>";
  if (inList) html += "</ul>";
  if (inCode) html += "</pre>";
  return html;
}

function dialog({ title, text, buttons = [], options = null, input = null }) {
  return new Promise((resolve) => {
    const layer = $("#dialogLayer");
    const box = $("#dialog");
    box.innerHTML = "";
    state.dialogResolve = resolve;
    state.dialogFocus = state.focus;
    box.append(el("div", { class: "dialog-title", text: title }));
    if (text) box.append(el("div", { class: "dialog-text", text }));
    let field = null;
    if (input !== null) {
      field = el("input", { class: "dialog-input", "data-focus": true, "data-key": "dialog:input", value: input });
      field.addEventListener("keydown", (event) => { if (event.key === "Enter") { event.preventDefault(); closeDialog(field.value); } });
      box.append(field);
    }
    if (options) {
      const list = el("div", { class: "dialog-options" });
      for (const option of options) {
        const node = el("button", { class: `menuitem ${option.active ? "active" : ""}`, "data-focus": true, "data-key": `opt:${option.label}`, html: `${option.active ? ICONS.check : '<span style="width:22px"></span>'}<span>${escapeHtml(option.label)}</span>${option.sub ? `<small>${escapeHtml(option.sub)}</small>` : ""}` });
        node.addEventListener("click", () => closeDialog(option.value));
        list.append(node);
      }
      box.append(list);
    }
    const actions = el("div", { class: "dialog-actions" });
    for (const item of buttons) {
      const node = el("button", { class: `btn ${item.variant || (buttons.length === 1 || item.primary ? "primary" : "")}`, "data-focus": true, "data-key": `dlg:${item.label}`, text: item.label });
      node.addEventListener("click", () => closeDialog(item.value === undefined && buttons.length === 1 ? true : item.value));
      actions.append(node);
    }
    box.append(actions);
    layer.hidden = false;
    sound("open");
    requestAnimationFrame(() => { focusFirst(field || $(".dialog-options .active") || $(".dialog-actions .btn.primary") || null); if (field) field.focus(); });
  });
}

function prompt(title, value) {
  return dialog({ title, input: value || "", buttons: [{ label: "Cancel", value: null }, { label: "OK", value: "__ok", primary: true }] }).then((result) => {
    if (result === "__ok") return state.lastInputValue;
    return result;
  });
}

function closeDialog(value) {
  const layer = $("#dialogLayer");
  if (layer.hidden) return;
  const field = $("#dialog input");
  state.lastInputValue = field ? field.value : null;
  layer.hidden = true;
  const resolve = state.dialogResolve;
  state.dialogResolve = null;
  if (document.activeElement) document.activeElement.blur();
  const previous = state.dialogFocus;
  requestAnimationFrame(() => focusFirst(previous && focusables().includes(previous) ? previous : null));
  if (resolve) resolve(value);
}

function openControlCenter() {
  const panel = $("#controlCenter");
  if (!panel.hidden) { closeControlCenter(); return; }
  state.ccFocus = state.focus;
  const icons = $("#ccIcons");
  icons.innerHTML = "";
  const running = state.data.running;
  const game = running && state.data.games.find((item) => item.id === running.id);
  const settings = state.data.settings;
  const entries = [
    ["Home", "home", () => { closeControlCenter(); state.history = []; showScreen("home", { replace: true }); }],
    ["Notifications", "bell", showNotifications],
    [settings.ui_sounds ? "Sound on" : "Sound off", "sound", () => saveSetting("ui_sounds", !settings.ui_sounds).then(() => { closeControlCenter(); openControlCenter(); }), settings.ui_sounds],
    ["Controllers", "pad", showControllers],
    ["Fullscreen", "fullscreen", toggleFullscreen],
    [`Theme: ${THEMES[currentTheme()].label}`, "grid", () => { closeControlCenter(); cycleTheme(); }],
    ["Profile", "user", () => { closeControlCenter(); openSettings("interface"); }],
    ["Settings", "settings", () => { closeControlCenter(); openSettings("paths"); }],
    ["Power", "power", powerMenu],
  ];
  for (const [label, icon, handler, active] of entries) {
    const node = el("button", { class: `cc-icon ${active ? "active" : ""}`, "data-focus": true, "data-key": `cc:${label}`, html: `${ICONS[icon]}<span class="cc-label">${escapeHtml(label)}</span>` });
    node.addEventListener("click", handler);
    icons.append(node);
  }
  const cards = $("#ccCards");
  cards.innerHTML = "";
  if (game) {
    const cardNode = el("div", { class: "cc-card", "data-focus": true, "data-key": "cc:game" }, [el("div", { class: "card-kicker", text: "Now playing" }), el("div", { class: "card-title", text: game.title }), el("div", { class: "card-text", text: `PID ${running.pid} · running ${formatDuration(Math.floor(Date.now() / 1000 - running.started))} · press to close` })]);
    cardNode.addEventListener("click", async () => { const choice = await dialog({ title: `Close ${game.title}?`, text: "Unsaved progress is lost.", buttons: [{ label: "Cancel", value: null }, { label: "Close game", value: true, variant: "danger" }] }); if (choice) { closeControlCenter(); stopGame(); } });
    cards.append(cardNode);
  }
  const host = state.data.host;
  cards.append(el("div", { class: "cc-card" }, [el("div", { class: "card-kicker", text: "System" }), el("div", { class: "card-title", text: `${state.data.games.filter((item) => item.installed).length} installed · ${state.data.games.length} in library` }), el("div", { class: "card-text", text: `${host.libs_count} system libraries · ${host.cpu_vendor.toUpperCase()} CPU · ${host.platform}` })]));
  $("#ccStatus").textContent = game ? `Playing ${game.title}` : "Online";
  panel.hidden = false;
  sound("open");
  requestAnimationFrame(() => focusFirst());
}

function closeControlCenter() {
  const panel = $("#controlCenter");
  if (panel.hidden) return;
  panel.hidden = true;
  focusFirst(state.ccFocus);
}

function showNotifications() {
  const items = [...state.data.notifications].reverse();
  dialog({ title: "Notifications", text: items.length ? "" : "Nothing new.", options: items.map((item) => ({ label: item.title, sub: item.text, value: item })), buttons: [{ label: "Close", value: null }] });
}

function showControllers() {
  const pads = [...(navigator.getGamepads ? navigator.getGamepads() : [])].filter(Boolean);
  dialog({ title: "Controllers", text: pads.length ? pads.map((pad) => `${pad.id} (${pad.mapping || "custom"} mapping)`).join("\n") : "No controller detected by the browser. Press a button on the pad and try again. In games, controllers are handled by SDL and work regardless of this list.", buttons: [{ label: "OK" }] });
}

async function powerMenu() {
  const choice = await dialog({ title: "Power", options: [{ label: "Exit launcher", value: "quit" }, { label: "Close running game", value: "stop" }, { label: "Toggle fullscreen", value: "fullscreen" }], buttons: [{ label: "Cancel", value: null }] });
  if (choice === "quit") quitLauncher();
  else if (choice === "stop") { closeControlCenter(); stopGame(); }
  else if (choice === "fullscreen") toggleFullscreen();
}

async function quitLauncher() {
  const choice = await dialog({ title: "Exit AnyPS5 launcher?", text: state.data.running ? "The running game keeps running." : "", buttons: [{ label: "Cancel", value: null }, { label: "Exit", value: true, primary: true }] });
  if (!choice) return;
  try { await api("quit", {}); } catch (error) { }
  document.body.innerHTML = '<div style="display:grid;place-items:center;height:100%;color:#fff;font-size:22px">AnyPS5 launcher closed. You can close this window.</div>';
}

function toggleFullscreen() {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen().catch(() => toast("Fullscreen", "Press F11 in this window."));
}

function toast(title, text) {
  const node = el("div", { class: "toast", html: `<div class="t-icon">${ICONS.info}</div><div><div class="t-title">${escapeHtml(title)}</div><div class="t-text">${escapeHtml(text || "")}</div></div>` });
  $("#toasts").append(node);
  setTimeout(() => { node.classList.add("out"); setTimeout(() => node.remove(), 260); }, 5200);
}

function pressTriangle() {
  if (!$("#dialogLayer").hidden || !$("#controlCenter").hidden) return;
  if (!$("#sidemenu").hidden) { closeSideMenu(); return; }
  const focused = state.focus;
  const id = focused && (focused.dataset.game || (focused.dataset.key || "").split(":")[1]);
  const game = id && state.data.games.find((item) => item.id === id);
  if (game) openGameMenu(game);
  else if (state.screen === "home" && state.selectedTile) { const selected = state.data.games.find((item) => item.id === state.selectedTile); if (selected) openGameMenu(selected); }
}

function handleKey(event) {
  const editing = document.activeElement && (document.activeElement.tagName === "TEXTAREA" || document.activeElement.tagName === "INPUT");
  if (editing) {
    if (event.key === "Escape") { event.preventDefault(); if (document.activeElement.tagName === "INPUT") closeDialog(null); else document.activeElement.blur(); }
    return;
  }
  const map = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down" };
  if (map[event.key]) { event.preventDefault(); move(map[event.key]); return; }
  if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activate(); return; }
  if (event.key === "Escape" || event.key === "Backspace") { event.preventDefault(); goBack(); return; }
  if (event.key === "Tab") { event.preventDefault(); move(event.shiftKey ? "left" : "right"); return; }
  if (event.key.toLowerCase() === "t") { pressTriangle(); return; }
  if (event.key === "Home" || event.key.toLowerCase() === "p") { openControlCenter(); return; }
  if (event.key === "F11" || event.key.toLowerCase() === "f") { event.preventDefault(); toggleFullscreen(); return; }
  if (event.key.toLowerCase() === "y") { cycleTheme(); return; }
  if (event.key === "PageDown" || event.key === "PageUp") { const scroller = $(".docs-body") || $("#consoleOut"); if (scroller) scroller.scrollBy({ top: (event.key === "PageDown" ? 1 : -1) * scroller.clientHeight * 0.8, behavior: "smooth" }); }
}

function pollGamepads() {
  const pads = navigator.getGamepads ? navigator.getGamepads() : [];
  const now = performance.now();
  for (const pad of pads) {
    if (!pad) continue;
    const memory = state.gamepads[pad.index] || (state.gamepads[pad.index] = { buttons: [], repeat: {} });
    const press = (name, pressed) => {
      const was = memory.buttons[name] || false;
      const repeatAt = memory.repeat[name] || 0;
      let fire = false;
      if (pressed && !was) { fire = true; memory.repeat[name] = now + 380; }
      else if (pressed && now > repeatAt) { fire = true; memory.repeat[name] = now + 110; }
      memory.buttons[name] = pressed;
      return fire;
    };
    const button = (index) => !!(pad.buttons[index] && pad.buttons[index].pressed);
    const axisX = pad.axes[0] || 0, axisY = pad.axes[1] || 0, rightY = pad.axes[3] || 0;
    if (press("left", button(14) || axisX < -0.5)) move("left");
    if (press("right", button(15) || axisX > 0.5)) move("right");
    if (press("up", button(12) || axisY < -0.5)) move("up");
    if (press("down", button(13) || axisY > 0.5)) move("down");
    if (press("cross", button(0))) { const editing = document.activeElement && document.activeElement.tagName === "TEXTAREA"; if (!editing) activate(); }
    if (press("circle", button(1))) goBack();
    if (press("triangle", button(3))) pressTriangle();
    if (press("ps", button(16))) openControlCenter();
    if (press("options", button(9))) openControlCenter();
    if (Math.abs(rightY) > 0.3) { const scroller = $(".screen.active .docs-body") || $(".screen.active .console") || $(".screen.active .settings-body") || $(".screen.active .grid"); if (scroller) scroller.scrollBy({ top: rightY * 18 }); }
    memory.buttons.any = pad.buttons.some((item) => item.pressed);
  }
  requestAnimationFrame(pollGamepads);
}

function bootProblem(text) {
  const sub = $("#splash .splash-sub");
  if (sub) { sub.textContent = text; sub.style.textTransform = "none"; sub.style.letterSpacing = "0"; sub.style.maxWidth = "720px"; sub.style.margin = "14px auto 0"; sub.style.lineHeight = "1.5"; }
}

window.addEventListener("error", (event) => { if (!state.data) bootProblem(`The interface hit an error while starting: ${event.message}. Reload the page (F5); if it persists, open ${location.href} in Chrome or Edge.`); });
window.addEventListener("unhandledrejection", (event) => { if (!state.data) bootProblem(`Cannot reach the launcher: ${event.reason && event.reason.message ? event.reason.message : event.reason}. Is the PowerShell window still open?`); });

function init() {
  setTimeout(() => { if (!state.data) bootProblem(`Still waiting for the launcher at ${location.host}. Keep the terminal window open, then reload this page (F5).`); }, 8000);
  document.addEventListener("keydown", handleKey);
  document.addEventListener("mouseover", (event) => { const node = event.target.closest("[data-focus]"); if (node && node !== state.focus && focusables().includes(node)) setFocus(node); });
  document.addEventListener("click", (event) => { const node = event.target.closest("[data-focus]"); if (node && node !== state.focus) { state.focus = node; } });
  $$(".tab").forEach((tab) => tab.addEventListener("click", () => { state.history = []; showScreen(tab.dataset.tab, { replace: true }); }));
  $('[data-action="settings"]').addEventListener("click", () => openSettings(state.settingsSection));
  $('[data-action="profile"]').addEventListener("click", openControlCenter);
  $('[data-action="search"]').addEventListener("click", async () => {
    const query = await prompt("Search games", "");
    if (!query) return;
    const games = state.data.games.filter((game) => `${game.title} ${game.title_id}`.toLowerCase().includes(query.toLowerCase()));
    if (!games.length) return dialog({ title: "No results", text: `Nothing matches “${query}”.`, buttons: [{ label: "OK" }] });
    const game = await dialog({ title: `Results for “${query}”`, options: games.map((item) => ({ label: item.title, sub: item.title_id, value: item })), buttons: [{ label: "Cancel", value: null }] });
    if (game) { state.selectedTile = game.id; state.history = []; showScreen("home", { replace: true, focus: null }); requestAnimationFrame(() => focusFirst($(`[data-key="tile:${CSS.escape(game.id)}"]`))); }
  });
  $("#dialogLayer").addEventListener("click", (event) => { if (event.target === event.currentTarget) closeDialog(null); });
  $("#sidemenu").addEventListener("click", (event) => { if (event.target === event.currentTarget) closeSideMenu(); });
  $("#controlCenter").addEventListener("click", (event) => { if (event.target === event.currentTarget) closeControlCenter(); });
  window.addEventListener("gamepadconnected", (event) => toast("Controller connected", event.gamepad.id));
  window.addEventListener("gamepaddisconnected", () => toast("Controller disconnected", ""));
  setInterval(tickClock, 15000);
  setInterval(() => refresh({ quiet: true }), 2500);
  refresh();
  requestAnimationFrame(pollGamepads);
}

init();
