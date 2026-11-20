/* defaults/default-layout.js — 插件默认布局
 * v6.5.8: 取自用户手工配置的「6.5.8新测试布局」+ Dock 配置(2026-08-02)
 * v7:     重排主区。原来 presets/bodypreset 被顶栏挤到底部，导致第 2~3 行空 142px；
 *         生成中心 4 行 → 2 行。只调位置，不动任何磁贴功能。
 * 含磁贴位置/尺寸/颜色/展开模式/外观 + Dock(钉选按钮/位置/大小/透明度)
 * 已剔除开发工具磁贴(perftest); 用户有任何存储值都会覆盖这些默认
 */
(function() {
'use strict';
window._DEFAULT_LAYOUT = {
  "__tile_layout_v6": {
    "prompt": {
      "col": 3,
      "row": 2,
      "w": 2,
      "h": 4,
      "group": "main"
    },
    "params": {
      "col": 1,
      "row": 2,
      "w": 2,
      "h": 1,
      "group": "main"
    },
    "refimages": {
      "col": 1,
      "row": 3,
      "w": 2,
      "h": 1,
      "group": "main"
    },
    "batchworks": {
      "col": 1,
      "row": 5,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "records": {
      "col": 2,
      "row": 5,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "center": {
      "col": 1,
      "row": 9,
      "w": 4,
      "h": 2,
      "group": "main"
    },
    "presets": {
      "col": 1,
      "row": 6,
      "w": 2,
      "h": 3,
      "group": "main"
    },
    "bodypreset": {
      "col": 3,
      "row": 6,
      "w": 2,
      "h": 3,
      "group": "main"
    },
    "light": {
      "col": 1,
      "row": 4,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "hemisynth": {
      "col": 2,
      "row": 4,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "scope": {
      "col": 1,
      "row": 12,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "log": {
      "col": 1,
      "row": 11,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "drawer": {
      "col": 2,
      "row": 12,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "settings": {
      "col": 2,
      "row": 11,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "billing": {
      "col": 3,
      "row": 11,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "dock": {
      "col": 4,
      "row": 11,
      "w": 1,
      "h": 1,
      "group": "main"
    },
    "netdoctor": {
      "col": 3,
      "row": 12,
      "w": 1,
      "h": 1,
      "group": "main"
    }
  },
  "__tile_expand_modes": {
    "settings": "full",
    "info": "full",
    "chat": "full",
    "presets": "inline",
    "forge": "full",
    "translate": "full",
    "camera": "full",
    "welcome": "full",
    "params": "inline",
    "prompt": "inline",
    "balance": "full",
    "light": "full",
    "history": "full",
    "refimages": "inline",
    "batch": "full",
    "poster": "full",
    "recyclebin": "full",
    "community-mock": "full",
    "scope": "full",
    "kao": "full",
    "colorgrade": "full",
    "tiled": "full",
    "partition": "full",
    "comfyui": "full",
    "scene": "full",
    "run": "full",
    "satellite": "full",
    "drawer": "inline",
    "perf-monitor": "full",
    "hemisynth": "full",
    "canvas": "full"
  },
  "__tile_colors": {},
  "__tile_folders_v6": {},
  "__tile_drawer_stash_v6": [
    "dev-ruler",
    "perftest",
    "community-mock",
    "prompt-optimizer",
    "tiled",
    "partition",
    "batch",
    "colorgrade",
    "qa",
    "forge",
    "comfyui",
    "camera",
    "poster",
    "scene",
    "run",
    "chat",
    "info",
    "kao",
    "satellite",
    "perf-monitor",
    "browser",
    "canvas",
    "codex",
    "tutorial",
    "stitch"
  ],
  "appearance.themeColor": "#2680eb",
  "appearance.blur": 3,
  "appearance.opacity": 88,
  "appearance.tileColorOpacity": 9,
  "dock.items": [
    "common:gen",
    "common:repeatLast",
    "common:stop",
    "common:savePreset",
    "common:anti",
    "common:autoReturn",
    "common:autoGroup",
    "common:openPrompt",
    "common:openSettings",
    "common:openCacheFolder",
    "common:openPresetFolder",
    "common:colorMatchWavelet",
    "common:colorMatchGlobal",
    "common:provider",
    "open:records",
    "open:stitch",
    "common:collapseGroups"
  ],
  "dock.side": "right",
  "dock.scale": 1.15,
  "dock.iconScale": 1.3,
  "dock.opacity": 0.92,
  "dock.blur": 6
};
})();
