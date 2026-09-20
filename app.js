const items = [
['broast','Chicken Broast','بروست عادي','17','920 kcal','broast'],
['broast','Spicy Chicken Broast','بروست حراق','17','920 kcal','broast-spicy'],
['broast','Chicken Broast Bucket','دجاج بروست بكيت','34','8 pieces / ٨ قطع · 1920 kcal','bucket'],
['broast','Spicy Broast Bucket','دجاج بروست بكيت حراق','34','8 pieces / ٨ قطع · 1920 kcal','bucket-spicy'],
['broast','Chicken Fillet','دجاج فيليه','20','820 kcal','fillet'],
['broast','Shrimp Broast','بروست جمبري','22','670 kcal','shrimp'],
['broast','Chicken Strips','دجاج ستريبس','18','870 kcal','strips'],
['broast','Spicy Chicken Strips','دجاج ستريبس حراق','18','870 kcal','strips-spicy'],
['burgers','Chicken Burger','برجر دجاج','8','320 kcal','chicken-burger'],
['burgers','Chicken Burger Meal','وجبة برجر دجاج','15','450 kcal','chicken-meal'],
['burgers','Beef Burger','برجر لحم','8','350 kcal','beef-burger'],
['burgers','Beef Burger Meal','وجبة برجر لحم','15','480 kcal','beef-meal'],
['burgers','Zinger Burger','زنجر برجر','8','345 kcal','zinger'],
['burgers','Zinger Burger Meal','وجبة زنجر برجر','15','500 kcal','zinger-meal'],
['wraps','Nuggets Sandwich','ساندوتش مسحب','8','920 kcal','nuggets-wrap'],
['wraps','Nuggets Sandwich Meal','وجبة ساندوتش مسحب','15','920 kcal','nuggets-meal'],
['wraps','Fish Sandwich','ساندوتش سمك','8','920 kcal','fish-wrap'],
['wraps','Fish Sandwich Meal','وجبة ساندوتش سمك','15','920 kcal','fish-meal'],
['wraps','Shrimp Sandwich','ساندوتش جمبري','10','920 kcal','shrimp-wrap'],
['wraps','Shrimp Sandwich Meal','وجبة ساندوتش جمبري','16','920 kcal','shrimp-meal'],
['wraps','Zinger Sandwich','ساندوتش زنجر','8','920 kcal','zinger-wrap'],
['wraps','Zinger Sandwich Meal','وجبة ساندوتش زنجر','15','920 kcal','wrap-meal'],
['sides','French Fries','بطاطس','4 / 6 / 12','400 kcal','fries'],
['sides','Coleslaw Salad','سلطة ملفوف','3','100 kcal','coleslaw'],
['sides','Spicy Sauce','صلصة حراق','1','44 kcal','spicy-sauce'],
['sides','Garlic Sauce','صلصة ثوم','1','25 kcal','garlic']
];
const grid=document.querySelector('#menu-grid');
function showMenu(category,announce=false){
let index=0;
grid.querySelectorAll('.menu-card').forEach(card=>{const selected=card.dataset.category===category;card.hidden=!selected;if(selected){card.style.animationDelay=`${index*.035}s`;index++;}});
if(announce)document.querySelector('#menu-status').textContent=`Showing ${index} ${category} items`;
}
showMenu('broast');
document.querySelectorAll('.category').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.category').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button))});showMenu(button.dataset.category,true)}));
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
const toggle=document.querySelector('#motion-toggle');
let paused=reduced.matches;
function setMotion(){document.body.classList.toggle('motion-paused',paused);toggle.setAttribute('aria-pressed',String(paused));toggle.setAttribute('aria-label',paused?'Resume animations':'Pause animations');toggle.textContent=paused?'▶ Resume motion':'Ⅱ Pause motion'}
setMotion();toggle.addEventListener('click',()=>{paused=!paused;setMotion()});
reduced.addEventListener('change',e=>{paused=e.matches;setMotion()});
if('IntersectionObserver' in window){document.body.classList.add('js-motion');const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target)}})},{threshold:.12});document.querySelectorAll('.reveal').forEach(el=>observer.observe(el))}
const scene=document.querySelector('#hero-scene');
if(window.matchMedia('(pointer: fine)').matches){const hero=document.querySelector('.hero');hero.addEventListener('pointermove',e=>{if(paused||reduced.matches)return;const r=hero.getBoundingClientRect();scene.style.setProperty('--rx',`${(e.clientX-r.left-r.width/2)/r.width*9}deg`);scene.style.setProperty('--ry',`${-(e.clientY-r.top-r.height/2)/r.height*7}deg`)});hero.addEventListener('pointerleave',()=>{scene.style.setProperty('--rx','0deg');scene.style.setProperty('--ry','0deg')})}


/* Cross-browser image hardening for Safari, Chrome, Samsung Internet, and Android WebView. */
(() => {
  const RETRIES = 2;
  const targets = document.querySelectorAll('.menu-photo img, .store-gallery img, .hero-food, .brand img');

  function cleanUrl(url) {
    try {
      const u = new URL(url, location.href);
      u.searchParams.delete('img_retry');
      return u.pathname + (u.searchParams.size ? '?' + u.searchParams.toString() : '');
    } catch (_) { return url; }
  }

  function wire(img) {
    img.decoding = 'async';
    if (!img.dataset.originalSrc) img.dataset.originalSrc = cleanUrl(img.getAttribute('src') || img.src);

    img.addEventListener('load', () => {
      img.dataset.retries = '0';
      img.style.visibility = '';
      const p = img.closest('.menu-photo');
      if (p) p.classList.remove('image-retrying','image-failed');
    });

    img.addEventListener('error', () => {
      const p = img.closest('.menu-photo');
      const count = Number(img.dataset.retries || '0');
      if (p) p.classList.add('image-retrying');
      img.style.visibility = 'hidden';

      if (count < RETRIES) {
        img.dataset.retries = String(count + 1);
        const delay = count === 0 ? 450 : 1100;
        setTimeout(() => {
          const base = img.dataset.originalSrc;
          const join = base.includes('?') ? '&' : '?';
          img.src = base + join + 'img_retry=' + Date.now();
        }, delay);
      } else if (p) {
        p.classList.remove('image-retrying');
        p.classList.add('image-failed');
      }
    });
  }

  targets.forEach(wire);

  window.addEventListener('online', () => {
    document.querySelectorAll('.menu-photo.image-failed img').forEach(img => {
      const p = img.closest('.menu-photo');
      if (p) { p.classList.remove('image-failed'); p.classList.add('image-retrying'); }
      img.dataset.retries = '0';
      const base = img.dataset.originalSrc;
      const join = base.includes('?') ? '&' : '?';
      img.src = base + join + 'img_retry=' + Date.now();
    });
  });
})();
