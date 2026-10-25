document.addEventListener('DOMContentLoaded', () => {
  // KaTeX initialization
  function renderAllMath() {
    if (typeof renderMathInElement === 'function') {
      renderMathInElement(document.body, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false}
        ],
        throwOnError: false
      });
    }
  }

  // Initial render
  setTimeout(renderAllMath, 50);

  // Correct answer targets
  const answers = {
    ansH: { val: 3.0, tol: 0.1, fb: document.getElementById('fbH'), name: '深度 h' },
    ansFs: { val: 5.0, tol: 0.2, fb: document.getElementById('fbFs'), name: '彈簧彈力 Fs' },
    ansFnet: { val: 15.0, tol: 0.2, fb: document.getElementById('fbFnet'), name: '淨向下合力' },
    ansT1: { val: 9.0, tol: 0.2, fb: document.getElementById('fbT1'), name: '較長繩張力 T1' },
    ansT2: { val: 12.0, tol: 0.2, fb: document.getElementById('fbT2'), name: '較短繩張力 T2' }
  };

  const btnCheck = document.getElementById('btnCheckAnswer');
  const btnToggleHint = document.getElementById('btnToggleHint');
  const btnRevealSolution = document.getElementById('btnRevealSolution');
  const hintBox = document.getElementById('hintBox');
  const solutionSection = document.getElementById('solutionSection');
  const resultBanner = document.getElementById('resultBanner');

  // Check answers
  btnCheck.addEventListener('click', () => {
    let allCorrect = true;
    let anyFilled = false;

    for (const [key, item] of Object.entries(answers)) {
      const inputEl = document.getElementById(key);
      const userVal = parseFloat(inputEl.value.trim());

      if (isNaN(userVal)) {
        item.fb.textContent = '⚠️ 請填寫數值';
        item.fb.className = 'feedback-msg wrong';
        allCorrect = false;
        continue;
      }

      anyFilled = true;
      if (Math.abs(userVal - item.val) <= item.tol) {
        item.fb.textContent = `✅ 正確！(${item.val})`;
        item.fb.className = 'feedback-msg correct';
        inputEl.style.borderColor = '#00e676';
      } else {
        item.fb.textContent = `❌ 數值有誤，請再想一想`;
        item.fb.className = 'feedback-msg wrong';
        inputEl.style.borderColor = '#ff4081';
        allCorrect = false;
      }
    }

    if (allCorrect) {
      resultBanner.classList.remove('hidden');
      unlockSolution(true);
    } else if (anyFilled) {
      resultBanner.classList.add('hidden');
    }
  });

  // Toggle Hint
  btnToggleHint.addEventListener('click', () => {
    hintBox.classList.toggle('hidden');
    btnToggleHint.textContent = hintBox.classList.contains('hidden') ? '💡 顯示解題提示' : '🙈 隱藏解題提示';
  });

  // Unlock Solution
  function unlockSolution(autoScroll = false) {
    solutionSection.classList.remove('hidden');
    btnRevealSolution.textContent = '✅ 詳解已解鎖';
    btnRevealSolution.style.background = '#00e676';
    btnRevealSolution.style.color = '#0b0f19';

    // Re-render KaTeX in solution section
    renderAllMath();

    if (autoScroll) {
      setTimeout(() => {
        solutionSection.scrollIntoView({ behavior: 'smooth' });
      }, 200);
    }
  }

  btnRevealSolution.addEventListener('click', () => {
    unlockSolution(true);
  });
});
