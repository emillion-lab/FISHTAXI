/* fish.taxi/join — подробностите за шофьор с български номер (10.11.2026).

Рисува стъпката „Как работиш“ с бутончета вместо писане и сглобява
съобщението точно по drivers/TEMPLATE.txt, за да го прочете
scripts/driver_intake.py без ръчна намеса. Само на български: шаблонът
и приемът са на български; чуждите шофьори минават по краткия път.

Неизбрано поле остава празно — приемът слага разумна стойност и я пише
в отчета. Нищо не се публикува оттук: съобщението отива при Емил.
*/
var JD = (function () {
  var YNA = ['да', 'не', 'по договаряне'];
  var G = [
    ['type', 'Тип', 1, ['седан', 'джип', 'ван']],
    ['seats', 'Места за пътници', 1, ['4', '5', '6', '7', '8']],
    ['pay', 'Плащане', 0, ['кеш', 'карта', 'Revolut']],
    ['langs', 'Езици', 0, ['български', 'английски', 'руски', 'немски', 'френски', 'турски', 'италиански', 'испански', 'чешки', 'арабски', 'китайски']],
    ['air', 'Летище', 1, YNA],
    ['long', 'Дълги курсове', 1, YNA],
    ['night', 'Нощем', 1, YNA],
    ['pets', 'Домашни любимци', 1, YNA],
    ['smoke', 'Непушач ли си', 1, ['да', 'не']]   // само 🚭; „пушене OK“ няма — забранено е
  ];
  var S = { langs: ['български'] }, onchange = function () {};

  function chips(g) {
    return '<div class="dl">' + g[1] + '</div><div class="chips" data-k="' + g[0] + '" data-one="' + g[2] + '">' +
      g[3].map(function (o) { return '<button type="button" class="chip">' + o + '</button>'; }).join('') + '</div>';
  }
  function paint() {
    document.querySelectorAll('#s3b .chips').forEach(function (box) {
      var v = S[box.dataset.k] || [];
      box.querySelectorAll('.chip').forEach(function (c) { c.classList.toggle('on', v.indexOf(c.textContent) >= 0); });
    });
  }
  function render(el, cb) {
    onchange = cb || onchange;
    el.innerHTML =
      '<div class="step-n"><i>4</i><span>Как работиш</span></div>' +
      '<div class="hint" style="margin:-4px 0 6px">Натисни каквото важи. Неизбраното го питаме после.</div>' +
      chips(G[0]) + chips(G[1]) +
      '<div class="dl">Тарифа в евро</div><div class="tar">' +
      '<input id="t1" inputmode="decimal" placeholder="старт"><input id="t2" inputmode="decimal" placeholder="ден / км">' +
      '<input id="t3" inputmode="decimal" placeholder="нощ / км"></div>' +
      '<div class="hint">Или я пропусни — пращаш снимка на табелата.</div>' +
      G.slice(2).map(chips).join('') +
      '<div class="dl">Две изречения за теб и колата</div>' +
      '<textarea id="bio" rows="3" placeholder="Напр.: Карам в София от 12 години. Чиста кола, спокойно каране."></textarea>';
    el.querySelectorAll('.chips').forEach(function (box) {
      box.addEventListener('click', function (e) {
        var c = e.target.closest('.chip'); if (!c) return;
        var k = box.dataset.k, t = c.textContent, v = S[k] || [];
        if (box.dataset.one === '1') S[k] = v[0] === t ? [] : [t];
        else S[k] = v.indexOf(t) >= 0 ? v.filter(function (x) { return x !== t; }) : v.concat([t]);
        paint(); onchange();
      });
    });
    el.querySelectorAll('input,textarea').forEach(function (i) { i.addEventListener('input', function () { onchange(); }); });
    paint();
  }

  /* Тип по модела от регистъра — само предложение, шофьорът го сменя. */
  function guessType(model) {
    var m = (model || '').toUpperCase();
    if (/КАДДИ|ТУРАН|ШАРАН|ТРАНСПОРТЕР|МУЛТИВАН|ВИТО|В-КЛАС|ВИ КЛАС|ДОКЕР|БЕРЛИНГО|ПАРТНЕР|ЛОДЖИ|КАНГО|ДОБЛО|РИФТЪР|ТРАФИК|КАРЕНС|ЗАФИРА|ПРОЕЙС|ДЖОГЪР/.test(m)) return 'ван';
    if (/СПОРТИДЖ|СПОРТЕЙДЖ|ТУКСОН|ТУСАН|РАВ|RAV|КОДИАК|КАРОК|КАШКАЙ|ИКС-ТРЕЙЛ|ДЪСТЕР|ТИГУАН|НИРО|КОНА|ИД\.?4|ID\.?4|ЕНЯК|МОДЕЛ Y|СОРЕНТО|САНТА ФЕ|ВИТАРА/.test(m)) return 'джип';
    return 'седан';
  }
  function preset(model) { S.type = [guessType(model)]; paint(); }

  function titleCase(s) {
    return (s || '').toLowerCase().replace(/(^|[\s\-])(\S)/g, function (a, b, c) { return b + c.toUpperCase(); });
  }
  function one(k) { return (S[k] || [])[0] || ''; }
  function num(id) { var v = (document.getElementById(id).value || '').trim().replace(',', '.'); return v; }

  /* Текстът — точно точките от drivers/TEMPLATE.txt. Редовете преди „1.“ и
     с 📸 приемът ги прескача; там е информацията от регистъра. */
  function message(o) {
    var tar = [num('t1'), num('t2'), num('t3')];
    var trip = [one('air'), one('long'), one('night')];
    var tripTxt = trip.some(Boolean) ? trip.map(function (x) { return x || 'по договаряне'; }).join(' / ') : '';
    var bio = (document.getElementById('bio').value || '').replace(/\s+/g, ' ').trim();
    return '🐟 Заявка за fish.taxi — Founder\n' + o.head + '\n\n' +
      '1. Име и фамилия: ' + o.name + '\n' +
      '2. Телефон: ' + o.phone + '\n' +
      '3. Кола (марка и модел): ' + titleCase(o.model) + '\n' +
      '4. Рег. номер: ' + o.plate + '\n' +
      '5. Тип (седан, джип или ван): ' + one('type') + '\n' +
      '6. Места за пътници: ' + one('seats') + '\n' +
      '7. Тарифа — старт / ден на км / нощ на км: ' + (tar.some(Boolean) ? tar.join(' / ') : 'на снимката') + '\n' +
      '8. Плащане (кеш, карта, Revolut): ' + (S.pay || []).join(', ') + '\n' +
      '9. Езици: ' + (S.langs || []).join(', ') + '\n' +
      '10. Летище / дълги курсове / нощем (да, не или по договаряне): ' + tripTxt + '\n' +
      '11. Домашни любимци (да, не или по договаряне): ' + one('pets') + '\n' +
      '12. Непушач ли си (да/не): ' + one('smoke') + '\n' +
      '13. Две изречения за теб и колата: ' + bio + '\n\n' +
      '📸 Пращам и снимки: лице, колата отвън, салона, табелата с тарифата.';
  }
  return { render: render, preset: preset, message: message };
})();
