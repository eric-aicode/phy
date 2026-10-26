/**
 * shared.js - 高中物理靜力學 全域圖案畫布高階縮放與平移拖曳引擎
 * 為所有題目頁面的 .diagram-container 自動提供：
 * 1. 拖曳平移 (Pan / Drag) - 按住滑鼠左鍵任意移動，游標為 grab / grabbing
 * 2. 縮放工具 (Zoom In / Out / Reset) - 支援 50% ~ 350% 向量平滑無損縮放
 * 3. 滑鼠滾輪縮放 (Mouse Wheel Zoom)
 * 4. 雙擊復原置中 (Double Click Reset)
 * 5. 手機觸控平移 (Touch Drag)
 */

(function () {
  function initAllDiagramContainers() {
    const containers = document.querySelectorAll('.diagram-container');
    containers.forEach((container, idx) => {
      if (container.dataset.panZoomInited === 'true') return;
      container.dataset.panZoomInited = 'true';

      const svg = container.querySelector('svg');
      if (!svg) return;

      // 檢查是否已存在控制列
      let controlBar = container.parentElement.querySelector('.diagram-zoom-tools-bar');
      if (!controlBar) {
        controlBar = document.createElement('div');
        controlBar.className = 'diagram-zoom-tools-bar';
        controlBar.style.cssText = `
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 10px;
          margin-bottom: 8px;
          flex-wrap: wrap;
        `;
        controlBar.innerHTML = `
          <div style="display:inline-flex; align-items:center; gap:4px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.14); border-radius:8px; padding:2px 6px;">
            <button type="button" class="panzoom-btn-out" style="background:none; border:none; color:#94a3b8; cursor:pointer; font-weight:700; padding:3px 6px; font-size:0.82rem;" title="縮小 (Zoom Out)">🔍−</button>
            <span class="panzoom-level-text" style="font-size:0.78rem; font-weight:700; color:#00e5ff; min-width:40px; text-align:center; font-family:'Fira Code',monospace;">100%</span>
            <button type="button" class="panzoom-btn-in" style="background:none; border:none; color:#94a3b8; cursor:pointer; font-weight:700; padding:3px 6px; font-size:0.82rem;" title="放大 (Zoom In)">🔍+</button>
            <button type="button" class="panzoom-btn-reset" style="background:none; border:none; color:#94a3b8; cursor:pointer; font-weight:700; padding:3px 6px; font-size:0.82rem;" title="重置比例與位置 (Reset)">⟲</button>
          </div>
          <span style="font-size:0.76rem; font-weight:600; color:#94a3b8; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); padding:3px 8px; border-radius:6px; user-select:none;" title="按住滑鼠左鍵可任意拖曳移動・滾輪可縮放・雙擊置中">🖐️ 拖曳移動</span>
        `;
        container.parentElement.insertBefore(controlBar, container);
      }

      let zoom = 1.0;
      let panX = 0;
      let panY = 0;
      let isDragging = false;
      let startX = 0;
      let startY = 0;

      const levelText = controlBar.querySelector('.panzoom-level-text');
      const btnIn = controlBar.querySelector('.panzoom-btn-in');
      const btnOut = controlBar.querySelector('.panzoom-btn-out');
      const btnReset = controlBar.querySelector('.panzoom-btn-reset');

      function updateTransform(smooth = false) {
        svg.style.transition = smooth ? 'transform 0.2s cubic-bezier(0.2, 0, 0, 1)' : 'none';
        svg.style.transformOrigin = 'center center';
        svg.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
      }

      function setZoom(delta) {
        if (delta === 0) {
          zoom = 1.0;
          panX = 0;
          panY = 0;
        } else {
          zoom = Math.max(0.5, Math.min(3.5, zoom + delta));
        }
        if (levelText) levelText.textContent = Math.round(zoom * 100) + '%';
        updateTransform(true);
      }

      if (btnIn) btnIn.onclick = () => setZoom(0.15);
      if (btnOut) btnOut.onclick = () => setZoom(-0.15);
      if (btnReset) btnReset.onclick = () => setZoom(0);

      // Mouse drag pan
      container.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return;
        isDragging = true;
        startX = e.clientX - panX;
        startY = e.clientY - panY;
        container.style.cursor = 'grabbing';
        e.preventDefault();
      });

      window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        panX = e.clientX - startX;
        panY = e.clientY - startY;
        updateTransform(false);
      });

      window.addEventListener('mouseup', () => {
        if (isDragging) {
          isDragging = false;
          container.style.cursor = 'grab';
        }
      });

      // Mouse wheel zoom
      container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.15 : -0.15;
        setZoom(delta);
      }, { passive: false });

      // Double-click reset
      container.addEventListener('dblclick', () => {
        setZoom(0);
      });

      // Touch events for mobile
      let touchStartX = 0, touchStartY = 0;
      container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
          isDragging = true;
          touchStartX = e.touches[0].clientX - panX;
          touchStartY = e.touches[0].clientY - panY;
        }
      }, { passive: true });

      window.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        panX = e.touches[0].clientX - touchStartX;
        panY = e.touches[0].clientY - touchStartY;
        updateTransform(false);
      }, { passive: true });

      window.addEventListener('touchend', () => {
        isDragging = false;
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllDiagramContainers);
  } else {
    initAllDiagramContainers();
  }
})();


