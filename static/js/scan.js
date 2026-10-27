// ============================================================
// Document picker — import a file OR scan from a scanner/camera
// Requires templates/_doc_picker.html in the DOM.
// ============================================================
(function () {
  'use strict';

  var IMAGE_RE = /\.(png|jpe?g|gif|webp|bmp|tiff?)$/i;
  var ALLOWED_RE = /\.(png|jpe?g|gif|webp|bmp|tiff?|pdf)$/i;

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  document.querySelectorAll('[data-docpicker]').forEach(init);

  function init(root) {
    var fileInput = root.querySelector('[data-file-input]');
    var scannedInput = root.querySelector('[data-scanned-input]');
    var pendingBox = root.querySelector('[data-pending]');
    var pendingGrid = root.querySelector('[data-pending-grid]');
    var pendingLabel = root.querySelector('[data-pending-label]');
    var sourceGrid = root.querySelector('[data-source-grid]');

    var modal = root.querySelector('[data-scan-modal]');
    var deviceSel = root.querySelector('[data-scan-device]');
    var dpiSel = root.querySelector('[data-scan-dpi]');
    var colorSel = root.querySelector('[data-scan-color]');
    var startBtn = root.querySelector('[data-scan-start]');
    var cameraBtn = root.querySelector('[data-camera-start]');
    var captureBtn = root.querySelector('[data-camera-capture]');
    var retakeBtn = root.querySelector('[data-camera-retake]');
    var addBtn = root.querySelector('[data-scan-add]');
    var previewImg = root.querySelector('[data-scan-preview]');
    var video = root.querySelector('[data-scan-video]');
    var placeholder = root.querySelector('[data-scan-placeholder]');
    var statusEl = root.querySelector('[data-scan-status]');
    var readyBadge = root.querySelector('[data-scan-ready]');

    if (!fileInput || !scannedInput) return;

    var msg = {
      scanning: root.dataset.msgScanning || 'Scanning…',
      wait: root.dataset.msgWait || '',
      noScanner: root.dataset.msgNoScanner || 'No scanner found.',
      scanFailed: root.dataset.msgScanFailed || 'Scanning failed.',
      cameraFailed: root.dataset.msgCameraFailed || 'Could not access the camera.',
      pagesReady: root.dataset.msgPagesReady || 'page(s) ready',
      noPreview: root.dataset.msgNoPreview || 'No page captured yet.',
      remove: root.dataset.msgRemove || 'Remove',
      pending: root.dataset.msgPending || 'Ready to save'
    };

    // ---- state -------------------------------------------------
    var scanned = [];
    try {
      var parsed = JSON.parse(scannedInput.value || '[]');
      if (Array.isArray(parsed)) scanned = parsed;
    } catch (e) { /* ignore malformed value */ }
    scannedInput.value = JSON.stringify(scanned);

    var preview = null;      // data URL waiting to be added
    var stream = null;       // active camera stream
    var objectUrls = [];     // object URLs to revoke on re-render
    var devicesLoaded = false;
    var statusTimer = null;

    // ---- pending list ------------------------------------------
    function renderPending() {
      objectUrls.forEach(function (u) { URL.revokeObjectURL(u); });
      objectUrls = [];
      pendingGrid.innerHTML = '';

      var files = Array.prototype.slice.call(fileInput.files || []);
      var total = files.length + scanned.length;
      pendingBox.hidden = total === 0;
      if (pendingLabel) {
        pendingLabel.textContent = msg.pending + (total ? ' · ' + total : '');
      }

      files.forEach(function (file, index) {
        pendingGrid.appendChild(makeTile({
          kind: 'file', index: index, name: file.name, file: file
        }));
      });

      scanned.forEach(function (url, index) {
        pendingGrid.appendChild(makeTile({
          kind: 'scan', index: index, name: 'scan-' + (index + 1) + '.jpg', dataUrl: url
        }));
      });
    }

    function makeTile(opts) {
      var item = document.createElement('div');
      item.className = 'pending-item';

      var isPdf = (opts.file && /\.pdf$/i.test(opts.name)) ||
                  (opts.dataUrl && /^data:application\/pdf/i.test(opts.dataUrl));

      if (isPdf) {
        var box = document.createElement('div');
        box.className = 'pending-doc';
        box.innerHTML =
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">' +
          '<path stroke-linecap="round" stroke-linejoin="round" d="M14 2v5a1 1 0 0 0 1 1h5M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7l-5-5Z"/>' +
          '</svg><span>PDF</span>';
        item.appendChild(box);
      } else {
        var img = document.createElement('img');
        img.className = 'pending-thumb';
        img.alt = opts.name;
        var src = opts.dataUrl;
        if (!src && opts.file) {
          src = URL.createObjectURL(opts.file);
          objectUrls.push(src);
        }
        img.src = src;
        item.appendChild(img);
      }

      var cap = document.createElement('div');
      cap.className = 'pending-name';
      cap.title = opts.name;
      cap.textContent = opts.name;
      item.appendChild(cap);

      var del = document.createElement('button');
      del.type = 'button';
      del.className = 'pending-del';
      del.title = msg.remove;
      del.setAttribute('aria-label', msg.remove);
      del.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">' +
        '<path stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>';
      del.addEventListener('click', function () { removeAt(opts.kind, opts.index); });
      item.appendChild(del);

      return item;
    }

    function removeAt(kind, index) {
      if (kind === 'file') {
        var dt = new DataTransfer();
        Array.prototype.slice.call(fileInput.files || []).forEach(function (f, i) {
          if (i !== index) dt.items.add(f);
        });
        try { fileInput.files = dt.files; } catch (e) { /* older browsers */ }
      } else {
        scanned.splice(index, 1);
        scannedInput.value = JSON.stringify(scanned);
      }
      renderPending();
    }

    function addFiles(list) {
      var incoming = Array.prototype.slice.call(list || []).filter(function (f) {
        return ALLOWED_RE.test(f.name);
      });
      if (!incoming.length) return;
      var dt = new DataTransfer();
      Array.prototype.slice.call(fileInput.files || []).forEach(function (f) { dt.items.add(f); });
      incoming.forEach(function (f) { dt.items.add(f); });
      try { fileInput.files = dt.files; } catch (e) { /* older browsers */ }
      renderPending();
    }

    // ---- import ------------------------------------------------
    var importBtn = root.querySelector('[data-import]');
    if (importBtn) {
      importBtn.addEventListener('click', function () { fileInput.click(); });
    }
    fileInput.addEventListener('change', renderPending);

    if (sourceGrid) {
      ['dragenter', 'dragover'].forEach(function (ev) {
        sourceGrid.addEventListener(ev, function (e) {
          e.preventDefault();
          sourceGrid.classList.add('drag');
        });
      });
      ['dragleave', 'drop'].forEach(function (ev) {
        sourceGrid.addEventListener(ev, function () {
          sourceGrid.classList.remove('drag');
        });
      });
      sourceGrid.addEventListener('drop', function (e) {
        e.preventDefault();
        if (e.dataTransfer && e.dataTransfer.files) {
          addFiles(e.dataTransfer.files);
          // Dropped files bypass the file input in some browsers; keep them there
          // so the form posts them. Re-add via DataTransfer when needed.
        }
      });
    }

    // ---- modal helpers -----------------------------------------
    function setStatus(text, kind) {
      if (!statusEl) return;
      if (statusTimer) { clearTimeout(statusTimer); statusTimer = null; }
      if (!text) {
        statusEl.hidden = true;
        statusEl.textContent = '';
        statusEl.className = 'scan-status';
        return;
      }
      statusEl.hidden = false;
      statusEl.className = 'scan-status' + (kind ? ' ' + kind : '');
      statusEl.innerHTML = '';
      if (kind === 'busy') {
        var sp = document.createElement('span');
        sp.className = 'spinner';
        statusEl.appendChild(sp);
      }
      var span = document.createElement('span');
      span.textContent = text;
      statusEl.appendChild(span);
      if (kind === 'ok') {
        statusTimer = setTimeout(function () { setStatus('', ''); }, 6000);
      }
    }

    function setBusy(busy) {
      [startBtn, cameraBtn].forEach(function (b) { if (b) b.disabled = busy; });
      modal.classList.toggle('is-busy', busy);
    }

    function clearPreview(message) {
      preview = null;
      if (previewImg) {
        previewImg.hidden = true;
        previewImg.removeAttribute('src');
      }
      if (video) video.hidden = true;
      if (placeholder) {
        placeholder.hidden = false;
        placeholder.textContent = message || msg.noPreview;
      }
      if (addBtn) addBtn.disabled = true;
      if (captureBtn) captureBtn.hidden = true;
      if (retakeBtn) retakeBtn.hidden = true;
    }

    function showPreview(url) {
      preview = url;
      if (previewImg) {
        previewImg.src = url;
        previewImg.hidden = false;
      }
      if (placeholder) placeholder.hidden = true;
      if (video) video.hidden = true;
      if (captureBtn) captureBtn.hidden = true;
      if (retakeBtn) retakeBtn.hidden = true;
      if (addBtn) addBtn.disabled = false;
    }

    function openModal() {
      modal.hidden = false;
      document.body.style.overflow = 'hidden';
      clearPreview();
      setStatus('', '');
      if (!devicesLoaded) loadDevices();
      if (startBtn) startBtn.focus();
    }

    function closeModal() {
      stopCamera();
      modal.hidden = true;
      document.body.style.overflow = '';
      clearPreview();
      setStatus('', '');
    }

    var scanBtn = root.querySelector('[data-scan]');
    if (scanBtn) scanBtn.addEventListener('click', openModal);
    root.querySelectorAll('[data-scan-close]').forEach(function (b) {
      b.addEventListener('click', closeModal);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !modal.hidden) closeModal();
    });

    // ---- devices -----------------------------------------------
    function loadDevices() {
      devicesLoaded = true;
      setStatus(msg.wait || msg.scanning, 'busy');
      fetch('/scan/devices', { headers: { Accept: 'application/json' }, credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          deviceSel.innerHTML = '';
          var placeholderOpt = new Option(deviceSel.dataset.placeholder || '—', '');
          deviceSel.appendChild(placeholderOpt);

          var list = (data && data.devices) || [];
          if (!data || !data.available || !list.length) {
            if (startBtn) startBtn.disabled = true;
            if (readyBadge) readyBadge.hidden = true;
            setStatus(msg.noScanner, 'warn');
            return;
          }
          list.forEach(function (d) { deviceSel.appendChild(new Option(d.name, d.id)); });
          if (startBtn) startBtn.disabled = false;
          if (readyBadge) readyBadge.hidden = false;
          setStatus('', '');
        })
        .catch(function () {
          if (startBtn) startBtn.disabled = true;
          if (readyBadge) readyBadge.hidden = true;
          setStatus(msg.noScanner, 'warn');
        });
    }

    // ---- scan --------------------------------------------------
    if (startBtn) {
      startBtn.addEventListener('click', function () {
        stopCamera();
        setBusy(true);
        setStatus(msg.scanning, 'busy');
        fetch('/scan/capture', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            device: deviceSel.value || null,
            dpi: parseInt(dpiSel.value, 10) || 200,
            color: colorSel.value === '1'
          })
        })
          .then(function (r) {
            return r.json().then(function (data) { return { ok: r.ok, data: data }; });
          })
          .then(function (res) {
            if (!res.ok || !res.data || !res.data.ok || !res.data.image) {
              throw new Error((res.data && res.data.error) || msg.scanFailed);
            }
            showPreview(res.data.image);
            setStatus('', '');
          })
          .catch(function (err) {
            setStatus(err.message || msg.scanFailed, 'error');
          })
          .finally(function () { setBusy(false); });
      });
    }

    // ---- camera ------------------------------------------------
    function startCamera() {
      stopCamera();
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setStatus(msg.cameraFailed, 'error');
        return;
      }
      navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1440 } },
        audio: false
      }).then(function (s) {
        stream = s;
        video.srcObject = s;
        video.hidden = false;
        if (previewImg) previewImg.hidden = true;
        if (placeholder) placeholder.hidden = true;
        if (captureBtn) captureBtn.hidden = false;
        if (retakeBtn) retakeBtn.hidden = true;
        if (addBtn) addBtn.disabled = true;
        preview = null;
        setStatus('', '');
        var p = video.play();
        if (p && p.catch) p.catch(function () { /* autoplay blocked; user can tap capture */ });
      }).catch(function () {
        setStatus(msg.cameraFailed, 'error');
      });
    }

    function stopCamera() {
      if (stream) {
        stream.getTracks().forEach(function (t) { t.stop(); });
        stream = null;
      }
      if (video) {
        video.srcObject = null;
        video.hidden = true;
      }
    }

    if (cameraBtn) cameraBtn.addEventListener('click', startCamera);
    if (retakeBtn) retakeBtn.addEventListener('click', startCamera);

    if (captureBtn) {
      captureBtn.addEventListener('click', function () {
        if (!video || !video.videoWidth) {
          setStatus(msg.cameraFailed, 'error');
          return;
        }
        var w = video.videoWidth;
        var h = video.videoHeight;
        var canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        canvas.getContext('2d').drawImage(video, 0, 0, w, h);
        var url = canvas.toDataURL('image/jpeg', 0.92);
        stopCamera();
        showPreview(url);
        if (retakeBtn) retakeBtn.hidden = false;
      });
    }

    // ---- add the previewed page to the record -------------------
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        if (!preview) return;
        scanned.push(preview);
        scannedInput.value = JSON.stringify(scanned);
        renderPending();
        clearPreview();
        setStatus(scanned.length + ' ' + msg.pagesReady, 'ok');
      });
    }

    renderPending();
  }
})();
