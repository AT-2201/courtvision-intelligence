let data = window.COURTVISION_DATA;
const root = document.querySelector("#page-root");
const nav = document.querySelector("#primary-nav");
const title = document.querySelector("#page-title");
const kicker = document.querySelector("#page-kicker");

const pages = [
  {id:"overview", label:"League", title:"League pulse", kicker:"SEASON INTELLIGENCE", icon:"⌂"},
  {id:"games", label:"Games", title:"Game center", kicker:"RESULTS / GAME FLOW", icon:"◫"},
  {id:"teams", label:"Teams", title:"Team lab", kicker:"IDENTITY / PERFORMANCE", icon:"◎"},
  {id:"players", label:"Players", title:"Player lab", kicker:"PRODUCTION / EFFICIENCY", icon:"◉"},
  {id:"scouting", label:"Scout", title:"Similarity finder", kicker:"PLAYER DISCOVERY", icon:"⌁"},
  {id:"compare", label:"Compare", title:"Comparison room", kicker:"SIDE-BY-SIDE ANALYSIS", icon:"⇄"},
  {id:"pipeline", label:"Pipeline", title:"Data platform", kicker:"ENGINEERING / ANALYTICS", icon:"⌘"}
];

const playerIdFor = name => data.players.find(player => player.name === name)?.id;
const featuredPlayerIds = ["Nikola Jokić","Luka Dončić","Shai Gilgeous-Alexander"].map(playerIdFor).filter(Boolean);
const state = {selectedPlayer:playerIdFor("Luka Dončić") || data.players[0].id, selectedGame:data.games[0].id, selectedTeam:data.teams[0].abbr, compareIds:featuredPlayerIds, compareQuery:"", conference:"All", leaderMetric:"pts"};
const fmt = (value, digits = 1) => Number(value).toFixed(digits);
const signed = value => `${value > 0 ? "+" : ""}${fmt(value)}`;
const playerById = id => data.players.find(player => player.id === Number(id));
const teamByAbbr = abbr => data.teams.find(team => team.abbr === abbr);
const family = pos => pos.includes("G") && !pos.includes("F") ? "Guard" : pos === "C" ? "Center" : "Wing / Forward";
const netRating = team => team.ortg - team.drtg;

function teamBadge(abbr, small = false) {
  const hues = {BOS:145,OKC:205,DEN:43,MIN:207,LAC:222,NYK:24,DAL:199,MIL:151,CLE:350,ORL:220,PHX:284,GSW:44,LAL:276,SAC:268};
  const hue = hues[abbr] || [...abbr].reduce((sum,char) => sum + char.charCodeAt(0),0) % 360;
  return `<span class="team-badge ${small ? "small" : ""}" style="--team-hue:${hue}">${abbr}</span>`;
}

function metricCard(label,value,note="",tone="") {
  return `<article class="metric-card ${tone}"><span>${label}</span><strong>${value}</strong>${note ? `<small>${note}</small>` : ""}</article>`;
}

function emptyState(message) {
  return `<div class="empty-state"><span>○</span><strong>No results</strong><p>${message}</p></div>`;
}

function similarity(target) {
  const candidates = data.players.filter(player => player.id !== target.id && player.totalMin >= 500 && family(player.pos) === family(target.pos));
  const pool = [target,...candidates];
  const metrics = ["pts","reb","ast","stl","blk","tov","ts"];
  const labels = {pts:"Scoring",reb:"Rebounding",ast:"Playmaking",stl:"Steals",blk:"Blocks",tov:"Turnovers",ts:"True shooting"};
  const deviations = Object.fromEntries(metrics.map(metric => {
    const mean = pool.reduce((sum,player) => sum + player[metric],0) / pool.length;
    const variance = pool.reduce((sum,player) => sum + (player[metric] - mean) ** 2,0) / pool.length;
    return [metric,Math.sqrt(variance) || 1];
  }));
  return candidates.map(player => {
    const gaps = metrics.map(metric => ({metric,gap:Math.abs(target[metric] - player[metric]) / deviations[metric]}));
    const distance = Math.sqrt(gaps.reduce((sum,item) => sum + item.gap ** 2,0) / gaps.length);
    gaps.sort((a,b) => a.gap - b.gap);
    return {player,score:100*Math.exp(-.65*distance),close:gaps.slice(0,3).map(({metric}) => ({label:labels[metric],a:target[metric],b:player[metric]})),tradeoffs:gaps.slice(-2).reverse().map(({metric}) => ({label:labels[metric],diff:player[metric]-target[metric]}))};
  }).sort((a,b) => b.score-a.score).slice(0,5);
}

