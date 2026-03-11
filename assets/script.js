/* Command the Future — The NeamCode Handbook Scripts */
(function() {
  'use strict';

  // ── Theme ──
  function getTheme() {
    return localStorage.getItem('neamcode-theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  function setTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('neamcode-theme', t);
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = t === 'dark' ? '\u2600\ufe0f' : '\ud83c\udf19';
  }
  setTheme(getTheme());
  document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = getTheme() === 'dark' ? '\u2600\ufe0f' : '\ud83c\udf19';
      btn.addEventListener('click', function() {
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
      });
    }
  });

  // ── Sidebar ──
  document.addEventListener('DOMContentLoaded', function() {
    var hamburger = document.getElementById('hamburger');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebar-overlay');

    if (hamburger && sidebar) {
      hamburger.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        if (overlay) overlay.classList.toggle('open');
      });
      if (overlay) {
        overlay.addEventListener('click', function() {
          sidebar.classList.remove('open');
          overlay.classList.remove('open');
        });
      }
    }

    // Collapsible parts
    document.querySelectorAll('.sidebar-part-title').forEach(function(title) {
      title.addEventListener('click', function() {
        this.classList.toggle('open');
        var chapters = this.nextElementSibling;
        if (chapters) chapters.classList.toggle('open');
      });
    });

    // Auto-open the part containing the active link
    var activeLink = document.querySelector('.sidebar-link.active');
    if (activeLink) {
      var part = activeLink.closest('.sidebar-part');
      if (part) {
        var title = part.querySelector('.sidebar-part-title');
        var chapters = part.querySelector('.sidebar-chapters');
        if (title) title.classList.add('open');
        if (chapters) chapters.classList.add('open');
      }
      setTimeout(function() {
        activeLink.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }, 300);
    }
  });

  // ── Progress Bar ──
  document.addEventListener('DOMContentLoaded', function() {
    var fill = document.querySelector('.progress-fill');
    if (!fill) return;
    function updateProgress() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
      fill.style.width = pct + '%';
    }
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  });

  // ── Visited Chapters ──
  function markVisited() {
    var path = window.location.pathname;
    var visited = JSON.parse(localStorage.getItem('neamcode-visited') || '{}');
    visited[path] = Date.now();
    localStorage.setItem('neamcode-visited', JSON.stringify(visited));
  }
  function isVisited(url) {
    var visited = JSON.parse(localStorage.getItem('neamcode-visited') || '{}');
    // Normalize: try both with and without leading slash
    if (visited[url]) return true;
    // Check by filename
    var parts = url.split('/');
    var fname = parts[parts.length - 1];
    for (var k in visited) {
      if (k.endsWith(fname)) return true;
    }
    return false;
  }
  document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.content')) markVisited();

    // Mark visited chapters in sidebar
    document.querySelectorAll('.sidebar-link').forEach(function(link) {
      var href = link.getAttribute('href');
      if (href && isVisited(href)) {
        var dot = document.createElement('span');
        dot.className = 'visited-dot';
        link.insertBefore(dot, link.firstChild);
      }
    });

    // Mark visited chapter cards on index page
    document.querySelectorAll('.chapter-card').forEach(function(card) {
      var href = card.getAttribute('href');
      if (href && isVisited(href)) {
        card.classList.add('visited');
      }
    });
  });

  // ── Back to Top (Rocket) ──
  document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('back-to-top');
    if (!btn) return;
    btn.innerHTML = '\uD83D\uDE80'; // rocket emoji
    window.addEventListener('scroll', function() {
      btn.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });
    btn.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // ── Code Copy Buttons ──
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.copy-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var pre = this.closest('.code-header') ?
          this.closest('.code-header').nextElementSibling :
          this.closest('pre');
        var code = pre ? pre.querySelector('code') || pre : pre;
        if (!code) return;
        var text = code.textContent;
        navigator.clipboard.writeText(text).then(function() {
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          setTimeout(function() {
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
          }, 2000);
        });
      });
    });
  });

  // ── Syntax Highlighting (Neam) ──
  var NEAM_KEYWORDS = [
    'agent', 'tool', 'knowledge', 'guardrail', 'runner', 'handoff',
    'claw', 'forge', 'session', 'channel', 'lane', 'memory',
    'fn', 'let', 'mut', 'if', 'else', 'for', 'while', 'in',
    'return', 'emit', 'try', 'catch', 'match', 'impl', 'struct',
    'trait', 'enum', 'use', 'mod', 'pub', 'self', 'true', 'false',
    'nil', 'ask', 'run', 'provider', 'model', 'system', 'temperature',
    'max_tokens', 'tools', 'guardrails', 'instructions', 'prompt',
    'import', 'from', 'as', 'type', 'break', 'continue', 'loop',
    'skill', 'reflect', 'plan', 'observe', 'act', 'evaluate',
    'config', 'deploy', 'service', 'endpoint'
  ];

  // Safe escaping for syntax highlighting — work on plain text, not innerHTML
  function esc(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // Tokenize a line into segments, highlight each, return HTML
  function tokenize(line, rules) {
    var result = [];
    var i = 0;
    while (i < line.length) {
      var best = null;
      for (var r = 0; r < rules.length; r++) {
        rules[r].re.lastIndex = i;
        var m = rules[r].re.exec(line);
        if (m && m.index === i) {
          if (!best || m[0].length > best.text.length) {
            best = {text: m[0], cls: rules[r].cls};
          }
        }
      }
      if (best) {
        result.push('<span class="' + best.cls + '">' + esc(best.text) + '</span>');
        i += best.text.length;
      } else {
        result.push(esc(line[i]));
        i++;
      }
    }
    return result.join('');
  }

  function highlightNeam(text) {
    var kwPattern = new RegExp('\\b(?:' + NEAM_KEYWORDS.join('|') + ')\\b', 'g');
    var rules = [
      {re: /\/\/.*/g, cls: 'cm'},
      {re: /"(?:[^"\\]|\\.)*"/g, cls: 'str'},
      {re: /\d+\.?\d*/g, cls: 'num'},
      {re: kwPattern, cls: 'kw'}
    ];
    return text.split('\n').map(function(line) { return tokenize(line, rules); }).join('\n');
  }

  function highlightBash(text) {
    var rules = [
      {re: /#.*/g, cls: 'cm'},
      {re: /"(?:[^"\\]|\\.)*"/g, cls: 'str'},
      {re: /'(?:[^'\\]|\\.)*'/g, cls: 'str'},
      {re: /\b(?:sudo|apt|brew|curl|wget|cd|ls|mkdir|rm|cp|mv|echo|cat|grep|pip|npm|cargo|docker|kubectl|neamc|neam)\b/g, cls: 'kw'}
    ];
    return text.split('\n').map(function(line) { return tokenize(line, rules); }).join('\n');
  }

  function highlightJSON(text) {
    var rules = [
      {re: /"(?:[^"\\]|\\.)*"\s*(?=:)/g, cls: 'kw'},
      {re: /"(?:[^"\\]|\\.)*"/g, cls: 'str'},
      {re: /\b(?:true|false|null)\b/g, cls: 'kw'},
      {re: /\d+\.?\d*/g, cls: 'num'}
    ];
    return text.split('\n').map(function(line) { return tokenize(line, rules); }).join('\n');
  }

  function highlightTOML(text) {
    var rules = [
      {re: /#.*/g, cls: 'cm'},
      {re: /\[[\w\.\-]+\]/g, cls: 'kw'},
      {re: /"(?:[^"\\]|\\.)*"/g, cls: 'str'},
      {re: /\b(?:true|false)\b/g, cls: 'kw'},
      {re: /\d+\.?\d*/g, cls: 'num'}
    ];
    return text.split('\n').map(function(line) { return tokenize(line, rules); }).join('\n');
  }

  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach(function(block) {
      var lang = '';
      block.classList.forEach(function(c) {
        if (c.startsWith('language-')) lang = c.replace('language-', '');
      });
      if (!lang) {
        var header = block.closest('pre') && block.closest('pre').previousElementSibling;
        if (header && header.classList.contains('code-header')) {
          lang = (header.querySelector('.code-lang') || {}).textContent || '';
          lang = lang.toLowerCase().trim();
        }
      }
      var fn = null;
      if (lang === 'neam') fn = highlightNeam;
      else if (lang === 'bash' || lang === 'shell' || lang === 'sh') fn = highlightBash;
      else if (lang === 'json') fn = highlightJSON;
      else if (lang === 'toml') fn = highlightTOML;
      if (fn) block.innerHTML = fn(block.textContent);
    });
  });

  // ── Search ──
  var searchIndex = null;
  function loadSearchIndex(basePath) {
    if (searchIndex) return Promise.resolve(searchIndex);
    return fetch(basePath + 'assets/search-index.json')
      .then(function(r) { return r.json(); })
      .then(function(data) { searchIndex = data; return data; });
  }

  function searchFor(query, basePath) {
    if (!searchIndex) return [];
    var q = query.toLowerCase().trim();
    if (!q) return [];
    var terms = q.split(/\s+/);
    var results = [];
    searchIndex.forEach(function(entry) {
      var haystack = (entry.title + ' ' + entry.preview + ' ' + (entry.chapter || '')).toLowerCase();
      var score = 0;
      terms.forEach(function(term) {
        if (haystack.indexOf(term) !== -1) score++;
      });
      if (score > 0) {
        results.push({ entry: entry, score: score });
      }
    });
    results.sort(function(a, b) { return b.score - a.score; });
    return results.slice(0, 20).map(function(r) { return r.entry; });
  }

  document.addEventListener('DOMContentLoaded', function() {
    var searchOverlay = document.getElementById('search-overlay');
    var searchInput = document.getElementById('search-input');
    var searchResults = document.getElementById('search-results');
    var searchBtn = document.querySelector('.search-btn');
    if (!searchOverlay || !searchInput) return;

    var basePath = document.body.getAttribute('data-base') || '';
    var activeIdx = -1;

    function openSearch() {
      loadSearchIndex(basePath);
      searchOverlay.classList.add('open');
      searchInput.value = '';
      searchResults.innerHTML = '<div class="search-empty">Start typing to search...</div>';
      activeIdx = -1;
      setTimeout(function() { searchInput.focus(); }, 50);
    }
    function closeSearch() {
      searchOverlay.classList.remove('open');
      activeIdx = -1;
    }

    if (searchBtn) searchBtn.addEventListener('click', openSearch);
    searchOverlay.addEventListener('click', function(e) {
      if (e.target === searchOverlay) closeSearch();
    });

    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (searchOverlay.classList.contains('open')) closeSearch();
        else openSearch();
      }
      if (e.key === 'Escape' && searchOverlay.classList.contains('open')) {
        closeSearch();
      }
    });

    searchInput.addEventListener('input', function() {
      var hits = searchFor(this.value, basePath);
      activeIdx = -1;
      if (hits.length === 0 && this.value.trim()) {
        searchResults.innerHTML = '<div class="search-empty">No results found</div>';
        return;
      }
      if (!this.value.trim()) {
        searchResults.innerHTML = '<div class="search-empty">Start typing to search...</div>';
        return;
      }
      searchResults.innerHTML = hits.map(function(h, i) {
        return '<a class="search-result" href="' + basePath + h.url + '" data-idx="' + i + '">' +
          '<div class="search-result-title">' + escapeHtml(h.title) + '</div>' +
          (h.chapter ? '<div class="search-result-chapter">' + escapeHtml(h.chapter) + '</div>' : '') +
          '<div class="search-result-preview">' + escapeHtml(h.preview) + '</div>' +
          '</a>';
      }).join('');
    });

    searchInput.addEventListener('keydown', function(e) {
      var items = searchResults.querySelectorAll('.search-result');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, items.length - 1);
        items.forEach(function(el, i) { el.classList.toggle('active', i === activeIdx); });
        if (items[activeIdx]) items[activeIdx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, 0);
        items.forEach(function(el, i) { el.classList.toggle('active', i === activeIdx); });
        if (items[activeIdx]) items[activeIdx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeIdx >= 0 && items[activeIdx]) {
          window.location.href = items[activeIdx].getAttribute('href');
        } else if (items.length > 0) {
          window.location.href = items[0].getAttribute('href');
        }
      }
    });
  });

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ── Arrow Key Navigation ──
  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (document.querySelector('.search-overlay.open')) return;
    var prev = document.querySelector('.nav-prev');
    var next = document.querySelector('.nav-next');
    if (e.key === 'ArrowLeft' && prev) window.location.href = prev.getAttribute('href');
    if (e.key === 'ArrowRight' && next) window.location.href = next.getAttribute('href');
  });

  // ── Heading Anchors (click to copy) ──
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.heading-anchor').forEach(function(a) {
      a.addEventListener('click', function(e) {
        e.preventDefault();
        var url = window.location.origin + window.location.pathname + this.getAttribute('href');
        navigator.clipboard.writeText(url).then(function() {
          a.textContent = '\u2713';
          setTimeout(function() { a.textContent = '#'; }, 1500);
        });
      });
    });
  });

  // ── Scroll-Reveal Entrance Animations ──
  document.addEventListener('DOMContentLoaded', function() {
    if (!('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var selectors = '.callout, .table-wrap, .code-header, .info-box, .box-diagram, .diagram-figure, blockquote';
    var elements = document.querySelectorAll(selectors);

    elements.forEach(function(el) {
      el.classList.add('reveal-on-scroll');
    });

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    elements.forEach(function(el) { observer.observe(el); });
  });

  // ── Staggered Card Entrance on Index Page ──
  document.addEventListener('DOMContentLoaded', function() {
    if (!('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var cards = document.querySelectorAll('.chapter-card');
    if (cards.length === 0) return;

    cards.forEach(function(card) {
      card.classList.add('reveal-on-scroll');
    });

    var cardObserver = new IntersectionObserver(function(entries) {
      var visible = entries.filter(function(e) { return e.isIntersecting; });
      visible.forEach(function(entry, idx) {
        setTimeout(function() {
          entry.target.classList.add('revealed');
        }, idx * 70);
        cardObserver.unobserve(entry.target);
      });
    }, { threshold: 0.05 });

    cards.forEach(function(card) { cardObserver.observe(card); });
  });

  // ── Reading Time Estimate ──
  document.addEventListener('DOMContentLoaded', function() {
    var content = document.querySelector('.content');
    if (!content) return;
    var text = content.textContent || '';
    var words = text.trim().split(/\s+/).length;
    var mins = Math.max(1, Math.ceil(words / 220));
    var h1 = content.querySelector('h1');
    if (h1) {
      var badge = document.createElement('div');
      badge.className = 'reading-time';
      badge.innerHTML = '\u23F1\uFE0F ' + mins + ' min read &middot; ' + words.toLocaleString() + ' words';
      h1.insertAdjacentElement('afterend', badge);
    }
  });
})();
