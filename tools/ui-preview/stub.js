/**
 * stub.js — 浏览器预览用的宿主桩
 *
 * 只在 tools/ui-preview/preview.html 里加载，不进插件包。
 * 作用：把 panel 侧发往 UXP 宿主（index.js）的消息就地应答，
 *      让真实的磁贴代码在普通浏览器里能跑起来，从而截图做 UI 迭代。
 *
 * 原理：core/message-bridge.js 在没有 window.uxpHost 时会 postMessage 给自己，
 *      这里监听 source==='panel' 的消息，用 source==='host' 应答。
 */
(function () {
  'use strict';

  var M = window.__PREVIEW_TILES || { js: [], css: [] };

  // ---- 虚拟面板尺寸 ---------------------------------------------------------
  // macOS 上无头 Chromium 的最小窗口宽约 500px，--window-size=280 会被抬到 492，
  // 网格按 492 算完再截图就是错的。所以这里把「面板宽度」显式钉死：
  //   preview.html#w=280&h=650
  // 同时覆盖 innerWidth/innerHeight，让 tile-engine 的展开态也按 280 算。
  var Q = {};
  (location.hash || '').replace(/^#/, '').split('&').forEach(function (kv) {
    var p = kv.split('=');
    if (p[0]) Q[p[0]] = p[1] || '';
  });
  var FW = parseInt(Q.w, 10) || 0;
  var FH = parseInt(Q.h, 10) || 0;

  if (FW > 0) {
    try { Object.defineProperty(window, 'innerWidth', { get: function () { return FW; } }); } catch (e) {}
    if (FH > 0) {
      try { Object.defineProperty(window, 'innerHeight', { get: function () { return FH; } }); } catch (e) {}
    }
    var fs = document.createElement('style');
    fs.textContent = 'html,body{width:' + FW + 'px!important;'
      + (FH > 0 ? 'height:' + FH + 'px!important;' : '')
      + 'overflow:hidden!important}';
    (document.head || document.documentElement).appendChild(fs);
  }

  // 部分磁贴渲染时会并行请求宿主数据；给个通用的空应答，避免它们卡在 await。
  var ACK_WITH_EMPTY = [
    'presetList', 'presetsLoaded', 'refreshPresetsDone', 'comfyWorkflowLoaded',
    'forgeLoras', 'posterPromptsLoaded', 'grsCredits', 'balance',
    'probeSelectionRect', 'selectionRect', 'conversationLayerVisibility'
  ];

  window.addEventListener('message', function (e) {
    var m = e.data;
    if (!m || m.source !== 'panel') return;

    function reply(action, data) {
      window.postMessage({ source: 'host', action: action, data: data || {} }, '*');
    }

    if (m.action === 'scanTiles') {
      reply('tilesList', { jsFiles: M.js, cssFiles: M.css });
    } else if (m.action === 'ready') {
      // 宿主在 ready 之后主动推存储；没真数据时给空对象，storage-manager 会用
      // defaults/default-layout.js 里的默认布局兜底。
      reply('storageLoaded', window.__PREVIEW_STORAGE || {});
    } else if (ACK_WITH_EMPTY.indexOf(m.action) >= 0) {
      reply(m.action, {});
    }
  });

  // 实验用：URL 带 css=相对路径 时追加一份样式表（不影响插件本身）
  if (Q.css) {
    var ex = document.createElement('link');
    ex.rel = 'stylesheet';
    ex.href = '../tools/ui-preview/' + Q.css;
    (document.head || document.documentElement).appendChild(ex);
  }

  // 跳过「开始使用」欢迎页，直接进主界面
  window._welcomeOverlay = {
    showAndWait: function () { return Promise.resolve(); },
    show: function () {},
    hide: function () {}
  };

  // 模拟「老用户」的存储状态：一次性引导、首启欢迎页都已看过。
  // 用真实的存储键而不是 CSS 硬藏，这样预览里看到的布局和真实第二屏一致。
  window.__PREVIEW_STORAGE = window.__PREVIEW_STORAGE || {
    'tutorial.mainlineDone': true,
    'firstrun.welcomeShown': true,
    // Dock 默认开启会吃掉 78px 宽（--dock-w = 半个标准磁贴），网格只剩 202px。
    // 默认关掉看网格本体；要看带 Dock 的样子加 #dock=1。
    'appearance.dockEnabled': Q.dock === '1'
  };

  // 预览指定磁贴的展开态：#open=settings
  if (Q.open) {
    setTimeout(function () {
      try { if (window.TileAPI && TileAPI.expandTile) TileAPI.expandTile(Q.open); } catch (e) {}
    }, 3000);
  }

  // 真实流程里欢迎页点「开始使用」后自己淡出 #bootOverlay；
  // 桩把 showAndWait 直接 resolve 了，所以这里补一刀把启动遮罩按住。
  var s = document.createElement('style');
  s.textContent =
    '#bootOverlay{display:none!important}'
    // 入场动画在无头环境里常常没跑完，截图就会拍到半透明/空白的中间态。
    // 预览只关心静态版式，全部动画与过渡直接关掉。
    + '*,*::before,*::after{animation:none!important;transition:none!important}';
  (document.head || document.documentElement).appendChild(s);

  // 一次性引导/推荐弹窗会随版本变化，逐个关不划算。
  // 统一规则：z-index ≥ 1000 的全屏浮层都是「首次打开才弹」的，预览里压掉。
  // 磁贴展开态是 700、顶栏 600，阈值取 1000 不会误伤主界面。
  var Z_MAX = 1000, GUARD_MS = 20000, _t0 = Date.now();

  function killOverlays() {
    var nodes = document.body ? document.body.children : [];
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (!el || el.id === 'vp' || el.id === 'bgLayer' || el.id === 'bgBlur') continue;
      var cs = window.getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'absolute') continue;
      if (parseInt(cs.zIndex, 10) < Z_MAX) continue;
      var r = el.getBoundingClientRect();
      if (r.width < window.innerWidth * 0.5) continue;   // 小卡片不算浮层
      el.style.setProperty('display', 'none', 'important');
    }
    if (Date.now() - _t0 < GUARD_MS) setTimeout(killOverlays, 400);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(killOverlays, 300); });
  } else {
    setTimeout(killOverlays, 300);
  }

  // 调试用：URL 带 debug=1 时把量到的几何数据写进 <title>，方便 --dump-dom 读取
  if (Q.debug) {
    setTimeout(function () {
      var vp = document.getElementById('vp');
      var cell = getComputedStyle(document.documentElement).getPropertyValue('--cell');
      var g = document.querySelector('.group') || vp;
      var gtc = g ? getComputedStyle(g).gridTemplateColumns : 'n/a';
      var rows = [];
      var ts = document.querySelectorAll('.tile');
      var hidden = [];
      for (var h = 0; h < ts.length; h++) {
        if (getComputedStyle(ts[h]).display === 'none') hidden.push(ts[h].getAttribute('data-id'));
      }
      rows.push('HIDDEN=' + (hidden.join(',') || 'none'));
      var exp = document.querySelector('.tile.expanded');
      if (exp) {
        var er = exp.getBoundingClientRect();
        rows.push('EXP=' + Math.round(er.width) + '@' + Math.round(er.left));
        var row = null;
        var allRows = exp.querySelectorAll('.w10-row');
        for (var z = 0; z < allRows.length; z++) {
          if (allRows[z].textContent.indexOf('图层类型') >= 0) { row = allRows[z]; break; }
        }
        rows.push('EXPS=' + document.querySelectorAll('.tile.expanded').length
          + ' id=' + exp.getAttribute('data-id') + ' cls=' + exp.className.split(' ').slice(0,3).join('.'));
        if (row) {
          var rc = row.querySelector('.w10-row-right');
          rows.push('ROW=row' + Math.round(row.clientWidth) + '/' + Math.round(row.scrollWidth)
            + ' right' + (rc ? Math.round(rc.clientWidth) + '/' + Math.round(rc.scrollWidth) : '-')
            + ' btns=' + (rc ? rc.querySelectorAll('.w10-btn').length : 0));
        }
        var bad = [];
        var all = exp.querySelectorAll('.w10-row, .w10-row-right, .w10-panel');
        for (var q = 0; q < all.length && bad.length < 4; q++) {
          if (all[q].scrollWidth > all[q].clientWidth + 1) {
            bad.push((all[q].className || '').split(' ')[0] + ':' + all[q].clientWidth + '<' + all[q].scrollWidth);
          }
        }
        rows.push('OVERFLOW=' + (bad.join(' ') || 'none'));
      }
      for (var i = 0; i < Math.min(ts.length, 8); i++) {
        var r = ts[i].getBoundingClientRect();
        rows.push(ts[i].getAttribute('data-id') + ':' + Math.round(r.width) + 'x'
          + Math.round(r.height) + '@' + Math.round(r.left) + ',' + Math.round(r.top));
      }
      document.title = 'W=' + window.innerWidth + ' vp=' + (vp ? vp.clientWidth : -1)
        + ' sw=' + (vp ? vp.scrollWidth : -1) + ' cell=' + cell.trim()
        + ' | gtc=' + gtc + ' | ' + rows.join(' ');
    }, 9500);
  }
})();