function renderOverview() {
  const teams = data.teams.filter(team => state.conference === "All" || team.conference === state.conference).sort((a,b) => b.wins-a.wins);
  const leaderLabels = {pts:"PPG",reb:"RPG",ast:"APG",ts:"TS%"};
  const qualifiedPlayers = data.players.filter(player => player.games >= 58);
  const leaders = [...qualifiedPlayers].sort((a,b) => b[state.leaderMetric]-a[state.leaderMetric]).slice(0,5);
  const best = [...data.teams].sort((a,b) => b.wins-a.wins)[0];
  const offense = [...data.teams].sort((a,b) => b.ortg-a.ortg)[0];
  const defense = [...data.teams].sort((a,b) => a.drtg-b.drtg)[0];
  const scorer = [...qualifiedPlayers].sort((a,b) => b.pts-a.pts)[0];
  const maxWins = Math.max(...teams.map(team => team.wins));
  const paceMin = Math.min(...data.teams.map(team => team.pace));
  const paceMax = Math.max(...data.teams.map(team => team.pace));
  const netMin = Math.min(...data.teams.map(netRating));
  const netMax = Math.max(...data.teams.map(netRating));

  root.innerHTML = `
    <section class="overview-intro"><p>Read the season in seconds. Start with the league picture, then move directly into a team, player or matchup.</p><div class="segmented" aria-label="Filter overview by conference">${["All","East","West"].map(item => `<button class="${state.conference === item ? "active" : ""}" data-conference="${item}">${item}</button>`).join("")}</div></section>
    <section class="signal-strip">
      <button class="signal featured" data-team-jump="${best.abbr}"><span class="signal-index">01</span><small>BEST RECORD</small><strong>${best.wins}–${best.losses}</strong><p>${best.name}</p><i>Open team →</i></button>
      <button class="signal" data-team-jump="${offense.abbr}"><span class="signal-index">02</span><small>TOP OFFENSE</small><strong>${offense.ortg}</strong><p>${offense.name} ORTG</p><i>Open team →</i></button>
      <button class="signal" data-team-jump="${defense.abbr}"><span class="signal-index">03</span><small>TOP DEFENSE</small><strong>${defense.drtg}</strong><p>${defense.name} DRTG</p><i>Open team →</i></button>
      <button class="signal" data-player-jump="${scorer.id}"><span class="signal-index">04</span><small>SCORING LEADER</small><strong>${scorer.pts}</strong><p>${scorer.name} PPG</p><i>Open player →</i></button>
    </section>
    <section class="dashboard-grid">
      <article class="panel standings-panel"><div class="panel-heading"><div><span class="eyebrow">RECORD RACE</span><h2>${state.conference === "All" ? "League" : `${state.conference}ern Conference`} standings</h2></div><button class="ghost-button" data-go="teams">Team lab <span>→</span></button></div><div class="standings-list">${teams.map((team,index) => `<button class="standing-row" data-team-jump="${team.abbr}"><span class="standing-rank">${String(index+1).padStart(2,"0")}</span>${teamBadge(team.abbr,true)}<span class="standing-name"><strong>${team.name}</strong><small>${team.conference} · ${signed(netRating(team))} NET</small></span><span class="record-bar"><i style="width:${team.wins/maxWins*100}%"></i></span><strong class="standing-record">${team.wins}<small>–${team.losses}</small></strong></button>`).join("")}</div></article>
      <article class="panel leaders-panel"><div class="panel-heading stacked"><div><span class="eyebrow">PLAYER LEADERS · 58+ GP</span><h2>Who is setting the pace?</h2></div><div class="metric-tabs">${[["pts","PTS"],["reb","REB"],["ast","AST"],["ts","TS%"]].map(([key,label]) => `<button class="${state.leaderMetric === key ? "active" : ""}" data-leader-metric="${key}">${label}</button>`).join("")}</div></div><div class="leader-list">${leaders.map((player,index) => `<button data-player-jump="${player.id}" class="leader-row ${index === 0 ? "first" : ""}"><span class="leader-rank">${index+1}</span>${teamBadge(player.team,true)}<span><strong>${player.name}</strong><small>${player.team} · ${player.pos}</small></span><b>${player[state.leaderMetric]}<small>${leaderLabels[state.leaderMetric]}</small></b></button>`).join("")}</div></article>
      <article class="panel landscape-panel"><div class="panel-heading"><div><span class="eyebrow">TEAM LANDSCAPE</span><h2>Pace vs. net rating</h2></div><div class="chart-legend"><span><i></i> Each dot is a team</span></div></div><div class="scatter-wrap"><span class="axis-label y">BETTER NET RATING</span><span class="axis-label x">FASTER PACE →</span><div class="scatter-grid"><i class="axis-v"></i><i class="axis-h"></i>${data.teams.map(team => { const x=6+((team.pace-paceMin)/(paceMax-paceMin||1))*88; const y=92-((netRating(team)-netMin)/(netMax-netMin||1))*80; return `<button class="scatter-dot" style="left:${x}%;top:${y}%" data-team-jump="${team.abbr}" aria-label="${team.name}: pace ${team.pace}, net rating ${signed(netRating(team))}"><span>${team.abbr}</span><em><strong>${team.name}</strong>Pace ${team.pace} · ${signed(netRating(team))} net</em></button>`; }).join("")}</div></div></article>
      <article class="panel results-panel"><div class="panel-heading"><div><span class="eyebrow">LATEST RESULTS</span><h2>Game tape</h2></div><button class="ghost-button" data-go="games">All games <span>→</span></button></div><div class="result-stack">${data.games.slice(0,4).map(game => `<button class="result-row" data-game-jump="${game.id}"><small>${game.date.slice(5).replace("-",".")}</small><span>${teamBadge(game.away,true)}<strong>${game.away}</strong><b>${game.awayScore}</b></span><i>—</i><span><b>${game.homeScore}</b><strong>${game.home}</strong>${teamBadge(game.home,true)}</span></button>`).join("")}</div></article>
    </section>`;
  bindOverview();
}

