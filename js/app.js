/* ==========================================================================
   POONIA MOVERS - MASTER INTERACTIVE APPLICATION LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initHeaderScroll();
  initCalculator();
  initPackingSwitcher();
  initPricingTabs();
  initCorridorFilters();
  initFleetSelector();
  initFaqAccordion();
  initTrackingModal();
  initMobileNav();
  initWhatsAppAutoHide();
  initReviewsCarousel();
  init404Search();
});

/* 1. Header Sticky Effect */
function initHeaderScroll() {
  const header = document.querySelector('.main-header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });
}

/* 2. Interactive Instant Quote & Cost Estimator Engine */
function initCalculator() {
  const calcCards = document.querySelectorAll('.calculator-card, .calc-card');
  if (calcCards.length === 0) return;

  calcCards.forEach(card => {
    const tabBtns = card.querySelectorAll('.calc-tab-btn');
    const calcForm = card.querySelector('#hero-calc-form, .calc-form');
    const resultBox = card.querySelector('#calc-result-box, .calc-result-box');
    const priceDisplay = card.querySelector('#calc-price-display, .price-val');
    const timeDisplay = card.querySelector('#calc-time-display, .result-time');
    const moveTypeSelect = card.querySelector('#calc-move-size');
    const originInput = card.querySelector('#calc-origin');
    const destInput = card.querySelector('#calc-dest');
    const waQuoteBtn = card.querySelector('#calc-whatsapp-btn');
    const moveLabel = card.querySelector('#calc-move-size-label, label[for="calc-move-size"]');

    // Detect initial active mode from HTML
    const initialActiveBtn = card.querySelector('.calc-tab-btn.active');
    let activeMode = initialActiveBtn ? (initialActiveBtn.dataset.mode || 'household') : 'household';

    const householdOptions = [
      { value: '1bhk', text: '1 RK / 1 BHK Apartment' },
      { value: '2bhk', text: '2 BHK Apartment / Floor', selected: true },
      { value: '3bhk', text: '3 BHK Apartment / Independent House' },
      { value: 'villa', text: '4+ BHK / Luxury Villa' },
      { value: 'vehicle', text: 'Only Car / Two-Wheeler' }
    ];

    const truckOptions = [
      { value: 'partload', text: 'Part Load / Parcel Box (Up to 500 Kg)' },
      { value: 'tataace', text: 'Tata Ace / Chota Hathi (750 Kg - 1 Ton)', selected: true },
      { value: 'bolero', text: 'Bolero Pickup (1.5 - 2 Tons)' },
      { value: '14ft', text: '14ft Eicher Container (3.5 - 4 Tons)' },
      { value: '19ft', text: '19ft Heavy Truck (7 - 8 Tons)' },
      { value: '32ft', text: '32ft SXL / MXL Multi-Axle (15+ Tons)' }
    ];

    function renderSelectOptions(mode) {
      if (!moveTypeSelect) return;
      const opts = mode === 'household' ? householdOptions : truckOptions;
      moveTypeSelect.innerHTML = opts.map(opt => 
        `<option value="${opt.value}" ${opt.selected ? 'selected' : ''}>${opt.text}</option>`
      ).join('');
      
      if (moveLabel) {
        moveLabel.textContent = mode === 'household' ? 'Move Size / Requirement' : 'Truck Type / Cargo Volume';
      }
    }

    tabBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeMode = btn.dataset.mode || 'household';
        renderSelectOptions(activeMode);
        calculatePrice();
      });
    });

    if (moveTypeSelect) {
      moveTypeSelect.addEventListener('change', () => calculatePrice());
    }
    if (originInput) {
      originInput.addEventListener('input', () => calculatePrice());
    }
    if (destInput) {
      destInput.addEventListener('input', () => calculatePrice());
    }

    if (calcForm) {
      calcForm.addEventListener('submit', (e) => {
        e.preventDefault();
        calculatePrice(true);
      });
    }

    function calculatePrice(forceShowResult = false) {
      if (!originInput || !destInput || !moveTypeSelect) return;

      const origin = originInput.value.trim().toLowerCase() || 'jaipur';
      const dest = destInput.value.trim().toLowerCase() || 'delhi';
      const moveSize = moveTypeSelect.value || (activeMode === 'household' ? '2bhk' : 'tataace');

      let minPrice = 3500;
      let maxPrice = 6500;
      let transitTime = "Same Day (4 - 6 Hours)";

      const isLocal = origin.includes('jaipur') && (dest.includes('jaipur') || dest === '' || dest.includes('local') || dest.includes('mansarovar') || dest.includes('vaishali') || dest.includes('jagatpura') || dest.includes('vki') || dest.includes('sitapura'));

      if (isLocal) {
        transitTime = "Same Day (3 - 5 Hours)";
        if (activeMode === 'household') {
          switch (moveSize) {
            case '1bhk': minPrice = 3200; maxPrice = 5200; break;
            case '2bhk': minPrice = 5800; maxPrice = 8800; break;
            case '3bhk': minPrice = 9800; maxPrice = 14500; break;
            case 'villa': minPrice = 15000; maxPrice = 22000; break;
            case 'vehicle': minPrice = 1200; maxPrice = 2500; break;
            default: minPrice = 5500; maxPrice = 8500;
          }
        } else {
          switch (moveSize) {
            case 'partload': minPrice = 1200; maxPrice = 2500; break;
            case 'tataace': minPrice = 1800; maxPrice = 3200; break;
            case 'bolero': minPrice = 2800; maxPrice = 4500; break;
            case '14ft': minPrice = 5500; maxPrice = 8500; break;
            case '19ft': minPrice = 9500; maxPrice = 14000; break;
            case '32ft': minPrice = 16000; maxPrice = 24000; break;
            default: minPrice = 2500; maxPrice = 4500;
          }
        }
      } else {
        // Intercity Corridor Calculations
        if (dest.includes('delhi') || dest.includes('gurgaon') || dest.includes('noida') || dest.includes('faridabad')) {
          transitTime = "12 - 18 Hours (Next Day)";
          if (activeMode === 'household') {
            minPrice = moveSize === '1bhk' ? 7500 : moveSize === '2bhk' ? 12500 : moveSize === '3bhk' ? 18500 : moveSize === 'villa' ? 28000 : 4500;
            maxPrice = Math.round(minPrice * 1.28);
          } else {
            minPrice = moveSize === 'partload' ? 2500 : moveSize === 'tataace' ? 6500 : moveSize === 'bolero' ? 8500 : moveSize === '14ft' ? 14000 : moveSize === '19ft' ? 22000 : 34000;
            maxPrice = Math.round(minPrice * 1.25);
          }
        } else if (dest.includes('mumbai') || dest.includes('pune') || dest.includes('ahmedabad') || dest.includes('surat')) {
          transitTime = "2 - 3 Days";
          if (activeMode === 'household') {
            minPrice = moveSize === '1bhk' ? 14000 : moveSize === '2bhk' ? 22000 : moveSize === '3bhk' ? 32000 : moveSize === 'villa' ? 45000 : 7500;
            maxPrice = Math.round(minPrice * 1.25);
          } else {
            minPrice = moveSize === 'partload' ? 4500 : moveSize === 'tataace' ? 14000 : moveSize === 'bolero' ? 18000 : moveSize === '14ft' ? 28000 : moveSize === '19ft' ? 42000 : 65000;
            maxPrice = Math.round(minPrice * 1.22);
          }
        } else if (dest.includes('bangalore') || dest.includes('bengaluru') || dest.includes('hyderabad') || dest.includes('chennai')) {
          transitTime = "3 - 4 Days";
          if (activeMode === 'household') {
            minPrice = moveSize === '1bhk' ? 22000 : moveSize === '2bhk' ? 34000 : moveSize === '3bhk' ? 48000 : moveSize === 'villa' ? 68000 : 9500;
            maxPrice = Math.round(minPrice * 1.22);
          } else {
            minPrice = moveSize === 'partload' ? 6000 : moveSize === 'tataace' ? 22000 : moveSize === 'bolero' ? 28000 : moveSize === '14ft' ? 42000 : moveSize === '19ft' ? 62000 : 95000;
            maxPrice = Math.round(minPrice * 1.2);
          }
        } else if (dest.includes('kolkata') || dest.includes('patna') || dest.includes('ranchi')) {
          transitTime = "3 - 4 Days";
          if (activeMode === 'household') {
            minPrice = moveSize === '1bhk' ? 19000 : moveSize === '2bhk' ? 29000 : moveSize === '3bhk' ? 42000 : moveSize === 'villa' ? 58000 : 8500;
            maxPrice = Math.round(minPrice * 1.25);
          } else {
            minPrice = moveSize === 'partload' ? 5000 : moveSize === 'tataace' ? 19000 : moveSize === 'bolero' ? 24000 : moveSize === '14ft' ? 38000 : moveSize === '19ft' ? 56000 : 88000;
            maxPrice = Math.round(minPrice * 1.22);
          }
        } else {
          transitTime = "2 - 4 Days";
          minPrice = 8500;
          maxPrice = 16500;
        }
      }

      if (priceDisplay) {
        priceDisplay.textContent = `₹${minPrice.toLocaleString('en-IN')} - ₹${maxPrice.toLocaleString('en-IN')}`;
      }
      if (timeDisplay) {
        timeDisplay.textContent = transitTime;
      }
      if (resultBox && forceShowResult) {
        resultBox.style.display = 'block';
        resultBox.classList.add('active');
      }

      // Safe WhatsApp URL generation
      if (waQuoteBtn) {
        const selectedText = moveTypeSelect.options && moveTypeSelect.selectedIndex >= 0 && moveTypeSelect.options[moveTypeSelect.selectedIndex] 
          ? moveTypeSelect.options[moveTypeSelect.selectedIndex].text 
          : 'Shifting';
        const fromCity = originInput.value || 'Jaipur';
        const toCity = destInput.value || 'Destination';
        const waMsg = `Hi Poonia Movers, I need a ${activeMode === 'household' ? 'Household Shifting' : 'Commercial Truck'} quote from ${fromCity} to ${toCity} (${selectedText}). Estimated Rate shown: ₹${minPrice.toLocaleString('en-IN')} - ₹${maxPrice.toLocaleString('en-IN')}. Please confirm availability!`;
        waQuoteBtn.href = `https://wa.me/918529206001?text=${encodeURIComponent(waMsg)}`;
      }
    }

    // Initial render for each card
    renderSelectOptions(activeMode);
  });
}

