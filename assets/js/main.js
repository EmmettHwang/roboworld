/* 로보월드캠퍼스 — 사이트 인터랙션
   외부 라이브러리 없음. 파일을 그대로 열어도(file://) 동작합니다. */
(function () {
  'use strict';

  /* ---------- 1. 스크롤 시 헤더 배경 ---------- */
  var hdr = document.getElementById('hdr');
  function onScroll() {
    hdr.classList.toggle('solid', window.scrollY > 40);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- 2. 모바일 메뉴 ---------- */
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('nav');

  function closeNav() {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', '메뉴 열기');
  }

  toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
  });

  nav.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') closeNav();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeNav();
  });

  /* ---------- 3. 스크롤 리빌 ---------- */
  var targets = document.querySelectorAll('.rv');

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        io.unobserve(en.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    // 같은 그리드 안의 카드들은 순서대로 살짝씩 늦게
    targets.forEach(function (el) {
      var siblings = el.parentElement ? el.parentElement.children : [];
      var idx = Array.prototype.indexOf.call(siblings, el);
      if (idx > 0 && idx < 8) el.style.transitionDelay = (idx * 90) + 'ms';
      io.observe(el);
    });
  } else {
    targets.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- 4. 프로그램 탭 ---------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));

  function selectTab(tab) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      if (!panel) return;
      panel.hidden = !on;
      if (on) {
        // 새로 열린 패널의 카드도 리빌 처리
        panel.querySelectorAll('.rv').forEach(function (el) { el.classList.add('in'); });
      }
    });
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () { selectTab(tab); });
    tab.addEventListener('keydown', function (e) {
      var dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!dir) return;
      e.preventDefault();
      var next = tabs[(i + dir + tabs.length) % tabs.length];
      next.focus();
      selectTab(next);
    });
  });

  /* ---------- 5. 영상 재생 시 다른 영상 정지 ---------- */
  var videos = Array.prototype.slice.call(document.querySelectorAll('video'));
  videos.forEach(function (v) {
    v.addEventListener('play', function () {
      videos.forEach(function (o) { if (o !== v) o.pause(); });
    });
  });
})();
