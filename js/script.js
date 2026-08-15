const originalFetch = window.fetch;
window.fetch = function() {
    let [resource, config] = arguments;
    if (typeof resource === 'string' && resource.startsWith('/api/')) {
        if (location.protocol === 'file:' || (location.hostname.match(/localhost|127\.0\.0\.1/) && location.port !== '5000')) {
            resource = 'http://127.0.0.1:5000' + resource;
        }
    }
    return originalFetch(resource, config);
};
['css/enhancements.css', 'css/premium.css', 'css/commerce.css', 'css/discover.css', 'css/catalog.css', 'css/journal-gifts.css', 'css/bell-notify.css'].forEach(href => { const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = href; document.head.append(link); });
const formatCurrency = value => `₹${Math.round(Number(value) * 25 / 10) * 10}`;
const formatINR = value => `₹${Number(value).toLocaleString('en-IN')}`;
window.escapeHTML = str => String(str).replace(/[&<>'"]/g, tag => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[tag]));
const localizeCafe = () => {
  document.title = document.title.replaceAll('Boojee', 'Boojee');
  document.querySelectorAll('a[href*="boojeecafe.com"]').forEach(link => link.href = link.href.replace('boojeecafe.com', 'boojeecafe.in'));
  document.querySelectorAll('[data-price]').forEach(button => { if (button.dataset.currency !== 'inr') { button.dataset.price = String(Math.round(Number(button.dataset.price) * 25 / 10) * 10); button.dataset.currency = 'inr'; } });
  document.querySelectorAll('[data-gift]').forEach(button => { if (button.dataset.currency !== 'inr') { const amount = Math.round(Number(button.dataset.gift) * 25 / 100) * 100; button.dataset.gift = String(amount); button.textContent = `₹${amount}`; button.dataset.currency = 'inr'; } });
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textNodes = []; while (walker.nextNode()) textNodes.push(walker.currentNode);
  textNodes.forEach(node => { node.nodeValue = node.nodeValue.replaceAll('Boojee Cafe', 'Boojee Cafe').replaceAll('Boojee', 'Boojee').replaceAll('53 Clerkenwell Road', 'Shop No. 6, New Kantwadi Road').replaceAll('London EC1M 5PS', 'Off Perry Cross Road, Bandra West, Mumbai 400050').replaceAll('CLERKENWELL, LONDON', 'BANDRA WEST, MUMBAI').replaceAll('CLERKENWELL', 'BANDRA WEST').replaceAll('ISLINGTON', 'BANDRA').replaceAll('LONDON', 'MUMBAI').replaceAll('London', 'Mumbai').replace(/£(\d+(?:\.\d+)?)/g, (_, amount) => formatCurrency(amount)); });
};
localizeCafe(); setTimeout(localizeCafe, 0);
const header = document.querySelector('.header');
const setHeaderState = () => header?.classList.toggle('is-scrolled', window.scrollY > 36);
setHeaderState(); window.addEventListener('scroll', setHeaderState, { passive: true });
const pageName = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav a').forEach(link => { if (link.getAttribute('href') === pageName) link.setAttribute('aria-current', 'page'); });
setTimeout(() => document.querySelectorAll('.nav a').forEach(link => { if (link.getAttribute('href') === pageName) link.setAttribute('aria-current', 'page'); }), 0);
const revealTargets = document.querySelectorAll('.section, .craft, .experience, .guest-notes, .club, .cta-band, .journal-card, .gift-panel');
if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) { const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); } }), { threshold: 0.12 }); revealTargets.forEach(target => { target.classList.add('reveal'); observer.observe(target); }); }
const navToggle = document.querySelector('.nav-toggle'); const nav = document.querySelector('.nav');
if (navToggle && nav) { [['experiences.html', 'Experiences'], ['journal.html', 'Journal'], ['gifts.html', 'Gifts']].forEach(([href, label]) => { if (!nav.querySelector(`[href="${href}"]`)) nav.insertAdjacentHTML('beforeend', `<a href="${href}">${label}</a>`); }); nav.querySelector('[href="login.html"]')?.remove(); const isLoggedIn = !!localStorage.getItem('boojee_token'); const orderButton = document.querySelector('.header .order-button'); if (orderButton && !document.querySelector('.header .account-button')) orderButton.insertAdjacentHTML('beforebegin', `<a class="account-button" href="${isLoggedIn ? 'profile.html' : 'login.html'}">${isLoggedIn ? 'Profile' : 'Log in'}</a>`); navToggle.addEventListener('click', () => { const open = nav.classList.toggle('open'); navToggle.setAttribute('aria-expanded', String(open)); navToggle.textContent = open ? 'Close' : 'Menu'; }); nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => { nav.classList.remove('open'); navToggle.setAttribute('aria-expanded', 'false'); navToggle.textContent = 'Menu'; })); }
const toast = document.querySelector('#toast'); let timer; const notify = message => { if (!toast) return; toast.textContent = message; toast.classList.add('show'); clearTimeout(timer); timer = setTimeout(() => toast.classList.remove('show'), 2600); };
const savedCart = localStorage.getItem('boojee-cart');
const cart = new Map(savedCart ? JSON.parse(savedCart) : []);
window.saveCart = () => {
    localStorage.setItem('boojee-cart', JSON.stringify([...cart]));
    const token = localStorage.getItem('boojee_token');
    if (token) {
        fetch('/api/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ cart: Object.fromEntries(cart) })
        }).catch(err => window.console.error(err));
    }
};
window.syncCartFromBackend = async () => {
    const token = localStorage.getItem('boojee_token');
    if (!token) return;
    try {
        const res = await fetch('/api/cart', { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) {
            const data = await res.json();
            if (data.cart && Object.keys(data.cart).length > 0) {
                cart.clear();
                Object.entries(data.cart).forEach(([k, v]) => cart.set(k, v));
                localStorage.setItem('boojee-cart', JSON.stringify([...cart]));
                if (typeof renderCart === 'function') renderCart();
            }
        }
    } catch (e) { window.console.error(e); }
};
window.syncCartFromBackend();
const count = document.querySelector('#cartCount'); const prices = {'Velvet Hot Chocolate':120,'Garden Strawberry Tart':150,'Dark Chocolate Cookie':100};
document.body.insertAdjacentHTML('beforeend', '<div class="desk-backdrop"></div><aside class="order-desk" aria-label="Your order"><div class="desk-head"><div><p class="kicker">CLICK & COLLECT</p><h2>Your order</h2></div><button class="desk-close" type="button">Close</button></div><div class="desk-items"><p class="desk-empty">Your order is waiting for something delicious.</p></div><div class="collection"><label for="collectionTime">⏳ Collection time</label><select id="collectionTime"></select></div><div class="desk-total"><span>Total</span><strong>£0.00</strong></div><button class="button dark desk-checkout" type="button">Continue to secure checkout</button><p class="checkout-note">A secure payment flow can be connected here.</p></aside>');
const updateCollectionTimes = () => {
    const select = document.getElementById('collectionTime');
    if (!select) return;
    const now = new Date();
    const formatTime = (addMinutes) => {
        const t = new Date(now.getTime() + addMinutes * 60000);
        return t.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    };
    const prevValue = select.value;
    select.innerHTML = `
        <option value="15">Asap · ${formatTime(15)}</option>
        <option value="30">In 30 mins · ${formatTime(30)}</option>
        <option value="45">In 45 mins · ${formatTime(45)}</option>
        <option value="60">In 1 hour · ${formatTime(60)}</option>
    `;
    if (prevValue && select.querySelector(`[value="${prevValue}"]`)) {
        select.value = prevValue;
    }
};
updateCollectionTimes();
setInterval(updateCollectionTimes, 60000);
const desk = document.querySelector('.order-desk'), backdrop = document.querySelector('.desk-backdrop'), deskItems = document.querySelector('.desk-items'), deskTotal = document.querySelector('.desk-total strong');
const openDesk = () => { desk.classList.add('open'); backdrop.classList.add('open'); document.body.style.overflow = 'hidden'; };
const closeDesk = () => { desk.classList.remove('open'); backdrop.classList.remove('open'); document.body.style.overflow = ''; };
document.querySelectorAll('.order-button,[data-order]').forEach(button => button.addEventListener('click', event => { event.preventDefault(); openDesk(); })); document.querySelector('.desk-close').addEventListener('click', closeDesk); backdrop.addEventListener('click', closeDesk);
function renderCart(){ let quantity=0,total=0; deskItems.replaceChildren(); if(!cart.size){deskItems.innerHTML='<p class="desk-empty">Your order is waiting for something delicious.</p>';} cart.forEach((item,name)=>{quantity+=item.quantity;total+=item.price*item.quantity;const row=document.createElement('article');row.className='desk-item';row.innerHTML=`<strong>${window.escapeHTML(name)}</strong><span>${window.escapeHTML(item.quantity)} × ${formatINR(item.price)}</span><button type="button" aria-label="Remove ${window.escapeHTML(name)}">Remove</button>`;row.querySelector('button').addEventListener('click',()=>{cart.delete(name);renderCart();});deskItems.append(row);}); if(count) count.textContent=quantity; deskTotal.textContent=formatINR(total); window.saveCart(); }
renderCart();
document.querySelectorAll('[data-add]').forEach(button => button.addEventListener('click', () => { const name=button.dataset.add, product=cart.get(name)||{price:Number(button.dataset.price)||prices[name]||0,quantity:0}; product.quantity+=1;cart.set(name,product);renderCart();notify(`${name} added to your order.`); }));
document.querySelector('.desk-checkout').addEventListener('click', async () => {
    if(!cart.size) { notify('Please add something to your order first.'); return; }
    const token = localStorage.getItem('boojee_token');
    if (!token) { notify('Please log in to proceed to checkout.'); setTimeout(() => location.href='login.html', 2000); return; }
    location.href = 'checkout.html';
});
let selectedGift = Number(document.querySelector('[data-gift].selected')?.dataset.gift || 500); document.querySelectorAll('[data-gift]').forEach(button => button.addEventListener('click', () => { selectedGift = Number(button.dataset.gift); document.querySelectorAll('[data-gift]').forEach(item => item.classList.toggle('selected', item === button)); })); document.querySelector('#giftForm')?.addEventListener('submit', event => { event.preventDefault(); const name = `Digital Gift Card · ${formatINR(selectedGift)}`; const product = cart.get(name) || {price:selectedGift,quantity:0}; product.quantity += 1; cart.set(name, product); renderCart(); event.currentTarget.reset(); openDesk(); notify('Gift card added to your order.'); });
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('[data-filter]').forEach(item => item.classList.toggle('selected', item === button)); const filter = button.dataset.filter; document.querySelectorAll('.products article').forEach(card => card.hidden = filter !== 'all' && card.dataset.category !== filter); }));
document.querySelector('#enquiryForm')?.addEventListener('submit', event => { event.preventDefault(); event.currentTarget.reset(); notify('Thank you. We will be in touch shortly.'); });
(() => {
  const bell = document.querySelector('[data-bell-toggle]');
  const button = document.querySelector('[data-bell-button]');
  if (!bell || !button) return;
  
  const style = document.createElement('style');
  style.textContent = '[data-bell-button]:focus, [data-bell-toggle]:focus { outline: none !important; -webkit-tap-highlight-color: transparent; }';
  document.head.append(style);

  if (localStorage.getItem('boojee-bell') === 'on') {
    bell.classList.remove('off');
  }

  const syncBell = () => {
    const enabled = !bell.classList.contains('off');
    bell.setAttribute('aria-pressed', String(enabled));
    bell.setAttribute('aria-label', enabled ? 'Turn cafe notifications off' : 'Turn cafe notifications on');
    button.classList.toggle('is-on', enabled);
    button.textContent = enabled ? 'Alerts On' : 'Notify Me';
  };
  const toggleBell = () => {
    bell.classList.toggle('off');
    localStorage.setItem('boojee-bell', bell.classList.contains('off') ? 'off' : 'on');
    syncBell();
    notify(bell.classList.contains('off') ? 'Cafe alerts are off.' : 'Cafe alerts are on for fresh drops.');
  };
  
  button.addEventListener('click', toggleBell);
  syncBell();
})();
if (document.querySelector('.hero')) { document.querySelector('.hero').insertAdjacentHTML('beforeend','<p class="service-status" id="serviceStatus">Checking today’s service</p>'); const status=document.querySelector('#serviceStatus'); const updateStatus=()=>{const now=new Date(),day=now.getDay(),hour=now.getHours(),open=day>0&&day<6&&hour>=7&&hour<18||day===6&&hour>=8&&hour<17; status.textContent=open?'Open now · walk-ins welcome':'Currently closed · see you soon';status.classList.toggle('closed',!open);};updateStatus();setInterval(updateStatus,60000); }
if (document.querySelector('.intro')) { document.body.insertAdjacentHTML('afterbegin', '<div class="announcement">Summer table service is now available <span>·</span> Private gatherings at Boojee</div>'); const craft = document.querySelector('.craft'); craft.insertAdjacentHTML('afterend', '<section class="experience"><div class="experience-copy"><p class="kicker">THE SALON AT Boojee</p><h2>For days worth<br><em>lingering over.</em></h2><p>A beautiful, understated space for intimate breakfasts, team gatherings and celebrations. Our team creates a table that feels entirely yours.</p><a class="button light" href="experiences.html">Explore private dining</a></div><div class="experience-image"><img src="images/boojee-cafe-mark.svg" alt="Boojee Cafe custom logo"></div></section><section class="guest-notes"><div class="notes-heading"><div><p class="kicker">GUEST NOTES</p><h2>A local <em>favourite.</em></h2></div><p>Kind words from the guests who have made Boojee part of their ritual.</p></div><div class="note-grid"><article class="note"><blockquote>“The kind of place that makes a weekday feel considered.”</blockquote><cite>MARTHA G. · CLERKENWELL</cite></article><article class="note"><blockquote>“Exceptional coffee, even better attention to detail.”</blockquote><cite>JAMES R. · LONDON</cite></article><article class="note"><blockquote>“Our table for every small celebration.”</blockquote><cite>FLORENCE & TOM · ISLINGTON</cite></article></div></section><section class="club"><div><p class="kicker">THE Boojee LETTER</p><h2>Notes from<br><em>lingering over.</em></h2></div><div><p>Seasonal menus, first invitations and the occasional recipe from our kitchen—sent thoughtfully, never often.</p><form class="club-form" data-club-form><input aria-label="Email address" type="email" required placeholder="Your email address"><button class="button dark">Join the letter</button></form></div></section>'); document.querySelector('[data-club-form]')?.addEventListener('submit', event => { event.preventDefault(); event.currentTarget.reset(); notify('You are now on the Boojee letter.'); }); }
// Gift card live preview and enhancements
(() => { const amount = document.querySelector('#giftPreviewAmount'), recipient = document.querySelector('#giftPreviewRecipient'), occasion = document.querySelector('#giftPreviewOccasion'), date = document.querySelector('#giftPreviewDate'), message = document.querySelector('#giftPreviewMessage'), custom = document.querySelector('#customGift'); if (!amount) return; let liveAmount = Number(document.querySelector('[data-gift].selected')?.dataset.gift || 500); const refresh = () => { const delivery = document.querySelector('#giftDate')?.value; selectedGift = liveAmount; amount.textContent = formatINR(liveAmount); if (recipient) recipient.textContent = document.querySelector('#giftRecipient')?.value || 'your recipient'; if (occasion) occasion.textContent = document.querySelector('#giftOccasion')?.value || 'Just because'; if (date) date.textContent = delivery ? new Date(`${delivery}T00:00:00`).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' }) : 'Instant digital delivery'; if (message) message.textContent = document.querySelector('#giftMessage')?.value || 'Your thoughtful note will appear here.'; }; document.querySelectorAll('[data-gift]').forEach(button => button.addEventListener('click', () => { liveAmount = Number(button.dataset.gift); if (custom) custom.value = ''; refresh(); })); custom?.addEventListener('input', () => { if (Number(custom.value) >= 5) { liveAmount = Number(custom.value); document.querySelectorAll('[data-gift]').forEach(button => button.classList.remove('selected')); refresh(); } }); ['#giftRecipient','#giftMessage','#giftOccasion','#giftDate'].forEach(selector => { const field = document.querySelector(selector); field?.addEventListener('input', refresh); field?.addEventListener('change', refresh); }); refresh(); })();
const copyAddress = document.querySelector('[data-copy-address]'); copyAddress?.addEventListener('click', async () => { const address = 'Shop No. 6, New Kantwadi Road, off Perry Cross Road, Bandra West, Mumbai, Maharashtra 400050'; try { await navigator.clipboard.writeText(address); notify('Address copied to your clipboard.'); } catch { notify(`Address: ${address}`); } });
const menuPhotoBySection = { coffee: 'images/menu-coffee.png', breakfast: 'images/menu-breakfast.png', lunch: 'images/menu-lunch.png', sweet: 'images/menu-pastries.png', tea: 'images/menu-drinks.png' };
const menuPhotoByItem = { 'House Espresso': 'images/menu-espresso.png', 'Americano': 'images/menu-americano.png', 'Flat White': 'images/menu-flat-white.png', 'Oat Flat White': 'images/menu-oat-flat-white.png', 'Cappuccino': 'images/menu-cappuccino.png', 'Filter of the Day': 'images/menu-filter-coffee.png', 'Mocha': 'images/menu-mocha.png', 'Velvet Hot Chocolate': 'images/Cup-of-Hot-Chocolate.png', 'Garden Strawberry Tart': 'images/Strawberry-Tarts.png', 'Dark Chocolate Cookie': 'images/Cookies.png' };
const menuCategoryNotes = { coffee: ['OUR BAR', 'Built around seasonal lots and carefully calibrated extraction, every cup is balanced for sweetness, clarity and a quietly memorable finish.'], breakfast: ['THE MORNING TABLE', 'Generous plates, warm pastries and bright seasonal produce—designed for slow starts, quick catch-ups and a second coffee.'], lunch: ['FROM THE KITCHEN', 'Our lunch plates lean fresh and satisfying, with vibrant vegetables, good bread and thoughtful details in every bite.'], sweet: ['BAKED TODAY', 'Small-batch pastries and cakes arrive through the day. Choose something familiar, or ask what has just come from the oven.'], tea: ['A DIFFERENT RITUAL', 'Loose-leaf teas and house-made cold drinks offer a refreshing pause, whether you are staying a while or taking one to go.'] };
Object.entries(menuCategoryNotes).forEach(([sectionId, [label, copy]]) => { const heading = document.querySelector(`#${sectionId} .catalog-heading`); if (heading && !heading.querySelector('.catalog-detail')) heading.insertAdjacentHTML('beforeend', `<p class="catalog-detail"><strong>${label}</strong>${copy}</p>`); });
Object.entries(menuPhotoBySection).forEach(([sectionId, src]) => document.querySelectorAll(`#${sectionId} .catalog-grid article`).forEach(card => { const name = card.querySelector('h3')?.textContent.trim(); const photo = menuPhotoByItem[name] || src; if (name && !card.querySelector('img')) card.insertAdjacentHTML('afterbegin', `<img class="catalog-card-image" src="${photo}" alt="${name}">`); }));
['css/visit.css', 'css/site-features.css'].forEach(href => { const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = href; document.head.append(link); });
// Site-wide quality-of-life features
const savedTheme = localStorage.getItem('boojee-theme'); if (savedTheme === 'dark') document.documentElement.classList.add('dark-mode');
const utility = document.createElement('div'); utility.className = 'site-utility'; utility.innerHTML = '<button type="button" data-theme-toggle aria-label="Toggle dark mode">☾</button><button type="button" data-top aria-label="Back to top">↑</button>'; document.body.append(utility);
const themeButton = utility.querySelector('[data-theme-toggle]'); const syncThemeButton = () => { const dark = document.documentElement.classList.contains('dark-mode'); themeButton.textContent = dark ? '☀' : '☾'; themeButton.setAttribute('aria-label', dark ? 'Use light mode' : 'Use dark mode'); }; syncThemeButton(); themeButton.addEventListener('click', () => { document.documentElement.classList.toggle('dark-mode'); localStorage.setItem('boojee-theme', document.documentElement.classList.contains('dark-mode') ? 'dark' : 'light'); syncThemeButton(); });
const topButton = utility.querySelector('[data-top]'); const updateTop = () => topButton.classList.toggle('visible', window.scrollY > 420); updateTop(); window.addEventListener('scroll', updateTop, { passive: true }); topButton.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
const journalCards = [...document.querySelectorAll('.journal-card')]; const journalButtons = [...document.querySelectorAll('[data-journal-filter]')]; const journalSearch = document.querySelector('#journalSearch'); const applyJournalFilter = () => { const category = document.querySelector('[data-journal-filter].selected')?.dataset.journalFilter || 'all'; const query = (journalSearch?.value || '').trim().toLowerCase(); journalCards.forEach(card => { const matchesCategory = category === 'all' || card.dataset.journalCategory === category; const matchesQuery = !query || card.textContent.toLowerCase().includes(query); card.hidden = !(matchesCategory && matchesQuery); }); }; journalButtons.forEach(button => button.addEventListener('click', () => { journalButtons.forEach(item => item.classList.toggle('selected', item === button)); applyJournalFilter(); })); journalSearch?.addEventListener('input', applyJournalFilter);
const storyModal = document.querySelector('#storyModal'); const storyTitle = document.querySelector('#storyTitle'); const storyBody = document.querySelector('#storyBody'); const storyCopy = { 'Why summer berries deserve the simplest table.': 'Peak fruit asks for very little: a crisp shell, softly whipped cream and a table shared with friends. We let the berries lead, then finish with a bright leaf of lemon verbena.', 'The quiet craft of an excellent hot chocolate.': 'Our bar team balances dark chocolate, whole milk and a pinch of sea salt. The result is deep, silky and never too sweet.', 'The brown butter cookie, perfected over time.': 'A patient bake gives the butter time to turn nutty and golden. Add a little flaky salt just before the tray leaves the oven.' }; document.querySelectorAll('[data-read-story]').forEach(link => link.addEventListener('click', event => { event.preventDefault(); const card = link.closest('.journal-card'); const title = card?.querySelector('h2,h3')?.textContent.trim() || 'A note from our table.'; if (storyTitle) storyTitle.textContent = title; if (storyBody) storyBody.textContent = storyCopy[title] || 'A considered recipe, a good cup and a little time to linger. We will share the full story soon.'; storyModal?.classList.add('open'); storyModal?.setAttribute('aria-hidden', 'false'); })); document.querySelector('.story-close')?.addEventListener('click', () => { storyModal.classList.remove('open'); storyModal.setAttribute('aria-hidden', 'true'); }); storyModal?.addEventListener('click', event => { if (event.target === storyModal) { storyModal.classList.remove('open'); storyModal.setAttribute('aria-hidden', 'true'); } });
document.querySelectorAll('[data-save-story]').forEach(button => { const card = button.closest('.journal-card'); const title = card?.querySelector('h2,h3')?.textContent.trim(); const savedStories = JSON.parse(localStorage.getItem('boojee-saved-stories') || '[]'); if (savedStories.includes(title)) button.textContent = 'Saved ✓'; button.addEventListener('click', () => { const saved = JSON.parse(localStorage.getItem('boojee-saved-stories') || '[]'); const index = saved.indexOf(title); if (index >= 0) { saved.splice(index, 1); button.textContent = 'Save for later'; notify('Story removed from your saved notes.'); } else { saved.push(title); button.textContent = 'Saved ✓'; notify('Story saved for later.'); } localStorage.setItem('boojee-saved-stories', JSON.stringify(saved)); }); });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && storyModal?.classList.contains('open')) document.querySelector('.story-close')?.click(); });
document.querySelector('.club h2 em')?.replaceChildren('our table.');
