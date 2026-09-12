const evidence = {};
const companyContext = { company: 'NVIDIA', industry: 'Semiconductors / AI', website: 'nvidia.com', account_owner: 'Sofia Patel', account_type: 'Strategic Account' };
const allButton = document.querySelector('#researchAll');
const toast = document.querySelector('#toast');

function showToast(message) { toast.textContent = message; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 2800); }
function fieldEl(name) { return document.querySelector(`.field[data-field="${name}"]`); }
function currentMissing() { return [...document.querySelectorAll('.field.missing:not(.is-researched):not(.is-researching)')]; }
function setResearchCopy(el, text) { el.querySelector('.research-copy').textContent = text; }
function wait(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function research(name) {
  const el = fieldEl(name);
  if (!el || el.classList.contains('is-researched') || el.classList.contains('is-researching')) return;
  el.classList.add('is-researching');
  setResearchCopy(el, `Understanding NVIDIA + ${name}…`);
  await wait(430);
  setResearchCopy(el, 'Searching trusted web sources…');
  try {
    const response = await fetch('/research', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ company: 'NVIDIA', field: name, existing_context: companyContext }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Research unavailable');
    setResearchCopy(el, 'Verifying selected evidence…');
    await wait(460);
    evidence[name] = data;
    el.querySelector('.field-value').textContent = data.value;
    el.querySelector('.field-value').classList.remove('empty');
    el.classList.remove('is-researching'); el.classList.add('is-researched');
    el.removeAttribute('data-field'); el.dataset.field = name;
    el.addEventListener('click', event => { if (!event.target.closest('button')) openEvidence(name); });
    return data;
  } catch (error) { el.classList.remove('is-researching'); showToast(error.message); throw error; }
}
function openEvidence(name) {
  const data = evidence[name]; if (!data) return;
  document.querySelector('.evidence-empty').classList.add('hidden'); document.querySelector('.evidence-detail').classList.remove('hidden');
  document.querySelector('#evidenceField').textContent = name; document.querySelector('#evidenceValue').textContent = data.value;
  document.querySelector('#sourceTitle').textContent = data.source_title;
  const url = document.querySelector('#sourceUrl'); url.href = data.source_url; url.textContent = data.source_url.replace(/^https?:\/\//, '');
  const confidence = Math.round(data.confidence * 100); document.querySelector('#confidenceBar').style.width = `${confidence}%`; document.querySelector('#confidenceText').textContent = `${confidence}%`;
  document.querySelector('#rationale').textContent = data.rationale;
  document.querySelector('#researchedAt').textContent = new Date(data.researched_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
  document.querySelector('#modeNote').textContent = data.mode === 'demo' ? 'Demo reliability mode — deterministic, source-backed NVIDIA fixture.' : `Research pipeline: ${data.mode.replace('+', ' + ')}.`;
  document.querySelector('#evidencePanel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
document.querySelectorAll('.lens-action').forEach(button => button.addEventListener('click', event => { event.stopPropagation(); research(button.closest('.field').dataset.field).then(() => openEvidence(button.closest('.field').dataset.field)); }));
allButton.addEventListener('click', async () => {
  const fields = currentMissing().map(el => el.dataset.field); if (!fields.length) return showToast('All available fields are researched.');
  allButton.disabled = true; allButton.innerHTML = '<span>✦</span> Researching context…';
  for (const name of fields) { await research(name); await wait(210); }
  allButton.disabled = false; allButton.innerHTML = '<span>✓</span> All Fields Researched'; showToast(`${fields.length} fields enriched with evidence.`);
});
document.querySelector('#closeEvidence').addEventListener('click', () => { document.querySelector('.evidence-detail').classList.add('hidden'); document.querySelector('.evidence-empty').classList.remove('hidden'); });
