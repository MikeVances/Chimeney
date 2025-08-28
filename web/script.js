(function(){
  const form = document.getElementById('search-form');
  const resultDiv = document.getElementById('result');

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
    colRasp.classList.toggle('hidden', k !== 'поворотный');
    colGrav.classList.toggle('hidden', k !== 'гравитационный');
  }

  function toggleKoronaVisibility(){
    if(!colKorona) return; // Korona UI may not exist in current HTML
    const t = fldType.value;
    const k = fldKlapan.value;
    const show = (t === 'приточная пассивная' || t === 'приточная активная') && (k === 'поворотный' || k === 'гравитационный');
    colKorona.classList.toggle('hidden', !show);
    if(!show && cbKorona){ cbKorona.checked = false; }
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
    } else {
      // вернуть опции в исходное состояние
      Array.from(fldKlapan.options).forEach(opt => { if(opt.value === 'гравитационный') opt.disabled = false; });
    }
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

  fldKlapan.addEventListener('change', ()=>{ enforceValveConstraints(); toggleValveFields(); toggleMotorFields(); toggleKoronaVisibility(); enforcePowerByDiamAndType(); });
  fldType.addEventListener('change', ()=>{ enforceValveConstraints(); toggleMotorFields(); toggleValveFields(); toggleKoronaVisibility(); enforcePowerByDiamAndType(); });
  fldDiam.addEventListener('change', ()=>{ enforcePowerByDiamAndType(); });
  enforceValveConstraints(); toggleMotorFields(); toggleValveFields(); toggleKoronaVisibility(); enforcePowerByDiamAndType();

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
      korona: (cbKorona ? ( (fldType.value === 'приточная пассивная' || fldType.value === 'приточная активная') && fldKlapan.value !== 'двустворчатый' ? cbKorona.checked : false ) : false),
      udlinenie_m: Number(fldExt.value || 0)
    };

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
        resultDiv.innerHTML = data.message ? html + `<div class="result-item"><br><em>${data.message}</em></div>` : html;
      } else {
        resultDiv.textContent = data.message || 'Ничего не найдено';
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
})();