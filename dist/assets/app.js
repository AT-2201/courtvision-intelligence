const data = window.COURTVISION_DATA;
const root = document.querySelector("#page-root");
const nav = document.querySelector("#primary-nav");
const title = document.querySelector("#page-title");
const kicker = document.querySelector("#page-kicker");

const pages = [
  ["overview", "Overview", "Season command center", "LEAGUE INTELLIGENCE"],
  ["games", "Games", "Game analysis", "SCHEDULE / RESULTS"],
  ["teams", "Teams", "Team intelligence", "STYLE / PERFORMANCE"],
  ["players", "Players", "Player performance", "PRODUCTION / EFFICIENCY"],
  ["scouting", "Scouting", "Similarity explorer", "RECRUITMENT INTELLIGENCE"],
  ["compare", "Compare", "Player comparison", "DECISION WORKSPACE"]
];

let selectedPlayer = 1;
let selectedGame = data.games[0].id;
let selectedTeam = data.teams[0].abbr;
let compareIds = [5, 1, 3];

const fmt = (value, digits = 1) => Number(value).toFixed(digits);
const playerById = id => data.players.find(player => player.id === Number(id));
const teamByAbbr = abbr => data.teams.find(team => team.abbr === abbr);
const family = pos => pos.includes("G") && !pos.includes("F") ? "Guard" : pos === "C" ? "Center" : "Wing / Forward";

function teamBadge(abbr, small = false) {
  return `<span class="team-badge ${small ? "small" : ""}">${abbr}</span>`;
}

function metricCard(label, value, note = "") {
  return `<article class="metric-card"><span>${label}</span><strong>${value}</strong>${note ? `<small>${note}</small>` : ""}</article>`;
}

function positionCandidates(target) {
  const targetFamily = family(target.pos);
  return data.players.filter(player => player.id !== target.id && family(player.pos) === targetFamily);
}

function similarity(target) {
  const candidates = positionCandidates(target);
  const pool = [target, ...candidates];
  const metrics = ["pts", "reb", "ast", "stl", "blk", "tov", "ts"];
  const labels = {pts:"Points",reb:"Rebounds",ast:"Assists",stl:"Steals",blk:"Blocks",tov:"Turnovers",ts:"True shooting"};
  const deviations = Object.fromEntries(metrics.map(metric => {
    const mean = pool.reduce((sum, p) => sum + p[metric], 0) / pool.length;
    const variance = pool.reduce((sum, p) => sum + (p[metric] - mean) ** 2, 0) / pool.length;
    return [metric, Math.sqrt(variance) || 1];
  }));
  return candidates.map(player => {
    const gaps = metrics.map(metric => ({metric, gap: Math.abs(target[metric] - player[metric]) / deviations[metric]}));
    const distance = Math.sqrt(gaps.reduce((sum, item) => sum + item.gap ** 2, 0) / gaps.length);
    const score = 100 * Math.exp(-0.65 * distance);
    gaps.sort((a, b) => a.gap - b.gap);
    return {
      player,
      score,
      close: gaps.slice(0, 3).map(({metric}) => ({label: labels[metric], a: target[metric], b: player[metric]})),
      tradeoffs: gaps.slice(-2).reverse().map(({metric}) => ({label: labels[metric], diff: player[metric] - target[metric]}))
    };
  }).sort((a, b) => b.score - a.score).slice(0, 5);
}

function renderOverview() {
  const best = [...data.teams].sort((a, b) => b.wins - a.wins)[0];
  const scorer = [...data.players].sort((a, b) => b.pts - a.pts)[0];
  const offense = [...data.teams].sort((a, b) => b.ortg - a.ortg)[0];
  root.innerHTML = `
    <section class="hero-grid">
      <article class="hero-card orange">
        <span class="eyebrow dark">VERSION 1 · PORTFOLIO PREVIEW</span>
        <h2>See the season.<br>Understand the game.</h2>
        <p>One decision-support workspace for league trends, team identity, player performance and explainable scouting.</p>
        <button class="dark-button" data-go="scouting">Explore player similarity →</button>
      </article>
      <article class="hero-card court-card" aria-label="Abstract basketball court diagram">
        <div class="court"><span class="rim"></span><span class="arc"></span><span class="center-circle"></span></div>
        <div class="court-caption"><span>2023/24 REGULAR SEASON</span><strong>Analytics-ready foundation</strong></div>
      </article>
    </section>
    <section class="metrics-grid four">
      ${metricCard("League leader", best.name, `${best.wins}–${best.losses}`)}
      ${metricCard("Scoring leader", scorer.name, `${scorer.pts} PPG`)}
      ${metricCard("Best offense", offense.abbr, `${offense.ortg} rating`)}
      ${metricCard("Sample coverage", "10 teams", "12 players · 6 games")}
    </section>
    <section class="content-grid two-one">
      <article class="panel">
        <div class="panel-heading"><div><span class="eyebrow">LEAGUE TABLE</span><h3>Top records</h3></div><button class="text-button" data-go="teams">View teams →</button></div>
        <div class="table-wrap"><table><thead><tr><th>Team</th><th>Conf.</th><th>W</th><th>L</th><th>Diff.</th></tr></thead><tbody>
          ${data.teams.slice(0, 7).map(team => `<tr><td class="team-cell">${teamBadge(team.abbr, true)}<strong>${team.name}</strong></td><td>${team.conference}</td><td>${team.wins}</td><td>${team.losses}</td><td class="positive">+${fmt(team.ppg - team.oppg)}</td></tr>`).join("")}
        </tbody></table></div>
      </article>
      <article class="panel methodology">
        <span class="eyebrow">WHY THIS PROJECT</span>
        <h3>Analytics you can audit</h3>
        <p>Every derived metric will have a documented definition, data lineage and test. Similarity explains matching traits and trade-offs rather than returning a mysterious score.</p>
        <ul class="check-list"><li>PostgreSQL-ready model</li><li>dbt-style transformations</li><li>FastAPI foundation</li><li>Reproducible source adapter</li></ul>
      </article>
    </section>`;
}