function bindOverview() {
  document.querySelectorAll("[data-conference]").forEach(button => button.addEventListener("click",() => { state.conference=button.dataset.conference; renderOverview(); }));
  document.querySelectorAll("[data-leader-metric]").forEach(button => button.addEventListener("click",() => { state.leaderMetric=button.dataset.leaderMetric; renderOverview(); }));
  document.querySelectorAll("[data-team-jump]").forEach(button => button.addEventListener("click",() => { state.selectedTeam=button.dataset.teamJump; location.hash="teams"; }));
  document.querySelectorAll("[data-player-jump]").forEach(button => button.addEventListener("click",() => { state.selectedPlayer=Number(button.dataset.playerJump); location.hash="players"; }));
  document.querySelectorAll("[data-game-jump]").forEach(button => button.addEventListener("click",() => { state.selectedGame=button.dataset.gameJump; location.hash="games"; }));
  bindPageLinks();
}

function renderGames() {
  const game = data.games.find(item => item.id === state.selectedGame) || data.games[0];
  const maxQuarter = Math.max(...game.quarters);
  root.innerHTML = `<section class="workspace-toolbar"><div class="search-field"><span>⌕</span><input aria-label="Search games" placeholder="Search a team or date" id="game-search"></div><span class="result-count">${data.games.length} GAMES</span></section><section class="split-workspace"><div class="list-panel"><div class="list-label"><span>DATE / MATCHUP</span><span>FINAL</span></div><div class="scroll-list">${data.games.map(item => `<button class="list-row game-row ${item.id === game.id ? "active" : ""}" data-game="${item.id}"><span><small>${item.date}</small><strong>${item.away} at ${item.home}</strong></span><span class="score">${item.awayScore}<em>:</em>${item.homeScore}</span></button>`).join("")}</div></div><article class="detail-panel game-detail"><div class="detail-meta"><span class="status-pill">FINAL</span><span>${game.date}</span></div><div class="scoreboard"><div>${teamBadge(game.away)}<span><strong>${game.away}</strong><small>AWAY</small></span><b>${game.awayScore}</b></div><span>—</span><div><b>${game.homeScore}</b><span><strong>${game.home}</strong><small>HOME</small></span>${teamBadge(game.home)}</div></div><div class="section-heading"><span class="eyebrow">SCORING RHYTHM</span><h2>Quarter-by-quarter output</h2></div><div class="quarter-chart">${game.quarters.map((quarter,index) => `<div><strong>${quarter}</strong><i style="height:${Math.max(14,quarter/maxQuarter*100)}%"></i><span>${index === 4 ? "OT" : `Q${index+1}`}</span></div>`).join("")}</div><div class="analyst-note"><span>READ</span><p>${game.note}</p></div></article></section>`;
  document.querySelectorAll("[data-game]").forEach(button => button.addEventListener("click",() => { state.selectedGame=button.dataset.game; renderGames(); }));
  bindListSearch("#game-search","[data-game]");
}

