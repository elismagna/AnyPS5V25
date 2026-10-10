(function () {
  "use strict";

  const ICONS = {
    search: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
    gear: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
    x: '<svg viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    play: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l12-7.5z" fill="currentColor" stroke="none"/></svg>',
    stop: '<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" stroke="none"/></svg>',
    back: '<svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>',
    folder: '<svg viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
    "folder-down": '<svg viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M12 10v6m-3-3 3 3 3-3"/></svg>',
    refresh: '<svg viewBox="0 0 24 24"><path d="M20 11a8 8 0 0 0-14.5-4.5L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.5 4.5L20 16"/><path d="M20 20v-4h-4"/></svg>',
    trash: '<svg viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></svg>',
    chip: '<svg viewBox="0 0 24 24"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M4 10h3M4 14h3M17 10h3M17 14h3M10 4v3M14 4v3M10 17v3M14 17v3"/></svg>',
    tag: '<svg viewBox="0 0 24 24"><path d="M20 13 13 20 3 10V3h7z"/><circle cx="8" cy="8" r="1.5"/></svg>',
    info: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>',
    alert: '<svg viewBox="0 0 24 24"><path d="M12 3 2.5 20h19z"/><path d="M12 10v4M12 17h.01"/></svg>',
    check: '<svg viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></svg>',
    copy: '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>',
    eraser: '<svg viewBox="0 0 24 24"><path d="m4 15 9-9 6 6-6 6H8z"/><path d="M4 21h16"/></svg>',
    external: '<svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/></svg>',
    gamepad: '<svg viewBox="0 0 24 24"><path d="M6 9h12a4 4 0 0 1 4 4v3a2 2 0 0 1-3.5 1.3L16 15H8l-2.5 2.3A2 2 0 0 1 2 16v-3a4 4 0 0 1 4-4z"/><path d="M8 12v2M7 13h2M16 12h.01M18 14h.01"/></svg>',
  };

  const STATUS_TEXT = {
    new: "Not converted yet",
    ready: "Ready to play",
    stale: "Needs a new conversion",
    converting: "Converting",
    running: "Running",
    error: "Last start failed",
    gone: "Missing",
  };
  const STATUS_SHORT = { new: "New", ready: "Ready", stale: "Rebuild", converting: "Converting", running: "Running", error: "Failed", gone: "Missing" };

  const state = {
    games: [],
    settings: {},
    tooling: {},
    home: "",
    platform: "",
    frozen: false,
    view: "library",
    selected: null,
    filter: "",
    icons: {},
    logs: {},
    errors: {},
    confirmRemove: false,
    pendingPlay: {},
  };

  const $ = (selector, root) => (root || document).querySelector(selector);
  const el = (tag, attrs, children) => {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [key, value] of Object.entries(attrs)) {
        if (key === "class") node.className = value;
        else if (key === "html") node.innerHTML = value;
        else if (key === "text") node.textContent = value;
        else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
        else if (value !== null && value !== undefined && value !== false) node.setAttribute(key, value === true ? "" : value);
      }
    }
    for (const child of children || []) {
      if (child === null || child === undefined || child === false) continue;
      node.append(child.nodeType ? child : document.createTextNode(String(child)));
    }
    return node;
  };
  const icon = (name, extra) => el("span", { class: "icon" + (extra ? " " + extra : ""), html: ICONS[name] || "" });

  function hydrateIcons(root) {
    for (const node of (root || document).querySelectorAll("[data-icon]")) {
      node.innerHTML = ICONS[node.dataset.icon] || "";
    }
  }

  async function api(name, ...args) {
    const bridge = window.pywebview && window.pywebview.api;
    if (!bridge || typeof bridge[name] !== "function") throw new Error("The launcher backend is not connected (" + name + ")");
    const response = await bridge[name](...args);
    if (!response || response.ok !== true) throw new Error((response && response.error) || "Unknown error");
    return response.result;
  }

  function toast(message, kind) {
    const node = el("div", { class: "toast " + (kind || "") }, [icon(kind === "error" ? "alert" : kind === "ok" ? "check" : "info"), el("div", { class: "msg", text: message })]);
    $("#toasts").append(node);
    setTimeout(() => { node.style.opacity = "0"; node.style.transition = "opacity .3s"; setTimeout(() => node.remove(), 320); }, kind === "error" ? 7000 : 3200);
  }

  function game(id) {
    return state.games.find((entry) => entry.id === id) || null;
  }

  function initials(title) {
    return (title || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((word) => word[0].toUpperCase()).join("");
  }

  function status(entry) {
    if (state.errors[entry.id] && entry.status !== "running" && entry.status !== "converting") return "error";
    return entry.status || "new";
  }

  function cover(entry, extraClass) {
    const node = el("div", { class: "cover " + (extraClass || "") });
    const src = state.icons[entry.id];
    if (src) node.append(el("img", { src, alt: "" }));
    else {
      node.append(el("span", { class: "initials", text: initials(entry.title) }));
      if (entry.icon && src === undefined) loadIcon(entry.id);
    }
    return node;
  }

  async function loadIcon(id) {
    state.icons[id] = null;
    try {
      const data = await api("icon", id);
      state.icons[id] = data;
      if (data) render();
    } catch (error) {
      state.icons[id] = null;
    }
  }

  function filteredGames() {
    const query = state.filter.trim().toLowerCase();
    const games = state.games.slice().sort((a, b) => (b.played || 0) - (a.played || 0) || a.title.localeCompare(b.title));
    if (!query) return games;
    return games.filter((entry) => [entry.title, entry.title_id, entry.folder].filter(Boolean).some((text) => text.toLowerCase().includes(query)));
  }

  function renderLibrary(main) {
    $("#brand-sub").textContent = "Library";
    $("#search-box").style.visibility = "visible";
    if (!state.games.length) {
      main.append(el("div", { class: "empty view" }, [
        el("div", { class: "empty-card" }, [
          icon("folder-down", "icon-xl"),
          el("h1", { text: "Add your first game" }),
          el("p", { text: "Drop a game folder anywhere in this window, or pick it with the button. AnyPS5 converts it on the first start and keeps it ready." }),
          el("button", { class: "btn btn-primary btn-lg", onclick: () => addGame() }, [icon("plus"), "Add game"]),
          el("div", { class: "steps" }, [
            step(1, "Pick the folder", "The one that holds eboot.bin and sce_module."),
            step(2, "Press Play", "The executable is converted once, in a few seconds to a few minutes."),
            step(3, "Play again", "Later starts are instant. Logs stay here if something goes wrong."),
          ]),
        ]),
      ]));
      return;
    }
    const games = filteredGames();
    const view = el("div", { class: "view" });
    if (!state.tooling.relinker || !state.tooling.libs) view.append(toolingBanner());
    view.append(el("div", { class: "section-head" }, [
      el("h1", {}, ["Games", el("span", { class: "count", text: String(state.games.length) })]),
      el("span", { class: "muted", text: state.filter ? games.length + " match" + (games.length === 1 ? "" : "es") : "Sorted by last played" }),
    ]));
    const grid = el("div", { class: "grid" });
    for (const entry of games) {
      const current = status(entry);
      const card = el("button", { class: "card", type: "button", onclick: () => openGame(entry.id) });
      const art = cover(entry);
      if (current === "running") art.append(el("span", { class: "badge-running" }, [el("span", { class: "dot running" }), "Running"]));
      else if (current === "converting") art.append(el("span", { class: "badge-running" }, [el("span", { class: "spinner" }), "Converting"]));
      else art.append(el("div", { class: "play-hint", onclick: (event) => { event.stopPropagation(); play(entry.id); } }, [el("span", { class: "circle" }, [icon("play")])]));
      card.append(art);
      card.append(el("div", { class: "card-title truncate", text: entry.title, title: entry.title }));
      card.append(el("div", { class: "card-meta" }, [
        el("span", { class: "truncate", text: entry.title_id || entry.executable }),
        el("span", { class: "row", style: "gap:6px" }, [el("span", { class: "dot " + current }), STATUS_SHORT[current]]),
      ]));
      grid.append(card);
    }
    if (!games.length) grid.append(el("p", { class: "muted", text: "No game matches your search." }));
    view.append(grid);
    main.append(view);
  }

  function step(number, title, text) {
    return el("div", { class: "step" }, [el("span", { class: "n", text: String(number) }), el("b", { text: title }), text]);
  }

  function toolingBanner() {
    const missing = [];
    if (!state.tooling.relinker) missing.push("relinker");
    if (!state.tooling.libs) missing.push("the system libraries (libs/*.prx)");
    return el("div", { class: "warn-banner" }, [
      icon("alert"),
      el("div", {}, [
        el("b", { text: "Games cannot start yet: " + missing.join(" and ") + " not found. " }),
        "Put the launcher in the AnyPS5 package next to relinker, or choose the files in ",
        el("a", { href: "#", onclick: (event) => { event.preventDefault(); openSettings(); } }, ["Settings"]),
        ".",
      ]),
    ]);
  }

  function renderDetail(main) {
    const entry = game(state.selected);
    if (!entry) { state.view = "library"; renderLibrary(main); return; }
    $("#brand-sub").textContent = entry.title;
    $("#search-box").style.visibility = "hidden";
    const current = status(entry);
    const view = el("div", { class: "view" });
    view.append(el("button", { class: "btn btn-ghost back", onclick: () => { state.view = "library"; state.selected = null; render(); } }, [icon("back"), "All games"]));
    const detail = el("div", { class: "detail" });
    const side = el("div", { class: "detail-side" });

    side.append(el("div", { class: "hero" }, [
      cover(entry),
      el("div", { class: "grow" }, [
        el("h1", { text: entry.title }),
        el("div", { class: "meta" }, [
          el("span", { class: "chip " + current }, [el("span", { class: "dot " + current }), STATUS_TEXT[current]]),
          entry.title_id ? el("span", {}, [icon("tag"), entry.title_id]) : null,
          entry.version ? el("span", { text: "v" + entry.version }) : null,
        ]),
      ]),
    ]));

    if (state.errors[entry.id]) view.append(el("div", { class: "error-banner" }, [icon("alert"), el("div", {}, [el("b", { text: "The last start failed. " }), state.errors[entry.id]])]));
    if (entry.problems && entry.problems.length) view.append(el("div", { class: "warn-banner" }, [icon("alert"), el("div", {}, entry.problems.map((text) => el("div", { text })))]));

    const actions = el("div", { class: "actions" });
    if (current === "running") actions.append(el("button", { class: "btn btn-lg btn-stop", onclick: () => stop(entry.id) }, [icon("stop"), "Stop"]));
    else if (current === "converting") actions.append(el("button", { class: "btn btn-lg btn-primary", disabled: true }, [el("span", { class: "spinner" }), "Converting"]));
    else actions.append(el("button", { class: "btn btn-lg btn-primary", onclick: () => play(entry.id), disabled: !state.tooling.relinker }, [icon("play"), current === "ready" ? "Play" : "Convert and play"]));
    actions.append(el("button", { class: "btn", title: "Convert the executable again", onclick: () => rebuild(entry.id), disabled: current === "running" || current === "converting" }, [icon("refresh"), "Rebuild"]));
    actions.append(el("button", { class: "btn", onclick: () => api("open_folder", entry.id).catch(fail) }, [icon("folder"), "Game folder"]));
    side.append(actions);

    const removeRow = el("div", { class: "row" });
    if (state.confirmRemove) {
      removeRow.append(el("span", { class: "muted grow", text: "Remove from the library and delete the converted files? The game folder stays untouched." }));
      removeRow.append(el("button", { class: "btn btn-sm", onclick: () => { state.confirmRemove = false; render(); } }, ["Keep"]));
      removeRow.append(el("button", { class: "btn btn-sm btn-danger", onclick: () => remove(entry.id) }, [icon("trash"), "Remove"]));
    } else {
      removeRow.append(el("span", { class: "grow" }));
      removeRow.append(el("button", { class: "btn btn-sm btn-ghost", onclick: () => { state.confirmRemove = true; render(); } }, [icon("trash"), "Remove from library"]));
    }
    side.append(removeRow);

    side.append(panel("Options", [
      field("Instruction conversion", select("intel", entry.intel || "auto", [
        ["auto", "Automatic (" + (entry.intel_effective ? "converting for an Intel processor" : "AMD processor, nothing to convert") + ")"],
        ["on", "Always convert for Intel"],
        ["off", "Never convert"],
      ], (value) => updateGame(entry.id, { intel: value })), "AMD-only instructions are rewritten so the game runs on Intel processors. Changing this converts the game again."),
      field("GPU", input("gpu", entry.gpu || "", "Part of the device name, e.g. GeForce", (value) => updateGame(entry.id, { gpu: value })), "Leave empty to use the first discrete Vulkan GPU."),
      field("Input mapping file", inputRow("input_config", entry.input_config || "", "anyps5-input.ini", (value) => updateGame(entry.id, { input_config: value }), async () => {
        const path = await api("pick_file");
        if (path) updateGame(entry.id, { input_config: path });
      }), "Optional keyboard and mouse bindings; see Input mapping in the docs."),
    ]));

    side.append(panel("Files", [
      el("dl", { class: "kv" }, [
        el("dt", { text: "Executable" }), el("dd", { class: "path", text: entry.executable }),
        el("dt", { text: "Modules" }), el("dd", { class: "path", text: (entry.modules || []).join(", ") || "none" }),
        el("dt", { text: "Game folder" }), el("dd", { class: "path path-link", text: entry.folder, onclick: () => api("open_folder", entry.id).catch(fail) }),
        el("dt", { text: "Converted files" }), el("dd", { class: "path path-link", text: entry.game_dir, onclick: () => api("open_game_dir", entry.id).catch(fail) }),
      ]),
    ]));

    detail.append(side);

    const logPanel = el("div", { class: "panel log" });
    logPanel.append(el("div", { class: "panel-head" }, [
      el("h3", { text: "Log" }),
      el("div", { class: "row" }, [
        el("button", { class: "btn btn-sm btn-ghost", onclick: () => copyLog(entry.id) }, [icon("copy"), "Copy"]),
        el("button", { class: "btn btn-sm btn-ghost", onclick: () => clearLog(entry.id) }, [icon("eraser"), "Clear"]),
      ]),
    ]));
    const body = el("div", { class: "log-body", id: "log-body" });
    const lines = state.logs[entry.id] || [];
    if (!lines.length) body.append(el("span", { class: "log-empty", text: "Output of the conversion and of the game appears here." }));
    for (const line of lines) body.append(logLine(line));
    logPanel.append(body);
    detail.append(logPanel);
    view.append(detail);
    main.append(view);
    body.scrollTop = body.scrollHeight;
  }

  function logLine(line) {
    let kind = "";
    if (line.startsWith("$ ")) kind = "cmd";
    else if (/^(FAIL|Error|error:|terminate called|what\(\))/.test(line)) kind = "err";
    else if (line.startsWith("Exited with code")) kind = "exit";
    else if (/^(Converted |Output file:)/.test(line)) kind = "ok";
    return el("span", { class: "l " + kind, text: line });
  }

  function panel(title, children) {
    return el("div", { class: "panel" }, [el("div", { class: "panel-head" }, [el("h3", { text: title })]), el("div", { class: "panel-body" }, children)]);
  }

  function field(label, control, hint) {
    return el("div", { class: "field" }, [el("label", { text: label }), control, hint ? el("span", { class: "hint", text: hint }) : null]);
  }

  function select(name, value, options, onChange) {
    const node = el("select", { class: "input", name, onchange: (event) => onChange(event.target.value) });
    for (const [key, text] of options) node.append(el("option", { value: key, selected: key === value, text }));
    return node;
  }

  function input(name, value, placeholder, onChange) {
    return el("input", { class: "input", name, value, placeholder, spellcheck: "false", onchange: (event) => onChange(event.target.value.trim()) });
  }

  function inputRow(name, value, placeholder, onChange, onBrowse) {
    return el("div", { class: "input-row" }, [input(name, value, placeholder, onChange), el("button", { class: "btn", onclick: () => onBrowse().catch(fail) }, [icon("folder"), "Browse"])]);
  }

  function render() {
    const main = $("#main");
    const scroll = main.scrollTop;
    main.replaceChildren();
    if (state.view === "detail") renderDetail(main);
    else renderLibrary(main);
    main.scrollTop = scroll;
  }

  function fail(error) {
    toast(error && error.message ? error.message : String(error), "error");
  }

  function openGame(id) {
    state.selected = id;
    state.view = "detail";
    state.confirmRemove = false;
    render();
    if (!state.logs[id]) api("log", id).then((lines) => { state.logs[id] = lines; if (state.selected === id) render(); }).catch(() => {});
  }

  async function addGame(path) {
    try {
      const entry = await api("add_game", path || null);
      if (!entry) return;
      const existing = state.games.findIndex((candidate) => candidate.id === entry.id);
      if (existing >= 0) state.games[existing] = entry; else state.games.push(entry);
      toast((existing >= 0 ? "Updated " : "Added ") + entry.title, "ok");
      openGame(entry.id);
    } catch (error) {
      fail(error);
    }
  }

  async function play(id) {
    const entry = game(id);
    if (!entry) return;
    delete state.errors[id];
    try {
      entry.status = "converting";
      render();
      await api("play", id);
    } catch (error) {
      entry.status = "error";
      state.errors[id] = error.message;
      render();
      fail(error);
    }
  }

  async function rebuild(id) {
    const entry = game(id);
    if (!entry) return;
    delete state.errors[id];
    try {
      entry.status = "converting";
      render();
      await api("rebuild", id);
    } catch (error) {
      fail(error);
      refresh();
    }
  }

  async function stop(id) {
    try {
      await api("stop", id);
    } catch (error) {
      fail(error);
    }
  }

  async function remove(id) {
    try {
      await api("remove_game", id, true);
      state.games = state.games.filter((entry) => entry.id !== id);
      delete state.logs[id];
      delete state.icons[id];
      state.view = "library";
      state.selected = null;
      state.confirmRemove = false;
      render();
      toast("Removed from the library", "ok");
    } catch (error) {
      fail(error);
    }
  }

  async function updateGame(id, fields) {
    try {
      const entry = await api("update_game", id, fields);
      const index = state.games.findIndex((candidate) => candidate.id === id);
      if (index >= 0) state.games[index] = entry;
      render();
    } catch (error) {
      fail(error);
    }
  }

  async function copyLog(id) {
    const text = (state.logs[id] || []).join("\n");
    try {
      await navigator.clipboard.writeText(text);
      toast("Log copied", "ok");
    } catch (error) {
      const area = el("textarea", { style: "position:fixed;opacity:0" }, [text]);
      document.body.append(area);
      area.select();
      document.execCommand("copy");
      area.remove();
      toast("Log copied", "ok");
    }
  }

  async function clearLog(id) {
    state.logs[id] = [];
    render();
    api("clear_log", id).catch(() => {});
  }

  async function refresh() {
    const data = await api("bootstrap");
    state.games = data.games;
    state.settings = data.settings;
    state.tooling = data.tooling;
    state.home = data.home;
    state.platform = data.platform;
    state.frozen = data.frozen;
    render();
  }

  function openSettings() {
    const body = $("#settings-body");
    body.replaceChildren();
    const draft = Object.assign({}, state.settings);
    const tooling = state.tooling;
    const line = (ok, text) => el("div", { class: "status-line" }, [el("span", { class: ok ? "ok" : "bad" }, [icon(ok ? "check" : "alert")]), text]);
    body.append(el("div", { class: "panel", style: "margin-bottom:18px" }, [
      el("div", { class: "panel-head" }, [el("h3", { text: "Toolchain" })]),
      el("div", { class: "panel-body" }, [
        line(!!tooling.relinker, tooling.relinker ? "relinker: " + tooling.relinker : "relinker not found"),
        el("div", { style: "height:8px" }),
        line(!!tooling.libs, tooling.libs ? tooling.library_count + " system libraries in " + tooling.libs : "System libraries (libs/*.prx) not found"),
        el("div", { style: "height:8px" }),
        line(true, "This computer: " + (tooling.intel_host ? "Intel processor, AMD-only instructions are converted" : "AMD processor") + (tooling.commit ? " · package " + tooling.commit : "")),
      ]),
    ]));
    body.append(field("relinker", inputRow("relinker", draft.relinker || "", "Detected automatically when empty", (value) => { draft.relinker = value; }, async () => {
      const path = await api("pick_file");
      if (path) { draft.relinker = path; $("#settings-body input[name=relinker]").value = path; }
    }), "Only needed when the launcher does not sit next to relinker."));
    body.append(field("System libraries folder", inputRow("libs", draft.libs || "", "Detected automatically when empty", (value) => { draft.libs = value; }, async () => {
      const path = await api("pick_folder");
      if (path) { draft.libs = path; $("#settings-body input[name=libs]").value = path; }
    }), "The libs folder with the *.prx files built by AnyPS5."));
    body.append(field("Instruction conversion for new games", select("intel", draft.intel || "auto", [["auto", "Automatic, by processor"], ["on", "Always convert for Intel"], ["off", "Never convert"]], (value) => { draft.intel = value; })));
    body.append(field("Default GPU", input("gpu", draft.gpu || "", "Part of the device name", (value) => { draft.gpu = value; }), "Used when a game has no GPU of its own."));
    body.append(field("Launcher data", el("div", { class: "row" }, [el("span", { class: "path grow truncate", text: state.home, title: state.home }), el("button", { class: "btn btn-sm", onclick: () => api("open_home").catch(fail) }, [icon("external"), "Open"])]), "Library, converted executables and logs. Converted modules are written next to each game's own modules."));
    $("#settings-note").textContent = state.frozen ? "AnyPS5 package" : "Running from source";
    const modal = $("#settings-modal");
    modal.hidden = false;
    $("#save-settings").onclick = async () => {
      try {
        const result = await api("update_settings", draft);
        state.settings = result.settings;
        state.tooling = result.tooling;
        modal.hidden = true;
        render();
        toast("Settings saved", "ok");
      } catch (error) {
        fail(error);
      }
    };
  }

  function closeSettings() {
    $("#settings-modal").hidden = true;
  }

  function droppedPaths(event) {
    const paths = [];
    const files = event.dataTransfer && event.dataTransfer.files ? Array.from(event.dataTransfer.files) : [];
    for (const file of files) {
      const path = file.pywebviewFullPath || file.path;
      if (path) paths.push(path);
    }
    return paths;
  }

  function bindDragAndDrop() {
    const overlay = $("#drop-overlay");
    let depth = 0;
    document.addEventListener("dragenter", (event) => { event.preventDefault(); depth += 1; overlay.classList.add("active"); });
    document.addEventListener("dragover", (event) => { event.preventDefault(); if (event.dataTransfer) event.dataTransfer.dropEffect = "copy"; });
    document.addEventListener("dragleave", (event) => { event.preventDefault(); depth = Math.max(0, depth - 1); if (!depth) overlay.classList.remove("active"); });
    document.addEventListener("drop", (event) => {
      event.preventDefault();
      depth = 0;
      overlay.classList.remove("active");
      const paths = droppedPaths(event);
      if (!paths.length) { toast("Drop a folder from the file manager, or use Add game", "error"); return; }
      for (const path of paths) addGame(path);
    });
  }

  window.anyps5 = {
    push(event) {
      if (!event) return;
      if (event.type === "log") {
        const lines = state.logs[event.id] || (state.logs[event.id] = []);
        lines.push(...event.lines);
        if (lines.length > 2000) lines.splice(0, lines.length - 2000);
        if (state.view === "detail" && state.selected === event.id) {
          const body = $("#log-body");
          if (body) {
            const stick = body.scrollHeight - body.scrollTop - body.clientHeight < 40;
            const empty = body.querySelector(".log-empty");
            if (empty) empty.remove();
            for (const line of event.lines) body.append(logLine(line));
            if (stick) body.scrollTop = body.scrollHeight;
          }
        }
      } else if (event.type === "status") {
        const entry = game(event.id);
        if (!entry) return;
        entry.status = event.status;
        if (event.error) { state.errors[event.id] = event.error; toast(event.error, "error"); }
        else if (event.status === "running") delete state.errors[event.id];
        if (typeof event.code === "number" && event.code !== 0 && !event.error) toast(entry.title + " exited with code " + event.code, "error");
        render();
      }
    },
    state,
  };

  function boot() {
    hydrateIcons();
    $("#add-game").addEventListener("click", () => addGame());
    $("#open-settings").addEventListener("click", openSettings);
    $("#close-settings").addEventListener("click", closeSettings);
    $("#cancel-settings").addEventListener("click", closeSettings);
    $("#settings-modal").addEventListener("click", (event) => { if (event.target === event.currentTarget) closeSettings(); });
    $("#search").addEventListener("input", (event) => { state.filter = event.target.value; if (state.view === "library") render(); });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (!$("#settings-modal").hidden) closeSettings();
        else if (state.view === "detail") { state.view = "library"; state.selected = null; render(); }
      }
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "f") { event.preventDefault(); $("#search").focus(); }
    });
    bindDragAndDrop();
    refresh().catch((error) => { render(); fail(error); });
  }

  if (window.pywebview && window.pywebview.api) boot();
  else window.addEventListener("pywebviewready", boot, { once: true });
})();