/* 3. 5-Layer Packing Interactive Switcher */
function initPackingSwitcher() {
  const layerItems = document.querySelectorAll('.packing-layer-item');
  const visualTitle = document.getElementById('packing-visual-title');
  const visualDesc = document.getElementById('packing-visual-desc');

  const layerData = [
    {
      title: "Layer 1: High-Density Air Bubble Wrap",
      desc: "Thick shock-absorbing air pocket wrap applied directly to furniture finishes, electronics, and glassware to eliminate road vibration friction and scratches."
    },
    {
      title: "Layer 2: Hard Corner & Edge Angle Protectors",
      desc: "Rigid corrugated and L-shaped plastic edge protectors secured on all table edges, wardrobes, and delicate framing to avoid structural chipping."
    },
    {
      title: "Layer 3: 5-Ply Virgin Corrugated Sheets",
      desc: "Industrial-strength impact-resistant cardboard wrap that shields bulky appliances, refrigerators, and heavy wood against transit impacts."
    },
    {
      title: "Layer 4: Waterproof Stretch Film Sealing",
      desc: "Continuous high-grade plastic stretch membrane wrapping that creates an impenetrable barrier against monsoon rain, road dust, and moisture."
    },
    {
      title: "Layer 5: Sealed Container & Custom Wooden Crates",
      desc: "Custom-built plywood wooden crates specifically tailored for 65-85 inch OLED TVs, marble mandirs, glass dining tops, and luxury paintings."
    }
  ];

  layerItems.forEach((item, index) => {
    item.addEventListener('click', () => {
      layerItems.forEach(l => l.classList.remove('active'));
      item.classList.add('active');
      if (visualTitle && layerData[index]) visualTitle.textContent = layerData[index].title;
      if (visualDesc && layerData[index]) visualDesc.textContent = layerData[index].desc;
    });
  });
}

