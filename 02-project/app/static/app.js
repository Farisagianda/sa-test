'use strict';

const byId = (id) => document.getElementById(id);

const f = byId('f');
const preview = byId('preview');
const resp = byId('resp');
const fill = byId('fill');

function currentPayload() {
  const pkgs = (byId('packages').value || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  return {
    name: byId('name').value.trim(),
    team: byId('team').value.trim(),
    pool: byId('pool').value,
    priority: byId('priority').value,
    owner: byId('owner')?.value.trim() || undefined,
    base_image: byId('base_image').value.trim(),
    packages: pkgs,
    cpu: byId('cpu').value.trim(),
    memory: byId('memory').value.trim(),
    gpu: Number(byId('gpu').value || 0),
  };
}

function renderPreview() {
  if (preview) preview.textContent = JSON.stringify(currentPayload(), null, 2);
}

if (f) {
  f.addEventListener('input', renderPreview);
  renderPreview();

  f.addEventListener('submit', async (e) => {
    e.preventDefault();
    resp.textContent = 'Submitting...';
    try {
      const r = await fetch('/envs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentPayload()),
      });
      const j = await r.json();
      resp.textContent = (r.ok ? '✔ ' : '✗ ') + JSON.stringify(j, null, 2);
    } catch (err) {
      resp.textContent = '✗ ' + err;
    }
  });

  if (fill) {
    fill.addEventListener('click', () => {
      byId('name').value = 'env1';
      byId('team').value = 'dev-faris';
      byId('pool').value = 'cpu-small';
      byId('priority').value = 'dev-low';
      byId('owner').value = 'faris';
      byId('base_image').value = 'docker.io/farisagianda/sa-test:v1';
      byId('packages').value = 'numpy,pandas';
      byId('cpu').value = '500m';
      byId('memory').value = '1Gi';
      byId('gpu').value = '0';
      renderPreview();
    });
  }
}

function parseCpuToMilli(s) {
  if (!s) return null;
  const t = String(s).trim().toLowerCase();
  if (t.endsWith('m')) return parseFloat(t.slice(0, -1));
  const v = parseFloat(t);                 // cores
  return Number.isFinite(v) ? v * 1000 : null;
}

function parseMemToMi(s) {
  if (!s) return null;
  const t = String(s).trim().toLowerCase();
  if (t.endsWith('mi')) return parseFloat(t.slice(0, -2));
  if (t.endsWith('gi')) return parseFloat(t.slice(0, -2)) * 1024;
  if (t.endsWith('ki')) return parseFloat(t.slice(0, -2)) / 1024;
  const v = parseFloat(t);                 // raw bytes (fallback)
  return Number.isFinite(v) ? v / (1024 * 1024) : null;
}

function fmtCpu(milli) {
  if (milli == null) return '';
  return `${Math.round(milli)}m`;
}

function fmtMem(mi) {
  if (mi == null) return '';
  if (mi >= 1024) {
    const gi = mi / 1024;
    return `${gi >= 10 ? gi.toFixed(0) : gi.toFixed(1)}Gi`;
  }
  return `${mi >= 10 ? mi.toFixed(0) : mi.toFixed(1)}Mi`;
}

function fmtPct(used, req) {
  if (used == null || req == null || req === 0) return '';
  return `${Math.round((used / req) * 100)}%`;
}