function renderTeams() {
  const team = teamByAbbr(state.selectedTeam) || data.teams[0];
  const metrics = [["Offense",team.ortg,125,"ORTG"],["Defense",125-team.drtg,20,"DRTG"],["Pace",team.pace,105,"PACE"],["Point margin",team.ppg-team.oppg,14,"DIFF"]];
  root.innerHTML = `<section class="workspace-toolbar"><div class="search-field"><span>⌕</span><input aria-label="Search teams" placeholder="Find a team" id="team-search"></div><div class="toolbar-note">Select a team to inspect its profile</div></section><section class="split-workspace"><div class="list-panel"><div class="list-label"><span>TEAM</span><span>RECORD</span></div><div class="scroll-list">${data.teams.map(item => `<button class="list-row ${item.abbr === team.abbr ? "active" : ""}" data-team="${item.abbr}"><span class="team-cell">${teamBadge(item.abbr,true)}<span><strong>${item.name}</strong><small>${item.conference} Conference</small></span></span><span><strong>${item.wins}–${item.losses}</strong><small>${signed(netRating(item))} NET</small></span></button>`).join("")}</div></div><article class="detail-panel"><div class="profile-hero"><div class="profile-identity">${teamBadge(team.abbr)}<div><span class="eyebrow">${team.conference.toUpperCase()} CONFERENCE</span><h2>${team.name}</h2><p>${team.wins} wins · ${team.losses} losses</p></div></div><div class="profile-record"><strong>${team.wins}</strong><span>WINS</span></div></div><section class="metrics-grid three">${metricCard("Offensive rating",team.ortg,"points / 100")}${metricCard("Defensive rating",team.drtg,"allowed / 100")}${metricCard("Net rating",signed(netRating(team)),"per 100 possessions",netRating(team)>0?"positive":"")}${metricCard("Points / game",team.ppg)}${metricCard("Opponent PPG",team.oppg)}${metricCard("Pace",team.pace,"possessions / 48")}</section><div class="section-heading"><span class="eyebrow">PERFORMANCE FINGERPRINT</span><h2>How this team plays</h2></div><div class="profile-bars">${metrics.map(([label,value,max,short]) => `<div><span><strong>${label}</strong><small>${short}</small></span><div><i style="width:${Math.max(8,Math.min(100,value/max*100))}%"></i></div><b>${fmt(label === "Defense" ? team.drtg : value)}</b></div>`).join("")}</div></article></section>`;
  document.querySelectorAll("[data-team]").forEach(button => button.addEventListener("click",() => { state.selectedTeam=button.dataset.team; renderTeams(); }));
  bindListSearch("#team-search","[data-team]");
}

function playerList(selected,mode="player") {
  return data.players.map(player => `<button class="list-row ${player.id === selected ? "active" : ""}" data-${mode}="${player.id}"><span class="team-cell">${teamBadge(player.team,true)}<span><strong>${player.name}</strong><small>${player.team} · ${player.pos} · ${player.games} GP</small></span></span><span><strong>${player.pts}</strong><small>PPG</small></span></button>`).join("");
}

function renderPlayerDetail(player) {
  const profile = [["Scoring",player.pts,35],["Playmaking",player.ast,11],["Rebounding",player.reb,15],["Efficiency",player.ts,70]];
  return `<div class="profile-hero"><div class="profile-identity">${teamBadge(player.team)}<div><span class="eyebrow">${player.team} · ${family(player.pos).toUpperCase()}</span><h2>${player.name}</h2><p>${player.games} games · ${player.min} minutes per game</p></div></div><button class="primary-button" data-scout-from-player="${player.id}">Find similar players <span>→</span></button></div><section class="metrics-grid three">${metricCard("Points",player.pts,"per game")}${metricCard("Rebounds",player.reb,"per game")}${metricCard("Assists",player.ast,"per game")}${metricCard("True shooting",`${player.ts}%`,"scoring efficiency")}${metricCard("Steals",player.stl,"per game")}${metricCard("Turnovers",player.tov,"per game")}</section><div class="section-heading"><span class="eyebrow">PLAYER FINGERPRINT</span><h2>Production and efficiency</h2></div><div class="profile-bars">${profile.map(([label,value,max]) => `<div><span><strong>${label}</strong><small>SEASON</small></span><div><i style="width:${Math.min(100,value/max*100)}%"></i></div><b>${fmt(value)}</b></div>`).join("")}</div>`;
}

function renderPlayers() {
  const player = playerById(state.selectedPlayer) || data.players[0];
  root.innerHTML = `<section class="workspace-toolbar"><div class="search-field"><span>⌕</span><input aria-label="Search players" placeholder="Find a player" id="player-search"></div><div class="toolbar-note">${data.meta.playerCount} players · complete regular season</div></section><section class="split-workspace"><div class="list-panel"><div class="list-label"><span>PLAYER</span><span>SCORING</span></div><div class="scroll-list">${playerList(player.id)}</div></div><article class="detail-panel">${renderPlayerDetail(player)}</article></section>`;
  document.querySelectorAll("[data-player]").forEach(button => button.addEventListener("click",() => { state.selectedPlayer=Number(button.dataset.player); renderPlayers(); }));
  document.querySelector("[data-scout-from-player]").addEventListener("click",() => { location.hash="scouting"; });
  bindListSearch("#player-search","[data-player]");
}

