(function(){
  const form = document.getElementById('search-form');
  const resultDiv = document.getElementById('result');

  // Храним последний payload для экспорта
  let lastPayload = null;

  // Кнопка для выгрузки Excel. Если её нет в вёрстке — создадим динамически.
  let btnDownload = document.getElementById('download-xlsx');
  function ensureDownloadButton(){
    if (!btnDownload) {
      btnDownload = document.createElement('button');
      btnDownload.type = 'button';
      btnDownload.id = 'download-xlsx';
      btnDownload.textContent = 'Скачать Excel (КП)';
      btnDownload.disabled = true;
      // попробуем вставить в конец формы
      if (form) {
        const wrapper = document.createElement('div');
        wrapper.style.marginTop = '8px';
        wrapper.appendChild(btnDownload);
        form.appendChild(wrapper);
      } else {
        document.body.appendChild(btnDownload);
      }
    }
  }
  ensureDownloadButton();

  const fldType = document.getElementById('тип');
  const fldDiam = document.getElementById('диаметр');
  const fldKlapan = document.getElementById('тип_клапана');
  const fldRasp = document.getElementById('расположение_клапана');
  const fldGrav = document.getElementById('тип_гравитационного');
  const colRasp = document.getElementById('col-расположение');
  const colGrav = document.getElementById('col-тип-гравитационного');
  const fldMotor = document.getElementById('тип_мотора');
  const fldPower = document.getElementById('мощность');
  const fldTop = document.getElementById('верхняя_часть');
  const cbMem = document.getElementById('герм_мембрана');
  const cbLenta = document.getElementById('герм_лента');
  const cbAuto = document.getElementById('автомат');
  const cbKap = document.getElementById('каплеулавливатель');
  const cbMount = document.getElementById('монтажный_комплект');
  const fldExt = document.getElementById('удлинение');
  const cbKorona = document.getElementById('корона');
  const colKorona = document.getElementById('col-корона');

  function mapType(x){
    switch(x){
      case 'вытяжная': return 'VBV';
      case 'приточная активная': return 'VBA';
      case 'приточная пассивная': return 'VBP';
      case 'приточная с подмешиванием': return 'VBR';
      default: return '';
    }
  }
  function mapKlapan(x){
    switch(x){
      case 'поворотный': return 'pov';
      case 'гравитационный': return 'grav';
      case 'двустворчатый': return 'dvustv';
      default: return '';
    }
  }
  function mapPos(x){
    switch(x){
      case 'низ': return 'niz';
      case 'верх': return 'verh';
      default: return '';
    }
  }
  function mapGrav(x){
    switch(x){
      case 'внутренний': return 'vnut';
      case 'внешний': return 'vnesh';
      default: return '';
    }
  }

  function toggleValveFields(){
    const k = fldKlapan.value;
    const isPov = (k === 'поворотный');
    const isGrav = (k === 'гравитационный');

    // Поворотный → требуем и показываем «расположение»
    colRasp.classList.toggle('hidden', !isPov);
    fldRasp.required = isPov;
    if(!isPov){ fldRasp.value = ''; }

    // Гравитационный → требуем и показываем «тип гравитационного»
    colGrav.classList.toggle('hidden', !isGrav);
    fldGrav.required = isGrav;
    if(!isGrav){ fldGrav.value = ''; }
  }

  function toggleKoronaVisibility(){
    if(!colKorona) return; // Korona UI may not exist in current HTML
    const t = fldType.value;
    const k = fldKlapan.value;
    const show = (t === 'приточная пассивная' || t === 'приточная активная') && (k === 'поворотный' || k === 'гравитационный');
    colKorona.classList.toggle('hidden', !show);
    if(!show && cbKorona){ cbKorona.checked = false; }
  }

  function toggleMountVisibility(){
    if(!cbMount) return;
    const t = fldType.value;               // человекочитаемый тип
    const k = fldKlapan.value;             // человекочитаемый клапан
    // Показать только для VB-вариантов (вытяжная/VBV, приточная активная/VBA, приточная пассивная/VBP)
    // и только когда клапан поворотный или гравитационный
    const show = (t === 'вытяжная' || t === 'приточная активная' || t === 'приточная пассивная' || t === 'приточная с подмешиванием') &&
                 (k === 'поворотный' || k === 'гравитационный');
    // сам чекбокс у нас в вёрстке без отдельной колонки; отключим по месту
    const wrapper = cbMount.closest('div');
    if(wrapper){ wrapper.classList.toggle('hidden', !show); }
    if(!show){ cbMount.checked = false; }
  }

  function toggleMotorFields(){
    const t = fldType.value;
    const k = fldKlapan.value;
    const needsMotor = (t === 'вытяжная' || t === 'приточная активная' || t === 'приточная с подмешиванием') && (k === 'поворотный' || k === 'гравитационный');
    fldMotor.disabled = !needsMotor;
    fldPower.disabled = !needsMotor;
    if(!needsMotor){ fldMotor.value=''; fldPower.value=''; }
  }

  function enforceValveConstraints(){
    const t = fldType.value;
    // Для VBA (приточная активная) всегда поворотный клапан — гравитационного не бывает
    if(t === 'приточная активная'){
      // установить значение и запретить выбор гравитационного/двустворчатого
      if(fldKlapan.value !== 'поворотный') fldKlapan.value = 'поворотный';
      // disable gravity option
      Array.from(fldKlapan.options).forEach(opt => {
        if(opt.value === 'гравитационный') opt.disabled = true; else if(opt.value === 'двустворчатый') opt.disabled = false; else opt.disabled = false;
      });
      // показать/требовать расположение, скрыть тип гравитационного
      colRasp.classList.remove('hidden');
      fldRasp.required = true;
      colGrav.classList.add('hidden');
      fldGrav.required = false; fldGrav.value = '';
    } else if(t === 'приточная с подмешиванием'){
      // Для VBR (приточная с подмешиванием) всегда поворотный клапан + расположение низ
      if(fldKlapan.value !== 'поворотный') fldKlapan.value = 'поворотный';
      Array.from(fldKlapan.options).forEach(opt => {
        if(opt.value !== 'поворотный') opt.disabled = true; else opt.disabled = false;
      });
      colRasp.classList.remove('hidden');
      fldRasp.value = 'низ';
      fldRasp.disabled = true;
      fldRasp.required = true;
      colGrav.classList.add('hidden');
      fldGrav.required = false; fldGrav.value = '';
    } else if(t === 'приточная пассивная'){
      // В каталоге нет двустворчатого для VBP — запрещаем и при необходимости переключаем на поворотный
      Array.from(fldKlapan.options).forEach(opt => {
        if(opt.value === 'двустворчатый') opt.disabled = true; else opt.disabled = false;
      });
      if(fldKlapan.value === 'двустворчатый'){
        fldKlapan.value = 'поворотный';
      }
      // Остальные требования к полям (расположение/тип грав.) выставит toggleValveFields()
    } else {
      // вернуть опции в исходное состояние; требования к полям выставит toggleValveFields()
      Array.from(fldKlapan.options).forEach(opt => { opt.disabled = false; });
      fldRasp.disabled = false;
      fldGrav.disabled = false;
    }

    // Ограничение верхней части для приточных шахт (VBA, VBP, VBR)
    if(t === 'приточная активная' || t === 'приточная пассивная' || t === 'приточная с подмешиванием'){
      fldTop.value = 'зонт';
      Array.from(fldTop.options).forEach(opt => { opt.disabled = (opt.value !== 'зонт'); });
      fldTop.disabled = true; // полный запрет изменения
    } else {
      // восстановить доступность опций верхней части
      Array.from(fldTop.options).forEach(opt => { opt.disabled = false; });
      fldTop.disabled = false;
    }
    toggleMountVisibility();
  }

  // --- New function: enforcePowerByDiamAndType ---
  function enforcePowerByDiamAndType(){
    const t = fldType.value;           // человекочитаемый тип
    const d = (fldDiam.value || '').trim();
    const motorized = (t === 'вытяжная' || t === 'приточная активная' || t === 'приточная с подмешиванием');
    if(!motorized){
      // вернуть опции мощности в исходное состояние
      Array.from(fldPower.options).forEach(opt => { opt.disabled = false; });
      return;
    }
    let forced = '';
    if(d === '800') forced = '750';
    else if(d === '560' || d === '710') forced = '370';
    if(forced){
      fldPower.value = forced;
      // визуально ограничим выбор до допустимого значения
      Array.from(fldPower.options).forEach(opt => {
        if(!opt.value) return; // placeholder
        opt.disabled = (opt.value !== forced);
      });
    } else {
      Array.from(fldPower.options).forEach(opt => { opt.disabled = false; });
    }
  }

  async function exportToExcel(payload){
    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || lastPayload || {})
      });
      if (!res.ok) {
        const txt = await res.text();
        alert('Ошибка экспорта: ' + txt);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const fileName = 'KP_' + new Date().toISOString().replaceAll(':','-').slice(0,19) + '.xlsx';
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert('Ошибка экспорта: ' + (e?.message || e));
    }
  }

  function enableDownloadIfResults(results, payload){
    if (Array.isArray(results) && results.length > 0) {
      btnDownload.disabled = false;
      lastPayload = payload || lastPayload;
      btnDownload.onclick = () => exportToExcel(payload);
    } else {
      btnDownload.disabled = true;
      btnDownload.onclick = null;
    }
  }

  // --- Helper to render backend messages with safe <br> and bullet lists ---
  function formatMessage(msg){
    const raw = String(msg || '');
    // Разрешаем только перенос строк: превращаем &lt;br&gt; в <br>
    const withBr = raw.replaceAll('&lt;br&gt;', '<br>');
    // Превратим «• ...» в маркированный список (если такие строки есть)
    const tmp = withBr.replaceAll('<br />', '<br>');
    const lines = tmp.split('<br>').map(s => s.trim()).filter(Boolean);
    const hasBullets = lines.some(l => l.startsWith('•'));
    if (hasBullets){
      const [title, ...rest] = lines;
      const items = rest.map(l => l.replace(/^•\s*/, '')).filter(Boolean);
      const ul = items.length ? `<ul>${items.map(li => `<li>${li}</li>`).join('')}</ul>` : '';
      return `<div>${title || ''}</div>${ul}`;
    }
    return withBr;
  }

  fldKlapan.addEventListener('change', ()=>{ enforceValveConstraints(); toggleValveFields(); toggleMotorFields(); toggleKoronaVisibility(); enforcePowerByDiamAndType(); toggleMountVisibility(); });
  fldType.addEventListener('change', ()=>{ enforceValveConstraints(); toggleMotorFields(); toggleValveFields(); toggleKoronaVisibility(); enforcePowerByDiamAndType(); toggleMountVisibility(); });
  fldDiam.addEventListener('change', ()=>{ enforcePowerByDiamAndType(); });
  enforceValveConstraints(); toggleMotorFields(); toggleValveFields(); toggleKoronaVisibility(); enforcePowerByDiamAndType(); toggleMountVisibility();

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    resultDiv.textContent = 'Расчёт...';

    const payload = {
      tip: mapType(fldType.value),
      diametr: fldDiam.value,
      tip_klapana: mapKlapan(fldKlapan.value),
      raspolozhenie: mapPos(fldRasp.value),
      grav_variant: mapGrav(fldGrav.value),
      tip_motora: document.getElementById('тип_мотора').value, // 6e/6d
      moshchnost: document.getElementById('мощность').value,   // 370/750
      verhnyaya_chast: (fldTop.value === 'зонт' ? 'zont' : (fldTop.value === 'раструб' ? 'rastrub' : '')),
      germetizatsiya: {
        membrana: cbMem.checked,
        lenta: cbLenta.checked
      },
      avtomat: cbAuto.checked,
      kapleulavlivatel: cbKap.checked,
      montazhny_komplekt: cbMount ? cbMount.checked : false,
      korona: (cbKorona ? ( (fldType.value === 'приточная пассивная' || fldType.value === 'приточная активная') && fldKlapan.value !== 'двустворчатый' ? cbKorona.checked : false ) : false),
      udlinenie_m: Number(fldExt.value || 0)
    };
    lastPayload = payload;

    try {
      const resp = await fetch('/api/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();

      if(Array.isArray(data.results) && data.results.length){
        const html = data.results.map(it => {
          const art = it.article ?? '-';
          const name = it.name ?? '-';
          const qty = it.quantity ?? '-';
          return `<div class="result-item"><strong>Артикул:</strong> ${art}<br><strong>Наименование:</strong> ${name}<br><strong>Количество:</strong> ${qty}</div>`;
        }).join('');
        const messageHtml = data.message ? `<div class="result-item"><br><em>${formatMessage(data.message)}</em></div>` : '';
        resultDiv.innerHTML = html + messageHtml;
        enableDownloadIfResults(data.results, payload);
      } else {
        resultDiv.innerHTML = data.message ? `<em>${formatMessage(data.message)}</em>` : 'Ничего не найдено';
        enableDownloadIfResults([], payload);
      }
    } catch(err){
      console.error(err);
      resultDiv.textContent = 'Ошибка запроса';
    }
  });
  const newCalcBtn = document.getElementById('new-calc-btn');
  if (newCalcBtn) {
    newCalcBtn.addEventListener('click', (e)=>{
      e.preventDefault();
      window.location.reload();
    });
  }
  // На старте — кнопка выгрузки не активна
  if (btnDownload) { btnDownload.disabled = true; }
  // --- Swipe navigation between pages (main <-> "Скоро выпуск") ---
  (function setupSwipePages(){
    // Prevent double init
    if (window.__chimeneySwipeInit) return;
    window.__chimeneySwipeInit = true;

    const container = document.getElementById('page-container');
    if (!container) return; // safety: index.html may not yet be updated
    const pageMain = document.getElementById('page-main');
    const pageUpcoming = document.getElementById('page-upcoming');
    const hint = document.querySelector('.hint');
    const pager = document.getElementById('pager');
    const pages = Array.from(container.querySelectorAll('.page'));

    let currentPage = 0; // 0: main, 1: upcoming
    const THRESHOLD = 50;     // min px for swipe
    const ANGLE_GUARD = 0.6;  // ignore mostly vertical gestures

    function updateDots(){
      if (!pager) return;
      for (let i = 0; i < pager.children.length; i++) {
        pager.children[i].classList.toggle('active', i === currentPage);
      }
    }

    function renderPager(){
      if (!pager) return;
      pager.innerHTML = '';
      pages.forEach((_, idx) => {
        const dot = document.createElement('span');
        dot.className = 'dot' + (idx === currentPage ? ' active' : '');
        dot.title = `Страница ${idx + 1}`;
        dot.addEventListener('click', () => goTo(idx));
        pager.appendChild(dot);
      });
    }

    function goTo(page){
      currentPage = Math.max(0, Math.min(pages.length - 1, page));
      const dx = currentPage * -100; // vw
      container.style.transform = `translateX(${dx}vw)`;
      if (pageMain) pageMain.classList.toggle('active', currentPage === 0);
      if (pageUpcoming) pageUpcoming.classList.toggle('active', currentPage === 1);
      if (hint) hint.style.display = (currentPage === 0) ? 'block' : 'none';
      updateDots();
    }

    // --- Touch support on the container (mobile/tablets)
    let startX = 0, startY = 0, tracking = false;
    container.addEventListener('touchstart', (e)=>{
      const t = e.touches[0];
      startX = t.clientX; startY = t.clientY; tracking = true;
    }, {passive:true});

    container.addEventListener('touchmove', (e)=>{
      if (!tracking) return;
      const t = e.touches[0];
      const dx = t.clientX - startX;
      const dy = t.clientY - startY;
      // if horizontal intent dominates — prevent vertical scroll to capture the swipe
      if (Math.abs(dx) > Math.abs(dy) / ANGLE_GUARD) {
        e.preventDefault();
      }
    }, {passive:false});

    container.addEventListener('touchend', (e)=>{
      if (!tracking) return;
      tracking = false;
      const t = e.changedTouches[0];
      const dx = t.clientX - startX;
      const dy = t.clientY - startY;
      if (Math.abs(dx) < THRESHOLD || Math.abs(dx) < Math.abs(dy)) return;
      if (dx < 0 && currentPage < pages.length - 1) goTo(currentPage + 1);
      else if (dx > 0 && currentPage > 0) goTo(currentPage - 1);
    });

    // --- Trackpad / wheel support (desktop & laptops)
    let wheelAccum = 0;
    let lastWheelTs = 0;
    const WHEEL_THRESHOLD = 120; // typical per "one notch"
    container.addEventListener('wheel', (e) => {
      const now = Date.now();
      const absX = Math.abs(e.deltaX), absY = Math.abs(e.deltaY);
      if (absX < absY) return; // mostly vertical — ignore

      if (now - lastWheelTs > 300) wheelAccum = 0; // decay
      wheelAccum += e.deltaX;
      lastWheelTs = now;

      if (wheelAccum > WHEEL_THRESHOLD && currentPage < pages.length - 1) {
        e.preventDefault();
        wheelAccum = 0;
        goTo(currentPage + 1);
      } else if (wheelAccum < -WHEEL_THRESHOLD && currentPage > 0) {
        e.preventDefault();
        wheelAccum = 0;
        goTo(currentPage - 1);
      }
    }, { passive: false });

    // --- Mouse drag support (desktop)
    let mouseDown = false, mStartX = 0, mStartY = 0;
    container.addEventListener('mousedown', (e)=>{
      mouseDown = true; mStartX = e.clientX; mStartY = e.clientY;
    });
    container.addEventListener('mouseup', (e)=>{
      if (!mouseDown) return;
      mouseDown = false;
      const dx = e.clientX - mStartX;
      const dy = e.clientY - mStartY;
      if (Math.abs(dx) < THRESHOLD || Math.abs(dx) < Math.abs(dy)) return;
      if (dx < 0 && currentPage < pages.length - 1) goTo(currentPage + 1);
      else if (dx > 0 && currentPage > 0) goTo(currentPage - 1);
    });

    // --- Keyboard support (desktop): arrows ← →
    document.addEventListener('keydown', (e)=>{
      if (e.key === 'ArrowLeft') goTo(Math.max(0, currentPage - 1));
      else if (e.key === 'ArrowRight') goTo(Math.min(pages.length - 1, currentPage + 1));
    });

    // Init: render dots and always start on page 0 (also after bfcache restore)
    renderPager();
    goTo(0);
    window.addEventListener('pageshow', () => { goTo(0); });
  })();
})();