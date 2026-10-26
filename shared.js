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