function renderScouting() {
  const player = playerById(state.selectedPlayer) || data.players[0];
  const results = similarity(player);
  root.innerHTML = `<section class="scouting-header"><div><h2>Start with a player. See who plays like them.</h2><p>Matches use normalized per-game production and efficiency. Every result shows the traits driving the match.</p></div><div class="scout-search"><span>⌕</span><input id="scout-search" placeholder="Search reference player"><select id="position-filter"><option>All positions</option><option>Guard</option><option>Wing / Forward</option><option>Center</option></select></div></section><section class="scouting-main"><div class="reference-list panel"><div class="list-label"><span>REFERENCE PLAYER</span><span>${data.players.length}</span></div><div class="scroll-list compact">${playerList(player.id,"scout-player")}</div></div><article class="detail-panel scouting-results"><div class="profile-hero compact"><div class="profile-identity">${teamBadge(player.team)}<div><span class="eyebrow">REFERENCE · ${family(player.pos).toUpperCase()}</span><h2>${player.name}</h2><p>${player.pts} PTS · ${player.reb} REB · ${player.ast} AST · ${player.ts}% TS</p></div></div></div><div class="section-heading inline"><div><span class="eyebrow">CLOSEST STATISTICAL PROFILES</span><h2>Why they match</h2></div><span class="method-chip">7 metrics · equal weight</span></div><div class="similarity-list">${results.length ? results.map((result,index) => `<article class="similarity-card"><span class="rank">${String(index+1).padStart(2,"0")}</span><div class="candidate">${teamBadge(result.player.team,true)}<div><h3>${result.player.name}</h3><p>${result.player.team} · ${result.player.pos}</p></div></div><div class="match-score"><strong>${fmt(result.score)}<small>%</small></strong><span>PROFILE MATCH</span></div><div class="match-evidence">${result.close.map(item => `<span><small>${item.label}</small><strong>${item.a}</strong><i>≈</i><strong>${item.b}</strong></span>`).join("")}</div><div class="tradeoff"><small>BIGGEST DIFFERENCE</small><strong>${result.tradeoffs[0].diff>0?"+":""}${fmt(result.tradeoffs[0].diff)} ${result.tradeoffs[0].label}</strong></div><button class="compare-button" data-compare="${result.player.id}">Compare <span>→</span></button></article>`).join("") : emptyState("Choose another position family to see comparable players.")}</div><p class="method-note">A profile match describes statistical shape. It does not measure player quality, contract value or tactical fit.</p></article></section>`;
  document.querySelectorAll("[data-scout-player]").forEach(button => button.addEventListener("click",() => { state.selectedPlayer=Number(button.dataset.scoutPlayer); renderScouting(); }));
  document.querySelector("#scout-search").addEventListener("input",filterScoutPlayers);
  document.querySelector("#position-filter").addEventListener("change",filterScoutPlayers);
  document.querySelectorAll("[data-compare]").forEach(button => button.addEventListener("click",() => { state.compareIds=[...new Set([state.selectedPlayer,Number(button.dataset.compare)])].slice(0,4); location.hash="compare"; }));
}

function filterScoutPlayers() {
  const query = document.querySelector("#scout-search").value.toLowerCase();
  const position = document.querySelector("#position-filter").value;
  document.querySelectorAll("[data-scout-player]").forEach(button => { const player=playerById(button.dataset.scoutPlayer); button.hidden=!player.name.toLowerCase().includes(query) || (position !== "All positions" && family(player.pos) !== position); });
}

function buildRadarChart(selected,metrics) {
  const center = 180;
  const radius = 116;
  const colors = ["#ff6846","#76a5ff","#c9ff4a","#b58cff"];
  const point = (index,scale=1) => {
    const angle = -Math.PI / 2 + (Math.PI * 2 * index / metrics.length);
    return [center + Math.cos(angle) * radius * scale,center + Math.sin(angle) * radius * scale];
  };
  const polygon = scale => metrics.map((_,index) => point(index,scale).map(value => value.toFixed(1)).join(",")).join(" ");
  const playerPolygon = player => metrics.map(([,key,max],index) => point(index,Math.min(1,player[key]/max)).map(value => value.toFixed(1)).join(",")).join(" ");
  const labelPoint = index => point(index,1.23);
  return `<div class="radar-layout">
    <div class="radar-chart-wrap">
      <svg class="radar-chart" viewBox="0 0 360 360" role="img" aria-label="Radar chart comparing ${selected.map(player => player.name).join(", ")}">
        ${[.25,.5,.75,1].map(scale => `<polygon class="radar-grid" points="${polygon(scale)}"></polygon>`).join("")}
        ${metrics.map((_,index) => { const [x,y]=point(index); return `<line class="radar-axis" x1="${center}" y1="${center}" x2="${x}" y2="${y}"></line>`; }).join("")}
        ${selected.map((player,index) => `<polygon class="radar-player" style="--radar-color:${colors[index]}" points="${playerPolygon(player)}"></polygon>${metrics.map(([,key,max],metricIndex) => { const [x,y]=point(metricIndex,Math.min(1,player[key]/max)); return `<circle class="radar-point" style="--radar-color:${colors[index]}" cx="${x}" cy="${y}" r="3"></circle>`; }).join("")}`).join("")}
        ${metrics.map(([label],index) => { const [x,y]=labelPoint(index); const anchor=x<center-5?"end":x>center+5?"start":"middle"; return `<text class="radar-label" x="${x}" y="${y}" text-anchor="${anchor}" dominant-baseline="middle">${label}</text>`; }).join("")}
      </svg>
      <div class="radar-scale"><span>Normalized to the comparison scale</span><strong>Shape shows profile · size shows output</strong></div>
    </div>
    <div class="radar-legend">${selected.map((player,index) => `<button data-player-jump="${player.id}" style="--radar-color:${colors[index]}"><i></i><span><strong>${player.name}</strong><small>${player.team} · ${player.pos}</small></span></button>`).join("")}</div>
  </div>`;
}

