/* Poonia Movers — Free Quote modal (2026-10-05) */
(function(){
  "use strict";
  var MODAL_HTML =
  '<div id="pm-quote-modal" role="dialog" aria-label="Get free quote" aria-hidden="true">' +
  '<div class="pq-backdrop" data-pq-close></div>' +
  '<div class="pq-box">' +
  '<button class="pq-close" data-pq-close aria-label="Close">×</button>' +
  '<h3>📝 Get Your FREE Quote</h3>' +
  '<p class="pq-sub">Fill in 30 seconds — quote arrives on WhatsApp. <strong>0% advance.</strong></p>' +
  '<form id="pq-form">' +
  '<input type="text" id="pq-name" placeholder="Your name *" required maxlength="60">' +
  '<input type="tel" id="pq-phone" placeholder="Mobile number *" required pattern="[0-9+ ]{10,15}" maxlength="15">' +
  '<div class="pq-row">' +
  '<input type="text" id="pq-from" placeholder="Pickup area (e.g. Mansarovar) *" required maxlength="60">' +
  '<input type="text" id="pq-to" placeholder="Drop city/area *" required maxlength="60">' +
  '</div>' +
  '<div class="pq-row">' +
  '<select id="pq-service">' +
  '<option value="House shifting">House shifting</option>' +
  '<option value="Office relocation">Office relocation</option>' +
  '<option value="Car / bike transport">Car / bike transport</option>' +
  '<option value="Truck rental">Truck rental</option>' +
  '<option value="Warehouse storage">Warehouse storage</option>' +
  '<option value="Part load">Part load</option>' +
  '</select>' +
  '<input type="date" id="pq-date" aria-label="Preferred moving date">' +
  '</div>' +
  '<button type="submit" class="pq-submit">Get Quote on WhatsApp →</button>' +
  '<p class="pq-privacy">No spam, no sharing. Your details go only to Poonia Movers.</p>' +
  '</form></div></div>' +
  '<button id="pm-quote-fab" aria-label="Get free quote">📝 Free Quote</button>';

  function openModal(){
    var m = document.getElementById('pm-quote-modal');
    m.classList.add('open'); m.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
  }
  function closeModal(){
    var m = document.getElementById('pm-quote-modal');
    m.classList.remove('open'); m.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
  }

  document.addEventListener('DOMContentLoaded', function(){
    if(document.getElementById('pm-quote-modal')) return;
    document.body.insertAdjacentHTML('beforeend', MODAL_HTML);
    document.getElementById('pm-quote-fab').addEventListener('click', openModal);
    document.querySelectorAll('[data-pq-close]').forEach(function(el){
      el.addEventListener('click', closeModal);
    });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeModal(); });
    // any [data-open-quote] trigger
    document.querySelectorAll('[data-open-quote]').forEach(function(el){
      el.addEventListener('click', function(ev){ ev.preventDefault(); openModal(); });
    });
    document.getElementById('pq-form').addEventListener('submit', function(e){
      e.preventDefault();
      var v = function(id){ return (document.getElementById(id).value||'').trim(); };
      var msg = 'Hi Poonia Movers! I need a FREE quote.\n'
        + 'Name: ' + v('pq-name') + '\n'
        + 'Phone: ' + v('pq-phone') + '\n'
        + 'From: ' + v('pq-from') + '\n'
        + 'To: ' + v('pq-to') + '\n'
        + 'Service: ' + v('pq-service')
        + (v('pq-date') ? '\nDate: ' + v('pq-date') : '');
      if(window.dataLayer){ window.dataLayer.push({event:'quote_requested'}); }
      window.open('https://wa.me/919829044445?text=' + encodeURIComponent(msg), '_blank', 'noopener');
      closeModal();
    });
  });
})();