/* 4. Pricing Matrix Tab Switcher */
function initPricingTabs() {
  const tabBtns = document.querySelectorAll('.price-pill-btn');
  const tables = document.querySelectorAll('.price-table-block');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.table;

      tables.forEach(table => {
        if (table.id === target) {
          table.style.display = 'block';
        } else {
          table.style.display = 'none';
        }
      });
    });
  });
}

/* 5. 28-Corridor Filter System */
function initCorridorFilters() {
  const filterBtns = document.querySelectorAll('.corridor-tab-btn');
  const corridorCards = document.querySelectorAll('.corridor-card');
  const corridorRows = document.querySelectorAll('.corridor-row');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const category = btn.dataset.filter || btn.dataset.region;

      corridorCards.forEach(card => {
        if (category === 'all' || card.dataset.region === category || card.dataset.service === category) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });

      corridorRows.forEach(row => {
        if (category === 'all' || row.dataset.region === category) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  });
}

/* 6. Fleet Matrix Selector */
function initFleetSelector() {
  const fleetCards = document.querySelectorAll('.fleet-card');
  fleetCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      fleetCards.forEach(c => c.style.borderColor = 'var(--border-light)');
      card.style.borderColor = 'var(--primary-blue)';
    });
  });
}

/* 7. Universal High-Traffic FAQ Accordion Engine */
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');
  if (faqItems.length === 0) return;

  faqItems.forEach(item => {
    const btn = item.querySelector('.faq-question-btn, .faq-question, button, summary');
    if (!btn) return;

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const parent = item.closest('.faq-container, .faq-accordion, .faq-list, section') || item.parentElement;
      const siblingItems = parent ? parent.querySelectorAll('.faq-item') : [item];
      const isOpen = item.classList.contains('active');

      siblingItems.forEach(i => {
        i.classList.remove('active');
        const b = i.querySelector('.faq-question-btn, .faq-question, button, summary');
        if (b) b.setAttribute('aria-expanded', 'false');
      });

      if (!isOpen) {
        item.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });
}

