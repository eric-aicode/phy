document.addEventListener('DOMContentLoaded', () => {
  // Initialize KaTeX if available
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ],
      throwOnError: false
    });
  }

  // Mode Buttons
  const btnPhysical = document.getElementById('btnModePhysical');
  const btnVector = document.getElementById('btnModeVector');
  const btnCompare = document.getElementById('btnModeCompare');
  const viewportsContainer = document.getElementById('viewportsContainer');
  const cardPhysical = document.getElementById('cardPhysical');
  const cardVector = document.getElementById('cardVector');

  // Action Buttons
  const btnCombineForces = document.getElementById('btnCombineForces');
  const btnAnimateMorph = document.getElementById('btnAnimateMorph');

  // SVG Elements
  const vecGravity = document.getElementById('vecGravity');
  const vecSpring = document.getElementById('vecSpring');
  const vecCombined = document.getElementById('vecCombinedVertical');
  const triangleGroup = document.getElementById('triangleGroup');

  let isCombined = false;

  // Viewport display modes
  function setMode(mode) {
    [btnPhysical, btnVector, btnCompare].forEach(b => b.classList.remove('active'));

    if (mode === 'physical') {
      btnPhysical.classList.add('active');
      viewportsContainer.style.gridTemplateColumns = '1fr';
      cardPhysical.style.display = 'flex';
      cardVector.style.display = 'none';
    } else if (mode === 'vector') {
      btnVector.classList.add('active');
      viewportsContainer.style.gridTemplateColumns = '1fr';
      cardPhysical.style.display = 'none';
      cardVector.style.display = 'flex';
    } else {
      btnCompare.classList.add('active');
      viewportsContainer.style.gridTemplateColumns = window.innerWidth <= 900 ? '1fr' : '1fr 1fr';
      cardPhysical.style.display = 'flex';
      cardVector.style.display = 'flex';
    }
  }

  btnPhysical.addEventListener('click', () => setMode('physical'));
  btnVector.addEventListener('click', () => setMode('vector'));
  btnCompare.addEventListener('click', () => setMode('compare'));

  // Toggle combining vertical forces (10 - 4 = 6)
  btnCombineForces.addEventListener('click', () => {
    isCombined = !isCombined;
    if (isCombined) {
      btnCombineForces.classList.add('active-state');
      btnCombineForces.innerHTML = '<span class="icon">🔄</span> 恢復原始 4 個力';
      
      // Animate out W and Fs, animate in Net 6kgw
      vecGravity.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      vecSpring.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      vecCombined.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

      vecGravity.style.opacity = '0.2';
      vecSpring.style.opacity = '0.2';
      vecCombined.style.opacity = '1';
    } else {
      btnCombineForces.classList.remove('active-state');
      btnCombineForces.innerHTML = '<span class="icon">⚡</span> 合併鉛直力 ($10 - 4 = 6$)';

      vecGravity.style.opacity = '1';
      vecSpring.style.opacity = '1';
      vecCombined.style.opacity = '0';
    }
  });

  // Dynamic Morphing Animation of the Closed Triangle
  btnAnimateMorph.addEventListener('click', () => {
    // If we're only in physical mode, switch to compare mode to see the effect!
    if (btnPhysical.classList.contains('active')) {
      setMode('compare');
    }

    // Trigger visual pop animation on the triangle elements
    triangleGroup.classList.remove('active-morph');
    void triangleGroup.offsetWidth; // trigger reflow
    triangleGroup.classList.add('active-morph');

    const vElemNetDown = document.getElementById('vElemNetDown');
    const vElemT2 = document.getElementById('vElemT2');
    const vElemT1 = document.getElementById('vElemT1');

    // Sequential highlight animation
    [vElemNetDown, vElemT2, vElemT1].forEach(el => {
      el.style.opacity = '0.1';
      el.style.transition = 'all 0.5s ease';
    });

    // Step 1: Net Downward
    setTimeout(() => {
      vElemNetDown.style.opacity = '1';
      vElemNetDown.style.filter = 'drop-shadow(0 0 10px #ff4081)';
    }, 150);

    // Step 2: T2 (Short rope)
    setTimeout(() => {
      vElemT2.style.opacity = '1';
      vElemT2.style.filter = 'drop-shadow(0 0 10px #ffab00)';
    }, 700);

    // Step 3: T1 (Long rope - Closes the loop!)
    setTimeout(() => {
      vElemT1.style.opacity = '1';
      vElemT1.style.filter = 'drop-shadow(0 0 14px #00e676)';
    }, 1250);

    // Remove glow after animation completes
    setTimeout(() => {
      [vElemNetDown, vElemT2, vElemT1].forEach(el => {
        el.style.filter = 'none';
      });
    }, 2500);
  });

  // Responsive check
  window.addEventListener('resize', () => {
    if (btnCompare.classList.contains('active')) {
      viewportsContainer.style.gridTemplateColumns = window.innerWidth <= 900 ? '1fr' : '1fr 1fr';
    }
  });

  // Default mode: Compare
  setMode('compare');
});