async function loadList() {
  const team = (byId('flt-team')?.value || '').trim();
  const url = team ? `/envs?team=${encodeURIComponent(team)}` : '/envs';
  const tbody = document.querySelector('#tbl tbody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="12">Loading…</td></tr>';

  try {
    const r = await fetch(url);
    const items = await r.json();

    if (!Array.isArray(items) || items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="12">No environments found</td></tr>';
      return;
    }

    tbody.innerHTML = '';
    for (const it of items) {
      const spec = it.spec ?? it;
      const status = it.status ?? {};

      const cpuReqM  = parseCpuToMilli(spec.cpu);
      const memReqMi = parseMemToMi(spec.memory);

      const cpuUsed = status.cpu_used_m;
      const memUsed = status.mem_used_mi;

      const cpuCell = cpuUsed != null
        ? `${fmtCpu(cpuUsed)}${cpuReqM ? ` (${fmtPct(cpuUsed, cpuReqM)})` : ''}`
        : '';

      const memCell = memUsed != null
        ? `${fmtMem(memUsed)}${memReqMi ? ` (${fmtPct(memUsed, memReqMi)})` : ''}`
        : '';

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><code>${spec.name}</code></td>
        <td>${spec.team}</td>
        <td>${spec.pool ?? ''}</td>
        <td>${spec.priority ?? ''}</td>
        <td class="muted">${spec.base_image ?? ''}</td>
        <td>${spec.cpu ?? ''}</td>
        <td>${spec.memory ?? ''}</td>
        <td>${status.ready ?? 0}/${status.replicas ?? 0}</td>
        <td>${cpuCell}</td>
        <td>${memCell}</td>
        <td class="muted">${status.service ?? ''}</td>
        <td><button class="btn secondary" data-name="${spec.name}" data-team="${spec.team}">Delete</button></td>
      `;
      tbody.appendChild(tr);
    }

    tbody.querySelectorAll('button[data-name]').forEach((btn) => {
      btn.onclick = async () => {
        const { name, team } = btn.dataset;
        if (!confirm(`Delete ${name} in ${team}?`)) return;
        await fetch(`/envs/${team}/${name}`, { method: 'DELETE' });
        loadList();
      };
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="12">Error: ${String(err)}</td></tr>`;
  }
}

function fmt(ts) {
  const d = new Date(ts);
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ` +
         `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

async function loadEvents(){
  const tbody = document.querySelector('#evt tbody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="7">Loading…</td></tr>';
  try{
    const r = await fetch('/events?limit=100');
    const items = await r.json();
    if (!Array.isArray(items) || items.length === 0){
      tbody.innerHTML = '<tr><td colspan="7" class="muted">No events found</td></tr>';
      return;
    }
    tbody.innerHTML = '';
    for (const e of items){
      const tr = document.createElement('tr');
      const when = e.ts ? new Date(e.ts).toLocaleString() : '';
      tr.innerHTML = `
        <td>${fmt(e.ts)}</td>
        <td>${e.kind || ''}</td>
        <td><code>${e.namespace || ''}</code></td>
        <td><code>${e.name || ''}</code></td>
        <td>${(e.extra && e.extra.owner) || ''}</td>
        <td>${(e.extra && e.extra.pool)  || ''}</td>
        <td class="muted">${e.msg || ''}</td>`;
      tbody.appendChild(tr);
    }
  }catch(err){
    tbody.innerHTML = `<tr><td colspan="7">Error: ${String(err)}</td></tr>`;
  }
}

function switchTab(which) {
  const create = byId('tab-create');
  const existing = byId('tab-existing');
  document.querySelectorAll('.tab').forEach((b) => b.classList.remove('active'));

  if (which === 'existing') {
    create.hidden = true;
    existing.hidden = false;
    document.querySelector('.tab[data-tab="existing"]').classList.add('active');
    loadList();
    loadEvents();
  } else {
    existing.hidden = true;
    create.hidden = false;
    document.querySelector('.tab[data-tab="create"]').classList.add('active');
  }
}

function setupAutoRefresh(fn, intervalMs, countdownElId) {
  let remaining = intervalMs / 1000;
  const el = byId(countdownElId);

  function tick() {
    if (el) el.textContent = `refreshing in ${remaining}s`;
    remaining--;
    if (remaining < 0) {
      fn(); // run refresh
      remaining = intervalMs / 1000;
    }
  }

  fn();
  tick();
  setInterval(tick, 1000);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab').forEach((btn) => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  const btnRefresh = byId('btn-refresh');
  if (btnRefresh) btnRefresh.addEventListener('click', loadList);
  const flt = byId('flt-team');
  if (flt) flt.addEventListener('change', loadList);

  const btnRefreshEvents = byId('refresh-events');
  if (btnRefreshEvents) btnRefreshEvents.addEventListener('click', loadEvents);

  setupAutoRefresh(loadList, 10000, 'list-refresh-countdown');
  setupAutoRefresh(loadEvents, 10000, 'auto-refresh-countdown');
});