/* 8. Live Consignment Tracking (Direct WhatsApp GPS Redirection) */
function initTrackingModal() {
  const openBtns = document.querySelectorAll('.trigger-track-modal');
  const modal = document.getElementById('tracking-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const trackForm = document.getElementById('tracking-form');
  const trackResult = document.getElementById('tracking-result-box');

  openBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (modal) modal.classList.add('active');
    });
  });

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }

  if (trackForm) {
    trackForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = trackForm.querySelector('input[type="text"], input[name="text"], input[name="lr_number"], input');
      const queryVal = input ? input.value.trim() : '';

      if (trackResult) {
        trackResult.innerHTML = `
          <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid var(--emerald-green); padding: 14px; border-radius: var(--radius-md); margin-top: 15px; text-align: center;">
            <p style="font-weight: 700; color: var(--emerald-dark); margin-bottom: 4px;">📲 Connecting to WhatsApp Live GPS Desk...</p>
            <p style="font-size: 0.85rem; color: var(--text-main);">Opening WhatsApp for LR / Mobile: <strong>${queryVal || 'Consignment'}</strong></p>
          </div>
        `;
      }

      const waMsg = `Hi Poonia Movers, please share the live GPS tracking status and driver contact for Consignment / LR / Mobile Number: ${queryVal || 'General Inquiry'}.`;
      const waUrl = `https://wa.me/918529206001?text=${encodeURIComponent(waMsg)}`;

      setTimeout(() => {
        window.location.href = waUrl;
      }, 350);
    });
  }
}

/* 9. Mobile Nav Drawer Toggle & Global Accordion Handlers */
function initMobileNav() {
  const toggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');
  if (!toggle || !navMenu) return;

  function closeMenu() {
    navMenu.classList.remove('active');
    toggle.classList.remove('active');
    document.querySelectorAll('.nav-item.mobile-open').forEach(item => item.classList.remove('mobile-open'));
  }

  function toggleMenu() {
    const isActive = navMenu.classList.toggle('active');
    toggle.classList.toggle('active', isActive);
    if (!isActive) {
      document.querySelectorAll('.nav-item.mobile-open').forEach(item => item.classList.remove('mobile-open'));
    }
  }

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleMenu();
  });

  // Handle dropdown accordions on mobile
  const navItems = navMenu.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    const link = item.querySelector('.nav-link');
    const dropdown = item.querySelector('.dropdown-menu');

    if (link && dropdown) {
      link.addEventListener('click', (e) => {
        if (window.innerWidth <= 992) {
          e.preventDefault();
          e.stopPropagation();
          const isOpen = item.classList.contains('mobile-open');
          
          // Close other submenus for clean accordion behavior
          navItems.forEach(other => {
            if (other !== item) other.classList.remove('mobile-open');
          });

          if (isOpen) {
            item.classList.remove('mobile-open');
          } else {
            item.classList.add('mobile-open');
          }
        }
      });
    }
  });

  // Auto-close drawer when clicking on any destination link
  navMenu.querySelectorAll('a').forEach(link => {
    const hasDropdown = link.parentElement.querySelector('.dropdown-menu');
    // If it's a direct destination or a submenu child item
    if (!hasDropdown || link.classList.contains('dropdown-item')) {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 992) {
          closeMenu();
        }
      });
    }
  });

  // Auto-close when clicking outside
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 992 && navMenu.classList.contains('active')) {
      if (!navMenu.contains(e.target) && !toggle.contains(e.target)) {
        closeMenu();
      }
    }
  });

  // Reset open submenus on window resize to desktop
  window.addEventListener('resize', () => {
    if (window.innerWidth > 992) {
      closeMenu();
    }
  });
}

