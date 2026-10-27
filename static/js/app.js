// ============ SH. ISAXAAQ NOTARY — client scripts ============

// Mobile sidebar
(function () {
  const btn = document.getElementById('menuBtn');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  if (!btn || !sidebar) return;

  function open()  { sidebar.classList.add('open');  overlay.classList.add('show'); }
  function close() { sidebar.classList.remove('open'); overlay.classList.remove('show'); }

  btn.addEventListener('click', () => sidebar.classList.contains('open') ? close() : open());
  overlay.addEventListener('click', close);
})();

// Auto-dismiss alerts after 5s
document.querySelectorAll('.alert').forEach((el) => {
  setTimeout(() => {
    el.style.transition = 'opacity .35s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 350);
  }, 5000);
});

// Confirm-before-submit: <form data-confirm="message">
document.querySelectorAll('form[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (e) => {
    if (!confirm(form.getAttribute('data-confirm'))) e.preventDefault();
  });
});

// Print button: [data-print]
document.querySelectorAll('[data-print]').forEach((el) => {
  el.addEventListener('click', (e) => { e.preventDefault(); window.print(); });
});