// ========================================================
// 【類題 9】逆風帆船逐步動態播放器 (Step-by-Step Interactive Player)
// ========================================================
window.sailboatCurrentStep = 1;
window.sailboatTotalSteps = 5;
window.sailboatAutoPlayTimer = null;

window.sailboatStepTexts = [
  "",
  "<strong>【步驟 1：建立基準線與航向】</strong><br>• 風向垂直向下吹（<span style=\'color:#38bdf8;\'>天藍色線 ↓</span>），以此作為鉛垂基準線。<br>• 船身前進方向朝向左上方西北（<span style=\'color:#fbbf24;\'>金黃色虛線 ↖</span>），題給其與向下風向夾角為 <strong style=\'color:#fbbf24;\'>135°</strong>。",
  "<strong>【步驟 2：放上船面（帆板）】</strong><br>• 穿過船體的細長木板為「<strong>船面（帆板）</strong>」（<span style=\'color:#facc15;\'>金黃色長板</span>）。<br>• 題給帆板與鉛垂風向線夾角為 <strong style=\'color:#facc15;\'>15°</strong>（由波浪引線標註）。",
  "<strong>【步驟 3：風力生成・垂直作用力 F 彈出】</strong><br>• 空氣打在帆板上，反作用力必定<strong>垂直於帆板</strong>（<span style=\'color:#ff007f;\'>粉紅色向量 F ↗</span>，帶直角記號 ⟂）。<br>• 幾何互餘：因為帆板偏鉛垂 15°，故垂直帆板的風力線偏鉛垂 <strong style=\'color:#ff007f;\'>90° - 15° = 75°</strong>！",
  "<strong>【步驟 4：關鍵幾何相減・核心夾角 60° 一秒得出】</strong><br>• 船身方向偏鉛垂線：<strong style=\'color:#fbbf24;\'>135°</strong>。<br>• 風力作用線偏鉛垂線：<strong style=\'color:#ff007f;\'>75°</strong>。<br>• 兩條線都在同一平面內，夾角直接相減：<strong style=\'color:#00e676; font-size:1.15rem;\'>Δθ = 135° - 75° = 60°</strong>！",
  "<strong>【步驟 5：正交投影求順著船頭推力】</strong><br>• 將風力 F 沿著朝向西北的船頭方向投影：<strong style=\'color:#00e5ff; font-size:1.15rem;\'>F_前進 = F · cos 60° = ½ F</strong>（即 0.5F）！<br>• 垂直於船身的橫向側滑力，被船底深水龍骨的水阻力完全抵消（✕ 相消），故船隻只順著船頭向前破浪！"
];

window.gotoSailboatStep = function(s) {
  window.sailboatCurrentStep = s;
  window.updateSailboatStepUI();
};

window.stepSailboatPrev = function() {
  window.sailboatCurrentStep = (window.sailboatCurrentStep > 1) ? window.sailboatCurrentStep - 1 : window.sailboatTotalSteps;
  window.updateSailboatStepUI();
};

window.stepSailboatNext = function() {
  window.sailboatCurrentStep = (window.sailboatCurrentStep < window.sailboatTotalSteps) ? window.sailboatCurrentStep + 1 : 1;
  window.updateSailboatStepUI();
};

window.toggleSailboatAutoPlay = function() {
  const btn = document.getElementById("btnAutoPlay");
  if (window.sailboatAutoPlayTimer) {
    clearInterval(window.sailboatAutoPlayTimer);
    window.sailboatAutoPlayTimer = null;
    if (btn) {
      btn.textContent = "▶ 自動播放";
      btn.style.background = "#0284c7";
    }
  } else {
    if (btn) {
      btn.textContent = "⏸ 暫停播放";
      btn.style.background = "#e11d48";
    }
    window.sailboatAutoPlayTimer = setInterval(() => {
      window.stepSailboatNext();
    }, 2400);
  }
};

window.updateSailboatStepUI = function() {
  for (let i = 1; i <= window.sailboatTotalSteps; i++) {
    const btn = document.getElementById("btnStep" + i);
    if (btn) {
      if (i === window.sailboatCurrentStep) {
        btn.style.background = "rgba(56, 189, 248, 0.25)";
        btn.style.borderColor = "#00e5ff";
        btn.style.color = "#00e5ff";
      } else {
        btn.style.background = "rgba(255, 255, 255, 0.05)";
        btn.style.borderColor = "rgba(255, 255, 255, 0.15)";
        btn.style.color = "#94a3b8";
      }
    }
  }

  for (let i = 1; i <= window.sailboatTotalSteps; i++) {
    const layer = document.getElementById("layerStep" + i);
    if (layer) {
      layer.style.opacity = (i <= window.sailboatCurrentStep) ? "1" : "0";
    }
  }

  const box = document.getElementById("stepExplanationBox");
  if (box && window.sailboatStepTexts[window.sailboatCurrentStep]) {
    box.innerHTML = window.sailboatStepTexts[window.sailboatCurrentStep];
  }
};