function renderGames() {
  const game = data.games.find(item => item.id === selectedGame) || data.games[0];
  root.innerHTML = `<section class="split-workspace">
    <div class="list-panel">
      <div class="filter-bar"><input aria-label="Search games" placeholder="Search team or date" id="game-search"><span>${data.games.length} SAMPLE GAMES</span></div>
      <div class="scroll-list" id="game-list">${data.games.map(item => `<button class="list-row ${item.id === game.id ? "active" : ""}" data-game="${item.id}"><span><small>${item.date}</small><strong>${item.away} @ ${item.home}</strong></span><span class="score">${item.awayScore}<em>–</em>${item.homeScore}</span></button>`).join("")}</div>
    </div>
    <article class="detail-panel">
      <span class="eyebrow">FINAL · ${game.date}</span>
      <div class="scoreboard"><div>${teamBadge(game.away)}<strong>${game.away}</strong><b>${game.awayScore}</b></div><span>FINAL</span><div>${teamBadge(game.home)}<strong>${game.home}</strong><b>${game.homeScore}</b></div></div>
      <div class="section-heading"><span class="eyebrow">GAME FLOW</span><h3>Quarter scoring</h3></div>
      <div class="quarter-chart">${game.quarters.map((q, index) => `<div><span>Q${index + 1}</span><i style="height:${Math.max(22, q * 2)}px"></i><strong>${q}</strong></div>`).join("")}</div>
      <div class="insight"><span>ANALYST NOTE</span><p>${game.note}</p></div>
      <div class="coming-next"><strong>Full-data milestone</strong><span>Possession timeline, box score leaders, substitutions and play-by-play events.</span></div>
    </article>
  </section>`;
  document.querySelectorAll("[data-game]").forEach(button => button.addEventListener("click", () => { selectedGame = button.dataset.game; renderGames(); }));
  document.querySelector("#game-search").addEventListener("input", event => {
    const query = event.target.value.toLowerCase();
    document.querySelectorAll("[data-game]").forEach(button => button.hidden = !button.textContent.toLowerCase().includes(query));
  });
}

function renderTeams() {
  const team = teamByAbbr(selectedTeam) || data.teams[0];
  root.innerHTML = `<section class="split-workspace">
    <div class="list-panel"><div class="filter-bar"><input aria-label="Search teams" placeholder="Search teams" id="team-search"></div><div class="scroll-list">${data.teams.map(item => `<button class="list-row ${item.abbr === team.abbr ? "active" : ""}" data-team="${item.abbr}"><span class="team-cell">${teamBadge(item.abbr, true)}<span><strong>${item.name}</strong><small>${item.conference} Conference</small></span></span><span><strong>${item.wins}–${item.losses}</strong><small>RECORD</small></span></button>`).join("")}</div></div>
    <article class="detail-panel">
      <div class="identity-heading">${teamBadge(team.abbr)}<div><span class="eyebrow">${team.conference.toUpperCase()} CONFERENCE</span><h2>${team.name}</h2><p>${team.wins} wins · ${team.losses} losses</p></div></div>
      <section class="metrics-grid three">${metricCard("Offensive rating", team.ortg)}${metricCard("Defensive rating", team.drtg)}${metricCard("Net rating", `${team.ortg - team.drtg > 0 ? "+" : ""}${fmt(team.ortg - team.drtg)}`)}${metricCard("Points / game", team.ppg)}${metricCard("Opponent PPG", team.oppg)}${metricCard("Pace", team.pace)}</section>
      <div class="section-heading"><span class="eyebrow">TEAM PROFILE</span><h3>Performance balance</h3></div>
      <div class="bar-list">${[["Offense",team.ortg,125],["Defense",125-team.drtg,20],["Pace",team.pace,105],["Point margin",team.ppg-team.oppg,14]].map(([label,value,max]) => `<div><span>${label}</span><div><i style="width:${Math.max(10, Math.min(100, value/max*100))}%"></i></div><strong>${fmt(value)}</strong></div>`).join("")}</div>
    </article>
  </section>`;
  document.querySelectorAll("[data-team]").forEach(button => button.addEventListener("click", () => { selectedTeam = button.dataset.team; renderTeams(); }));
  document.querySelector("#team-search").addEventListener("input", event => { const query = event.target.value.toLowerCase(); document.querySelectorAll("[data-team]").forEach(button => button.hidden = !button.textContent.toLowerCase().includes(query)); });
}