/* 10. Floating WhatsApp Auto-Hide After 1.5s Idle */
function initWhatsAppAutoHide() {
  const waBtn = document.querySelector('.floating-whatsapp-btn');
  if (!waBtn) return;

  let idleTimer = null;

  function hideButton() {
    waBtn.classList.add('idle-hidden');
  }

  function showButton() {
    waBtn.classList.remove('idle-hidden');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(hideButton, 1500);
  }

  // Initial auto-hide after 1.5s on page load
  idleTimer = setTimeout(hideButton, 1500);

  // Smoothly pop back when scrolling, moving cursor, or tapping screen
  window.addEventListener('scroll', showButton, { passive: true });
  window.addEventListener('mousemove', showButton, { passive: true });
  window.addEventListener('touchstart', showButton, { passive: true });

  waBtn.addEventListener('mouseenter', () => {
    clearTimeout(idleTimer);
    waBtn.classList.remove('idle-hidden');
  });

  waBtn.addEventListener('mouseleave', () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(hideButton, 1500);
  });
}

/* 11. Interactive Snappy Reviews Auto-Slider (1.5s - 1.8s Snappy Pop-In Animation) */
function initReviewsCarousel() {
  const container = document.getElementById('reviews-slider-container');
  const track = document.getElementById('reviews-track');
  const prevBtn = document.getElementById('rev-prev-btn');
  const nextBtn = document.getElementById('rev-next-btn');
  const dotsWrap = document.getElementById('reviews-dots-wrap');

  if (!track || !container) return;

  const cards = Array.from(track.querySelectorAll('.review-card'));
  if (cards.length === 0) return;

  let currentIndex = 0;
  let autoSlideTimer = null;
  let isHovered = false;
  const slideIntervalTime = 4200; // 4.2 seconds comfortable reading cadence

  function getVisibleCount() {
    if (window.innerWidth > 1024) return 3;
    if (window.innerWidth > 768) return 2;
    return 1;
  }

  function getMaxIndex() {
    return Math.max(0, cards.length - getVisibleCount());
  }

  function renderDots() {
    if (!dotsWrap) return;
    dotsWrap.innerHTML = '';
    const max = getMaxIndex();
    const totalDots = max + 1;

    for (let i = 0; i < totalDots; i++) {
      const dot = document.createElement('button');
      dot.className = `rev-dot ${i === currentIndex ? 'active' : ''}`;
      dot.setAttribute('aria-label', `Go to review slide ${i + 1}`);
      dot.addEventListener('click', () => {
        goToSlide(i);
        restartAutoSlide();
      });
      dotsWrap.appendChild(dot);
    }
  }

  function updateSlidePosition() {
    const visibleCount = getVisibleCount();
    const max = getMaxIndex();
    if (currentIndex > max) currentIndex = 0;
    if (currentIndex < 0) currentIndex = max;

    const firstCard = cards[0];
    const cardWidth = firstCard.offsetWidth;
    const gap = 24; // 24px gap in css
    const offset = currentIndex * (cardWidth + gap);

    track.style.transform = `translateX(-${offset}px)`;

    // Snappy Pop-In Animation ("gayab hoke naya pop-in ho jaye")
    cards.forEach((card, idx) => {
      card.classList.remove('rev-animating');
      if (idx >= currentIndex && idx < currentIndex + visibleCount) {
        // Trigger reflow to restart css keyframe animation
        void card.offsetWidth;
        card.classList.add('rev-animating');
      }
    });

    // Update dots indicator
    if (dotsWrap) {
      const dots = dotsWrap.querySelectorAll('.rev-dot');
      dots.forEach((dot, idx) => {
        dot.classList.toggle('active', idx === currentIndex);
      });
    }
  }

  function nextSlide() {
    const max = getMaxIndex();
    if (currentIndex >= max) {
      currentIndex = 0;
    } else {
      currentIndex++;
    }
    updateSlidePosition();
  }

  function prevSlide() {
    const max = getMaxIndex();
    if (currentIndex <= 0) {
      currentIndex = max;
    } else {
      currentIndex--;
    }
    updateSlidePosition();
  }

  function goToSlide(index) {
    currentIndex = index;
    updateSlidePosition();
  }

  function startAutoSlide() {
    stopAutoSlide();
    autoSlideTimer = setInterval(() => {
      if (!isHovered) {
        nextSlide();
      }
    }, slideIntervalTime);
  }

  function stopAutoSlide() {
    if (autoSlideTimer) {
      clearInterval(autoSlideTimer);
      autoSlideTimer = null;
    }
  }

  function restartAutoSlide() {
    stopAutoSlide();
    startAutoSlide();
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      nextSlide();
      restartAutoSlide();
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      prevSlide();
      restartAutoSlide();
    });
  }

  container.addEventListener('mouseenter', () => {
    isHovered = true;
  });

  container.addEventListener('mouseleave', () => {
    isHovered = false;
  });

  // Touch Swipe Support for mobile devices
  let touchStartX = 0;
  let touchEndX = 0;

  container.addEventListener('touchstart', (e) => {
    isHovered = true;
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  container.addEventListener('touchend', (e) => {
    isHovered = false;
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
    restartAutoSlide();
  }, { passive: true });

  function handleSwipe() {
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > 40) {
      if (diff > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
    }
  }

  window.addEventListener('resize', () => {
    renderDots();
    updateSlidePosition();
  });

  // Initial Boot
  renderDots();
  updateSlidePosition();
  startAutoSlide();
}

/* ==========================================================================
   12. 404 Interactive Route Search & Fuzzy Destination Finder
   ========================================================================== */
function init404Search() {
  const searchInput = document.getElementById('route-search-input');
  const searchBtn = document.getElementById('route-search-btn');
  const resultsBox = document.getElementById('route-search-results');
  if (!searchInput || !resultsBox) return;

  const siteRoutes = [
    { title: 'Jaipur to Delhi NCR Transport & Packers', url: 'jaipur-to-delhi-transport-packers.html', tags: 'delhi ncr gurgaon noida faridabad transport shifting' },
    { title: 'Jaipur to Mumbai Transport & Packers', url: 'jaipur-to-mumbai-transport-packers.html', tags: 'mumbai maharashtra thane navi mumbai shifting express' },
    { title: 'Jaipur to Bangalore Express Transport', url: 'jaipur-to-bangalore-transport-packers.html', tags: 'bangalore bengaluru karnataka tech city shifting' },
    { title: 'Jaipur to Noida Transport & Packers', url: 'jaipur-to-noida-transport-packers.html', tags: 'noida greater noida up delhi ncr transport' },
    { title: 'Jaipur to Ahmedabad Transport & Packers', url: 'jaipur-to-ahmedabad-transport-packers.html', tags: 'ahmedabad gujarat surat vadodara transport' },
    { title: 'Jaipur to Pune Express Packers Movers', url: 'jaipur-to-pune-transport-packers.html', tags: 'pune hinjewadi maharashtra transport' },
    { title: 'Jaipur to Hyderabad Express Transport', url: 'jaipur-to-hyderabad-transport-packers.html', tags: 'hyderabad telangana secunderabad transport' },
    { title: 'Jaipur to Kolkata Express Transport', url: 'jaipur-to-kolkata-transport-packers.html', tags: 'kolkata west bengal howrah transport' },
    { title: 'Household Shifting Services Jaipur (1-4 BHK)', url: 'house-shifting-jaipur.html', tags: 'house home household shifting luggage 1bhk 2bhk 3bhk flat relocation' },
    { title: 'Corporate & Office Relocation Jaipur', url: 'office-relocation-jaipur.html', tags: 'office corporate commercial workplace relocation desk shifting' },
    { title: 'Car & Bike Transportation Jaipur', url: 'car-bike-transportation-jaipur.html', tags: 'car bike two wheeler vehicle auto transport carrier hydraulic' },
    { title: 'Part Load & Parcel Transport Jaipur', url: 'part-load-transport-jaipur.html', tags: 'part load parcel box luggage small move courier shared truck' },
    { title: 'Warehouse & Secure Storage Jaipur', url: 'warehouse-storage-jaipur.html', tags: 'warehouse storage luggage box safe storage industrial godown' },
    { title: 'Commercial Truck Rental & Fleet Jaipur', url: 'truck-rental-jaipur.html', tags: 'truck rental tata ace chota hathi bolero 14ft 19ft 32ft commercial hire' },
    { title: 'Jaipur Transport Hub & Fleet Operations', url: 'jaipur-transport-services.html', tags: 'jaipur transport hub vki harmada transport nagar goods booking' },
    { title: 'Packers and Movers Mansarovar Jaipur', url: 'packers-movers-mansarovar-jaipur.html', tags: 'mansarovar varun path patel marg shipra path shifting' },
    { title: 'Packers and Movers Vaishali Nagar Jaipur', url: 'packers-movers-vaishali-nagar-jaipur.html', tags: 'vaishali nagar amrapali circle chitrakoot gandhi path' },
    { title: 'Packers and Movers Jagatpura Jaipur', url: 'packers-movers-jagatpura-jaipur.html', tags: 'jagatpura mahal road skit akshaya patra shifting' },
    { title: 'Packers and Movers Malviya Nagar Jaipur', url: 'packers-movers-malviya-nagar-jaipur.html', tags: 'malviya nagar gaurav tower wtp d-block shifting' },
    { title: 'Packers and Movers Ajmer Road Jaipur', url: 'packers-movers-ajmer-road-jaipur.html', tags: 'ajmer road mahindra sez dcm bhankrota shifting' },
    { title: 'Packers and Movers C-Scheme Jaipur', url: 'packers-movers-c-scheme-jaipur.html', tags: 'c-scheme ashok nagar bhagwan das road civil lines' },
    { title: 'Packers and Movers Raja Park Jaipur', url: 'packers-movers-raja-park-jaipur.html', tags: 'raja park adarsh nagar tilak nagar jawahar nagar' },
    { title: 'Packers and Movers Vidhyadhar Nagar Jaipur', url: 'packers-movers-vidhyadhar-nagar-jaipur.html', tags: 'vidhyadhar nagar sector 1 2 3 4 5 6 7 8 9' },
    { title: 'About Poonia Movers & Asset Fleet', url: 'about-us.html', tags: 'about company history owners fleet credentials credentials' },
    { title: 'Contact Poonia Movers 24/7 Helpline', url: 'contact-us.html', tags: 'contact address phone email helpline office booking' }
  ];

  function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    if (query.length < 2) {
      resultsBox.style.display = 'none';
      resultsBox.innerHTML = '';
      return;
    }

    const matches = siteRoutes.filter(route => 
      route.title.toLowerCase().includes(query) || 
      route.tags.toLowerCase().includes(query) ||
      route.url.toLowerCase().includes(query)
    );

    if (matches.length > 0) {
      resultsBox.innerHTML = matches.slice(0, 6).map(m => `
        <a href="${m.url}" class="search-404-item">
          <span>${m.title}</span>
          <span style="font-size:0.75rem; color:var(--primary-blue); font-weight:700;">Open Page ➔</span>
        </a>
      `).join('');
      resultsBox.style.display = 'block';
    } else {
      resultsBox.innerHTML = `
        <div style="padding:16px 20px; font-size:0.88rem; color:#64748b; text-align:center;">
          No direct page matched "<strong>${query}</strong>". <br/>
          <a href="index.html" style="color:var(--primary-blue); font-weight:700; margin-top:6px; display:inline-block;">Return to Homepage</a> or call <a href="tel:+918529206001" style="color:var(--primary-blue); font-weight:700;">+91 85292 06001</a>
        </div>
      `;
      resultsBox.style.display = 'block';
    }
  }

  searchInput.addEventListener('input', performSearch);
  
  if (searchBtn) {
    searchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const firstResult = resultsBox.querySelector('.search-404-item');
      if (firstResult) {
        window.location.href = firstResult.getAttribute('href');
      } else {
        performSearch();
      }
    });
  }

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const firstResult = resultsBox.querySelector('.search-404-item');
      if (firstResult) {
        window.location.href = firstResult.getAttribute('href');
      }
    }
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !resultsBox.contains(e.target)) {
      resultsBox.style.display = 'none';
    }
  });
}



