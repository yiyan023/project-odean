/**
 * Motions API: motion brief filings (list + raw text).
 * Uses limit/offset pagination and data/meta response shape.
 */
const express = require('express');
const path = require('path');
const fs = require('fs');
const config = require('./config');

const app = express();

function listMotions(caseIdFilter) {
  const motionsDir = path.join(config.seedDataDir, 'motions');
  if (!fs.existsSync(motionsDir)) return [];
  const names = fs.readdirSync(motionsDir)
    .filter((n) => n.endsWith('.txt'))
    .sort();
  return names
    .map((name) => ({ filename: name, case_id: name.split('_')[0] }))
    .filter((m) => !caseIdFilter || m.case_id === caseIdFilter);
}

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'motions-api' });
});

// List: uses limit/offset and returns { data, meta } (different from other APIs)
app.get('/motions', (req, res) => {
  const caseId = req.query.case_id || '';
  const limit = Math.min(parseInt(req.query.limit || '100', 10), 500);
  const offset = parseInt(req.query.offset || '0', 10);
  const all = listMotions(caseId || undefined);
  const total = all.length;
  const data = all.slice(offset, offset + limit);
  res.json({
    data,
    meta: { total, limit, offset },
  });
});

app.get('/motions/:filename(*)', (req, res) => {
  const filename = req.params.filename;
  if (filename.includes('..')) return res.status(404).json({ error: 'not found' });
  const filePath = path.join(config.seedDataDir, 'motions', filename);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'not found' });
  res.type('text/plain').sendFile(filePath);
});

app.listen(config.port, () => {
  console.log(JSON.stringify({
    level: 'info',
    msg: 'motions-api listening',
    port: config.port,
    seed_dir: config.seedDataDir,
  }));
});