function playerList(selected, mode = "player") {
  return data.players.map(player => `<button class="list-row ${player.id === selected ? "active" : ""}" data-${mode}="${player.id}"><span class="team-cell">${teamBadge(player.team, true)}<span><strong>${player.name}</strong><small>${player.team} · ${player.pos} · ${player.games} games</small></span></span><span><strong>${player.pts}</strong><small>PPG</small></span></button>`).join("");
}

function renderPlayerDetail(player) {
  return `<div class="identity-heading">${teamBadge(player.team)}<div><span class="eyebrow">${player.team} · ${family(player.pos)}</span><h2>${player.name}</h2><p>${player.games} games · ${player.min} minutes per game</p></div></div>
    <section class="metrics-grid three">${metricCard("Points", player.pts, "per game")}${metricCard("Rebounds", player.reb, "per game")}${metricCard("Assists", player.ast, "per game")}${metricCard("True shooting", `${player.ts}%`)}${metricCard("Steals", player.stl, "per game")}${metricCard("Turnovers", player.tov, "per game")}</section>
    <div class="section-heading"><span class="eyebrow">SEASON PROFILE</span><h3>Production and efficiency</h3></div>
    <div class="bar-list">${[["Scoring",player.pts,35],["Playmaking",player.ast,11],["Rebounding",player.reb,15],["Efficiency",player.ts,70]].map(([label,value,max]) => `<div><span>${label}</span><div><i style="width:${value/max*100}%"></i></div><strong>${fmt(value)}</strong></div>`).join("")}</div>`;
}

function renderPlayers() {
  const player = playerById(selectedPlayer) || data.players[0];
  root.innerHTML = `<section class="split-workspace"><div class="list-panel"><div class="filter-bar"><input aria-label="Search players" placeholder="Search players" id="player-search"></div><div class="scroll-list">${playerList(player.id)}</div></div><article class="detail-panel">${renderPlayerDetail(player)}</article></section>`;
  document.querySelectorAll("[data-player]").forEach(button => button.addEventListener("click", () => { selectedPlayer = Number(button.dataset.player); renderPlayers(); }));
  document.querySelector("#player-search").addEventListener("input", event => { const query = event.target.value.toLowerCase(); document.querySelectorAll("[data-player]").forEach(button => button.hidden = !button.textContent.toLowerCase().includes(query)); });
}