const foldSearchText = value => value.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();

function compareSearchMatches(query) {
  const folded = foldSearchText(query.trim());
  if(!folded || state.compareIds.length >= 4) return [];
  return data.players.filter(player => {
    if(state.compareIds.includes(player.id)) return false;
    return foldSearchText(`${player.name} ${player.team} ${player.pos}`).includes(folded);
  }).slice(0,8);
}

function compareSearchResults() {
  if(state.compareIds.length >= 4) return `<div class="compare-search-prompt limit"><strong>Comparison group full</strong><span>Remove a player before adding another.</span></div>`;
  if(!state.compareQuery.trim()) return `<div class="compare-search-prompt"><strong>Search ${data.meta.playerCount} players</strong><span>Type a name, team or position to add someone.</span></div>`;
  const matches = compareSearchMatches(state.compareQuery);
  if(!matches.length) return `<div class="compare-search-prompt"><strong>No matching players</strong><span>Try another name, team abbreviation or position.</span></div>`;
  return matches.map(player => `<button class="compare-search-result" data-add-compare="${player.id}">${teamBadge(player.team,true)}<span><strong>${player.name}</strong><small>${player.team} · ${player.pos} · ${player.pts} PPG</small></span><i>＋ ADD</i></button>`).join("");
}

function bindCompareSearch() {
  const input = document.querySelector("#compare-search");
  const results = document.querySelector("#compare-search-results");
  input.value=state.compareQuery;
  const bindResults = () => document.querySelectorAll("[data-add-compare]").forEach(button => button.addEventListener("click",() => {
    if(state.compareIds.length >= 4) return;
    state.compareIds.push(Number(button.dataset.addCompare));
    state.compareQuery="";
    renderCompare();
    setTimeout(() => document.querySelector("#compare-search")?.focus(),0);
  }));
  input.addEventListener("input",event => {
    state.compareQuery=event.target.value;
    results.innerHTML=compareSearchResults();
    bindResults();
  });
  input.addEventListener("keydown",event => {
    if(event.key === "Enter") {
      event.preventDefault();
      document.querySelector("[data-add-compare]")?.click();
    }
    if(event.key === "Escape") {
      state.compareQuery="";
      input.value="";
      results.innerHTML=compareSearchResults();
    }
  });
  bindResults();
  document.querySelectorAll("[data-remove-compare]").forEach(button => button.addEventListener("click",() => {
    state.compareIds=state.compareIds.filter(id => id !== Number(button.dataset.removeCompare));
    renderCompare();
    setTimeout(() => document.querySelector("#compare-search")?.focus(),0);
  }));
}

