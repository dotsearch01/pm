/* Poonia Movers — Fare Calculator (real rate-card data, 2026-10-05) */
(function(){
  "use strict";
  // Local Jaipur shifting ranges [min, max, vehicle, crew] — from site rate card
  var LOCAL = {
    "1rk":  {label:"1 RK",      min:3200,  max:5500,  vehicle:"Tata Ace / Bolero Pickup", crew:"2 movers"},
    "1bhk": {label:"1 BHK",     min:3200,  max:5500,  vehicle:"Tata Ace / Bolero Pickup", crew:"2 movers"},
    "2bhk": {label:"2 BHK",     min:5800,  max:9500,  vehicle:"14ft closed container",    crew:"3\u20134 movers"},
    "3bhk": {label:"3 BHK",     min:9800,  max:15500, vehicle:"17ft / 19ft container",    crew:"4\u20135 movers"},
    "4bhk": {label:"4+ BHK / Villa", min:15000, max:24000, vehicle:"22ft multi-axle truck", crew:"6 movers"},
    "office":{label:"Office",   min:15000, max:35000, vehicle:"17ft / 19ft container",   crew:"5\u20136 movers"}
  };
  // Intercity FTL "starts at" per destination — from corridor rate data
  var ROUTES = {
    "delhi":      {label:"Delhi NCR",   base:6500},
    "noida":      {label:"Noida / Gr. Noida", base:6500},
    "chandigarh": {label:"Chandigarh",  base:13000},
    "lucknow":    {label:"Lucknow",     base:13500},
    "ahmedabad":  {label:"Ahmedabad",   base:14000},
    "mumbai":     {label:"Mumbai",      base:15000},
    "pune":       {label:"Pune",        base:15000},
    "hyderabad":  {label:"Hyderabad",   base:18000},
    "bangalore":  {label:"Bengaluru",   base:22000},
    "kolkata":    {label:"Kolkata",     base:32000},
    "udaipur":    {label:"Udaipur",     base:9500},
    "jodhpur":    {label:"Jodhpur",     base:8500}
  };
  // size multiplier for intercity household moves (packing + handling)
  var SIZE_F = {"1rk":1.3,"1bhk":1.3,"2bhk":1.6,"3bhk":2.0,"4bhk":2.6,"office":2.4};

  function fmt(n){ return "\u20B9" + Math.round(n/100)*100 .toLocaleString("en-IN"); }
  function fmtN(n){ return "\u20B9" + (Math.round(n/100)*100).toLocaleString("en-IN"); }

  function calc(){
    var typeEl = document.querySelector('input[name="fc-type"]:checked');
    var sizeEl = document.getElementById("fc-size");
    var destEl = document.getElementById("fc-dest");
    var out = document.getElementById("fc-result");
    if(!typeEl || !sizeEl || !out) return;
    var size = sizeEl.value, L = LOCAL[size];
    var html = "";
    if(typeEl.value === "local"){
      html = resultHTML(L.label + " shifting within Jaipur",
        fmtN(L.min), fmtN(L.max), L.vehicle, L.crew,
        "Packing + loading + transport + unloading included");
      setWA(size, "local", null, L);
    } else {
      var d = destEl ? destEl.value : "delhi";
      var R = ROUTES[d] || ROUTES.delhi;
      var f = SIZE_F[size] || 1.6;
      var lo = R.base * f * 0.9, hi = R.base * f * 1.35;
      html = resultHTML(L.label + " shifting: Jaipur \u2192 " + R.label,
        fmtN(lo), fmtN(hi), "Shared / dedicated truck", "Full crew",
        "Rough estimate \u2014 final quote after free video survey");
      setWA(size, "intercity", R, {min:Math.round(lo/100)*100, max:Math.round(hi/100)*100});
    }
    out.innerHTML = html;
    out.style.display = "block";
    if(window.dataLayer){ window.dataLayer.push({event:"fare_calculated", move_type:typeEl.value, home_size:size}); }
  }

  function resultHTML(title, lo, hi, vehicle, crew, note){
    return '<div class="fc-card">'
      + '<p class="fc-title">' + title + '</p>'
      + '<p class="fc-price">' + lo + ' \u2013 ' + hi + '</p>'
      + '<p class="fc-meta">\uD83D\uDE9A ' + vehicle + ' &nbsp;\u00B7&nbsp; \uD83D\uDC65 ' + crew + '</p>'
      + '<p class="fc-note">' + note + '</p>'
      + '<div class="fc-cta"><a class="btn-call" id="fc-wa" href="#" target="_blank" rel="noopener">\uD83D\uDCAC Confirm exact quote on WhatsApp</a></div>'
      + '</div>';
  }

  function setWA(size, type, route, L){
    var btn = document.getElementById("fc-wa");
    if(!btn) return;
    var msg;
    if(type === "local"){
      msg = "Hi Poonia Movers! Calculator estimate for " + LOCAL[size].label +
        " shifting within Jaipur: " + fmtN(L.min) + "\u2013" + fmtN(L.max) +
        ". Please confirm my exact quote.";
    } else {
      msg = "Hi Poonia Movers! Calculator estimate for " + LOCAL[size].label +
        " shifting Jaipur to " + route.label + ": " + fmtN(L.min) + "\u2013" + fmtN(L.max) +
        ". Please confirm my exact quote.";
    }
    btn.href = "https://wa.me/919829044445?text=" + encodeURIComponent(msg);
  }

  function toggleDest(){
    var typeEl = document.querySelector('input[name="fc-type"]:checked');
    var wrap = document.getElementById("fc-dest-wrap");
    if(wrap) wrap.style.display = (typeEl && typeEl.value === "intercity") ? "block" : "none";
  }

  document.addEventListener("DOMContentLoaded", function(){
    if(!document.getElementById("pm-fare-calculator")) return;
    var dest = document.getElementById("fc-dest");
    if(dest){
      Object.keys(ROUTES).forEach(function(k){
        var o = document.createElement("option");
        o.value = k; o.textContent = ROUTES[k].label + " (from " + fmtN(ROUTES[k].base) + ")";
        dest.appendChild(o);
      });
    }
    document.querySelectorAll('input[name="fc-type"]').forEach(function(r){
      r.addEventListener("change", function(){ toggleDest(); calc(); });
    });
    ["fc-size","fc-dest"].forEach(function(id){
      var el = document.getElementById(id);
      if(el) el.addEventListener("change", calc);
    });
    var btn = document.getElementById("fc-btn");
    if(btn) btn.addEventListener("click", calc);
    toggleDest(); calc();
  });
})();