function renderScouting() {
  const player = playerById(selectedPlayer) || data.players[0];
  const results = similarity(player);
  root.innerHTML = `<section class="scouting-layout">
    <div class="scouting-controls panel"><div><label for="scout-search">Player</label><input id="scout-search" value="${player.name}" aria-label="Search scouting players"></div><div><label for="position-filter">Position</label><select id="position-filter"><option>All positions</option><option>Guard</option><option>Wing / Forward</option><option>Center</option></select></div><div><label for="minimum-minutes">Minimum minutes</label><input id="minimum-minutes" type="number" value="500"></div></div>
    <div class="scouting-main">
      <div class="reference-list panel"><span class="eyebrow">REFERENCE PLAYER</span><div class="scroll-list compact">${playerList(player.id, "scout-player")}</div></div>
      <article class="detail-panel scouting-results">
        <div class="identity-heading">${teamBadge(player.team)}<div><span class="eyebrow">${family(player.pos)} COMPARISON POOL</span><h2>${player.name}</h2><p>Similarity uses seven normalized season metrics with equal weight.</p></div></div>
        <div class="section-heading"><span class="eyebrow">SIMILAR PROFILES</span><h3>Why these players match</h3></div>
        <div class="similarity-list">${results.length ? results.map((result, index) => `<article class="similarity-card"><div class="rank">0${index+1}</div><div class="candidate"><span>${teamBadge(result.player.team, true)}</span><div><h4>${result.player.name}</h4><p>${result.player.team} · ${result.player.pos}</p></div></div><div class="match-score"><strong>${fmt(result.score)}%</strong><span>PROFILE MATCH</span></div><div class="traits"><span>Closest traits</span>${result.close.map(item => `<div><strong>${item.label}</strong><em>${item.a} → ${item.b}</em></div>`).join("")}</div><div class="tradeoffs"><span>Key trade-offs</span>${result.tradeoffs.map(item => `<p><strong>${item.diff > 0 ? "+" : ""}${fmt(item.diff)}</strong> ${item.label}</p>`).join("")}</div><button class="text-button compare-add" data-compare="${result.player.id}">Compare players →</button></article>`).join("") : `<div class="empty-state">No other sampled players belong to this position family. The full-season import expands the candidate pool.</div>`}</div>
        <p class="method-note">Similarity describes statistical profile—not player quality, value or tactical fit.</p>
      </article>
    </div>
  </section>`;
  document.querySelectorAll("[data-scout-player]").forEach(button => button.addEventListener("click", () => { selectedPlayer = Number(button.dataset.scoutPlayer); renderScouting(); }));
  document.querySelector("#scout-search").addEventListener("input", event => { const query = event.target.value.toLowerCase(); document.querySelectorAll("[data-scout-player]").forEach(button => button.hidden = !button.textContent.toLowerCase().includes(query)); });
  document.querySelector("#position-filter").addEventListener("change", event => { const value = event.target.value; document.querySelectorAll("[data-scout-player]").forEach(button => { const p = playerById(button.dataset.scoutPlayer); button.hidden = value !== "All positions" && family(p.pos) !== value; }); });
  document.querySelectorAll("[data-compare]").forEach(button => button.addEventListener("click", () => { compareIds = [...new Set([selectedPlayer, Number(button.dataset.compare)])].slice(0,4); location.hash = "compare"; }));
}

function renderCompare() {
  const selected = compareIds.map(playerById).filter(Boolean);
  const metrics = [["Points","pts"],["Rebounds","reb"],["Assists","ast"],["Steals","stl"],["Blocks","blk"],["Turnovers","tov"],["True shooting %","ts"]];
  root.innerHTML = `<section class="panel compare-picker"><div><span class="eyebrow">SELECT 2–4 PLAYERS</span><h3>Build a comparison group</h3></div><div class="chip-grid">${data.players.map(player => `<label class="player-chip ${compareIds.includes(player.id) ? "selected" : ""}"><input type="checkbox" value="${player.id}" ${compareIds.includes(player.id) ? "checked" : ""}><span>${player.name}<small>${player.team} · ${player.pos}</small></span></label>`).join("")}</div></section>
    <section class="comparison-grid">${selected.map(player => `<article class="comparison-card">${teamBadge(player.team)}<span class="eyebrow">${player.team} · ${player.pos}</span><h3>${player.name}</h3><strong>${player.pts}<small> PPG</small></strong><p>${player.reb} REB · ${player.ast} AST · ${player.ts}% TS</p></article>`).join("")}</section>
    <section class="panel"><div class="panel-heading"><div><span class="eyebrow">NORMAL SEASON STATS</span><h3>Side-by-side output</h3></div><span class="sample-label">PER GAME</span></div><div class="table-wrap"><table class="comparison-table"><thead><tr><th>Metric</th>${selected.map(player => `<th>${player.name}</th>`).join("")}</tr></thead><tbody>${metrics.map(([label,key]) => `<tr><td>${label}</td>${selected.map(player => `<td><strong>${player[key]}</strong></td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
  document.querySelectorAll(".player-chip input").forEach(input => input.addEventListener("change", () => {
    const id = Number(input.value);
    if (input.checked && compareIds.length < 4) compareIds.push(id);
    if (!input.checked) compareIds = compareIds.filter(value => value !== id);
    if (input.checked && compareIds.length > 4) input.checked = false;
    renderCompare();
  }));
}

const renderers = {overview:renderOverview,games:renderGames,teams:renderTeams,players:renderPlayers,scouting:renderScouting,compare:renderCompare};

function renderPage() {
  const page = location.hash.replace("#", "") || "overview";
  const active = pages.find(item => item[0] === page) || pages[0];
  title.textContent = active[2];
  kicker.textContent = active[3];
  nav.innerHTML = pages.map(([id,label], index) => `<button class="${id === active[0] ? "active" : ""}" data-go="${id}"><span>0${index+1}</span>${label}</button>`).join("");
  (renderers[active[0]] || renderOverview)();
  document.querySelectorAll("[data-go]").forEach(button => button.addEventListener("click", () => { location.hash = button.dataset.go; }));
  window.scrollTo({top:0, behavior:"instant"});
}

window.addEventListener("hashchange", renderPage);
renderPage();