function renderCompare() {
  const selected = state.compareIds.map(playerById).filter(Boolean);
  const metrics = [["Points","pts",35],["Rebounds","reb",15],["Assists","ast",11],["Steals","stl",2.5],["Blocks","blk",2],["True shooting","ts",70]];
  const picker = `<section class="panel compare-picker"><div class="compare-picker-head"><div><span class="eyebrow">COMPARISON GROUP</span><h2>Players selected</h2></div><span>${selected.length} OF 4</span></div><div class="compare-selected">${selected.map(player => `<div class="compare-selected-player">${teamBadge(player.team,true)}<span><strong>${player.name}</strong><small>${player.team} · ${player.pos}</small></span><button data-remove-compare="${player.id}" aria-label="Remove ${player.name} from comparison">×</button></div>`).join("")}${Array.from({length:Math.max(0,2-selected.length)},() => `<div class="compare-slot"><span>＋</span><small>ADD PLAYER</small></div>`).join("")}</div><div class="compare-search"><label for="compare-search">ADD ANOTHER PLAYER</label><div><span>⌕</span><input id="compare-search" placeholder="Search by player, team or position" autocomplete="off" ${selected.length >= 4?"disabled":""}><kbd>ENTER</kbd></div><div class="compare-search-results" id="compare-search-results" aria-live="polite">${compareSearchResults()}</div></div></section>`;
  const radar = `<section class="panel comparison-output"><div class="panel-heading"><div><span class="eyebrow">PLAYER SHAPE</span><h2>Multi-metric radar</h2></div><span class="method-chip">PER GAME · NORMALIZED</span></div>${buildRadarChart(selected,metrics)}<div class="radar-table-wrap"><table class="radar-table"><thead><tr><th>Metric</th>${selected.map(player => `<th>${player.name}</th>`).join("")}</tr></thead><tbody>${metrics.map(([label,key]) => `<tr><td>${label}</td>${selected.map(player => `<td>${player[key]}${key === "ts"?"%":""}</td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
  const cards = `<section class="comparison-grid comparison-summaries">${selected.map((player,index) => `<article class="comparison-card"><span class="compare-number">0${index+1}</span>${teamBadge(player.team)}<div><span class="eyebrow">${player.team} · ${player.pos}</span><h3>${player.name}</h3><strong>${player.pts}<small> PPG</small></strong><p>${player.reb} REB · ${player.ast} AST · ${player.ts}% TS</p></div></article>`).join("")}</section>`;
  root.innerHTML = `<section class="compare-header"><div><h2>Build your comparison group</h2><p>Search and add two to four players. The radar updates instantly.</p></div><span>${selected.length}/4 SELECTED</span></section>${picker}${selected.length >= 2 ? `${radar}${cards}` : emptyState("Add at least two players to begin the comparison.")}`;
  bindCompareSearch();
  document.querySelectorAll(".radar-legend [data-player-jump]").forEach(button => button.addEventListener("click",() => { state.selectedPlayer=Number(button.dataset.playerJump); location.hash="players"; }));
}

function renderPipeline() {
  const apiConnected = document.body.dataset.dataMode === "api";
  const layers = [
    ["01","SOURCE","Public season CSVs","Games, team box scores and player box scores"],
    ["02","INGEST","Python normalization","Typed records, season filters and idempotent PostgreSQL upserts"],
    ["03","MODEL","dbt transformations","Staging views, dimensional joins, rolling form and season marts"],
    ["04","SERVE","FastAPI analytics","Filtered resources, pagination, similarity and quality endpoints"],
    ["05","EXPERIENCE","Decision interface","League, team, player, scouting and comparison workspaces"]
  ];
  const endpoints = [
    ["GET","/api/v1/summary","League leaders and season signals"],
    ["GET","/api/v1/players","Search, filter, sort and paginate players"],
    ["GET","/api/v1/players/{id}/similar","Explainable player similarity"],
    ["GET","/api/v1/games","Team and date-filtered game results"],
    ["GET","/api/v1/data-quality","Machine-readable validation report"],
    ["GET","/docs","Interactive OpenAPI documentation"]
  ];
  const checks = [
    ["Franchise coverage","30 / 30","passed"],
    ["Regular-season games","1,230 unique","passed"],
    ["Schedule completeness","82 per team","passed"],
    ["Player identity","572 unique IDs","passed"],
    ["Season date range","Oct 24 → Apr 14","passed"]
  ];
  root.innerHTML = `<section class="pipeline-hero"><div><span class="eyebrow">END-TO-END DATA PRODUCT</span><h2>From public box scores to decision-ready analytics.</h2><p>The dashboard is backed by a reproducible warehouse workflow: streamed source ingestion, PostgreSQL raw tables, dbt-style analytical marts and a documented FastAPI serving layer.</p></div><div class="runtime-card"><span class="runtime-dot ${apiConnected?"live":"snapshot"}"></span><div><small>CURRENT RUNTIME</small><strong>${apiConnected?"FASTAPI CONNECTED":"VERIFIED STATIC MART"}</strong><p>${apiConnected?"The interface loaded its dataset from /api/v1/bootstrap.":"The hosted portfolio uses the same validated mart as the API fallback."}</p></div></div></section><section class="pipeline-stats">${metricCard("Source rows","1,230","games")}${metricCard("Player profiles",data.meta.playerCount,"modeled")}${metricCard("REST routes","12","documented")}${metricCard("Quality checks","5 / 5","passing","positive")}</section><section class="panel pipeline-lineage"><div class="panel-heading"><div><span class="eyebrow">DATA LINEAGE</span><h2>One traceable analytical path</h2></div><span class="method-chip">BATCH · IDEMPOTENT · TESTED</span></div><div class="lineage-flow">${layers.map(([index,label,name,detail]) => `<article><span>${index}</span><small>${label}</small><strong>${name}</strong><p>${detail}</p></article>`).join("")}</div></section><section class="pipeline-grid"><article class="panel quality-panel"><div class="panel-heading"><div><span class="eyebrow">DATA QUALITY</span><h2>Release gates</h2></div><span class="quality-status">ALL PASSING</span></div><div class="quality-list">${checks.map(([name,value]) => `<div><i>✓</i><span><strong>${name}</strong><small>${value}</small></span></div>`).join("")}</div></article><article class="panel api-panel"><div class="panel-heading"><div><span class="eyebrow">SERVING LAYER</span><h2>FastAPI endpoint catalog</h2></div><span class="method-chip">OPENAPI</span></div><div class="endpoint-list">${endpoints.map(([method,path,detail]) => `<div><b>${method}</b><code>${path}</code><span>${detail}</span></div>`).join("")}</div></article></section><section class="panel engineering-notes"><div><span class="eyebrow">ENGINEERING DECISIONS</span><h2>Built for repeatability, not a one-off notebook</h2></div><div class="decision-grid"><article><strong>Idempotent loading</strong><p>PostgreSQL conflict keys allow safe reruns without duplicating games or box scores.</p></article><article><strong>Separated concerns</strong><p>Raw ingestion, transformations, analytics logic, API delivery and UI presentation remain modular.</p></article><article><strong>Portable serving</strong><p>The interface prefers FastAPI when available and falls back to the exact generated mart for static hosting.</p></article></div></section>`;
}

function bindListSearch(inputSelector,itemSelector) {
  document.querySelector(inputSelector).addEventListener("input",event => { const query=event.target.value.toLowerCase(); document.querySelectorAll(itemSelector).forEach(button => { button.hidden=!button.textContent.toLowerCase().includes(query); }); });
}
function bindPageLinks() { document.querySelectorAll("[data-go]").forEach(button => button.addEventListener("click",() => { location.hash=button.dataset.go; })); }

const renderers = {overview:renderOverview,games:renderGames,teams:renderTeams,players:renderPlayers,scouting:renderScouting,compare:renderCompare,pipeline:renderPipeline};
function renderPage() {
  const pageId = location.hash.replace("#","") || "overview";
  const active = pages.find(page => page.id === pageId) || pages[0];
  title.textContent=active.title; kicker.textContent=active.kicker;
  nav.innerHTML=pages.map(page => `<button class="${page.id === active.id ? "active" : ""}" data-go="${page.id}"><span>${page.icon}</span><strong>${page.label}</strong></button>`).join("");
  (renderers[active.id] || renderOverview)(); bindPageLinks(); document.querySelector("main").scrollTo({top:0,behavior:"instant"});
}

const palette = document.querySelector("#command-palette");
const paletteInput = document.querySelector("#palette-input");
const paletteResults = document.querySelector("#palette-results");
function paletteItems(query="") {
  const text=query.toLowerCase();
  const items=[...pages.map(page => ({type:"Page",label:page.title,detail:page.kicker,action:() => { location.hash=page.id; }})),...data.players.map(player => ({type:"Player",label:player.name,detail:`${player.team} · ${player.pos}`,action:() => { state.selectedPlayer=player.id; location.hash="players"; }})),...data.teams.map(team => ({type:"Team",label:team.name,detail:`${team.abbr} · ${team.conference}`,action:() => { state.selectedTeam=team.abbr; location.hash="teams"; }}))];
  return items.filter(item => `${item.label} ${item.detail}`.toLowerCase().includes(text)).slice(0,9);
}
function renderPalette(query="") {
  const items=paletteItems(query);
  paletteResults.innerHTML=items.length ? items.map((item,index) => `<button data-palette-index="${index}"><span><small>${item.type}</small><strong>${item.label}</strong></span><em>${item.detail}</em><i>↵</i></button>`).join("") : emptyState("Try a player, team or workspace name.");
  document.querySelectorAll("[data-palette-index]").forEach(button => button.addEventListener("click",() => { items[Number(button.dataset.paletteIndex)].action(); closePalette(); }));
}
function openPalette() { palette.hidden=false; document.body.classList.add("palette-open"); paletteInput.value=""; renderPalette(); setTimeout(() => paletteInput.focus(),0); }
function closePalette() { palette.hidden=true; document.body.classList.remove("palette-open"); }
document.querySelector("#command-button").addEventListener("click",openPalette);
document.querySelector("[data-close-palette]").addEventListener("click",closePalette);
paletteInput.addEventListener("input",event => renderPalette(event.target.value));
document.addEventListener("keydown",event => { if(event.key === "/" && !["INPUT","SELECT","TEXTAREA"].includes(document.activeElement.tagName)){event.preventDefault();openPalette();} if(event.key === "Escape" && !palette.hidden) closePalette(); if(event.key === "Enter" && !palette.hidden) document.querySelector("[data-palette-index]")?.click(); });
window.addEventListener("hashchange",renderPage);

async function startApp() {
  const sourceLabel = document.querySelector("#data-layer");
  try {
    const response = await fetch("/api/v1/bootstrap",{headers:{Accept:"application/json"}});
    const contentType = response.headers.get("content-type") || "";
    if(response.ok && contentType.includes("application/json")) {
      data=await response.json();
      document.body.dataset.dataMode="api";
      sourceLabel.textContent="FastAPI mart · live";
    } else {
      throw new Error("API unavailable");
    }
  } catch {
    document.body.dataset.dataMode="snapshot";
    sourceLabel.textContent="Validated analytical mart";
  }
  renderPage();
}
startApp();
