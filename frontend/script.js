let candidates = [];

document.getElementById('addCandidateBtn').addEventListener('click', () => {
  const id = Date.now();
  candidates.push({ id, name: '', resume: '' });
  renderCandidates();
});

function renderCandidates() {
  const list = document.getElementById('candidateList');
  list.innerHTML = '';
  candidates.forEach(c => {
    const div = document.createElement('div');
    div.className = 'candidate';
    div.innerHTML = `
      <input type="text" placeholder="Candidate name" data-id="${c.id}" class="cname" value="${c.name}">
      <textarea placeholder="Resume text..." data-id="${c.id}" class="cresume">${c.resume}</textarea>
    `;
    list.appendChild(div);
  });

  document.querySelectorAll('.cname').forEach(el =>
    el.addEventListener('input', e => {
      candidates.find(c => c.id == e.target.dataset.id).name = e.target.value;
    })
  );
  document.querySelectorAll('.cresume').forEach(el =>
    el.addEventListener('input', e => {
      candidates.find(c => c.id == e.target.dataset.id).resume = e.target.value;
    })
  );
}

document.getElementById('analyzeBtn').addEventListener('click', () => {
  const jobDesc = document.getElementById('jobDesc').value;
  document.getElementById('results').innerHTML =
    `<p>Analyze button clicked. Job desc length: ${jobDesc.length} chars, Candidates: ${candidates.length}</p>`;
  // Yahan par baad mein hum backend API call karwayenge
});