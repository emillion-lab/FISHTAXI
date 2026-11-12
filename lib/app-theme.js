/* fish.taxi v3.4 — дневен/нощен режим с докосване на логото.
 * Нощ: рибата на черна плочка; ден: златната риба. Изборът се помни; без избор — по часа (7–19 ден).
 */
(function(F){
"use strict";
var KEY='ft_theme',de=document.documentElement,img=document.querySelector('.brand img'),DAY=img?img.src:'',
NIGHT='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIwAAABCCAMAAACy/M7IAAAAkFBMVEVjUiaUbhn16Z2omF60kSrr0mXOslXZqyz94jAxJRCIelB7bkXKuodGOSG2rYEBAADyuQjjqAP6xQ7WmgPcogRNKgYpGARTNAlxRQX81io2JQkaEwhmOQWHVwWTZgj4yC/81k6qdwjoty+1hAv95HD0123+9rPWqCz90hnyyE7DigR1Vg3+/dH86JHmukfl141z77FrAAAAMHRSTlP///////////////////////////////////////////////////////////////9Ppz/1AAAIwElEQVR42u2aaZebuBKGAds4TjJjYSEJs68mmLb7//+7qdJm7Ab3cm5m7ofUSXLACOnhrZJKS5z9/5E5f2D+wPwrMHznOD++r4x9dxwR/wcwyc5ZrbzL6eXRvNefK0fwfw0mcdzVq3cC89p2s9l8QzuilWV78RDQ81dO8vthYmfVeSfPa8vj8RfYcWpwfwA7liiZt3I+4zPhuZ+D2bl+CxwbifEAYlG0IZDnOx91mChP3vrjMLHjdy0IAg3ZVqdAUxI0cija08vr6kPfKYb219HzPwjjrDaaZGKI8k3bG2mkFZeXkz++Gz5x3WJt3oa/D5OgKA8k6KcD2YZ03TQVWtOsaUi0KsqkPuXptHGf48TbVr236eJ3YBL3CqLcgxwIbfLMje4sjdI0yvKGkikPIaV36p7hJH1b6K8Y3KcwiQMoU1EAZJ1n0G4qhGAx54lqJ+E8juEnAU/cipIbDyHF5bQZF1vYWpYwe6rMIwqhueQAisVxOWZAmWaN5cHg8U6+mGdZd4WS8BBIliUYp+/aYoIiSQR7v78mAAQ8lBgcjJ3Leu5FxYIlSMaWe1O8LrvC9FPQsIrAM/GHR1bOGIuqibu6Uxe9KeV2g+HN2XLXdq5TFJohyScH9lgwkYca5wCh4zUP3+KWpWURi4MeyFJKCvyHVOier2SbhKUp4GhxSPkQOTeWgysW08FYlwVRHgeUlH19bgDeSnMTO6Tw2nwi/o2lEkuJMlkPUhZZrEnZJGQTa6ZDm0v98HZtcaC7Vxan9ZobS2fiqUqXsnbcG1kgViKN4m58HyYMXde9gnWvcuje4fWrp19fveJj9Yn+KxSGZPMjljgsooam9LZKZmeYZbmHierB9Mgg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',
SUN='<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>',
MOON='<svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>';
function T(bg,en){return F.lang==='bg'?bg:en;}
function auto(){var h=new Date().getHours();return (h>=7&&h<19)?'day':'night';}
function cur(){try{var s=localStorage.getItem(KEY);if(s==='day'||s==='night')return s;}catch(e){}return auto();}
var b=document.querySelector('.brand'),mi;
if(b){mi=document.createElement('i');mi.className='mode';b.appendChild(mi);b.setAttribute('role','button');b.tabIndex=0;}
function apply(m,say){
  de.classList.toggle('day',m==='day');
  var mc=document.querySelector('meta[name="theme-color"]');if(mc)mc.content=m==='day'?'#eceff1':'#0e1012';
  if(img)img.src=m==='day'?DAY:NIGHT;
  if(mi)mi.innerHTML=m==='day'?SUN:MOON;
  if(b)b.setAttribute('aria-label',m==='day'?T('Дневен режим — докосни за нощен','Day mode — tap for night'):T('Нощен режим — докосни за дневен','Night mode — tap for day'));
  if(say&&F.toast)F.toast(m==='day'?T('☀️ Дневен режим · докосни логото за нощен','☀️ Day mode · tap the logo for night'):T('🌙 Нощен режим · докосни логото за дневен','🌙 Night mode · tap the logo for day'));
  if(F.onTheme)F.onTheme(m);
}
F.theme=cur;
apply(cur());
function flip(){var n=de.classList.contains('day')?'night':'day';try{localStorage.setItem(KEY,n);}catch(e){}if(F.buzz)F.buzz(10);apply(n,true);}
if(b){b.addEventListener('click',flip);b.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();flip();}});}
/* без ръчен избор режимът следва часа */
setInterval(function(){try{if(localStorage.getItem(KEY))return;}catch(e){}var m=auto();if((m==='day')!==de.classList.contains('day'))apply(m);},5*60e3);
})(FT);
