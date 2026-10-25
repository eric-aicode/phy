import os
import json
import re
from bs4 import BeautifulSoup

def adapt_svg_to_dark(raw_svg):
    if not raw_svg:
        return ''
    soup = BeautifulSoup(raw_svg, 'html.parser')
    svg = soup.find('svg')
    if not svg:
        return raw_svg

    if not svg.get('style'):
        svg['style'] = 'max-width: 580px; width: 100%; height: auto;'

    for marker in svg.find_all('marker'):
        for p in marker.find_all(['path', 'polygon', 'polyline']):
            p['fill'] = '#cbd5e1'
            if p.get('stroke'):
                p['stroke'] = '#cbd5e1'

    for t in svg.find_all('text'):
        t['fill'] = '#f1f5f9'
        t['font-family'] = 'inherit'

    black_strokes = ['#000000', '#000', 'black', '#111827', '#1e293b', '#334155']
    for el in svg.find_all(True):
        st = el.get('stroke')
        if st in black_strokes:
            el['stroke'] = '#cbd5e1'
        elif not st and el.name in ['line', 'polyline']:
            el['stroke'] = '#cbd5e1'

        fl = el.get('fill')
        if fl in ['#000000', '#000', 'black'] and el.name != 'text':
            if el.name in ['circle', 'ellipse'] and float(el.get('r', 10)) <= 6:
                el['fill'] = '#38bdf8'
            elif el.name == 'rect':
                el['fill'] = '#1e293b'
                el['stroke'] = '#38bdf8'
            else:
                el['fill'] = '#cbd5e1'
        elif fl in ['#ffffff', '#fff', 'white'] and el.name == 'rect':
            el['fill'] = '#1e293b'
            el['stroke'] = '#475569'
        elif fl == '#334155':
            el['fill'] = '#1e293b'
            el['stroke'] = '#38bdf8'

    return str(svg)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print_path = os.path.join(base_dir, 'print.html')
    with open(print_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # 1. Parse answers
    ans_rows = soup.select('.answer-row')
    answers_map = {}
    for row in ans_rows:
        num_txt = row.select_one('.ans-num').get_text(strip=True)
        val_txt = row.select_one('.ans-val').get_text(strip=True)
        clean_key = re.sub(r'^\d+\.\s*', '', num_txt)
        answers_map[clean_key] = val_txt

    # 2. Canonical IDs
    canonical_id_map = {}
    for idx, row in enumerate(ans_rows):
        num_txt = row.select_one('.ans-num').get_text(strip=True)
        clean_key = re.sub(r'^\d+\.\s*', '', num_txt)
        canonical_id_map[idx] = clean_key

    # 3. Parse items
    items = soup.select('.exam-item')
    problems = []

    for idx, item in enumerate(items):
        cid = canonical_id_map.get(idx, f'q_{idx+1}')

        sec_container = item.find_parent('.section-container')
        sec_title_el = sec_container.select_one('.section-title') if sec_container else None
        sec_title = sec_title_el.get_text(strip=True) if sec_title_el else ''

        num_el = item.select_one('.item-num')
        raw_title = num_el.get_text(strip=True) if num_el else f'題 {idx+1}'

        tags = [t.get_text(strip=True) for t in item.select('.item-tags .tag-border')]

        text_el = item.select_one('.item-text')
        text_html = ''
        if text_el:
            for selector in ['.item-options', '.diagram-container', '.options-container', '.feedback-box']:
                for el in text_el.select(selector):
                    el.decompose()
            text_html = str(text_el).strip()

        options = []
        opt_cells = item.select('.option-cell')
        for opt in opt_cells:
            options.append(opt.get_text(' ', strip=True))

        svg_el = item.select_one('.item-diagram-box svg')
        svg_html = adapt_svg_to_dark(str(svg_el)) if svg_el else ''

        ans = answers_map.get(cid, '')

        problems.append({
            'id': cid,
            'index': idx + 1,
            'title': raw_title,
            'category': sec_title,
            'tags': tags,
            'content': text_html,
            'options': options,
            'svg': svg_html,
            'diagrams': [],
            'related': [],
            'answer': ans,
            'solutions': []
        })

    # ========================================================
    # Enrich Problem 1: 彈性繩對折與並聯
    # ========================================================
    problems[0]['answer'] = '(C) 3.2 N'
    p1_svg_raw = '''<svg viewBox="0 0 340 280" style="max-width: 440px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-axis-dm" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#94a3b8"/>
    </marker>
  </defs>
  <line x1="50" y1="220" x2="310" y2="220" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr-axis-dm)"/>
  <line x1="50" y1="220" x2="50" y2="35" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr-axis-dm)"/>
  <text x="305" y="245" fill="#94a3b8" font-size="12" font-weight="bold" text-anchor="end">伸長量 (cm)</text>
  <text x="45" y="26" fill="#94a3b8" font-size="12" font-weight="bold" text-anchor="middle">外力 (N)</text>
  <text x="42" y="236" fill="#64748b" font-size="12" text-anchor="end">0</text>
  <line x1="140" y1="220" x2="140" y2="226" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="140" y="240" fill="#94a3b8" font-size="12" text-anchor="middle">5</text>
  <line x1="230" y1="220" x2="230" y2="226" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="230" y="240" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">10</text>
  <line x1="44" y1="140" x2="50" y2="140" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="38" y="144" fill="#94a3b8" font-size="12" text-anchor="end">2</text>
  <line x1="44" y1="60" x2="50" y2="60" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="38" y="64" fill="#38bdf8" font-size="12" text-anchor="end" font-weight="bold">4</text>
  <line x1="50" y1="60" x2="230" y2="60" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="4,4"/>
  <line x1="230" y1="220" x2="230" y2="60" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="4,4"/>
  <line x1="50" y1="220" x2="230" y2="60" stroke="#00e5ff" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M230,60 Q265,56 295,45" fill="none" stroke="#00e5ff" stroke-width="2.5" stroke-dasharray="4,4"/>
  <circle cx="230" cy="60" r="5" fill="#00e5ff" stroke="#fff" stroke-width="1.5"/>
  <text x="240" y="55" fill="#00e5ff" font-size="12" font-weight="bold">(10 cm, 4 N)</text>
  <text x="110" y="130" fill="#facc15" font-size="12" font-weight="bold">斜率 k = 0.4 N/cm</text>
</svg>'''

    p1_svg_setup = '''<svg viewBox="0 0 340 300" style="max-width: 440px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p1-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p1-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>
  <line x1="30" y1="40" x2="310" y2="40" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>
  <circle cx="170" cy="40" r="5" fill="#38bdf8"/>
  <text x="170" y="24" fill="#94a3b8" font-size="12" text-anchor="middle">固定天花板同一點</text>
  <path d="M166,40 Q130,95 166,150" fill="none" stroke="#38bdf8" stroke-width="3.5"/>
  <path d="M174,40 Q210,95 174,150" fill="none" stroke="#c084fc" stroke-width="3.5"/>
  <text x="95" y="95" fill="#38bdf8" font-size="12" font-weight="bold">原長 10 cm</text>
  <text x="215" y="95" fill="#c084fc" font-size="12" font-weight="bold">原長 10 cm</text>
  <circle cx="170" cy="150" r="5" fill="#00e5ff"/>
  <line x1="170" y1="150" x2="170" y2="185" stroke="#94a3b8" stroke-width="2"/>
  <rect x="135" y="185" width="70" height="42" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="170" y="211" fill="#fff" font-size="14" font-weight="bold" text-anchor="middle">物體 W</text>
  <line x1="156" y1="145" x2="156" y2="90" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p1-cyan)"/>
  <text x="148" y="85" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="end">T₁ = 1.6 N</text>
  <line x1="184" y1="145" x2="184" y2="90" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p1-cyan)"/>
  <text x="192" y="85" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="start">T₂ = 1.6 N</text>
  <line x1="170" y1="228" x2="170" y2="275" stroke="#ff5252" stroke-width="3.5" marker-end="url(#arr-p1-red)"/>
  <text x="180" y="270" fill="#ff5252" font-size="13" font-weight="bold">W = 3.2 N</text>
  <line x1="235" y1="130" x2="235" y2="150" stroke="#facc15" stroke-width="2"/>
  <text x="245" y="144" fill="#facc15" font-size="11" font-weight="bold">Δy = 2.0 cm</text>
</svg>'''

    problems[0]['diagrams'] = [
        { 'label': '📐 原始題圖 (F-x 關係)', 'svg': p1_svg_raw },
        { 'label': '💡 圖解受力分析 (雙繩對稱懸掛)', 'svg': p1_svg_setup }
    ]
    problems[0]['svg'] = p1_svg_raw
    problems[0]['related'] = [
        { 'id': 'problem2', 'title': '範例 2：雙彈簧串聯平衡與脫離', 'badge': '彈簧串並聯' },
        { 'id': 'exercise1', 'title': '練習 1：彈簧裁半剛度換算', 'badge': '長度折半' },
        { 'id': 'exercise2', 'title': '練習 2：彈性繩伸長與外力分析', 'badge': '虎克定律' }
    ]
    problems[0]['solutions'] = [
        {
            'title': '【解法一・講義標準解】分段換算法',
            'type': 'textbook',
            'steps': [
                '📌 <strong>讀圖求彈力常數</strong>：原長 $20\\text{ cm}$ 時外力 $4.0\\text{ N}$ 伸長 $10\\text{ cm} \\implies k_0 = \\frac{4.0}{10} = \\mathbf{0.4\\text{ N/cm}}$。',
                '📐 <strong>折半伸長換算</strong>：半繩原長 $10\\text{ cm}$ 伸長 $2.0\\text{ cm}$，等效於全繩伸長 $\\Delta x_{\\text{全}} = 2 \\times 2.0 = 4.0\\text{ cm}$。',
                '⚡ <strong>雙股平衡求物重</strong>：每段張力 $T = 0.4 \\times 4.0 = 1.6\\text{ N}$，得：$$W = 2T = 2 \\times 1.6 = \\mathbf{3.2\\text{ N}} \\quad \\text{✅ 選 (C)}$$'
            ]
        },
        {
            'title': '【解法二・等效彈力常數法】（大考標準速解）',
            'type': 'standard',
            'steps': [
                '📌 <strong>長度折半剛度加倍</strong>：$k\' = 2k_0 = 2 \\times 0.4 = 0.8\\text{ N/cm}$。',
                '📐 <strong>雙繩並聯相加</strong>：$k_{\\text{並}} = k\' + k\' = 0.8 + 0.8 = 1.6\\text{ N/cm}$。',
                '⚡ <strong>虎克定律直接求解</strong>：$$W = k_{\\text{並}} \\times \\Delta y = 1.6 \\times 2.0 = \\mathbf{3.2\\text{ N}}$$'
            ]
        },
        {
            'title': '【解法三・極速倍率法】（直觀 10 秒秒殺）',
            'type': 'speed',
            'steps': [
                '📌 <strong>等效剛度 4 倍</strong>：折半（$\\times 2$）$\\times$ 並聯（$\\times 2$）$= \\mathbf{4\\text{ 倍}}$。',
                '⚡ <strong>外力放大直接計算</strong>：原繩伸長 $2.0\\text{ cm}$ 需 $0.4 \\times 2.0 = 0.8\\text{ N}$，故物重直接 4 倍：$$W = 4 \\times 0.8 = \\mathbf{3.2\\text{ N}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 2: 雙彈簧雙重物
    # ========================================================
    problems[1]['answer'] = '(1) a 長 22.5 cm，b 長 17.5 cm； (2) a 長 27.5 cm，平臺作用力 5 gw； (3) 55 cm'
    p2_svg_raw = '''<svg viewBox="0 0 240 350" style="max-width: 300px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="30" y1="45" x2="210" y2="45" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
  <text x="35" y="40" fill="#38bdf8" font-size="15" font-weight="bold">A</text>
  <path d="M120,45 L120,55 L130,67 L110,79 L130,91 L110,103 L130,115 L110,127 L130,139 L110,151 L120,163 L120,172" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="145" y="112" fill="#38bdf8" font-size="14" font-weight="bold">a (原長20)</text>
  <rect x="95" y="172" width="50" height="26" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="120" y="190" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">m (10g)</text>
  <path d="M120,198 L120,206 L130,218 L110,230 L130,242 L110,254 L130,266 L110,278 L120,288 L120,296" fill="none" stroke="#facc15" stroke-width="2.5"/>
  <text x="145" y="250" fill="#facc15" font-size="14" font-weight="bold">b (原長20)</text>
  <rect x="95" y="296" width="50" height="24" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="120" y="313" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">n (10g)</text>
  <line x1="30" y1="320" x2="210" y2="320" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
  <text x="35" y="338" fill="#38bdf8" font-size="15" font-weight="bold">B (平臺)</text>
</svg>'''

    p2_svg_s1 = '''<svg viewBox="0 0 240 350" style="max-width: 300px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="220" height="330" rx="8" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5"/>
  <line x1="30" y1="45" x2="210" y2="45" stroke="#64748b" stroke-width="4"/>
  <text x="25" y="40" fill="#38bdf8" font-size="13" font-weight="bold">A</text>
  <path d="M120,45 L120,55 L130,67 L110,79 L130,91 L110,103 L130,115 L110,127 L130,139 L110,151 L120,163 L120,172" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="145" y="105" fill="#38bdf8" font-size="12" font-weight="bold">彈簧 a (伸)</text>
  <text x="145" y="122" fill="#00e5ff" font-size="11" font-weight="bold">22.5 cm</text>
  <rect x="95" y="172" width="50" height="24" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="120" y="188" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">m</text>
  <path d="M120,196 L120,204 L130,214 L110,224 L130,234 L110,244 L130,254 L110,264 L120,272 L120,280" fill="none" stroke="#facc15" stroke-width="2.5"/>
  <text x="145" y="235" fill="#facc15" font-size="12" font-weight="bold">彈簧 b (縮)</text>
  <text x="145" y="252" fill="#fbbf24" font-size="11" font-weight="bold">17.5 cm</text>
  <rect x="95" y="280" width="50" height="22" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="120" y="295" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">n</text>
  <line x1="30" y1="302" x2="210" y2="302" stroke="#64748b" stroke-width="4"/>
  <text x="25" y="318" fill="#38bdf8" font-size="13" font-weight="bold">B</text>
  <text x="120" y="330" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">總間距 L = 40 cm</text>
</svg>'''

    problems[1]['diagrams'] = [
        { 'label': '📐 原始題圖 (串聯配置)', 'svg': p2_svg_raw },
        { 'label': '💡 (1) 40cm 受力圖解', 'svg': p2_svg_s1 }
    ]
    problems[1]['svg'] = p2_svg_raw
    problems[1]['related'] = [
        { 'id': 'problem1', 'title': '範例 1：彈性繩對折並聯', 'badge': '等效剛度' },
        { 'id': 'exercise3', 'title': '練習 3：雙重物串聯受力與離地臨界', 'badge': '臨界支持力' },
        { 'id': 'exercise4', 'title': '練習 4：三彈簧串並聯伸長量', 'badge': '形變疊加' }
    ]
    problems[1]['solutions'] = [
        {
            'title': '【解法一・講義標準解】隔離體受力平衡（重點精要）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>(1) $L_{AB} = 40\\text{ cm}$</strong>：a 伸長 $x$ 則 b 壓縮 $x$。m 鉛直平衡：$$F_a + F_b = W_m \\implies 2kx = 10 \\implies x = 2.5\\text{ cm}$$得 a 長 $\\ell_a = 20 + 2.5 = \\mathbf{22.5\\text{ cm}}$，b 長 $\\ell_b = 20 - 2.5 = \\mathbf{17.5\\text{ cm}}$。',
                '📌 <strong>(2) 下移至 $L_{AB} = 50\\text{ cm}$</strong>：總形變 $x_a + x_b = 10\\text{ cm}$。隔離 m：$$k(x_a - x_b) = 10 \\implies x_a - x_b = 5\\text{ cm}$$聯立解得 $x_a = 7.5\\text{ cm}$（a 長 $\\mathbf{27.5\\text{ cm}}$）、$x_b = 2.5\\text{ cm}$。隔離 n 得平臺支持力：$$N = W_n - F_b = 10 - 2 \\times 2.5 = \\mathbf{5\\text{ gw}}$$',
                '⚡ <strong>(3) 脫離臨界 ($N = 0$)</strong>：懸空平衡，全重 $20\\text{ gw}$ 由 a 吊起 $\\implies x_a = \\frac{20}{2} = 10\\text{ cm}$；n 重 $10\\text{ gw}$ 由 b 吊起 $\\implies x_b = \\frac{10}{2} = 5\\text{ cm}$。臨界總距：$$L = (20 + 10) + (20 + 5) = \\mathbf{55\\text{ cm}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 3: 三細線拉銅環之合力運算
    # ========================================================
    problems[2]['answer'] = '合力大小為 $10\\text{ kgw}$，方向與 $+x$ 軸夾 $217^\\circ$（或與 $-x$ 軸夾 $37^\\circ$）'
    p3_svg_raw = '''<svg viewBox="0 0 540 340" style="max-width: 520px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p3-axis" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#64748b"/>
    </marker>
    <marker id="arr-p3-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p3-yellow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
    <marker id="arr-p3-purple" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#c084fc"/>
    </marker>
  </defs>
  <line x1="40" y1="170" x2="500" y2="170" stroke="#475569" stroke-width="1.8" marker-end="url(#arr-p3-axis)"/>
  <line x1="260" y1="310" x2="260" y2="30" stroke="#475569" stroke-width="1.8" marker-end="url(#arr-p3-axis)"/>
  <text x="495" y="195" fill="#94a3b8" font-size="13" font-weight="bold">+x</text>
  <text x="275" y="45" fill="#94a3b8" font-size="13" font-weight="bold">+y</text>
  <text x="45" y="195" fill="#64748b" font-size="13">-x</text>
  <text x="275" y="305" fill="#64748b" font-size="13">-y</text>
  <circle cx="260" cy="170" r="7" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="245" y="190" fill="#38bdf8" font-size="12" font-weight="bold">O</text>
  <line x1="260" y1="170" x2="430" y2="170" stroke="#00e5ff" stroke-width="3.5" marker-end="url(#arr-p3-cyan)"/>
  <text x="350" y="155" fill="#00e5ff" font-size="13" font-weight="bold">F₁ = 25 kgw</text>
  <line x1="260" y1="170" x2="165" y2="44" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-p3-yellow)"/>
  <text x="140" y="35" fill="#facc15" font-size="13" font-weight="bold">F₂ = 15 kgw</text>
  <path d="M310,170 A50,50 0 0,0 230,130" fill="none" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="280" y="135" fill="#facc15" font-size="11" font-weight="bold">127°</text>
  <line x1="260" y1="170" x2="85" y2="301" stroke="#c084fc" stroke-width="3.5" marker-end="url(#arr-p3-purple)"/>
  <text x="50" y="315" fill="#c084fc" font-size="13" font-weight="bold">F₃ = 30 kgw</text>
  <path d="M233,134 L213,150 L240,186" fill="none" stroke="#e2e8f0" stroke-width="1.8"/>
  <text x="200" y="145" fill="#e2e8f0" font-size="11" font-weight="bold">90°</text>
</svg>'''

    p3_svg_triangle = '''<svg viewBox="0 0 540 320" style="max-width: 520px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p3t-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
  </defs>
  <rect x="20" y="20" width="500" height="280" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(0, 230, 118, 0.3)" stroke-width="1.5"/>
  <text x="45" y="55" fill="#00e676" font-size="14" font-weight="bold">🔺 合力直角三角形（3 : 4 : 5 特殊角）：</text>
  <line x1="380" y1="90" x2="160" y2="90" stroke="#38bdf8" stroke-width="3.5"/>
  <text x="270" y="80" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">|Rx| = 8 kgw (4 份)</text>
  <line x1="160" y1="90" x2="160" y2="225" stroke="#c084fc" stroke-width="3.5"/>
  <text x="135" y="165" fill="#c084fc" font-size="13" font-weight="bold" text-anchor="end">|Ry| = 6 kgw (3 份)</text>
  <line x1="380" y1="90" x2="164" y2="222" stroke="#00e676" stroke-width="4.5" marker-end="url(#arr-p3t-green)"/>
  <text x="310" y="175" fill="#00e676" font-size="15" font-weight="bold">R = 10 kgw (5 份)</text>
  <rect x="160" y="90" width="16" height="16" fill="none" stroke="#fff" stroke-width="1.5"/>
  <path d="M340,90 A40,40 0 0,1 346,110" fill="none" stroke="#facc15" stroke-width="2"/>
  <text x="325" y="112" fill="#facc15" font-size="12" font-weight="bold">37°</text>
  <rect x="250" y="210" width="250" height="70" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="265" y="235" fill="#fff" font-size="12" font-weight="bold">⚡ 答案直觀秒得：</text>
  <text x="265" y="255" fill="#00e676" font-size="13" font-weight="bold">大小 R = √(8² + 6²) = 10 kgw</text>
  <text x="265" y="272" fill="#facc15" font-size="11">方向與 +x 軸夾角 = 180° + 37° = 217°</text>
</svg>'''

    problems[2]['diagrams'] = [
        { 'label': '📐 原始題圖 (三力配置)', 'svg': p3_svg_raw },
        { 'label': '🔺 向量直角三角形 (R=10)', 'svg': p3_svg_triangle }
    ]
    problems[2]['svg'] = p3_svg_raw
    problems[2]['related'] = [
        { 'id': 'problem4', 'title': '範例 4：三力封閉直角三角形', 'badge': '封閉三角形' },
        { 'id': 'equil1', 'title': '平衡 1：正交分解多力平衡', 'badge': '正交投影' },
        { 'id': 'equil2', 'title': '平衡 2：三力共點向量合成', 'badge': '拉密定理' }
    ]
    problems[2]['solutions'] = [
        {
            'title': '【解法一・正交分解法】（大考標準標準解）',
            'type': 'standard',
            'steps': [
                '📌 <strong>分量正交投影</strong>：<br>$\\vec{F}_1 = (+25, 0)$。<br>$\\vec{F}_2$ 與 $-x$ 軸夾 $53^\\circ$：$F_{2x} = -15\\cos 53^\\circ = -9$，$F_{2y} = +15\\sin 53^\\circ = +12$。<br>$\\vec{F}_3$ 與 $-x$ 軸夾 $37^\\circ$：$F_{3x} = -30\\cos 37^\\circ = -24$，$F_{3y} = -30\\sin 37^\\circ = -18$。',
                '📐 <strong>各軸分量相加</strong>：$$R_x = 25 - 9 - 24 = \\mathbf{-8\\text{ kgw}}$$ $$R_y = 0 + 12 - 18 = \\mathbf{-6\\text{ kgw}}$$',
                '⚡ <strong>合成合力大小與方向</strong>：$$R = \\sqrt{(-8)^2 + (-6)^2} = \\mathbf{10\\text{ kgw}}$$位於第三象限，與 $-x$ 軸夾角為 $37^\\circ$（與 $+x$ 軸夾角為 $180^\\circ + 37^\\circ = \\mathbf{217^\\circ}$）。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 4: 細繩與彈簧懸吊平衡
    # ========================================================
    problems[3]['answer'] = '較長之細繩上張力為 $3\\text{ kgw}$'
    p4_svg_raw = '''<svg viewBox="0 0 540 340" style="max-width: 520px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p4-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>
  <line x1="40" y1="40" x2="500" y2="40" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>
  <g opacity="0.3" stroke="#94a3b8" stroke-width="1.5">
    <line x1="60" y1="40" x2="75" y2="25"/><line x1="120" y1="40" x2="135" y2="25"/>
    <line x1="180" y1="40" x2="195" y2="25"/><line x1="240" y1="40" x2="255" y2="25"/>
    <line x1="300" y1="40" x2="315" y2="25"/><line x1="360" y1="40" x2="375" y2="25"/>
    <line x1="420" y1="40" x2="435" y2="25"/><line x1="480" y1="40" x2="495" y2="25"/>
  </g>
  <line x1="82" y1="40" x2="290" y2="160" stroke="#00e5ff" stroke-width="3.5"/>
  <text x="145" y="115" fill="#00e5ff" font-size="12" font-weight="bold">長繩 4.0 cm (T₁)</text>
  <path d="M125,40 A45,45 0 0,1 120,62" fill="none" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="135" y="58" fill="#00e5ff" font-size="11" font-weight="bold">30°</text>
  <line x1="360" y1="40" x2="290" y2="160" stroke="#c084fc" stroke-width="3.5"/>
  <text x="350" y="115" fill="#c084fc" font-size="12" font-weight="bold">短繩 (T₂)</text>
  <path d="M335,40 A30,30 0 0,0 345,60" fill="none" stroke="#c084fc" stroke-width="1.5"/>
  <text x="325" y="68" fill="#c084fc" font-size="11" font-weight="bold">60°</text>
  <path d="M290,40 L290,52 L298,60 L282,68 L298,76 L282,84 L298,92 L282,100 L298,108 L282,116 L298,124 L282,132 L298,140 L290,148 L290,160" fill="none" stroke="#facc15" stroke-width="2.5"/>
  <text x="245" y="95" fill="#facc15" font-size="11" font-weight="bold">彈簧 (L₀=1.5)</text>
  <circle cx="290" cy="160" r="5" fill="#fff" stroke="#38bdf8" stroke-width="2"/>
  <text x="305" y="165" fill="#fff" font-size="11" font-weight="bold">節點</text>
  <line x1="290" y1="160" x2="290" y2="215" stroke="#94a3b8" stroke-width="2"/>
  <rect x="260" y="215" width="60" height="38" rx="6" fill="#1e293b" stroke="#ff5252" stroke-width="2"/>
  <text x="290" y="239" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">W = 10</text>
  <line x1="290" y1="253" x2="290" y2="295" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-p4-red)"/>
  <text x="305" y="290" fill="#ff5252" font-size="12" font-weight="bold">10 kgw</text>
</svg>'''

    p4_svg_triangle = '''<svg viewBox="0 0 540 320" style="max-width: 520px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p4t-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p4t-purple" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#c084fc"/>
    </marker>
    <marker id="arr-p4t-yellow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
  </defs>
  <rect x="20" y="20" width="500" height="280" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5"/>
  <text x="40" y="50" fill="#38bdf8" font-size="13" font-weight="bold">🔺 節點受力之向量封閉直角三角形：</text>
  <line x1="320" y1="70" x2="320" y2="242" stroke="#facc15" stroke-width="4" marker-end="url(#arr-p4t-yellow)"/>
  <text x="335" y="150" fill="#facc15" font-size="13" font-weight="bold">W_net = 6 kgw (斜邊)</text>
  <text x="335" y="168" fill="#94a3b8" font-size="11">(= 10 - 4 彈力)</text>
  <line x1="320" y1="250" x2="246" y2="164" stroke="#00e5ff" stroke-width="4" marker-end="url(#arr-p4t-cyan)"/>
  <text x="235" y="225" fill="#00e5ff" font-size="14" font-weight="bold">T₁ = 3 kgw</text>
  <line x1="242" y1="160" x2="314" y2="74" stroke="#c084fc" stroke-width="4" marker-end="url(#arr-p4t-purple)"/>
  <text x="235" y="105" fill="#c084fc" font-size="13" font-weight="bold">T₂ = 3√3 kgw</text>
  <path d="M250,150 L260,159 L251,168" fill="none" stroke="#fff" stroke-width="1.8"/>
  <path d="M320,215 A35,35 0 0,0 295,222" fill="none" stroke="#00e5ff" stroke-width="1.8"/>
  <text x="290" y="240" fill="#00e5ff" font-size="11" font-weight="bold">60°</text>
  <rect x="40" y="70" width="165" height="190" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="50" y="95" fill="#fff" font-size="11" font-weight="bold">📐 幾何與彈力解析：</text>
  <text x="50" y="118" fill="#94a3b8" font-size="11">深 h = 4.0×sin30° = 2.0</text>
  <text x="50" y="138" fill="#facc15" font-size="11">Δx = 2.0 - 1.5 = 0.5 cm</text>
  <text x="50" y="158" fill="#facc15" font-size="11">Fs = 8×0.5 = 4 kgw</text>
  <text x="50" y="182" fill="#fff" font-size="11" font-weight="bold">⚡ 封閉三角形投影：</text>
  <text x="50" y="205" fill="#00e5ff" font-size="12" font-weight="bold">T₁ = W_net × cos60°</text>
  <text x="50" y="225" fill="#00e5ff" font-size="12" font-weight="bold">   = 6 × (1/2) = 3</text>
  <text x="50" y="248" fill="#00e676" font-size="11" font-weight="bold">✅ 正確選 3 kgw</text>
</svg>'''

    problems[3]['diagrams'] = [
        { 'label': '📐 原始題圖 (懸吊配置)', 'svg': p4_svg_raw },
        { 'label': '🔺 向量封閉直角三角形 (T₁=3)', 'svg': p4_svg_triangle }
    ]
    problems[3]['svg'] = p4_svg_raw
    problems[3]['related'] = [
        { 'id': 'problem3', 'title': '範例 3：三細線拉銅環合力運算', 'badge': '向量分解' },
        { 'id': 'equil3', 'title': '平衡 3：細繩吊重張力比例', 'badge': '封閉直角三角形' },
        { 'id': 'equil4', 'title': '平衡 4：彈簧與懸繩組合受力', 'badge': '彈力淨重' }
    ]
    problems[3]['solutions'] = [
        {
            'title': '【解法一・向量封閉三角形法】（大考標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>求彈力與結點淨力</strong>：<br>結點深度 $h = 4.0 \\times \\sin 30^\\circ = 2.0\\text{ cm}$。<br>彈簧伸長量 $\\Delta x = 2.0 - 1.5 = 0.5\\text{ cm} \\implies F_s = 8\\text{ kgw/cm} \\times 0.5 = 4\\text{ kgw}$。<br>結點向下淨負載：$$W_{\\text{net}} = W - F_s = 10 - 4 = \\mathbf{6\\text{ kgw}}$$',
                '📐 <strong>向量封閉直角三角形</strong>：兩繩夾角 $90^\\circ$（直角），長繩 $T_1$ 與鉛垂線夾 $60^\\circ$。',
                '⚡ <strong>直角投影直接求張力</strong>：$$T_1 = W_{\\text{net}} \\cos 60^\\circ = 6 \\times \\frac{1}{2} = \\mathbf{3\\text{ kgw}} \\quad \\text{✅}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 5: 槽內雙球接觸正向力分析
    # ========================================================
    problems[4]['answer'] = '(1) 容器底對 B 正向力：$N_{\\text{底}} = \\mathbf{2W}$； (2) 容器壁對 B 正向力：$N_2 = \\mathbf{\\frac{1}{\\sqrt{3}}W}$； (3) 兩球間作用力：$N_{AB} = \\mathbf{\\frac{2}{\\sqrt{3}}W}$'
    p5_svg_raw = '''<svg viewBox="0 0 460 380" style="max-width: 440px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="110" y1="40" x2="110" y2="320" stroke="#64748b" stroke-width="4"/>
  <line x1="350" y1="40" x2="350" y2="320" stroke="#64748b" stroke-width="4"/>
  <line x1="80" y1="320" x2="380" y2="320" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
  <text x="230" y="350" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">槽寬 3r</text>
  <circle cx="270" cy="240" r="80" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
  <circle cx="270" cy="240" r="4" fill="#38bdf8"/>
  <text x="270" y="245" fill="#fff" font-size="16" font-weight="bold" text-anchor="middle">B</text>
  <text x="270" y="265" fill="#94a3b8" font-size="11" text-anchor="middle">重 W</text>
  <circle cx="190" cy="101" r="80" fill="#1e293b" stroke="#facc15" stroke-width="2.5"/>
  <circle cx="190" cy="101" r="4" fill="#facc15"/>
  <text x="190" y="106" fill="#fff" font-size="16" font-weight="bold" text-anchor="middle">A</text>
  <text x="190" y="126" fill="#94a3b8" font-size="11" text-anchor="middle">重 W</text>
  <line x1="190" y1="101" x2="270" y2="240" stroke="#ff5252" stroke-width="2" stroke-dasharray="4,4"/>
  <text x="245" y="165" fill="#ff5252" font-size="11" font-weight="bold">2r</text>
</svg>'''

    p5_svg_geom = '''<svg viewBox="0 0 480 340" style="max-width: 460px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="440" height="300" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5"/>
  <text x="40" y="50" fill="#38bdf8" font-size="14" font-weight="bold">📐 球心連線幾何直角三角形：</text>
  <line x1="160" y1="90" x2="260" y2="90" stroke="#38bdf8" stroke-width="3"/>
  <text x="210" y="80" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">Δx = 3r - 2r = r</text>
  <line x1="260" y1="90" x2="260" y2="263" stroke="#c084fc" stroke-width="3"/>
  <text x="275" y="180" fill="#c084fc" font-size="12" font-weight="bold">Δy = √3 r</text>
  <line x1="160" y1="90" x2="260" y2="263" stroke="#facc15" stroke-width="4"/>
  <text x="195" y="190" fill="#facc15" font-size="13" font-weight="bold">d = 2r</text>
  <rect x="245" y="90" width="15" height="15" fill="none" stroke="#fff" stroke-width="1.5"/>
  <path d="M190,90 A30,30 0 0,1 175,115" fill="none" stroke="#00e676" stroke-width="2"/>
  <text x="185" y="115" fill="#00e676" font-size="12" font-weight="bold">θ = 60°</text>
  <rect x="295" y="110" width="150" height="150" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="305" y="135" fill="#fff" font-size="11" font-weight="bold">⚡ 幾何結論：</text>
  <text x="305" y="160" fill="#00e5ff" font-size="11">cosθ = r / 2r = 1/2</text>
  <text x="305" y="180" fill="#00e676" font-size="12" font-weight="bold">⇒ θ = 60°</text>
  <text x="305" y="205" fill="#facc15" font-size="11">sin 60° = √3 / 2</text>
  <text x="305" y="225" fill="#facc15" font-size="11">cos 60° = 1 / 2</text>
</svg>'''

    problems[4]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙球配置)', 'svg': p5_svg_raw },
        { 'label': '💡 球心連線幾何 (θ=60°)', 'svg': p5_svg_geom }
    ]
    problems[4]['svg'] = p5_svg_raw
    problems[4]['related'] = [
        { 'id': 'equil5', 'title': '平衡 5：三球堆疊接觸正向力', 'badge': '幾何對稱' },
        { 'id': 'equil6', 'title': '平衡 6：槽內雙球整體受力', 'badge': '整體隔離' },
        { 'id': 'problem6', 'title': '範例 6：粗繩懸掛切線張力', 'badge': '切線受力' }
    ]
    problems[4]['solutions'] = [
        {
            'title': '【解法一・系統整體與隔離體分析】（大考標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>(1) 容器底對 B 正向力（整體法）</strong>：<br>將 A、B 兩球視為一體，鉛直方向僅受總重力與底部支持力平衡：$$N_{\\text{底}} = W_A + W_B = \\mathbf{2W}$$',
                '📐 <strong>(3) 兩球作用力 $N_{AB}$（隔離 A 球）</strong>：<br>球心連線與水平夾角 $\\theta = 60^\\circ$。<br>A 球鉛直受力平衡：$$N_{AB}\\sin 60^\\circ = W \\implies N_{AB} = \\frac{W}{\\sin 60^\\circ} = \\mathbf{\\frac{2}{\\sqrt{3}}W}$$',
                '⚡ <strong>(2) 容器壁對 B 正向力 $N_2$（水平平衡）</strong>：<br>整體水平平衡（左壁推力等於右壁推力）：$$N_2 = N_1 = N_{AB}\\cos 60^\\circ = \\frac{2}{\\sqrt{3}}W \\times \\frac{1}{2} = \\mathbf{\\frac{1}{\\sqrt{3}}W}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 6: 粗繩懸掛各點張力與水平恆定性
    # ========================================================
    problems[5]['answer'] = '(1) $T_0 = T_C = \\frac{W\\sin\\theta_1\\sin\\theta_2}{\\sin(\\theta_1+\\theta_2)}$，$T_A = \\frac{W\\sin\\theta_2}{\\sin(\\theta_1+\\theta_2)}$，$T_B = \\frac{W\\sin\\theta_1}{\\sin(\\theta_1+\\theta_2)}$； (2) 繩上無水平外力作用，各點水平張力皆相等'

    p6_svg_raw = '''<svg viewBox="0 0 520 340" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p6-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p6-yellow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
  </defs>
  <!-- Vertical walls -->
  <line x1="80" y1="30" x2="80" y2="300" stroke="#64748b" stroke-width="4"/>
  <line x1="440" y1="30" x2="440" y2="300" stroke="#64748b" stroke-width="4"/>

  <!-- Heavy Rope Catenary Curve: A(80, 70), Lowest C(230, 240), B(440, 110) -->
  <path d="M80,70 Q140,240 230,240 T440,110" fill="none" stroke="#facc15" stroke-width="4.5" stroke-linecap="round"/>

  <!-- Points A, B, C -->
  <circle cx="80" cy="70" r="5" fill="#00e5ff"/>
  <text x="60" y="75" fill="#00e5ff" font-size="14" font-weight="bold">A</text>
  <circle cx="440" cy="110" r="5" fill="#00e5ff"/>
  <text x="455" y="115" fill="#00e5ff" font-size="14" font-weight="bold">B</text>
  <circle cx="230" cy="240" r="5" fill="#00e676"/>
  <text x="230" y="265" fill="#00e676" font-size="14" font-weight="bold" text-anchor="middle">C (最低點)</text>

  <!-- Tangents and Angles -->
  <!-- A tangent -->
  <line x1="80" y1="70" x2="135" y2="155" stroke="#00e5ff" stroke-width="2.5" stroke-dasharray="4,4" marker-end="url(#arr-p6-cyan)"/>
  <text x="145" y="150" fill="#00e5ff" font-size="12" font-weight="bold">TA (夾 θ₁)</text>
  <path d="M80,105 A35,35 0 0,0 95,95" fill="none" stroke="#00e5ff" stroke-width="1.8"/>
  <text x="92" y="115" fill="#00e5ff" font-size="12">θ₁</text>

  <!-- B tangent -->
  <line x1="440" y1="110" x2="380" y2="175" stroke="#facc15" stroke-width="2.5" stroke-dasharray="4,4" marker-end="url(#arr-p6-yellow)"/>
  <text x="350" y="170" fill="#facc15" font-size="12" font-weight="bold">TB (夾 θ₂)</text>
  <path d="M440,140 A30,30 0 0,1 425,128" fill="none" stroke="#facc15" stroke-width="1.8"/>
  <text x="415" y="148" fill="#facc15" font-size="12">θ₂</text>

  <!-- Weight total W -->
  <text x="260" y="160" fill="#ff5252" font-size="14" font-weight="bold">均勻粗繩總重 W</text>
</svg>'''

    p6_svg_fbd = '''<svg viewBox="0 0 520 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p6f-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p6f-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
  </defs>
  <rect x="15" y="15" width="490" height="290" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5"/>
  <text x="35" y="45" fill="#38bdf8" font-size="13" font-weight="bold">💡 隔離體分析・水平與鉛直受力拆解：</text>

  <!-- AC Section -->
  <path d="M60,80 Q110,190 190,190" fill="none" stroke="#00e5ff" stroke-width="3.5"/>
  <text x="110" y="125" fill="#00e5ff" font-size="11" font-weight="bold">AC 段 (重 W_AC)</text>
  <line x1="60" y1="80" x2="60" y2="35" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arr-p6f-cyan)"/>
  <text x="65" y="55" fill="#38bdf8" font-size="11">TA cosθ₁ = W_AC</text>
  <line x1="190" y1="190" x2="245" y2="190" stroke="#00e676" stroke-width="3" marker-end="url(#arr-p6f-green)"/>
  <text x="210" y="212" fill="#00e676" font-size="11" font-weight="bold">T_C = T₀ (純水平)</text>

  <!-- BC Section -->
  <path d="M440,95 Q380,190 310,190" fill="none" stroke="#facc15" stroke-width="3.5"/>
  <text x="350" y="130" fill="#facc15" font-size="11" font-weight="bold">BC 段 (重 W_BC)</text>
  <line x1="440" y1="95" x2="440" y2="45" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-p6f-cyan)"/>
  <text x="365" y="65" fill="#facc15" font-size="11">TB cosθ₂ = W_BC</text>
  <line x1="310" y1="190" x2="255" y2="190" stroke="#00e676" stroke-width="3" marker-end="url(#arr-p6f-green)"/>

  <!-- Key Summary Box -->
  <rect x="50" y="235" width="420" height="55" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="65" y="256" fill="#00e676" font-size="12" font-weight="bold">⚡ 核心恆定理：</text>
  <text x="65" y="275" fill="#f1f5f9" font-size="11">水平方向無外力 ⇒ 任一點張力水平分量恆等於最低點張力：T_x = T₀ = T_C</text>
</svg>'''

    problems[5]['diagrams'] = [
        { 'label': '📐 原始題圖 (懸鏈情境)', 'svg': p6_svg_raw },
        { 'label': '💡 隔離體分析 (分量拆解)', 'svg': p6_svg_fbd }
    ]
    problems[5]['svg'] = p6_svg_raw
    problems[5]['related'] = [
        { 'id': 'equil10', 'title': '平衡 10：懸鏈線最低點張力', 'badge': '水平恆定' },
        { 'id': 'problem8', 'title': '範例 8：水平輕棒懸重樞鈕力', 'badge': '水平平衡' },
        { 'id': 'equil11', 'title': '平衡 11：對稱雙繩懸吊', 'badge': '張力分解' }
    ]
    problems[5]['solutions'] = [
        {
            'title': '【解法一・水平恆定與整體平衡法】（大考標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>水平張力恆定性 (第 2 小題)</strong>：<br>對粗繩上任意小段隔離，水平方向僅受左右切線張力作用，無其他外力，故由 $\\sum F_x = 0$ 可得：$$\\text{全繩任一點張力之水平分量恆等於常數 } T_0$$最低點 C 切線為水平，故 $T_C = T_0$。',
                '📐 <strong>整體與最低點平衡聯立 (第 1 小題)</strong>：<br>兩端水平分量相等：$T_A\\sin\\theta_1 = T_B\\sin\\theta_2 = T_0$。<br>兩端鉛直分量平衡全重：$T_A\\cos\\theta_1 + T_B\\cos\\theta_2 = W$。<br>以 $T_0$ 代換得：$$T_0(\\cot\\theta_1 + \\cot\\theta_2) = W \\implies T_C = T_0 = \\mathbf{\\frac{W\\sin\\theta_1\\sin\\theta_2}{\\sin(\\theta_1+\\theta_2)}}$$',
                '⚡ <strong>求得 A、B 兩端張力</strong>：$$T_A = \\frac{T_0}{\\sin\\theta_1} = \\mathbf{\\frac{W\\sin\\theta_2}{\\sin(\\theta_1+\\theta_2)}}, \\quad T_B = \\frac{T_0}{\\sin\\theta_2} = \\mathbf{\\frac{W\\sin\\theta_1}{\\sin(\\theta_1+\\theta_2)}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 7: 高架工作車之翻覆臨界力矩
    # ========================================================
    problems[6]['answer'] = '(B) 32a / 5'

    p7_svg_raw = '''<svg viewBox="0 0 520 360" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p7-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>
  <!-- Road ground -->
  <line x1="30" y1="310" x2="480" y2="310" stroke="#64748b" stroke-width="4"/>
  <!-- Front Wheel (Right): x = 360, Rear Wheel (Left): x = 160. Spacing = a = 200px -->
  <circle cx="360" cy="290" r="20" fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
  <circle cx="160" cy="290" r="20" fill="#1e293b" stroke="#facc15" stroke-width="3"/>
  <text x="260" y="335" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">輪距 a</text>
  <line x1="160" y1="318" x2="360" y2="318" stroke="#38bdf8" stroke-width="1.5"/>

  <!-- Truck Body -->
  <rect x="130" y="210" width="260" height="65" rx="8" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>
  <!-- Center of mass of truck body M (directly above front wheel x=360) -->
  <circle cx="360" cy="242" r="6" fill="#00e5ff"/>
  <line x1="360" y1="242" x2="360" y2="280" stroke="#00e5ff" stroke-width="2.5" marker-end="url(#arr-p7-red)"/>
  <text x="375" y="250" fill="#00e5ff" font-size="12" font-weight="bold">車體 M</text>

  <!-- Boom: Pivot above rear wheel (160, 210). Tilted 30° backward (left). Length L = 220px -->
  <!-- dx = -220 * sin30 = -110 (x = 50), dy = -220 * cos30 = -190.5 (y = 19.5) -->
  <line x1="160" y1="210" x2="50" y2="25" stroke="#facc15" stroke-width="5" stroke-linecap="round"/>
  <text x="110" y="105" fill="#facc15" font-size="12" font-weight="bold">支架 M/8 (長 L)</text>

  <!-- Angle 30° to vertical -->
  <line x1="160" y1="210" x2="160" y2="60" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4"/>
  <path d="M160,140 A70,70 0 0,0 125,150" fill="none" stroke="#facc15" stroke-width="1.8"/>
  <text x="140" y="135" fill="#facc15" font-size="12" font-weight="bold">30°</text>

  <!-- Platform and worker at top (50, 25) -->
  <rect x="20" y="5" width="60" height="30" rx="4" fill="#1e293b" stroke="#ff5252" stroke-width="2"/>
  <text x="50" y="25" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">人員 M/4</text>
  <circle cx="160" cy="210" r="5" fill="#facc15"/>
  <text x="175" y="215" fill="#facc15" font-size="11" font-weight="bold">支點 O</text>
</svg>'''

    p7_svg_torque = '''<svg viewBox="0 0 520 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="15" y="15" width="490" height="290" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(250, 204, 21, 0.3)" stroke-width="1.5"/>
  <text x="35" y="45" fill="#facc15" font-size="14" font-weight="bold">⚖️ 以後輪軸 O 為支點之臨界力矩平衡：</text>

  <!-- Resisting Torque (Clockwise) -->
  <rect x="35" y="70" width="210" height="100" rx="8" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="45" y="95" fill="#00e676" font-size="12" font-weight="bold">🛡️ 抗翻覆力矩（順時針）：</text>
  <text x="45" y="120" fill="#f1f5f9" font-size="12">車體重心力臂 = a</text>
  <text x="45" y="145" fill="#00e676" font-size="13" font-weight="bold">τ_抗 = M g × a</text>

  <!-- Overturning Torque (Counter-Clockwise) -->
  <rect x="260" y="70" width="225" height="150" rx="8" fill="#1e293b" stroke="#ff5252" stroke-width="1.5"/>
  <text x="270" y="95" fill="#ff5252" font-size="12" font-weight="bold">⚠️ 傾覆力矩（逆時針）：</text>
  <text x="270" y="120" fill="#f1f5f9" font-size="11">支架：(M/8)g × (L/2)sin30° = (1/32)MgL</text>
  <text x="270" y="145" fill="#f1f5f9" font-size="11">人員：(M/4)g × L sin30° = (4/32)MgL</text>
  <text x="270" y="175" fill="#ff5252" font-size="13" font-weight="bold">τ_翻 = (5/32) M g L</text>

  <!-- Critical Balance -->
  <rect x="35" y="235" width="450" height="55" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="50" y="258" fill="#38bdf8" font-size="12" font-weight="bold">⚡ 臨界翻覆平衡 (N_前 = 0)：</text>
  <text x="50" y="278" fill="#f1f5f9" font-size="12">M g a = (5/32) M g L ⇒ L_max = <strong style="color:#00e676;">(32/5) a</strong>  ✅ 選 (B)</text>
</svg>'''

    problems[6]['diagrams'] = [
        { 'label': '📐 原始題圖 (工作車配置)', 'svg': p7_svg_raw },
        { 'label': '💡 翻覆力矩平衡分析', 'svg': p7_svg_torque }
    ]
    problems[6]['svg'] = p7_svg_raw
    problems[6]['related'] = [
        { 'id': 'torque1', 'title': '力矩 1：起重機抗翻覆臨界', 'badge': '翻覆臨界' },
        { 'id': 'torque2', 'title': '力矩 2：雙輪支架力矩平衡', 'badge': '支點選擇' },
        { 'id': 'torque3', 'title': '力矩 3：均質桿件傾斜力矩', 'badge': '力臂計算' }
    ]
    problems[6]['solutions'] = [
        {
            'title': '【解法一・後輪軸支點力矩平衡】（大考秒殺標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>選定後輪軸為支點</strong>：當工作車即將翻覆時，前輪正向力恰為零（$N_{\\text{前}} = 0$）。選後輪軸為支點可避開未知支持力。',
                '📐 <strong>列出順時針抗翻覆與逆時針傾覆力矩</strong>：<br>順時針抗翻力矩：$$\\tau_{\\text{抗}} = M g \\cdot a$$逆時針傾覆力矩（支架中點力臂 $\\frac{L}{2}\\sin 30^\\circ$，頂端力臂 $L\\sin 30^\\circ$）：$$\\tau_{\\text{翻}} = \\left(\\frac{1}{8}Mg\\right)\\left(\\frac{L}{4}\\right) + \\left(\\frac{1}{4}Mg\\right)\\left(\\frac{L}{2}\\right) = \\left(\\frac{1}{32} + \\frac{4}{32}\\right)MgL = \\mathbf{\\frac{5}{32}MgL}$$',
                '⚡ <strong>臨界平衡直接解得最大長度</strong>：$$Mga = \\frac{5}{32}MgL \\implies L_{\\max} = \\mathbf{\\frac{32}{5}a} \\quad \\text{✅ 選 (B)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 8: 水平輕棒懸重之樞鈕力分析
    # ========================================================
    problems[7]['answer'] = '(A) 變大； (B) 變大； (C) 變小； (D) 變小'

    p8_svg_raw = '''<svg viewBox="0 0 520 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Wall -->
  <line x1="80" y1="30" x2="80" y2="280" stroke="#64748b" stroke-width="4"/>
  <!-- Rod OP: length L = 320px. From (80, 200) to (400, 200) -->
  <line x1="80" y1="200" x2="400" y2="200" stroke="#facc15" stroke-width="5" stroke-linecap="round"/>
  <circle cx="80" cy="200" r="5" fill="#38bdf8"/>
  <text x="60" y="205" fill="#38bdf8" font-size="14" font-weight="bold">O</text>
  <circle cx="400" cy="200" r="5" fill="#00e5ff"/>
  <text x="415" y="205" fill="#00e5ff" font-size="14" font-weight="bold">P</text>
  <text x="240" y="225" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">輕棒長 ℓ</text>

  <!-- Rope from wall (80, 60) to P(400, 200) -->
  <line x1="80" y1="60" x2="400" y2="200" stroke="#00e5ff" stroke-width="3"/>
  <text x="250" y="115" fill="#00e5ff" font-size="12" font-weight="bold">輕繩張力 T</text>
  <!-- Angle theta between rope and rod at P -->
  <path d="M350,200 A50,50 0 0,1 362,183" fill="none" stroke="#00e5ff" stroke-width="1.8"/>
  <text x="345" y="190" fill="#00e5ff" font-size="12">θ</text>

  <!-- Hanging weight W at distance x (x = 220, so position = 80 + 140 = 220) -->
  <line x1="220" y1="200" x2="220" y2="250" stroke="#94a3b8" stroke-width="2"/>
  <rect x="195" y="250" width="50" height="32" rx="4" fill="#1e293b" stroke="#ff5252" stroke-width="2"/>
  <text x="220" y="271" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">W</text>
  <line x1="80" y1="180" x2="220" y2="180" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="150" y="175" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">距離 x ➔</text>
</svg>'''

    p8_svg_fbd = '''<svg viewBox="0 0 520 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p8-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p8-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
    <marker id="arr-p8-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>
  <rect x="15" y="15" width="490" height="290" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5"/>
  <text x="35" y="42" fill="#38bdf8" font-size="13" font-weight="bold">💡 樞鈕力與張力公式推演：</text>

  <!-- Rod line -->
  <line x1="80" y1="130" x2="420" y2="130" stroke="#64748b" stroke-width="3"/>
  <!-- Pivot forces at O -->
  <line x1="80" y1="130" x2="140" y2="130" stroke="#00e676" stroke-width="3" marker-end="url(#arr-p8-green)"/>
  <text x="110" y="120" fill="#00e676" font-size="11" font-weight="bold">Fx (右)</text>
  <line x1="80" y1="130" x2="80" y2="75" stroke="#00e676" stroke-width="3" marker-end="url(#arr-p8-green)"/>
  <text x="90" y="85" fill="#00e676" font-size="11" font-weight="bold">Fy (上)</text>

  <!-- Tension components at P -->
  <line x1="420" y1="130" x2="360" y2="130" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p8-cyan)"/>
  <text x="370" y="120" fill="#00e5ff" font-size="11" font-weight="bold">T cosθ</text>
  <line x1="420" y1="130" x2="420" y2="70" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p8-cyan)"/>
  <text x="430" y="85" fill="#00e5ff" font-size="11" font-weight="bold">T sinθ</text>

  <!-- Weight at x -->
  <line x1="250" y1="130" x2="250" y2="185" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-p8-red)"/>
  <text x="260" y="175" fill="#ff5252" font-size="12" font-weight="bold">W</text>

  <!-- Deductions table -->
  <rect x="35" y="195" width="450" height="95" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="50" y="218" fill="#facc15" font-size="12" font-weight="bold">⚡ 當 x 增大時各物理量判斷：</text>
  <text x="50" y="240" fill="#f1f5f9" font-size="11">(A) 力矩平衡：T = (W·x)/(ℓ·sinθ) ⇒ <strong style="color:#00e676;">變大</strong></text>
  <text x="50" y="260" fill="#f1f5f9" font-size="11">(B) 水平平衡：Fx = T·cosθ ⇒ <strong style="color:#00e676;">變大</strong></text>
  <text x="50" y="280" fill="#f1f5f9" font-size="11">(C) 鉛直平衡：Fy = W(1 - x/ℓ) ⇒ <strong style="color:#ff5252;">變小</strong> ； (D) tanα = Fy/Fx ⇒ <strong style="color:#ff5252;">變小</strong></text>
</svg>'''

    problems[7]['diagrams'] = [
        { 'label': '📐 原始題圖 (懸重裝置)', 'svg': p8_svg_raw },
        { 'label': '💡 樞鈕力與分量平衡推演', 'svg': p8_svg_fbd }
    ]
    problems[7]['svg'] = p8_svg_raw
    problems[7]['related'] = [
        { 'id': 'torque4', 'title': '力矩 4：懸臂樑固定端樞鈕力', 'badge': '樞鈕力' },
        { 'id': 'equil12', 'title': '平衡 12：三力共點與樞鈕作用力', 'badge': '共點匯聚' },
        { 'id': 'torque5', 'title': '力矩 5：斜置木棒受力動態變化', 'badge': '力矩變化' }
    ]
    problems[7]['solutions'] = [
        {
            'title': '【解法一・力矩與水平鉛直平衡分析】（大考標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>(A) 對 O 點取力矩求張力 $T$</strong>：$$W \\cdot x = T\\sin\\theta \\cdot \\ell \\implies T = \\frac{W x}{\\ell \\sin\\theta}$$當 $x$ 增大時，張力 $T$ <strong>【變大】</strong>。',
                '📌 <strong>(B) 水平平衡求樞鈕力分量 $F_x$</strong>：$$F_x = T\\cos\\theta = \\frac{W x}{\\ell} \\cot\\theta$$當 $x$ 增大時，水平分量 $F_x$ <strong>【變大】</strong>。',
                '📌 <strong>(C) 鉛直平衡求樞鈕力分量 $F_y$</strong>：$$F_y + T\\sin\\theta = W \\implies F_y = W - \\frac{Wx}{\\ell} = W\\left(1 - \\frac{x}{\\ell}\\right)$$當 $x$ 增大時，鉛直分量 $F_y$ <strong>【變小】</strong>。',
                '⚡ <strong>(D) 樞鈕力夾角 $\\alpha$ 變化</strong>：$$\\tan\\alpha = \\frac{F_y}{F_x}$$分子 $F_y$ 變小且分母 $F_x$ 變大 $\\implies \\tan\\alpha$ 變小 $\\implies$ 夾角 $\\alpha$ <strong>【變小】</strong>。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 9: 斜面上物體靜止與等速下滑受力
    # ========================================================
    problems[8]['answer'] = '情境一：① f = ½W； ② R = W (鉛直向上)； ③ f地 = 0\\n情境二：① f_k = ⅗W； ② R = W (鉛直向上)； ③ f地 = 0'

    p9_svg_raw = '''<svg viewBox="0 0 680 320" style="max-width: 600px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Scenario 1: θ = 30° Static -->
  <g transform="translate(30, 20)">
    <text x="130" y="30" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">【情境一：θ = 30° 靜止】</text>
    <!-- Wedge -->
    <polygon points="30,240 240,240 240,120" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
    <line x1="10" y1="240" x2="260" y2="240" stroke="#64748b" stroke-width="3"/>
    <!-- Angle 30° -->
    <path d="M75,240 A45,45 0 0,0 71,217" fill="none" stroke="#facc15" stroke-width="2"/>
    <text x="80" y="232" fill="#facc15" font-size="12" font-weight="bold">30°</text>
    <!-- Block at (130, 182) -->
    <g transform="translate(130, 182) rotate(-29.7)">
      <rect x="-30" y="-26" width="60" height="26" rx="4" fill="#0f172a" stroke="#facc15" stroke-width="2"/>
      <text x="0" y="-8" fill="#facc15" font-size="11" font-weight="bold" text-anchor="middle">靜止 W</text>
    </g>
    <rect x="30" y="255" width="210" height="30" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
    <text x="135" y="275" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">加速度 a = 0 (靜態平衡)</text>
  </g>

  <!-- Scenario 2: θ = 37° Constant Velocity -->
  <g transform="translate(360, 20)">
    <text x="130" y="30" fill="#00e676" font-size="14" font-weight="bold" text-anchor="middle">【情境二：θ = 37° 等速下滑】</text>
    <!-- Wedge -->
    <polygon points="30,240 240,240 240,82" fill="#1e293b" stroke="#00e676" stroke-width="2.5"/>
    <line x1="10" y1="240" x2="260" y2="240" stroke="#64748b" stroke-width="3"/>
    <!-- Angle 37° -->
    <path d="M75,240 A45,45 0 0,0 67,212" fill="none" stroke="#facc15" stroke-width="2"/>
    <text x="78" y="232" fill="#facc15" font-size="12" font-weight="bold">37°</text>
    <!-- Block at (130, 164) -->
    <g transform="translate(130, 164) rotate(-37)">
      <rect x="-30" y="-26" width="60" height="26" rx="4" fill="#0f172a" stroke="#00e676" stroke-width="2"/>
      <text x="0" y="-8" fill="#00e676" font-size="11" font-weight="bold" text-anchor="middle">等速 v</text>
    </g>
    <rect x="30" y="255" width="210" height="30" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1"/>
    <text x="135" y="275" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">加速度 a = 0 (動態平衡)</text>
  </g>
</svg>'''

    p9_svg_fbd = '''<svg viewBox="0 0 680 320" style="max-width: 600px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p9-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
    <marker id="arr-p9-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p9-gold" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
    <marker id="arr-p9-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
  </defs>

  <!-- Left: Block FBD with resultant R -->
  <g transform="translate(30, 20)">
    <rect x="0" y="0" width="300" height="280" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="20" y="30" fill="#38bdf8" font-size="13" font-weight="bold">木塊受力平衡與接觸合力 R：</text>

    <!-- Center dot -->
    <circle cx="150" cy="150" r="6" fill="#f1f5f9"/>
    <!-- Gravity W down -->
    <line x1="150" y1="150" x2="150" y2="240" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-p9-red)"/>
    <text x="160" y="235" fill="#ff5252" font-size="12" font-weight="bold">重力 W (下)</text>

    <!-- Normal Force N perpendicular up-left -->
    <line x1="150" y1="150" x2="105" y2="72" stroke="#00e5ff" stroke-width="2.5" marker-end="url(#arr-p9-cyan)"/>
    <text x="75" y="75" fill="#00e5ff" font-size="11" font-weight="bold">正向力 N</text>

    <!-- Friction f along slope up-right -->
    <line x1="150" y1="150" x2="195" y2="72" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-p9-gold)"/>
    <text x="195" y="75" fill="#facc15" font-size="11" font-weight="bold">摩擦力 f</text>

    <!-- Contact Force R = N + f : Straight Up! -->
    <line x1="150" y1="150" x2="150" y2="60" stroke="#00e676" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arr-p9-green)"/>
    <text x="150" y="48" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">接觸合力 R = W (鉛直向上)</text>

    <text x="20" y="265" fill="#94a3b8" font-size="11">因 a = 0 ⟹ ΣF = 0 ⟹ R 與 W 必等大反向！</text>
  </g>

  <!-- Right: System Boundary & Ground Friction -->
  <g transform="translate(350, 20)">
    <rect x="0" y="0" width="310" height="280" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e676" stroke-width="1.5"/>
    <text x="20" y="30" fill="#00e676" font-size="13" font-weight="bold">系統整體法分析地面摩擦力：</text>

    <!-- System boundary dashed box -->
    <rect x="35" y="60" width="240" height="130" rx="12" fill="none" stroke="#00e5ff" stroke-width="2" stroke-dasharray="6,4"/>
    <text x="155" y="80" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="middle">【整體系統：木塊 ＋ 斜面體】</text>

    <!-- Center dot of system -->
    <circle cx="155" cy="125" r="5" fill="#facc15"/>
    <line x1="155" y1="125" x2="155" y2="175" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-p9-red)"/>
    <text x="165" y="165" fill="#ff5252" font-size="11" font-weight="bold">總重力 W總</text>

    <!-- Ground support -->
    <line x1="155" y1="220" x2="155" y2="185" stroke="#00e5ff" stroke-width="2.5" marker-end="url(#arr-p9-cyan)"/>
    <text x="165" y="210" fill="#00e5ff" font-size="11" font-weight="bold">地面正向力 N地</text>

    <rect x="25" y="215" width="260" height="50" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
    <text x="155" y="235" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">系統無水平外力 ⟹ f地 = 0</text>
    <text x="155" y="253" fill="#f1f5f9" font-size="11" text-anchor="middle">靜止或等速下滑時，木塊水平加速度均為 0！</text>
  </g>
</svg>'''

    p9_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (兩情境斜面模型)</div>
        ''' + p9_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 隔離體受力與系統分析並列</div>
        ''' + p9_svg_fbd + '''
      </div>
    </div>'''

    problems[8]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙情境斜面模型)', 'svg': p9_svg_raw },
        { 'label': '💡 隔離體受力平衡與接觸合力', 'svg': p9_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': p9_svg_dual }
    ]
    problems[8]['svg'] = p9_svg_raw
    problems[8]['related'] = [
        { 'id': 'equil7', 'title': '平衡 7：斜面上滑動與靜止摩擦力', 'badge': '接觸合力' },
        { 'id': 'frict1', 'title': '摩擦 1：斜面最大靜摩擦臨界角', 'badge': '摩擦臨界' },
        { 'id': 'equil8', 'title': '平衡 8：斜面體置於粗糙地面受力', 'badge': '整體法' }
    ]
    problems[8]['solutions'] = [
        {
            'title': '【重點解析・隔離體與系統整體法速解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・物體受力分析與摩擦力</strong>：<br>物體在斜面上受三力：重力 $W$、斜面正向力 $N = W\\cos\\theta$、摩擦力 $f = W\\sin\\theta$。<br>① 情境一（$\\theta = 30^\\circ$ 靜止）：$$f = W\\sin 30^\\circ = \\mathbf{\\frac{1}{2}W}$$② 情境二（$\\theta = 37^\\circ$ 等速下滑）：$$f_k = W\\sin 37^\\circ = \\mathbf{\\frac{3}{5}W} = 0.6W$$',
                '📐 <strong>重點二・斜面對物體的作用力（接觸合力必為鉛直向上）</strong>：<br>斜面對物體施加兩力：法向力 $N$ 與切向摩擦力 $f$。其向量和即為「接觸合力 $\\vec{R} = \\vec{N} + \\vec{f}$」。<br>因為物體「靜止」或「等速下滑」，其<strong>加速度均為零（$\\vec{a} = 0$）</strong>，由合力為零：$$\\vec{R} + \\vec{W} = 0 \\implies \\vec{R} = -\\vec{W}$$因此斜面對物體作用力大小恆等於 <strong>$W$</strong>，方向<strong>【鉛直向上】</strong>（兩情境皆同！）。',
                '⚡ <strong>重點三・斜面體受到地面的摩擦力（整體法秒殺）</strong>：<br>將「木塊 ＋ 斜面體」視為單一整體系統：<br>因系統在水平方向沒有任何加速度（木塊靜止或等速，斜面體靜止），根據牛頓第二運動定律：$$\\Sigma F_{x,\\text{外}} = M_{\\text{總}} \\cdot a_{x,\\text{cm}} = 0 \\implies \\mathbf{f_{\\text{地}} = 0}$$故兩情境中，地面給予斜面體的摩擦力皆為 <strong>$0$</strong>！'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 10: 均勻梯子靠光滑垂直牆面平衡
    # ========================================================
    problems[9]['answer'] = '(a) N牆 = ½W tanθ ； (b) R地 = W√(1 + ¼tan²θ) ； (c) μs ≥ ½ tanθ'

    p10_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Smooth Vertical Wall on Left: x = 80 -->
  <line x1="80" y1="30" x2="80" y2="280" stroke="#64748b" stroke-width="4"/>
  <g opacity="0.3" stroke="#64748b" stroke-width="1.5">
    <line x1="80" y1="40" x2="68" y2="50"/><line x1="80" y1="80" x2="68" y2="90"/>
    <line x1="80" y1="120" x2="68" y2="130"/><line x1="80" y1="160" x2="68" y2="170"/>
    <line x1="80" y1="200" x2="68" y2="210"/><line x1="80" y1="240" x2="68" y2="250"/>
  </g>
  <text x="45" y="100" fill="#64748b" font-size="12" font-weight="bold">光滑牆面</text>

  <!-- Rough Ground: y = 260 -->
  <line x1="60" y1="260" x2="440" y2="260" stroke="#64748b" stroke-width="3"/>
  <text x="320" y="285" fill="#64748b" font-size="12" font-weight="bold">粗糙地面 (μs)</text>

  <!-- Ladder: from A(80, 70) to O(260, 260) -->
  <line x1="80" y1="70" x2="260" y2="260" stroke="#facc15" stroke-width="7" stroke-linecap="round"/>
  <!-- Point A -->
  <circle cx="80" cy="70" r="5" fill="#00e5ff"/>
  <text x="60" y="75" fill="#00e5ff" font-size="14" font-weight="bold">A</text>
  <!-- Point O -->
  <circle cx="260" cy="260" r="5" fill="#00e676"/>
  <text x="275" y="265" fill="#00e676" font-size="14" font-weight="bold">O</text>

  <!-- Angle theta with wall at A -->
  <path d="M80,120 A50,50 0 0,0 102,108" fill="none" stroke="#00e5ff" stroke-width="2"/>
  <text x="95" y="132" fill="#00e5ff" font-size="13" font-weight="bold">θ</text>

  <!-- Midpoint Center of Gravity (170, 165) -->
  <circle cx="170" cy="165" r="5" fill="#ff5252"/>
  <line x1="170" y1="165" x2="170" y2="235" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-p9-red)"/>
  <text x="180" y="225" fill="#ff5252" font-size="12" font-weight="bold">重力 W</text>
  <text x="195" y="145" fill="#facc15" font-size="12">長度 L，重心在中點</text>
</svg>'''

    p10_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p10-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p10-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
    <marker id="arr-p10-gold" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
    <marker id="arr-p10-purple" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#c084fc"/>
    </marker>
  </defs>

  <!-- Ladder outline -->
  <line x1="80" y1="70" x2="260" y2="260" stroke="#475569" stroke-width="4"/>

  <!-- Wall force Nw at A: horizontal right -->
  <line x1="80" y1="70" x2="170" y2="70" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p10-cyan)"/>
  <text x="120" y="60" fill="#00e5ff" font-size="12" font-weight="bold">N牆 = ½W tanθ</text>

  <!-- Gravity W at midpoint -->
  <line x1="170" y1="165" x2="170" y2="245" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-p9-red)"/>
  <text x="180" y="225" fill="#ff5252" font-size="12" font-weight="bold">W</text>

  <!-- Ground normal Ng at O: vertical up -->
  <line x1="260" y1="260" x2="260" y2="180" stroke="#00e676" stroke-width="3" marker-end="url(#arr-p10-green)"/>
  <text x="270" y="200" fill="#00e676" font-size="12" font-weight="bold">N地 = W</text>

  <!-- Ground friction f at O: horizontal left -->
  <line x1="260" y1="260" x2="180" y2="260" stroke="#facc15" stroke-width="3" marker-end="url(#arr-p10-gold)"/>
  <text x="195" y="280" fill="#facc15" font-size="12" font-weight="bold">f = N牆</text>

  <!-- Ground total force R_ground: hypotenuse to top-left -->
  <line x1="260" y1="260" x2="180" y2="180" stroke="#c084fc" stroke-width="3" stroke-dasharray="5,3" marker-end="url(#arr-p10-purple)"/>
  <text x="155" y="175" fill="#c084fc" font-size="12" font-weight="bold">R地 = √(N地² + f²)</text>

  <!-- Three concurrent forces intersection C at (170, 70) -->
  <line x1="170" y1="165" x2="170" y2="70" stroke="#ff5252" stroke-width="1.5" stroke-dasharray="3,3"/>
  <circle cx="170" cy="70" r="5" fill="#c084fc"/>
  <text x="180" y="75" fill="#c084fc" font-size="12" font-weight="bold">共點 C (三力交會)</text>
  <line x1="260" y1="260" x2="170" y2="70" stroke="#c084fc" stroke-width="1.5" stroke-dasharray="3,3"/>
</svg>'''

    p10_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (梯子斜靠牆配置)</div>
        ''' + p10_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 受力圖與三力共點分析並列</div>
        ''' + p10_svg_fbd + '''
      </div>
    </div>'''

    problems[9]['diagrams'] = [
        { 'label': '📐 原始題圖 (梯子斜靠牆面)', 'svg': p10_svg_raw },
        { 'label': '💡 力矩平衡與三力共點推演', 'svg': p10_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': p10_svg_dual }
    ]
    problems[9]['svg'] = p10_svg_raw
    problems[9]['related'] = [
        { 'id': 'torque5', 'title': '力矩 5：均質梯子人攀爬臨界', 'badge': '攀爬力矩' },
        { 'id': 'frict5', 'title': '摩擦 5：雙接觸面摩擦力之斜置桿', 'badge': '雙面摩擦' },
        { 'id': 'torque4', 'title': '力矩 4：懸臂樑固定端力矩', 'badge': '支點力矩' }
    ]
    problems[9]['solutions'] = [
        {
            'title': '【重點解析・轉軸力矩與三力共點分析】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>(a) 對梯底 O 點取力矩求牆面正向力 $N_{\\text{牆}}$</strong>：<br>梯子長度為 $L$，與鉛直牆夾角為 $\\theta$。重力作用於中點，力臂為 $\\frac{L}{2}\\sin\\theta$；牆面作用力 $N_{\\text{牆}}$ 垂直牆面（水平向右），力臂為 $L\\cos\\theta$：$$\\Sigma \\tau_O = 0 \\implies W \\cdot \\left(\\frac{L}{2}\\sin\\theta\\right) = N_{\\text{牆}} \\cdot (L\\cos\\theta) \\implies \\mathbf{N_{\\text{牆}} = \\frac{1}{2}W \\tan\\theta}$$',
                '📌 <strong>(b) 水平與鉛直平衡求地面總作用力 $R_{\\text{地}}$</strong>：<br>水平合力為零：$$f = N_{\\text{牆}} = \\frac{1}{2}W \\tan\\theta$$鉛直合力為零：$$N_{\\text{地}} = W$$地面對梯子之作用力為法向正向力與摩擦力之向量和：$$\\mathbf{R_{\\text{地}} = \\sqrt{N_{\\text{地}}^2 + f^2} = \\sqrt{W^2 + \\left(\\frac{1}{2}W\\tan\\theta\\right)^2} = W\\sqrt{1 + \\frac{1}{4}\\tan^2\\theta}}$$',
                '⚡ <strong>(c) 梯子不致滑倒之靜摩擦係數 $\\mu_s$ 臨界條件</strong>：<br>地面靜摩擦力不可超過最大靜摩擦力：$$f \\le f_{s,\\max} = \\mu_s N_{\\text{地}} \\implies \\frac{1}{2}W\\tan\\theta \\le \\mu_s W \\implies \\mathbf{\\mu_s \\ge \\frac{1}{2}\\tan\\theta}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 11: 水平推力下木箱滑動與傾倒臨界
    # ========================================================
    problems[10]['answer'] = '(1) h = 2 m ； (2) h_max = 2.5 m ； (3) τ_N = 0.8 kgw·m (順時針)，距 O 點 0.4 m'

    p11_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ground -->
  <line x1="60" y1="260" x2="460" y2="260" stroke="#64748b" stroke-width="4"/>
  <rect x="60" y="260" width="400" height="8" fill="#1e293b"/>

  <!-- Box: width = 120px (2m), height = 180px (4m). Corner O at (160, 260) -->
  <rect x="160" y="80" width="120" height="180" rx="3" fill="#0f172a" stroke="#00e5ff" stroke-width="3"/>
  <circle cx="160" cy="260" r="6" fill="#facc15"/>
  <text x="140" y="278" fill="#facc15" font-size="14" font-weight="bold">O 軸</text>

  <!-- Dimensions labels -->
  <line x1="160" y1="65" x2="280" y2="65" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="220" y="58" fill="#94a3b8" font-size="12" font-weight="bold" text-anchor="middle">寬 2 m</text>
  <line x1="140" y1="80" x2="140" y2="260" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="120" y="175" fill="#94a3b8" font-size="12" font-weight="bold" text-anchor="middle">高 4 m</text>

  <!-- Center of mass at (220, 170) -->
  <circle cx="220" cy="170" r="5" fill="#ff5252"/>
  <line x1="220" y1="170" x2="220" y2="245" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-p9-red)"/>
  <text x="230" y="225" fill="#ff5252" font-size="12" font-weight="bold">W = 2 kgw</text>

  <!-- Push force F at P (x = 280, height h = 150 -> y = 260 - 100 = 160) -->
  <circle cx="280" cy="160" r="4.5" fill="#00e676"/>
  <line x1="360" y1="160" x2="285" y2="160" stroke="#00e676" stroke-width="3.5" marker-end="url(#arr-p10-green)"/>
  <text x="365" y="165" fill="#00e676" font-size="13" font-weight="bold">推力 F (向左)</text>

  <!-- Height h indicator -->
  <line x1="300" y1="160" x2="300" y2="260" stroke="#00e676" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="315" y="215" fill="#00e676" font-size="12" font-weight="bold">高度 h</text>
</svg>'''

    p11_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Box Base: x = 120 to 320 (width = 200px = 2m) -->
  <line x1="80" y1="240" x2="420" y2="240" stroke="#64748b" stroke-width="3"/>
  <rect x="140" y="100" width="180" height="140" rx="4" fill="#0f172a" stroke="#00e5ff" stroke-width="2"/>

  <!-- Pivot Corner O at (140, 240) -->
  <circle cx="140" cy="240" r="6" fill="#facc15"/>
  <text x="120" y="260" fill="#facc15" font-size="13" font-weight="bold">O 轉軸</text>

  <!-- Center of mass at x = 230 (1m from O) -->
  <circle cx="230" cy="170" r="5" fill="#ff5252"/>
  <line x1="230" y1="170" x2="230" y2="230" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-p9-red)"/>
  <text x="240" y="215" fill="#ff5252" font-size="12" font-weight="bold">W = 2 kgw</text>
  <line x1="140" y1="130" x2="230" y2="130" stroke="#ff5252" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="185" y="125" fill="#ff5252" font-size="11" text-anchor="middle">抗傾倒力臂 = 1 m</text>

  <!-- Shifted Normal force N acting at distance d from O -->
  <circle cx="176" cy="240" r="5" fill="#00e5ff"/>
  <line x1="176" y1="285" x2="176" y2="245" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p10-cyan)"/>
  <text x="185" y="275" fill="#00e5ff" font-size="12" font-weight="bold">N = 2 kgw</text>

  <!-- Distance d -->
  <line x1="140" y1="255" x2="176" y2="255" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="158" y="270" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="middle">d = 0.4m</text>

  <!-- Tilting condition card -->
  <rect x="330" y="70" width="195" height="170" rx="8" fill="#1e293b" stroke="#facc15" stroke-width="1.5"/>
  <text x="345" y="95" fill="#facc15" font-size="12" font-weight="bold">⚡ 臨界與偏心判斷：</text>
  <text x="345" y="120" fill="#f1f5f9" font-size="11">① 恰滑動：F = fs,max = 1</text>
  <text x="345" y="140" fill="#f1f5f9" font-size="11">　恰傾倒：F·h = W·1 ⟹ h=2</text>
  <text x="345" y="168" fill="#f1f5f9" font-size="11">② 等速下滑：F = fk = 0.8</text>
  <text x="345" y="188" fill="#f1f5f9" font-size="11">　不傾倒：0.8·h ≤ 2 ⟹ h ≤ 2.5</text>
  <text x="345" y="215" fill="#f1f5f9" font-size="11">③ h=1.5, F=0.8 ⟹ d=0.4m</text>
</svg>'''

    p11_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (木箱尺寸與推力配置)</div>
        ''' + p11_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 正向力作用點偏心與力矩分析並列</div>
        ''' + p11_svg_fbd + '''
      </div>
    </div>'''

    problems[10]['diagrams'] = [
        { 'label': '📐 原始題圖 (木箱尺寸與推力配置)', 'svg': p11_svg_raw },
        { 'label': '💡 轉動臨界與正向力等效作用點偏心', 'svg': p11_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': p11_svg_dual }
    ]
    problems[10]['svg'] = p11_svg_raw
    problems[10]['related'] = [
        { 'id': 'torque1', 'title': '力矩 1：起重機抗翻覆臨界', 'badge': '翻覆臨界' },
        { 'id': 'torque6', 'title': '力矩 6：長方體翻倒與滑動雙臨界', 'badge': '雙臨界' },
        { 'id': 'frict3', 'title': '摩擦 3：物體受傾斜推力臨界滑動', 'badge': '滑動分析' }
    ]
    problems[10]['solutions'] = [
        {
            'title': '【重點解析・滑動與傾倒雙臨界及正向力偏心】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>(1) 恰滑動同時亦恰傾倒（雙臨界共存）</strong>：<br>① 恰開始滑動時，水平推力恰達最大靜摩擦力：$$F = f_{s,\\max} = \\mu_s N = 0.5 \\times 2 = \\mathbf{1.0\\text{ kgw}}$$② 恰開始以 O 點為軸發生傾倒時，地面正向力全部集中在底角 O 點，正向力對 O 點力矩為零。對 O 點取力矩：$$\\Sigma \\tau_O = 0 \\implies F \\cdot h = W \\cdot \\left(\\frac{\\text{寬}}{2}\\right) \\implies 1.0 \\cdot h = 2 \\times 1 \\implies \\mathbf{h = 2.0\\text{ m}}$$',
                '📌 <strong>(2) 維持等速向左移動且不傾倒之推力最大高度 $h_{\\max}$</strong>：<br>等速移動時木箱處於動摩擦狀態，推力大小：$$F = f_k = \\mu_k N = 0.4 \\times 2 = \\mathbf{0.8\\text{ kgw}}$$欲使木箱不傾倒，順時針傾倒力矩不得超過逆時針重力矩：$$F \\cdot h_{\\max} \\le W \\cdot 1 \\implies 0.8 \\cdot h_{\\max} \\le 2.0 \\implies h_{\\max} = \\frac{2.0}{0.8} = \\mathbf{2.5\\text{ m}}$$',
                '⚡ <strong>(3) $h = 1.5\\text{ m}, F = 0.8\\text{ kgw}$ 時正向力力矩與作用點位置</strong>：<br>因 $F = 0.8\\text{ kgw} < f_{s,\\max} = 1.0\\text{ kgw}$，木箱保持靜止平衡。<br>對 O 點取力矩（設正向力對 O 軸之力矩為 $\\tau_N$，逆時針重力矩為 $\\tau_W$，順時針推力矩為 $\\tau_F$）：$$\\Sigma \\tau_O = 0 \\implies \\tau_W - \\tau_F - \\tau_N = 0$$$$\\tau_N = \\tau_W - \\tau_F = (2.0 \\times 1.0) - (0.8 \\times 1.5) = 2.0 - 1.2 = \\mathbf{0.8\\text{ kgw}\\cdot\\text{m}} \\quad (\\text{順時針})$$若將正向力視為集中在單一位置（離 O 點距離為 $d$），因 $N = W = 2.0\\text{ kgw}$：$$\\tau_N = N \\cdot d \\implies 2.0 \\cdot d = 0.8 \\implies \\mathbf{d = 0.4\\text{ m}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 12 (Index 11): 自主測驗 37°-53° 經典懸吊題 (q-104)
    # ========================================================
    problems[11]['answer'] = '彈簧彈力 Fs = 5.0 kgw ； 長繩張力 T1 = 9.0 kgw ； 短繩張力 T2 = 12.0 kgw'

    p104_svg_raw = '''<svg viewBox="0 0 600 380" style="max-width: 520px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ceiling -->
  <line x1="60" y1="50" x2="540" y2="50" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
  <g opacity="0.3" stroke="#64748b" stroke-width="1.5">
    <line x1="80" y1="50" x2="95" y2="36"/><line x1="130" y1="50" x2="145" y2="36"/>
    <line x1="180" y1="50" x2="195" y2="36"/><line x1="230" y1="50" x2="245" y2="36"/>
    <line x1="280" y1="50" x2="295" y2="36"/><line x1="330" y1="50" x2="345" y2="36"/>
    <line x1="380" y1="50" x2="395" y2="36"/><line x1="430" y1="50" x2="445" y2="36"/>
    <line x1="480" y1="50" x2="495" y2="36"/><line x1="520" y1="50" x2="535" y2="36"/>
  </g>

  <!-- Left Rope (Longer: 5.0 cm, angle 37° to ceiling) -->
  <!-- Knot at (300, 200). dy = 150 (represents 3.0 cm). dx = 150 / tan(37°) = 200. Left at (100, 50) -->
  <line x1="100" y1="50" x2="300" y2="200" stroke="#00e5ff" stroke-width="3.5"/>
  <text x="145" y="145" fill="#00e5ff" font-size="12" font-weight="bold">長繩 L₁ = 5.0 cm (T₁)</text>
  <!-- 37° arc -->
  <path d="M145,50 A45,45 0 0,1 138,77" fill="none" stroke="#00e5ff" stroke-width="1.8"/>
  <text x="152" y="75" fill="#00e5ff" font-size="12" font-weight="bold">37°</text>

  <!-- Right Rope (Shorter, angle 53° to ceiling) -->
  <!-- dx = 150 / tan(53°) = 112.5. Right at (412.5, 50) -->
  <line x1="412.5" y1="50" x2="300" y2="200" stroke="#facc15" stroke-width="3.5"/>
  <text x="365" y="145" fill="#facc15" font-size="12" font-weight="bold">短繩 (T₂)</text>
  <!-- 53° arc -->
  <path d="M380,50 A32,32 0 0,0 392,75" fill="none" stroke="#facc15" stroke-width="1.8"/>
  <text x="395" y="72" fill="#facc15" font-size="12" font-weight="bold">53°</text>

  <!-- Vertical Spring: from (300, 50) to (300, 200) -->
  <path d="M300,50 L300,65 L312,75 L288,85 L312,95 L288,105 L312,115 L288,125 L312,135 L288,145 L312,155 L288,165 L312,175 L300,185 L300,200" fill="none" stroke="#00e676" stroke-linecap="round" stroke-linejoin="round" stroke-width="3"/>
  <text x="325" y="115" fill="#00e676" font-size="12" font-weight="bold">彈簧 L₀ = 2.0 cm</text>
  <text x="325" y="132" fill="#94a3b8" font-size="10.5">k = 500 kgw/m</text>

  <!-- Knot -->
  <circle cx="300" cy="200" r="6" fill="#fff"/>
  <text x="255" y="205" fill="#fff" font-size="12" font-weight="bold">節點</text>

  <!-- Hanging mass W = 20 kgw -->
  <line x1="300" y1="200" x2="300" y2="280" stroke="#ff5252" stroke-width="3"/>
  <rect x="270" y="280" width="60" height="45" rx="5" fill="#1e293b" stroke="#ff5252" stroke-width="2.5"/>
  <text x="300" y="308" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">20 kgw</text>
</svg>'''

    p104_svg_fbd = '''<svg viewBox="0 0 620 340" style="max-width: 540px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-p104-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-p104-gold" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
    <marker id="arr-p104-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
    <marker id="arr-p104-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>

  <!-- Left: Geometry & Spring Force -->
  <g transform="translate(25, 20)">
    <rect x="0" y="0" width="270" height="295" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e676" stroke-width="1.5"/>
    <text x="15" y="28" fill="#00e676" font-size="13" font-weight="bold">① 幾何分析與彈簧伸長量：</text>

    <!-- Knot depth triangle -->
    <polygon points="40,60 180,60 180,165" fill="none" stroke="#64748b" stroke-width="1.5"/>
    <line x1="40" y1="60" x2="180" y2="165" stroke="#00e5ff" stroke-width="2.5"/>
    <text x="95" y="105" fill="#00e5ff" font-size="11" font-weight="bold">L₁ = 5.0 cm</text>
    <text x="55" y="75" fill="#00e5ff" font-size="11">37°</text>

    <!-- Vertical depth h -->
    <text x="188" y="120" fill="#facc15" font-size="11" font-weight="bold">h = 5·sin37°</text>
    <text x="188" y="136" fill="#facc15" font-size="11" font-weight="bold">= 3.0 cm</text>

    <!-- Spring calculation text -->
    <rect x="15" y="180" width="240" height="100" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
    <text x="25" y="202" fill="#38bdf8" font-size="11" font-weight="bold">彈簧現長 ℓ = h = 3.0 cm</text>
    <text x="25" y="222" fill="#f1f5f9" font-size="11">原長 ℓ₀ = 2.0 cm ⟹ 伸長 Δx = 1.0 cm</text>
    <text x="25" y="242" fill="#00e676" font-size="12" font-weight="bold">Fs = 500 kgw/m × 0.01 m = 5 kgw</text>
    <text x="25" y="264" fill="#ff5252" font-size="11" font-weight="bold">等效向下合力 W等效 = 20 - 5 = 15 kgw</text>
  </g>

  <!-- Right: 3-4-5 Vector Closed Right Triangle -->
  <g transform="translate(320, 20)">
    <rect x="0" y="0" width="280" height="295" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e5ff" stroke-width="1.5"/>
    <text x="15" y="28" fill="#00e5ff" font-size="13" font-weight="bold">② 兩繩垂直 3:4:5 向量直角三角形：</text>

    <!-- Vector triangle: Vertical 15 down, T2 along 53°, T1 along 37° closing -->
    <!-- Node O at (60, 220) -->
    <!-- Downward net 15 kgw -->
    <line x1="60" y1="60" x2="60" y2="240" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-p104-red)"/>
    <text x="15" y="155" fill="#ff5252" font-size="13" font-weight="bold">15 kgw</text>

    <!-- T2 (up-right along 53° to horizontal -> angle 37° to vertical): length = 180 * 0.8 = 144 -->
    <!-- dx = 144 * 0.6 = 86.4, dy = 144 * 0.8 = 115.2. from (60, 240) to (146.4, 124.8) -->
    <line x1="60" y1="240" x2="168" y2="96" stroke="#facc15" stroke-width="3" marker-end="url(#arr-p104-gold)"/>
    <text x="125" y="185" fill="#facc15" font-size="12" font-weight="bold">T₂ = 12 kgw</text>

    <!-- T1 (up-left closing to (60, 60)): from (168, 96) to (60, 60) -->
    <line x1="168" y1="96" x2="60" y2="60" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-p104-cyan)"/>
    <text x="120" y="70" fill="#00e5ff" font-size="12" font-weight="bold">T₁ = 9 kgw</text>

    <!-- Right-angle indicator at (168, 96) -->
    <polyline points="155,92 159,103 170,99" fill="none" stroke="#fff" stroke-width="1.5"/>

    <rect x="15" y="245" width="250" height="40" rx="5" fill="#1e293b" stroke="#facc15" stroke-width="1"/>
    <text x="140" y="270" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">T₁ : T₂ : W等效 = 3 : 4 : 5 (秒殺)</text>
  </g>
</svg>'''

    p104_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (懸掛幾何配置)</div>
        ''' + p104_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 深度幾何與向量直角三角形並列</div>
        ''' + p104_svg_fbd + '''
      </div>
    </div>'''

    problems[11]['diagrams'] = [
        { 'label': '📐 原始題圖 (懸吊情境)', 'svg': p104_svg_raw },
        { 'label': '💡 幾何深度與向量直角三角形', 'svg': p104_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': p104_svg_dual }
    ]
    problems[11]['svg'] = p104_svg_raw
    problems[11]['related'] = [
        { 'id': 'problem4', 'title': '範例 4：細繩與鉛直彈簧懸吊', 'badge': '彈簧懸吊' },
        { 'id': 'problem3', 'title': '範例 3：三細線拉銅環向量平衡', 'badge': '直角三角形' },
        { 'id': 'exercise1', 'title': '類題 1：懸掛彈簧與重錘壓木板', 'badge': '虎克定律' }
    ]
    problems[11]['solutions'] = [
        {
            'title': '【重點解析・幾何深度與 3:4:5 向量三角形速解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・幾何分析求鉛直深度與彈簧伸長量</strong>：<br>兩繩與天花板夾角分別為 $37^\\circ$ 與 $53^\\circ$。由對邊鉛直深度相同：$$h = L_1 \\sin 37^\\circ = L_2 \\sin 53^\\circ$$因 $\\sin 37^\\circ < \\sin 53^\\circ$，較長之細繩夾角必為 $37^\\circ$（$L_1 = 5.0\\text{ cm}$）：$$h = 5.0 \\times 0.6 = \\mathbf{3.0\\text{ cm}}$$彈簧鉛直懸掛，故彈簧現長 $\\ell = h = 3.0\\text{ cm}$，伸長量：$$\\Delta x = \\ell - \\ell_0 = 3.0 - 2.0 = 1.0\\text{ cm} = \\mathbf{0.01\\text{ m}}$$',
                '📌 <strong>重點二・彈簧彈力與兩繩等效向下合力</strong>：<br>彈力常數 $k = 500\\text{ kgw/m}$，彈簧向上拉力：$$F_s = k \\cdot \\Delta x = 500 \\times 0.01 = \\mathbf{5.0\\text{ kgw}}$$節點下方懸掛 $W = 20\\text{ kgw}$，故兩細繩須承擔之等效鉛直向下合力：$$W_{\\text{等效}} = W - F_s = 20 - 5.0 = \\mathbf{15.0\\text{ kgw}}$$',
                '⚡ <strong>重點三・3:4:5 向量直角三角形秒殺繩張力</strong>：<br>兩繩夾角為 $180^\\circ - 37^\\circ - 53^\\circ = 90^\\circ$（相互垂直）！<br>兩繩張力與等效合力構成經典 $3 : 4 : 5$ 直角三角形：$$T_1 = W_{\\text{等效}} \\cos 53^\\circ = 15.0 \\times 0.6 = \\mathbf{9.0\\text{ kgw}}$$$$T_2 = W_{\\text{等效}} \\cos 37^\\circ = 15.0 \\times 0.8 = \\mathbf{12.0\\text{ kgw}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 13 (Index 12): 類題 1 懸掛彈簧與重錘壓木板作用力 (q-12)
    # ========================================================
    problems[12]['answer'] = '(C) 2 kgw'

    ex1_svg_raw = '''<svg viewBox="0 0 520 320" style="max-width: 480px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ceiling -->
  <rect x="100" y="30" width="220" height="12" fill="#1e293b" stroke="#64748b" stroke-width="1.5"/>
  <g opacity="0.4" stroke="#64748b" stroke-width="1.5">
    <line x1="120" y1="30" x2="110" y2="18"/><line x1="160" y1="30" x2="150" y2="18"/>
    <line x1="200" y1="30" x2="190" y2="18"/><line x1="240" y1="30" x2="230" y2="18"/>
    <line x1="280" y1="30" x2="270" y2="18"/>
  </g>

  <!-- Spring from y=42 to y=162 (length 30cm) -->
  <path d="M 210,42 L 210,55 L 225,62 L 195,74 L 225,86 L 195,98 L 225,110 L 195,122 L 225,134 L 195,146 L 210,154 L 210,162" fill="none" stroke="#00e5ff" stroke-linecap="round" stroke-linejoin="round" stroke-width="3"/>

  <!-- Bob: 3 kgw at (180, 162) -->
  <rect x="180" y="162" width="60" height="48" rx="4" fill="#0f172a" stroke="#ff5252" stroke-width="2.5"/>
  <text x="210" y="192" fill="#ff5252" font-size="14" font-weight="bold" text-anchor="middle">3 kgw</text>

  <!-- Wooden Board at y=210 -->
  <rect x="80" y="210" width="260" height="20" rx="3" fill="#854d0e" stroke="#facc15" stroke-width="2"/>
  <text x="210" y="225" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">水平木板</text>

  <!-- Annotations -->
  <line x1="265" y1="42" x2="265" y2="162" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="275" y="95" fill="#94a3b8" font-size="12" font-weight="bold">現長 30 cm</text>
  <text x="275" y="112" fill="#64748b" font-size="11">(原長 20 cm)</text>
</svg>'''

    ex1_svg_fbd = '''<svg viewBox="0 0 520 320" style="max-width: 480px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-ex1-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-ex1-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
    <marker id="arr-ex1-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>

  <!-- Bob Box in Center -->
  <rect x="180" y="110" width="80" height="60" rx="6" fill="#1e293b" stroke="#f1f5f9" stroke-width="2"/>
  <text x="220" y="145" fill="#f1f5f9" font-size="13" font-weight="bold" text-anchor="middle">重錘 (3 kgw)</text>

  <!-- Force 1: Gravity W straight down -->
  <line x1="220" y1="170" x2="220" y2="260" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-ex1-red)"/>
  <text x="230" y="250" fill="#ff5252" font-size="12" font-weight="bold">重力 W = 3 kgw (下)</text>

  <!-- Force 2: Spring tension F_spring straight up -->
  <line x1="200" y1="110" x2="200" y2="35" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-ex1-cyan)"/>
  <text x="95" y="55" fill="#00e5ff" font-size="12" font-weight="bold">彈簧拉力 Fs = 1 kgw</text>

  <!-- Force 3: Board normal force N straight up -->
  <line x1="240" y1="110" x2="240" y2="45" stroke="#00e676" stroke-width="3" marker-end="url(#arr-ex1-green)"/>
  <text x="250" y="65" fill="#00e676" font-size="12" font-weight="bold">木板支持力 N = 2 kgw</text>

  <!-- Equilibrium equation box -->
  <rect x="60" y="235" width="400" height="55" rx="6" fill="#0f172a" stroke="#00e676" stroke-width="1.5"/>
  <text x="260" y="258" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">鉛直靜力平衡：ΣFy = Fs + N - W = 0</text>
  <text x="260" y="278" fill="#f1f5f9" font-size="12" text-anchor="middle">N = W - Fs = 3 - 1 = 2 kgw ➔ 重錘壓木板力 = 2 kgw (選 C)</text>
</svg>'''

    ex1_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (懸掛重錘裝置)</div>
        ''' + ex1_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 重錘鉛直受力平衡 (FBD)</div>
        ''' + ex1_svg_fbd + '''
      </div>
    </div>'''

    problems[12]['diagrams'] = [
        { 'label': '📐 原始題圖 (實驗裝置)', 'svg': ex1_svg_raw },
        { 'label': '💡 重錘受力隔離體圖 (FBD)', 'svg': ex1_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex1_svg_dual }
    ]
    problems[12]['svg'] = ex1_svg_raw
    problems[12]['related'] = [
        { 'id': 'problem1', 'title': '範例 1：彈簧伸長量與外力', 'badge': '虎克定律' },
        { 'id': 'practice', 'title': '自主測驗：37°-53° 經典懸吊題', 'badge': '彈簧吊重' },
        { 'id': 'exercise2', 'title': '類題 2：雙彈簧水平並聯推移', 'badge': '彈力平衡' }
    ]
    problems[12]['solutions'] = [
        {
            'title': '【重點解析・彈簧伸長量與正向力平衡】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・彈簧伸長量與彈簧拉力</strong>：<br>彈簧原長 $\\ell_0 = 20\\text{ cm}$，平衡時長度 $\\ell = 30\\text{ cm}$，伸長量為：$$\\Delta x = 30 - 20 = 10\\text{ cm} = \\mathbf{0.1\\text{ m}}$$彈力常數 $k = 10\\text{ kgw/m}$，彈簧向上拉力：$$F_s = k \\cdot \\Delta x = 10 \\times 0.1 = \\mathbf{1.0\\text{ kgw}}$$',
                '📌 <strong>重點二・重錘受力平衡求木板支持力</strong>：<br>重錘受到三力作用：向下重力 $W = 3\\text{ kgw}$、向上彈簧拉力 $F_s = 1\\text{ kgw}$、向上木板正向支持力 $N$。<br>由鉛直平衡條件 $\\Sigma F_y = 0$：$$F_s + N = W \\implies 1.0 + N = 3.0 \\implies \\mathbf{N = 2.0\\text{ kgw}}$$',
                '⚡ <strong>重點三・作用力與反作用力定律</strong>：<br>根據牛頓第三運動定律，重錘作用於木板之壓力與木板對重錘之支持力等大反向：$$N_{\\text{壓}} = N = \\mathbf{2\\text{ kgw}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 14 (Index 13): 類題 2 雙彈簧水平並聯推移所需外力 (q-13)
    # ========================================================
    problems[13]['answer'] = '(D) 18 kgw'

    ex2_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Left Wall -->
  <line x1="40" y1="40" x2="40" y2="220" stroke="#64748b" stroke-width="5"/>
  <!-- Right Wall -->
  <line x1="480" y1="40" x2="480" y2="220" stroke="#64748b" stroke-width="5"/>
  <!-- Smooth Ground -->
  <line x1="30" y1="200" x2="490" y2="200" stroke="#64748b" stroke-width="3"/>

  <!-- Shifted Right by 3cm: Center at x=280 (shifted from 240) -->
  <!-- Spring 1 (stretched): from 40 to 240, width=200 -->
  <path d="M 40,150 L 60,150 L 75,138 L 95,162 L 115,138 L 135,162 L 155,138 L 175,162 L 195,138 L 215,162 L 230,150 L 240,150" fill="none" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="140" y="125" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">彈簧 1 (k₁=2, 拉伸 3cm)</text>

  <!-- Mass at (240 to 300) -->
  <rect x="240" y="120" width="60" height="60" rx="8" fill="#1e293b" stroke="#f1f5f9" stroke-width="2.5"/>
  <text x="270" y="155" fill="#f1f5f9" font-size="14" font-weight="bold" text-anchor="middle">m</text>

  <!-- Spring 2 (compressed): from 300 to 480, width=180 -->
  <path d="M 300,150 L 315,150 L 330,138 L 345,162 L 360,138 L 375,162 L 390,138 L 405,162 L 420,138 L 435,162 L 450,138 L 465,150 L 480,150" fill="none" stroke="#facc15" stroke-width="2.5"/>
  <text x="390" y="125" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">彈簧 2 (k₂=4, 壓縮 3cm)</text>

  <!-- Applied Force F pointing right -->
  <line x1="300" y1="150" x2="380" y2="150" stroke="#00e676" stroke-width="3.5" marker-end="url(#arr-ex1-green)"/>
  <text x="335" y="175" fill="#00e676" font-size="13" font-weight="bold">外力 F</text>
  <text x="270" y="240" fill="#94a3b8" font-size="12" text-anchor="middle">向右平移 Δx = 3 cm 保持靜止</text>
</svg>'''

    ex2_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-ex2-left" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-ex2-gold" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
  </defs>

  <!-- Center Mass Box -->
  <rect x="220" y="90" width="80" height="70" rx="8" fill="#1e293b" stroke="#f1f5f9" stroke-width="2.5"/>
  <text x="260" y="130" fill="#f1f5f9" font-size="14" font-weight="bold" text-anchor="middle">物體</text>

  <!-- Spring 1 pull to left: F1 = 6 kgw -->
  <line x1="220" y1="110" x2="110" y2="110" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-ex2-left)"/>
  <text x="160" y="95" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">F₁ = k₁Δx = 6 kgw</text>

  <!-- Spring 2 push to left: F2 = 12 kgw -->
  <line x1="220" y1="140" x2="70" y2="140" stroke="#facc15" stroke-width="3" marker-end="url(#arr-ex2-gold)"/>
  <text x="140" y="160" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">F₂ = k₂Δx = 12 kgw</text>

  <!-- External force F to right -->
  <line x1="300" y1="125" x2="440" y2="125" stroke="#00e676" stroke-width="3.5" marker-end="url(#arr-ex1-green)"/>
  <text x="370" y="115" fill="#00e676" font-size="13" font-weight="bold">外力 F = 18 kgw</text>

  <!-- Parallel equivalence formula -->
  <rect x="50" y="190" width="440" height="65" rx="6" fill="#0f172a" stroke="#00e676" stroke-width="1.5"/>
  <text x="270" y="215" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">💡 等效並聯彈簧模型：兩彈簧恢復力方向皆向左！</text>
  <text x="270" y="238" fill="#f1f5f9" font-size="12" text-anchor="middle">F = F₁ + F₂ = (k₁ + k₂) Δx = (2 + 4) × 3 = 18 kgw ➔ 選 (D)</text>
</svg>'''

    ex2_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (雙彈簧水平裝置)</div>
        ''' + ex2_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 水平受力隔離體圖 (FBD)</div>
        ''' + ex2_svg_fbd + '''
      </div>
    </div>'''

    problems[13]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙彈簧配置)', 'svg': ex2_svg_raw },
        { 'label': '💡 水平受力隔離體圖 (FBD)', 'svg': ex2_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex2_svg_dual }
    ]
    problems[13]['svg'] = ex2_svg_raw
    problems[13]['related'] = [
        { 'id': 'exercise1', 'title': '類題 1：懸掛彈簧與重錘壓木板', 'badge': '單彈簧' },
        { 'id': 'exercise3', 'title': '類題 3：三彈簧兩物體連繫淨力', 'badge': '多彈簧' },
        { 'id': 'problem1', 'title': '範例 1：彈簧並聯等效力常數', 'badge': '並聯公式' }
    ]
    problems[13]['solutions'] = [
        {
            'title': '【重點解析・雙彈簧等效並聯與水平平衡】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・兩彈簧之形變與恢復力方向</strong>：<br>物體向右平移 $\\Delta x = 3\\text{ cm}$：<br>① 左側彈簧被拉長 $3\\text{ cm}$，產生向左的拉力：$$F_1 = k_1 \\Delta x = 2 \\times 3 = \\mathbf{6\\text{ kgw}} \\quad (\\text{向左})$$② 右側彈簧被壓縮 $3\\text{ cm}$，產生向左的推力：$$F_2 = k_2 \\Delta x = 4 \\times 3 = \\mathbf{12\\text{ kgw}} \\quad (\\text{向左})$$',
                '📐 <strong>重點二・等效並聯彈簧概念</strong>：<br>兩彈簧形變量相同且恢復力方向一致，此系統等效於兩彈簧<strong>並聯</strong>：$$k_{\\text{等效}} = k_1 + k_2 = 2 + 4 = \\mathbf{6\\text{ kgw/cm}}$$',
                '⚡ <strong>重點三・水平靜力平衡求外力</strong>：<br>物體保持靜止，外力 $F$ 與兩彈簧之總恢復力等大反向：$$F = F_1 + F_2 = k_{\\text{等效}} \\cdot \\Delta x = 6 \\times 3 = \\mathbf{18\\text{ kgw}} \\quad \\text{✅ 選 (D)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 15 (Index 14): 類題 3 三彈簧兩物體連繫系統之淨力 (q-14)
    # ========================================================
    problems[14]['answer'] = '(A) -(k₂ + k)x₂ + k x₁'

    ex3_svg_raw = '''<svg viewBox="0 0 560 260" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Left & Right Walls -->
  <line x1="40" y1="40" x2="40" y2="200" stroke="#64748b" stroke-width="5"/>
  <line x1="520" y1="40" x2="520" y2="200" stroke="#64748b" stroke-width="5"/>
  <line x1="30" y1="180" x2="530" y2="180" stroke="#64748b" stroke-width="2.5"/>

  <!-- Spring 1 (k1) -->
  <path d="M 40,130 L 60,130 L 72,118 L 88,142 L 104,118 L 120,142 L 136,118 L 148,130 L 160,130" fill="none" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="100" y="105" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">k₁</text>

  <!-- Mass 1 (m1) -->
  <rect x="160" y="100" width="50" height="55" rx="6" fill="#1e293b" stroke="#00e5ff" stroke-width="2"/>
  <text x="185" y="132" fill="#00e5ff" font-size="13" font-weight="bold" text-anchor="middle">m₁</text>

  <!-- Spring middle (k) -->
  <path d="M 210,130 L 230,130 L 244,118 L 262,142 L 280,118 L 298,142 L 316,118 L 330,130 L 340,130" fill="none" stroke="#facc15" stroke-width="2.5"/>
  <text x="275" y="105" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">k</text>

  <!-- Mass 2 (m2) -->
  <rect x="340" y="100" width="50" height="55" rx="6" fill="#1e293b" stroke="#ff5252" stroke-width="2.5"/>
  <text x="365" y="132" fill="#ff5252" font-size="13" font-weight="bold" text-anchor="middle">m₂</text>

  <!-- Spring 2 (k2) -->
  <path d="M 390,130 L 410,130 L 424,118 L 442,142 L 460,118 L 478,142 L 496,118 L 510,130 L 520,130" fill="none" stroke="#00e676" stroke-width="2.5"/>
  <text x="455" y="105" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">k₂</text>

  <!-- Displacements indicators -->
  <line x1="185" y1="160" x2="215" y2="160" stroke="#00e5ff" stroke-width="2" marker-end="url(#arr-ex1-cyan)"/>
  <text x="200" y="178" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="middle">x₁ (+)</text>

  <line x1="365" y1="160" x2="405" y2="160" stroke="#ff5252" stroke-width="2" marker-end="url(#arr-ex1-red)"/>
  <text x="385" y="178" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">x₂ (+)</text>
</svg>'''

    ex3_svg_fbd = '''<svg viewBox="0 0 560 260" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Isolation of m2 -->
  <rect x="230" y="60" width="100" height="80" rx="8" fill="#1e293b" stroke="#ff5252" stroke-width="2.5"/>
  <text x="280" y="105" fill="#ff5252" font-size="16" font-weight="bold" text-anchor="middle">質點 m₂</text>

  <!-- Force from middle spring k: to left -->
  <line x1="230" y1="85" x2="110" y2="85" stroke="#facc15" stroke-width="3" marker-end="url(#arr-ex2-gold)"/>
  <text x="160" y="75" fill="#facc15" font-size="11.5" font-weight="bold">F_k = -k(x₂ - x₁)</text>

  <!-- Force from right spring k2: to left -->
  <line x1="230" y1="120" x2="70" y2="120" stroke="#00e676" stroke-width="3" marker-end="url(#arr-ex1-green)"/>
  <text x="135" y="140" fill="#00e676" font-size="11.5" font-weight="bold">F_k2 = -k₂ x₂</text>

  <!-- Result Formula Card -->
  <rect x="40" y="165" width="480" height="70" rx="6" fill="#0f172a" stroke="#ff5252" stroke-width="1.5"/>
  <text x="280" y="190" fill="#f1f5f9" font-size="12" text-anchor="middle">m₂ 淨力合力：ΣF = F_k + F_k2 = -k(x₂ - x₁) - k₂ x₂</text>
  <text x="280" y="215" fill="#ff5252" font-size="13" font-weight="bold" text-anchor="middle">= -(k₂ + k)x₂ + k x₁ ➔ 選 (A)</text>
</svg>'''

    ex3_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (三彈簧系統配置)</div>
        ''' + ex3_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 m₂ 受力隔離體圖 (FBD)</div>
        ''' + ex3_svg_fbd + '''
      </div>
    </div>'''

    problems[14]['diagrams'] = [
        { 'label': '📐 原始題圖 (連繫系統)', 'svg': ex3_svg_raw },
        { 'label': '💡 m₂ 受力隔離體圖 (FBD)', 'svg': ex3_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex3_svg_dual }
    ]
    problems[14]['svg'] = ex3_svg_raw
    problems[14]['related'] = [
        { 'id': 'exercise2', 'title': '類題 2：雙彈簧水平並聯推移', 'badge': '彈簧串並' },
        { 'id': 'problem2', 'title': '範例 2：雙彈簧雙重物串聯', 'badge': '質點連繫' },
        { 'id': 'exercise4', 'title': '類題 4：自重均勻彈簧下垂刻度', 'badge': '虎克定律' }
    ]
    problems[14]['solutions'] = [
        {
            'title': '【重點解析・質點隔離受力與彈力方向辨識】（84聯考經典標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・中間彈簧 $k$ 對 $m_2$ 之施力</strong>：<br>中間彈簧左端位移為 $x_1$，右端位移為 $x_2$。<br>中間彈簧的伸長量為 $(x_2 - x_1)$。當 $x_2 > x_1$ 時彈簧被拉長，對右端物體 $m_2$ 產生<strong>向左（負方向）</strong>的拉力：$$F_k = -k(x_2 - x_1)$$',
                '📌 <strong>重點二・右側彈簧 $k_2$ 對 $m_2$ 之施力</strong>：<br>$m_2$ 向右位移 $x_2$，使固定於右牆的彈簧 $k_2$ 壓縮量為 $x_2$。<br>壓縮的彈簧施予 $m_2$ <strong>向左（負方向）</strong>的推力：$$F_{k2} = -k_2 x_2$$',
                '⚡ <strong>重點三・求 $m_2$ 所受淨力（代數相加）</strong>：<br>$$F_{\\text{淨}} = F_k + F_{k2} = -k(x_2 - x_1) - k_2 x_2 = \\mathbf{-(k_2 + k)x_2 + k x_1} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 16 (Index 15): 類題 4 自重均勻彈簧下垂刻度非均勻伸長 (q-15)
    # ========================================================
    problems[15]['answer'] = '(D) 刻度 74 與 76'

    ex4_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 480px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ceiling -->
  <rect x="60" y="20" width="180" height="10" fill="#1e293b" stroke="#64748b" stroke-width="1.5"/>
  <!-- Top fixed point: scale 0 -->
  <circle cx="120" cy="30" r="5" fill="#38bdf8"/>
  <text x="80" y="35" fill="#38bdf8" font-size="12" font-weight="bold">刻度 0</text>

  <!-- Spring gradient coils: sparse at top, dense at bottom -->
  <path d="M 120,30 L 132,44 L 108,58 L 132,72 L 108,86 L 132,100 L 108,114 L 132,128 L 110,140 L 130,150 L 110,160 L 130,170 L 110,180 L 130,190 L 110,200 L 128,208 L 112,216 L 128,224 L 112,232 L 128,240 L 120,250" fill="none" stroke="#f43f5e" stroke-linecap="round" stroke-width="3"/>

  <!-- Bottom free end: scale 100 -->
  <circle cx="120" cy="250" r="5" fill="#38bdf8"/>
  <text x="60" y="255" fill="#38bdf8" font-size="12" font-weight="bold">刻度 100</text>

  <!-- Mark 50-51 -->
  <line x1="100" y1="128" x2="140" y2="128" stroke="#facc15" stroke-width="2"/>
  <text x="148" y="132" fill="#facc15" font-size="11" font-weight="bold">刻度 50~51：間距 = 1.1 cm</text>
  <text x="148" y="148" fill="#94a3b8" font-size="10">(伸長量 = 0.1 cm)</text>

  <!-- Target Mark 74-76 -->
  <line x1="105" y1="200" x2="135" y2="200" stroke="#00e676" stroke-width="2"/>
  <text x="148" y="204" fill="#00e676" font-size="11" font-weight="bold">刻度 74~76：間距 ≈ 2.1 cm</text>
  <text x="148" y="220" fill="#94a3b8" font-size="10">(2格伸長 = 0.1 cm，平均每格 0.05 cm)</text>
</svg>'''

    ex4_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 480px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-ex4-axis" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#94a3b8"/>
    </marker>
  </defs>

  <!-- Axes: y is tension T, x is scale N (0 to 100) -->
  <line x1="60" y1="230" x2="480" y2="230" stroke="#64748b" stroke-width="2" marker-end="url(#arr-ex4-axis)"/>
  <text x="475" y="255" fill="#94a3b8" font-size="12" font-weight="bold">刻度 N</text>

  <line x1="60" y1="230" x2="60" y2="40" stroke="#64748b" stroke-width="2" marker-end="url(#arr-ex4-axis)"/>
  <text x="50" y="30" fill="#94a3b8" font-size="12" font-weight="bold">張力 T(N)</text>

  <!-- Linear Tension Line: from (60, 50) at N=0 to (440, 230) at N=100 -->
  <line x1="60" y1="50" x2="440" y2="230" stroke="#f43f5e" stroke-width="3"/>

  <!-- Point N=50: at x = 60 + 0.5*380 = 250, y = 50 + 0.5*180 = 140 -->
  <circle cx="250" cy="140" r="5" fill="#facc15"/>
  <line x1="250" y1="140" x2="250" y2="230" stroke="#facc15" stroke-width="1.5" stroke-dasharray="2,2"/>
  <text x="250" y="248" fill="#facc15" font-size="11" font-weight="bold" text-anchor="middle">N=50</text>
  <text x="260" y="130" fill="#facc15" font-size="10.5">承載 50 格自重 ➔ 伸長 0.1 cm</text>

  <!-- Point N=75: at x = 60 + 0.75*380 = 345, y = 50 + 0.75*180 = 185 -->
  <circle cx="345" cy="185" r="5" fill="#00e676"/>
  <line x1="345" y1="185" x2="345" y2="230" stroke="#00e676" stroke-width="1.5" stroke-dasharray="2,2"/>
  <text x="345" y="248" fill="#00e676" font-size="11" font-weight="bold" text-anchor="middle">N=75</text>
  <text x="355" y="180" fill="#00e676" font-size="10.5">承載 25 格自重 ➔ 伸長 0.05 cm</text>

  <!-- Conclusion box -->
  <rect x="60" y="260" width="420" height="30" rx="4" fill="#1e293b" stroke="#00e676" stroke-width="1"/>
  <text x="270" y="280" fill="#00e676" font-size="11.5" font-weight="bold" text-anchor="middle">2 格總長 = 2.0 + 2×(0.05) = 2.1 cm ➔ 位於 74 與 76 (選 D)</text>
</svg>'''

    ex4_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (下垂彈簧刻度模型)</div>
        ''' + ex4_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 張力與每格伸長量曲線並列</div>
        ''' + ex4_svg_fbd + '''
      </div>
    </div>'''

    problems[15]['diagrams'] = [
        { 'label': '📐 原始題圖 (下垂彈簧)', 'svg': ex4_svg_raw },
        { 'label': '💡 張力隨刻度線性遞減曲線', 'svg': ex4_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex4_svg_dual }
    ]
    problems[15]['svg'] = ex4_svg_raw
    problems[15]['related'] = [
        { 'id': 'problem1', 'title': '範例 1：彈簧截段力常數', 'badge': '彈簧切割' },
        { 'id': 'exercise1', 'title': '類題 1：懸掛彈簧受力平衡', 'badge': '自重平衡' },
        { 'id': 'exercise5', 'title': '類題 5：雙彈簧串聯吊重與平臺', 'badge': '串聯伸長' }
    ]
    problems[15]['solutions'] = [
        {
            'title': '【重點解析・均勻彈簧自重張力分佈與刻度伸長】（聯考經典秒殺解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・均勻自重彈簧各處張力分佈</strong>：<br>彈簧垂直懸掛時，刻度 $N$ 處所承受的張力等於其<strong>下方剩餘 $(100 - N)$ 格的總重量</strong>：$$T(N) = \\frac{100 - N}{100} W$$張力由頂端（$N=0$，$T=W$）向下線性遞減到底端（$N=100$，$T=0$）。',
                '📌 <strong>重點二・由刻度 50~51 建立比例關係</strong>：<br>每格原長為 $\\ell_0 = 1.0\\text{ cm}$。刻度 $50 \\sim 51$ 承受下方約 $50$ 格重量，測得長度 $1.1\\text{ cm}$，即每格伸長量：$$\\Delta \\ell_{50} = 1.1 - 1.0 = \\mathbf{0.1\\text{ cm}}$$',
                '⚡ <strong>重點三・反推兩刻度距離 2.1 cm 之位置</strong>：<br>題目選項皆為相距 2 格（原長 $2 \\times 1.0 = 2.0\\text{ cm}$）。<br>總長 $2.1\\text{ cm}$ 代表 2 格的總伸長量須為 $2.1 - 2.0 = 0.1\\text{ cm}$，即<strong>平均每格伸長量為 $0.05\\text{ cm}$</strong>。<br>因 $0.05\\text{ cm}$ 恰為 $0.1\\text{ cm}$ 的一半，其承載的自重格數必為 50 格的一半（$25$ 格）：$$100 - N = 25 \\implies N = \\mathbf{75}$$75 恰為刻度 <strong>74 與 76</strong> 之間中央！<br>✅ 選 <strong>(D)</strong>。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 17 (Index 16): 類題 5 雙彈簧串聯吊重與平臺交互作用力 (q-16)
    # ========================================================
    problems[16]['answer'] = 'AB 距離 = 50.0 cm'

    ex5_svg_raw = '''<svg viewBox="0 0 520 360" style="max-width: 480px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ceiling A -->
  <rect x="120" y="25" width="200" height="12" fill="#1e293b" stroke="#64748b" stroke-width="1.5"/>
  <circle cx="220" cy="37" r="5" fill="#38bdf8"/>
  <text x="185" y="32" fill="#38bdf8" font-size="13" font-weight="bold">A 點</text>

  <!-- Spring a (stretched by 7.5cm) -->
  <path d="M 220,37 L 220,50 L 234,60 L 206,74 L 234,88 L 206,102 L 234,116 L 206,130 L 234,144 L 220,152 L 220,160" fill="none" stroke="#00e5ff" stroke-width="2.8"/>
  <text x="245" y="105" fill="#00e5ff" font-size="12" font-weight="bold">彈簧 a (k=2.0)</text>

  <!-- Mass m (10gw) -->
  <circle cx="220" cy="175" r="15" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="220" y="180" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">m</text>
  <text x="245" y="180" fill="#94a3b8" font-size="11">10 gw</text>

  <!-- Spring b (stretched by 2.5cm) -->
  <path d="M 220,190 L 220,200 L 232,208 L 208,218 L 232,228 L 208,238 L 232,248 L 220,254 L 220,260" fill="none" stroke="#facc15" stroke-width="2.8"/>
  <text x="245" y="232" fill="#facc15" font-size="12" font-weight="bold">彈簧 b (k=2.0)</text>

  <!-- Mass n (10gw) -->
  <circle cx="220" cy="275" r="15" fill="#1e293b" stroke="#facc15" stroke-width="2.5"/>
  <text x="220" y="280" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">n</text>
  <text x="245" y="280" fill="#94a3b8" font-size="11">10 gw</text>

  <!-- Platform B -->
  <rect x="100" y="290" width="240" height="18" rx="3" fill="#854d0e" stroke="#00e676" stroke-width="2"/>
  <circle cx="220" cy="290" r="4" fill="#00e676"/>
  <text x="220" y="325" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">平臺 B (支持正向力 N = 5.0 gw)</text>
</svg>'''

    ex5_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-ex5-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-ex5-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e676"/>
    </marker>
    <marker id="arr-ex5-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
  </defs>

  <!-- Card 1: Mass n isolation -->
  <g transform="translate(30, 20)">
    <rect x="0" y="0" width="220" height="190" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#facc15" stroke-width="1.5"/>
    <text x="15" y="24" fill="#facc15" font-size="12" font-weight="bold">① 隔離重物 n：</text>
    <circle cx="110" cy="90" r="16" fill="#1e293b" stroke="#facc15" stroke-width="2"/>
    <text x="110" y="95" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">n</text>
    <!-- Gravity down -->
    <line x1="110" y1="106" x2="110" y2="155" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex5-red)"/>
    <text x="118" y="145" fill="#ff5252" font-size="11">Wn = 10</text>
    <!-- Normal up -->
    <line x1="125" y1="74" x2="125" y2="35" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex5-green)"/>
    <text x="132" y="45" fill="#00e676" font-size="11">N = 5</text>
    <!-- Spring b pull up -->
    <line x1="95" y1="74" x2="95" y2="35" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-ex5-cyan)"/>
    <text x="50" y="45" fill="#facc15" font-size="11">Fb = 5</text>

    <text x="15" y="175" fill="#f1f5f9" font-size="11">Fb = 5 gw ⟹ Δxb = 2.5 cm</text>
  </g>

  <!-- Card 2: System (m+n) or Mass m isolation -->
  <g transform="translate(280, 20)">
    <rect x="0" y="0" width="230" height="190" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e5ff" stroke-width="1.5"/>
    <text x="15" y="24" fill="#00e5ff" font-size="12" font-weight="bold">② 整體法 (m + n)：</text>
    <rect x="80" y="70" width="70" height="40" rx="6" fill="#1e293b" stroke="#00e5ff" stroke-width="2"/>
    <text x="115" y="95" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">m + n</text>
    <!-- Total weight down -->
    <line x1="115" y1="110" x2="115" y2="160" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex5-red)"/>
    <text x="122" y="150" fill="#ff5252" font-size="11">W總 = 20</text>
    <!-- Normal up -->
    <line x1="135" y1="70" x2="135" y2="35" stroke="#00e676" stroke-width="2" marker-end="url(#arr-ex5-green)"/>
    <text x="142" y="45" fill="#00e676" font-size="11">N = 5</text>
    <!-- Spring a pull up -->
    <line x1="95" y1="70" x2="95" y2="35" stroke="#00e5ff" stroke-width="2.5" marker-end="url(#arr-ex5-cyan)"/>
    <text x="50" y="45" fill="#00e5ff" font-size="11">Fa = 15</text>

    <text x="15" y="175" fill="#f1f5f9" font-size="11">Fa = 15 gw ⟹ Δxa = 7.5 cm</text>
  </g>

  <!-- Bottom Result Box -->
  <rect x="30" y="230" width="480" height="65" rx="8" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="270" y="255" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">③ 計算 AB 兩點總距離：</text>
  <text x="270" y="278" fill="#00e676" font-size="14" font-weight="bold" text-anchor="middle">AB = (20 + 7.5) + (20 + 2.5) = 27.5 + 22.5 = 50.0 cm</text>
</svg>'''

    ex5_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (雙彈簧吊重配置)</div>
        ''' + ex5_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 受力平衡與伸長量推導並列</div>
        ''' + ex5_svg_fbd + '''
      </div>
    </div>'''

    problems[16]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙彈簧吊重)', 'svg': ex5_svg_raw },
        { 'label': '💡 受力平衡與伸長量推導', 'svg': ex5_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex5_svg_dual }
    ]
    problems[16]['svg'] = ex5_svg_raw
    problems[16]['related'] = [
        { 'id': 'exercise1', 'title': '類題 1：懸掛彈簧與重錘壓木板', 'badge': '平臺支持力' },
        { 'id': 'problem2', 'title': '範例 2：雙彈簧雙重物串聯', 'badge': '串聯平衡' },
        { 'id': 'exercise4', 'title': '類題 4：自重均勻彈簧下垂伸長', 'badge': '伸長疊加' }
    ]
    problems[16]['solutions'] = [
        {
            'title': '【重點解析・隔離體與整體法聯立求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・隔離重物 n 求彈簧 b 之伸長量</strong>：<br>重物 n 受重力 $W_n = 10.0\\text{ gw}$ 向下、平臺支持力 $N = 5.0\\text{ gw}$ 向上、彈簧 b 拉力 $F_b$ 向上：$$F_b + N = W_n \\implies F_b = 10.0 - 5.0 = \\mathbf{5.0\\text{ gw}}$$$$\\Delta x_b = \\frac{F_b}{k} = \\frac{5.0}{2.0} = \\mathbf{2.5\\text{ cm}}$$',
                '📌 <strong>重點二・整體法求彈簧 a 之伸長量</strong>：<br>將 (m + n) 視為系統，總重 $20\\text{ gw}$，向上受彈簧 a 拉力 $F_a$ 及平臺支持力 $N = 5.0\\text{ gw}$：$$F_a + N = W_{\\text{總}} \\implies F_a = 20.0 - 5.0 = \\mathbf{15.0\\text{ gw}}$$$$\\Delta x_a = \\frac{F_a}{k} = \\frac{15.0}{2.0} = \\mathbf{7.5\\text{ cm}}$$',
                '⚡ <strong>重點三・求 A、B 兩點總距離</strong>：<br>兩彈簧原長均為 $20\\text{ cm}$（重物質點尺寸不計）：$$\\overline{AB} = (\\ell_0 + \\Delta x_a) + (\\ell_0 + \\Delta x_b) = (20 + 7.5) + (20 + 2.5) = 27.5 + 22.5 = \\mathbf{50.0\\text{ cm}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 18 (Index 17): 類題 6 二力反向合力與相互垂直合力 (q-17)
    # ========================================================
    problems[17]['answer'] = 'F1 = 8 kgw ； F2 = 6 kgw'

    ex6_svg_raw = '''<svg viewBox="0 0 540 260" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Case 1: Opposite (180 deg) -->
  <g transform="translate(30, 20)">
    <rect x="0" y="0" width="220" height="210" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="110" y="30" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">【情況一：反向 (180°)】</text>
    <circle cx="110" cy="110" r="5" fill="#fff"/>
    <!-- F1 right -->
    <line x1="110" y1="110" x2="190" y2="110" stroke="#00e5ff" stroke-width="3.5" marker-end="url(#arr-ex1-cyan)"/>
    <text x="155" y="98" fill="#00e5ff" font-size="12" font-weight="bold">F₁ = 8</text>
    <!-- F2 left -->
    <line x1="110" y1="110" x2="50" y2="110" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-ex2-gold)"/>
    <text x="75" y="98" fill="#facc15" font-size="12" font-weight="bold">F₂ = 6</text>
    <!-- Resultant -->
    <rect x="25" y="150" width="170" height="36" rx="5" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
    <text x="110" y="173" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">R = F₁ - F₂ = 2 kgw</text>
  </g>

  <!-- Case 2: Perpendicular (90 deg) -->
  <g transform="translate(280, 20)">
    <rect x="0" y="0" width="230" height="210" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e676" stroke-width="1.5"/>
    <text x="115" y="30" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">【情況二：垂直 (90°)】</text>
    <circle cx="60" cy="140" r="5" fill="#fff"/>
    <!-- F1 right -->
    <line x1="60" y1="140" x2="160" y2="140" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-ex1-cyan)"/>
    <text x="120" y="160" fill="#00e5ff" font-size="12" font-weight="bold">F₁ = 8</text>
    <!-- F2 up -->
    <line x1="60" y1="140" x2="60" y2="65" stroke="#facc15" stroke-width="3" marker-end="url(#arr-ex2-gold)"/>
    <text x="45" y="95" fill="#facc15" font-size="12" font-weight="bold" text-anchor="end">F₂ = 6</text>
    <!-- Resultant diagonal -->
    <line x1="60" y1="140" x2="160" y2="65" stroke="#00e676" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arr-ex1-green)"/>
    <text x="145" y="95" fill="#00e676" font-size="13" font-weight="bold">R = 10</text>
  </g>
</svg>'''

    ex6_svg_fbd = '''<svg viewBox="0 0 540 260" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Right Triangle (6, 8, 10) -->
  <polygon points="120,180 320,180 320,50" fill="rgba(15, 23, 42, 0.6)" stroke="#00e676" stroke-width="2.5"/>
  <polyline points="305,180 305,165 320,165" fill="none" stroke="#64748b" stroke-width="1.5"/>

  <!-- Base: F1 = 8 -->
  <text x="220" y="205" fill="#00e5ff" font-size="14" font-weight="bold" text-anchor="middle">F₁ = 8 kgw</text>
  <!-- Height: F2 = 6 -->
  <text x="345" y="120" fill="#facc15" font-size="14" font-weight="bold">F₂ = 6 kgw</text>
  <!-- Hypotenuse: R = 10 -->
  <text x="195" y="105" fill="#00e676" font-size="15" font-weight="bold">合力 R = √(8² + 6²) = 10 kgw</text>

  <!-- Formula deduction card -->
  <rect x="40" y="215" width="460" height="35" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="270" y="238" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">聯立驗算：(F₁ - F₂ = 2) 與 (F₁² + F₂² = 100) ⟹ F₁ = 8 kgw, F₂ = 6 kgw</text>
</svg>'''

    ex6_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 兩情況受力情境對照</div>
        ''' + ex6_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 6-8-10 向量直角三角形解析</div>
        ''' + ex6_svg_fbd + '''
      </div>
    </div>'''

    problems[17]['diagrams'] = [
        { 'label': '📐 原始題圖 (兩受力情境)', 'svg': ex6_svg_raw },
        { 'label': '💡 6-8-10 向量直角三角形', 'svg': ex6_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex6_svg_dual }
    ]
    problems[17]['svg'] = ex6_svg_raw
    problems[17]['related'] = [
        { 'id': 'problem3', 'title': '範例 3：三細線拉銅環向量平衡', 'badge': '直角三角形' },
        { 'id': 'exercise8', 'title': '類題 8：運河拖船三力平衡', 'badge': '正交分解' },
        { 'id': 'practice', 'title': '自主測驗：37°-53° 經典懸吊', 'badge': '向量合成' }
    ]
    problems[17]['solutions'] = [
        {
            'title': '【重點解析・聯立方程與畢氏三元數速解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・列出反向與垂直之合力方程</strong>：<br>設兩力量值分別為 $F_1, F_2$（設 $F_1 \\ge F_2$）：<br>① 兩力反向（$\\theta = 180^\\circ$）：$$F_1 - F_2 = 2$$② 兩力垂直（$\\theta = 90^\\circ$）：$$F_1^2 + F_2^2 = 10^2 = 100$$',
                '📐 <strong>重點二・代入消去法運算</strong>：<br>將 $F_1 = F_2 + 2$ 代入平方和方程式：$$(F_2 + 2)^2 + F_2^2 = 100 \\implies 2F_2^2 + 4F_2 + 4 = 100$$$$F_2^2 + 2F_2 - 48 = 0 \\implies (F_2 + 8)(F_2 - 6) = 0$$取正根 $F_2 = \\mathbf{6\\text{ kgw}}$，則 $F_1 = 6 + 2 = \\mathbf{8\\text{ kgw}}$。',
                '⚡ <strong>重點三・經典 3-4-5 畢氏數直觀秒殺</strong>：<br>直角三角形斜邊為 $10$，經典直角三角形邊長必為 $(6, 8, 10)$。<br>驗算兩股差值：$8 - 6 = 2$ 恰完全吻合反向合力！<br>故兩力大小分別為 <strong>$8\\text{ kgw}$</strong> 與 <strong>$6\\text{ kgw}$</strong>。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 19 (Index 18): 類題 7 光滑斜面跨滑輪雙物體平衡 (q-18)
    # ========================================================
    problems[18]['answer'] = 'W_B = 1.2 kgw'

    ex7_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Incline 30 deg: from (40, 240) to (340, 240) to (340, 67) -->
  <polygon points="40,240 340,240 340,67" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <line x1="20" y1="240" x2="480" y2="240" stroke="#64748b" stroke-width="3"/>
  <path d="M90,240 A50,50 0 0,0 83,215" fill="none" stroke="#facc15" stroke-width="2"/>
  <text x="96" y="232" fill="#facc15" font-size="12" font-weight="bold">30°</text>

  <!-- Pulley at apex (340, 67) -->
  <circle cx="340" cy="67" r="14" fill="#0f172a" stroke="#f1f5f9" stroke-width="2"/>

  <!-- Block A on slope: centered at (190, 153), angle 30 deg -->
  <g transform="translate(190, 153) rotate(-30)">
    <rect x="-35" y="-28" width="70" height="28" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="2"/>
    <text x="0" y="-9" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">A (2.4 kgw)</text>
  </g>

  <!-- String from A to Pulley -->
  <line x1="205" y1="145" x2="333" y2="71" stroke="#f1f5f9" stroke-width="2"/>
  <!-- String hanging B vertically from Pulley -->
  <line x1="354" y1="67" x2="354" y2="160" stroke="#f1f5f9" stroke-width="2"/>
  <!-- Mass B -->
  <rect x="334" y="160" width="40" height="40" rx="4" fill="#1e293b" stroke="#ff5252" stroke-width="2.5"/>
  <text x="354" y="185" fill="#ff5252" font-size="13" font-weight="bold" text-anchor="middle">B</text>
  <text x="385" y="185" fill="#facc15" font-size="12" font-weight="bold">W_B = ?</text>
</svg>'''

    ex7_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr-ex7-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#ff5252"/>
    </marker>
    <marker id="arr-ex7-cyan" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#00e5ff"/>
    </marker>
    <marker id="arr-ex7-gold" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 1L10 5L0 9z" fill="#facc15"/>
    </marker>
  </defs>

  <!-- Left: Block A FBD -->
  <g transform="translate(30, 20)">
    <rect x="0" y="0" width="240" height="230" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e5ff" stroke-width="1.5"/>
    <text x="15" y="24" fill="#00e5ff" font-size="12" font-weight="bold">① 隔離物體 A（沿斜面平衡）：</text>
    <circle cx="120" cy="110" r="5" fill="#fff"/>
    <!-- Tension T up-right along slope -->
    <line x1="120" y1="110" x2="190" y2="70" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-ex7-cyan)"/>
    <text x="175" y="60" fill="#00e5ff" font-size="12" font-weight="bold">張力 T</text>
    <!-- Gravity component down-left along slope -->
    <line x1="120" y1="110" x2="50" y2="150" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-ex7-red)"/>
    <text x="45" y="170" fill="#ff5252" font-size="11" font-weight="bold">WA·sin30° = 1.2</text>
    <!-- Normal Force perp -->
    <line x1="120" y1="110" x2="80" y2="40" stroke="#64748b" stroke-width="2"/>
    <text x="75" y="35" fill="#64748b" font-size="10">N</text>

    <text x="15" y="205" fill="#facc15" font-size="11" font-weight="bold">沿斜面：T = WA·sin30° = 1.2 kgw</text>
  </g>

  <!-- Right: Block B FBD -->
  <g transform="translate(290, 20)">
    <rect x="0" y="0" width="220" height="230" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#ff5252" stroke-width="1.5"/>
    <text x="15" y="24" fill="#ff5252" font-size="12" font-weight="bold">② 隔離物體 B（鉛直平衡）：</text>
    <circle cx="110" cy="110" r="5" fill="#fff"/>
    <!-- Tension T up -->
    <line x1="110" y1="110" x2="110" y2="40" stroke="#00e5ff" stroke-width="3" marker-end="url(#arr-ex7-cyan)"/>
    <text x="120" y="55" fill="#00e5ff" font-size="12" font-weight="bold">張力 T = 1.2</text>
    <!-- Gravity down -->
    <line x1="110" y1="110" x2="110" y2="180" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-ex7-red)"/>
    <text x="120" y="175" fill="#ff5252" font-size="12" font-weight="bold">W_B</text>

    <text x="15" y="205" fill="#00e676" font-size="12" font-weight="bold">鉛直平衡：W_B = T = 1.2 kgw</text>
  </g>
</svg>'''

    ex7_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 原始題圖 (斜面與滑輪配置)</div>
        ''' + ex7_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 A、B 兩物體隔離受力平衡並列</div>
        ''' + ex7_svg_fbd + '''
      </div>
    </div>'''

    problems[18]['diagrams'] = [
        { 'label': '📐 原始題圖 (斜面與滑輪)', 'svg': ex7_svg_raw },
        { 'label': '💡 隔離體受力平衡分析', 'svg': ex7_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex7_svg_dual }
    ]
    problems[18]['svg'] = ex7_svg_raw
    problems[18]['related'] = [
        { 'id': 'problem9', 'title': '範例 9：斜面上物體受力分析', 'badge': '斜面分量' },
        { 'id': 'equil7', 'title': '平衡 7：斜面上滑動與靜止摩擦力', 'badge': '斜面平衡' },
        { 'id': 'exercise1', 'title': '類題 1：懸掛物體受力平衡', 'badge': '繩張力' }
    ]
    problems[18]['solutions'] = [
        {
            'title': '【重點解析・光滑斜面下滑分量與繩張力平衡】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・隔離物體 A 求細繩張力 $T$</strong>：<br>物體 A 位於光滑斜面上（無摩擦力），沿斜面方向受向下之重力下滑分量 $W_A \\sin 30^\\circ$ 與向上之繩張力 $T$：$$T = W_A \\sin 30^\\circ = 2.4 \\times \\frac{1}{2} = \\mathbf{1.2\\text{ kgw}}$$',
                '📌 <strong>重點二・隔離物體 B 求其重量 $W_B$</strong>：<br>物體 B 鉛直懸掛，受向上繩張力 $T$ 與向下重力 $W_B$。<br>由鉛直平衡條件：$$W_B = T = \\mathbf{1.2\\text{ kgw}}$$',
                '⚡ <strong>重點三・秒殺結論</strong>：<br>光滑斜面跨滑輪平衡條件為：$$W_B = W_A \\sin\\theta \\implies W_B = 2.4 \\times \\sin 30^\\circ = \\mathbf{1.2\\text{ kgw}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 20 (Index 19): 類題 8 運河拖船三力平衡多選題 (q-19)
    # ========================================================
    problems[19]['answer'] = '橫向平衡：F3y = (200√3 - 160) N (向下) ； 若垂直向下拉為 (200√3 - 160) N ； 若夾 30° 拉為 (400√3 - 320) N'

    ex8_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Top & Bottom Canal Banks -->
  <line x1="30" y1="40" x2="510" y2="40" stroke="#64748b" stroke-width="3" stroke-dasharray="6,4"/>
  <text x="40" y="32" fill="#64748b" font-size="11">上側河岸 (F₁ 側)</text>
  <line x1="30" y1="240" x2="510" y2="240" stroke="#64748b" stroke-width="3" stroke-dasharray="6,4"/>
  <text x="40" y="255" fill="#64748b" font-size="11">下側河岸 (F₂ 側)</text>

  <!-- Centerline of Canal -->
  <line x1="20" y1="140" x2="520" y2="140" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="4,4"/>
  <text x="480" y="132" fill="#38bdf8" font-size="11">運河中心線</text>

  <!-- Boat in center at (150, 140) -->
  <polygon points="120,130 170,130 190,140 170,150 120,150" fill="#1e293b" stroke="#f1f5f9" stroke-width="2"/>
  <circle cx="150" cy="140" r="4" fill="#fff"/>

  <!-- F1: 400 N at 60 deg up -->
  <line x1="150" y1="140" x2="250" y2="53" stroke="#00e5ff" stroke-width="3.5" marker-end="url(#arr-ex1-cyan)"/>
  <text x="210" y="48" fill="#00e5ff" font-size="12" font-weight="bold">F₁ = 400 N (60°)</text>

  <!-- F2: 320 N at 30 deg down -->
  <line x1="150" y1="140" x2="270" y2="209" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="260" y="228" fill="#facc15" font-size="12" font-weight="bold">F₂ = 320 N (30°)</text>

  <!-- F3 Child Pull: downward compensation -->
  <line x1="150" y1="140" x2="150" y2="215" stroke="#00e676" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arr-ex5-green)"/>
  <text x="158" y="200" fill="#00e676" font-size="11" font-weight="bold">F₃ (小孩向下平衡拉力)</text>
</svg>'''

    ex8_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Axes: x is canal line, y is transverse perpendicular -->
  <line x1="60" y1="140" x2="480" y2="140" stroke="#64748b" stroke-width="2"/>
  <text x="470" y="160" fill="#94a3b8" font-size="11">x (運河中心方向)</text>
  <line x1="150" y1="260" x2="150" y2="30" stroke="#64748b" stroke-width="2"/>
  <text x="155" y="35" fill="#94a3b8" font-size="11">y (橫向河岸方向)</text>

  <!-- F1y up: 400*sin60 = 200√3 ≈ 346.4 -->
  <line x1="150" y1="140" x2="150" y2="50" stroke="#00e5ff" stroke-width="4" marker-end="url(#arr-ex1-cyan)"/>
  <text x="160" y="70" fill="#00e5ff" font-size="12" font-weight="bold">F1y = 400·sin60° = 200√3 N (上)</text>

  <!-- F2y down: 320*sin30 = 160 -->
  <line x1="150" y1="140" x2="150" y2="190" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="160" y="180" fill="#facc15" font-size="12" font-weight="bold">F2y = 320·sin30° = 160 N (下)</text>

  <!-- Difference: 200√3 - 160 upwards -->
  <rect x="250" y="70" width="270" height="150" rx="8" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="265" y="95" fill="#facc15" font-size="12" font-weight="bold">⚡ 橫向平衡條件 (ΣFy = 0)：</text>
  <text x="265" y="120" fill="#f1f5f9" font-size="11">兩大人向上橫向合力：</text>
  <text x="265" y="140" fill="#00e5ff" font-size="12" font-weight="bold">ΔFy = 200√3 - 160 N (向上偏)</text>
  <text x="265" y="165" fill="#f1f5f9" font-size="11">小孩必須向下拉補足：</text>
  <text x="265" y="185" fill="#00e676" font-size="12" font-weight="bold">F3y = 200√3 - 160 N (向下)</text>
  <text x="265" y="205" fill="#94a3b8" font-size="10.5">若垂直拉: 200√3 - 160 ； 若30°拉: 400√3 - 320</text>
</svg>'''

    ex8_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 運河拖船三力情境圖</div>
        ''' + ex8_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 橫向 y 軸分量平衡解析</div>
        ''' + ex8_svg_fbd + '''
      </div>
    </div>'''

    problems[19]['diagrams'] = [
        { 'label': '📐 原始題圖 (運河拖船)', 'svg': ex8_svg_raw },
        { 'label': '💡 橫向分量平衡解析', 'svg': ex8_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex8_svg_dual }
    ]
    problems[19]['svg'] = ex8_svg_raw
    problems[19]['related'] = [
        { 'id': 'exercise6', 'title': '類題 6：二力正交與反向合力', 'badge': '向量分解' },
        { 'id': 'problem3', 'title': '範例 3：三細線拉銅環平衡', 'badge': '三力平衡' },
        { 'id': 'exercise9', 'title': '類題 9：逆風航行帆船推力', 'badge': '角度分解' }
    ]
    problems[19]['solutions'] = [
        {
            'title': '【重點解析・橫向分量平衡與可能拉力解】（大考多選標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・直線前進之橫向平衡條件</strong>：<br>欲使船沿運河中心直線行駛，垂直於河岸的橫向合力必須為零（$\\Sigma F_y = 0$）。',
                '📌 <strong>重點二・計算兩大人施力之橫向分量</strong>：<br>① 大人之拉力 $\\vec{F}_1$（偏向上側河岸 $60^\\circ$）：$$F_{1y} = 400 \\sin 60^\\circ = 400 \\times \\frac{\\sqrt{3}}{2} = \\mathbf{200\\sqrt{3}\\text{ N}} \\quad (\\text{向上})$$② 大人之拉力 $\\vec{F}_2$（偏向下側河岸 $30^\\circ$）：$$F_{2y} = 320 \\sin 30^\\circ = 320 \\times \\frac{1}{2} = \\mathbf{160\\text{ N}} \\quad (\\text{向下})$$<br>兩大人產生的橫向淨向上拉力：$$\\Delta F_y = 200\\sqrt{3} - 160\\text{ N} \\quad (\\text{向上})$$',
                '⚡ <strong>重點三・小孩拉力之可能解（應選兩項）</strong>：<br>小孩拉力之向下分量必須滿足：$$F_{3y} = \\mathbf{(200\\sqrt{3} - 160)\\text{ N}} \\quad (\\text{向下})$$<br>① <strong>若小孩垂直河岸向下拉</strong>（最省力方案）：$$F_3 = \\mathbf{(200\\sqrt{3} - 160)\\text{ N}}$$<br>② <strong>若小孩沿偏向 $30^\\circ$ 角拉</strong>（$F_3 \\sin 30^\\circ = 200\\sqrt{3} - 160$）：$$F_3 = \\frac{200\\sqrt{3} - 160}{\\sin 30^\\circ} = \\mathbf{(400\\sqrt{3} - 320)\\text{ N}}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 21 (Index 20): 類題 9 逆風航行帆船前進推力分解 (q-20)
    # ========================================================
    problems[20]['answer'] = 'F_前進 = ½ F'

    ex9_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Wind direction: straight down -->
  <line x1="80" y1="30" x2="80" y2="120" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arr-ex1-cyan)"/>
  <text x="90" y="70" fill="#38bdf8" font-size="12" font-weight="bold">風向 (向下)</text>

  <!-- Boat center at (260, 160) -->
  <!-- Heading line: 45 deg to vertical (135 deg to wind) -->
  <line x1="160" y1="260" x2="360" y2="60" stroke="#f1f5f9" stroke-width="2" stroke-dasharray="4,4"/>
  <text x="355" y="55" fill="#f1f5f9" font-size="12" font-weight="bold">船頭前進方向</text>

  <!-- Boat hull -->
  <g transform="translate(260, 160) rotate(-45)">
    <polygon points="-50,-14 30,-14 55,0 30,14 -50,14" fill="#1e293b" stroke="#f1f5f9" stroke-width="2"/>
    <!-- Sail: angle 15 deg with wind (vertical) -->
    <!-- Wind is vertical down. Sail at 15 deg to vertical -->
    <line x1="-15" y1="0" x2="25" y2="-45" stroke="#facc15" stroke-width="3.5"/>
    <text x="-5" y="-50" fill="#facc15" font-size="11" font-weight="bold">帆面</text>
  </g>

  <!-- Wind force F: perpendicular to sail -->
  <line x1="260" y1="160" x2="330" y2="120" stroke="#00e676" stroke-width="3.5" marker-end="url(#arr-ex1-green)"/>
  <text x="335" y="115" fill="#00e676" font-size="13" font-weight="bold">風力 F (垂直帆面)</text>

  <!-- 135 deg angle arc -->
  <text x="195" y="220" fill="#38bdf8" font-size="12">風與船頭夾 135°</text>
</svg>'''

    ex9_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Force Resolution Decomposition on Boat Axis -->
  <!-- Boat axis line -->
  <line x1="60" y1="220" x2="420" y2="40" stroke="#64748b" stroke-width="2"/>
  <text x="410" y="30" fill="#f1f5f9" font-size="12" font-weight="bold">船頭方向軸</text>

  <!-- Perpendicular to Boat axis -->
  <line x1="140" y1="60" x2="300" y2="220" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="305" y="235" fill="#64748b" font-size="11">橫向漂移軸</text>

  <!-- Force vector F -->
  <!-- Center at (220, 140) -->
  <circle cx="220" cy="140" r="5" fill="#fff"/>
  <!-- F vector: angle 60 deg with boat axis (so 30 deg with perp) -->
  <line x1="220" y1="140" x2="320" y2="80" stroke="#00e676" stroke-width="4" marker-end="url(#arr-ex1-green)"/>
  <text x="290" y="70" fill="#00e676" font-size="14" font-weight="bold">風力 F</text>

  <!-- Component along boat: F * cos60° = F/2 -->
  <line x1="220" y1="140" x2="270" y2="115" stroke="#00e5ff" stroke-width="4" marker-end="url(#arr-ex1-cyan)"/>
  <text x="235" y="95" fill="#00e5ff" font-size="13" font-weight="bold">F_前進 = F·cos60° = ½ F</text>

  <!-- Component perp: F * sin60° -->
  <line x1="270" y1="115" x2="320" y2="80" stroke="#facc15" stroke-width="2" stroke-dasharray="3,3"/>
  <text x="330" y="110" fill="#facc15" font-size="11">F_橫向 (水阻平衡)</text>

  <!-- Angle arc between F and boat axis -->
  <path d="M260,120 A45,45 0 0,0 250,125" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text x="265" y="132" fill="#fff" font-size="12" font-weight="bold">60°</text>

  <!-- Deduction card -->
  <rect x="40" y="225" width="460" height="40" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.5"/>
  <text x="270" y="250" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">幾何角度推導：風力 F 與船頭軸線夾角恰為 60° ⟹ 前進力 = F·cos60° = ½ F</text>
</svg>'''

    ex9_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 帆船逆風航行情境圖</div>
        ''' + ex9_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 風力 F 正交分解至船頭方向</div>
        ''' + ex9_svg_fbd + '''
      </div>
    </div>'''

    problems[20]['diagrams'] = [
        { 'label': '📐 原始題圖 (逆風帆船)', 'svg': ex9_svg_raw },
        { 'label': '💡 風力正交分解前進推力', 'svg': ex9_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex9_svg_dual }
    ]
    problems[20]['svg'] = ex9_svg_raw
    problems[20]['related'] = [
        { 'id': 'exercise8', 'title': '類題 8：運河拖船三力平衡', 'badge': '力之正交' },
        { 'id': 'exercise7', 'title': '類題 7：斜面上分量平衡', 'badge': '分量分解' },
        { 'id': 'problem3', 'title': '範例 3：向量合成與分解', 'badge': '角度解析' }
    ]
    problems[20]['solutions'] = [
        {
            'title': '【重點解析・幾何夾角剖析與正交分解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・幾何角度分析</strong>：<br>① 船頭前進方向與向下風向夾角為 $135^\\circ$，故船頭方向與<strong>向上逆風方向</strong>夾角為：$$180^\\circ - 135^\\circ = 45^\\circ$$② 帆面與鉛直風向夾角為 $15^\\circ$。<br>③ 風力 $\\vec{F}$ 垂直於帆面，故 $\\vec{F}$ 與<strong>水平橫向軸</strong>之夾角為 $15^\\circ$（與向下風向之夾角為 $90^\\circ - 15^\\circ = 75^\\circ$）。',
                '📐 <strong>重點二・求風力 $\\vec{F}$ 與船頭前進方向之夾角 $\\theta$</strong>：<br>船頭前進方向與向下風向夾 $135^\\circ$，風力 $\\vec{F}$ 與向下風向夾 $75^\\circ$（兩者位於風向同側）：$$\\theta = 135^\\circ - 75^\\circ = \\mathbf{60^\\circ}$$',
                '⚡ <strong>重點三・分解求順著船頭方向之推力</strong>：<br>將風力 $\\vec{F}$ 沿船頭方向投影：$$F_{\\text{前進}} = F \\cos 60^\\circ = \\mathbf{\\frac{1}{2}F} \\quad (\\text{或 } 0.5F)$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 22 (Index 21): 類題 10 雙彈簧垂直彈射裝置伸長量 (q-21)
    # ========================================================
    problems[21]['answer'] = '(E) 6mg / k'

    ex10_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Symmetric spring launcher -->
  <!-- Top fixed points: left at (120, 60), right at (380, 60) -->
  <line x1="80" y1="60" x2="160" y2="60" stroke="#64748b" stroke-width="4"/>
  <circle cx="120" cy="60" r="5" fill="#38bdf8"/>
  <text x="120" y="48" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">固定端</text>

  <line x1="340" y1="60" x2="420" y2="60" stroke="#64748b" stroke-width="4"/>
  <circle cx="380" cy="60" r="5" fill="#38bdf8"/>
  <text x="380" y="48" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">固定端</text>

  <!-- Central vertical symmetry axis -->
  <line x1="250" y1="30" x2="250" y2="290" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>
  <text x="250" y="25" fill="#94a3b8" font-size="11" text-anchor="middle">鉛垂對稱軸</text>

  <!-- Left spring: from (120, 60) to (250, 200) -->
  <!-- dx = 130, dy = 140, angle to vertical is 60 deg approx -->
  <path d="M 120,60 L 132,74 L 148,68 L 160,90 L 176,84 L 188,106 L 204,100 L 216,122 L 232,116 L 238,138 L 244,160 L 250,200" fill="none" stroke="#00e5ff" stroke-width="2.8"/>
  <text x="160" y="125" fill="#00e5ff" font-size="12" font-weight="bold">彈簧 k</text>

  <!-- Right spring: from (380, 60) to (250, 200) -->
  <path d="M 380,60 L 368,74 L 352,68 L 340,90 L 324,84 L 312,106 L 296,100 L 284,122 L 268,116 L 262,138 L 256,160 L 250,200" fill="none" stroke="#00e5ff" stroke-width="2.8"/>
  <text x="340" y="125" fill="#00e5ff" font-size="12" font-weight="bold">彈簧 k</text>

  <!-- Angle theta = 60 deg arcs -->
  <path d="M 250,150 A 50,50 0 0,0 215,160" fill="none" stroke="#facc15" stroke-width="1.8"/>
  <text x="220" y="148" fill="#facc15" font-size="12" font-weight="bold">60°</text>
  <path d="M 250,150 A 50,50 0 0,1 285,160" fill="none" stroke="#facc15" stroke-width="1.8"/>
  <text x="270" y="148" fill="#facc15" font-size="12" font-weight="bold">60°</text>

  <!-- Launch Platform & Mass m at (250, 200) -->
  <line x1="210" y1="200" x2="290" y2="200" stroke="#f1f5f9" stroke-width="3"/>
  <rect x="225" y="170" width="50" height="30" rx="4" fill="#1e293b" stroke="#00e676" stroke-width="2"/>
  <text x="250" y="190" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">m</text>

  <!-- Acceleration arrow a = 5g (up) -->
  <line x1="250" y1="165" x2="250" y2="105" stroke="#00e676" stroke-width="3.5" marker-end="url(#arr-ex1-green)"/>
  <text x="260" y="125" fill="#00e676" font-size="13" font-weight="bold">a = 5g (↑)</text>

  <!-- Gravity mg down -->
  <line x1="250" y1="205" x2="250" y2="255" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="260" y="245" fill="#ff5252" font-size="12" font-weight="bold">mg (↓)</text>
</svg>'''

    ex10_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Dynamic Newton 2nd Law Analysis -->
  <rect x="30" y="20" width="480" height="235" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="#00e676" stroke-width="1.5"/>
  <text x="50" y="50" fill="#00e676" font-size="14" font-weight="bold">💡 鉛直方向力學受力與牛頓第二定律推導：</text>

  <!-- Force components -->
  <text x="50" y="85" fill="#38bdf8" font-size="12" font-weight="bold">1. 兩彈簧鉛直向上分力合力：</text>
  <text x="70" y="110" fill="#f1f5f9" font-size="12">每個彈簧伸長量為 x ⟹ 彈力 Fs = kx</text>
  <text x="70" y="132" fill="#00e5ff" font-size="13" font-weight="bold">F_up = 2 × (kx · cos 60°) = 2 × kx × ½ = kx</text>

  <text x="50" y="165" fill="#ff5252" font-size="12" font-weight="bold">2. 向下重力：W = mg</text>

  <rect x="50" y="180" width="440" height="60" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.5"/>
  <text x="70" y="205" fill="#facc15" font-size="13" font-weight="bold">3. 牛頓第二運動定律 ΣFy = m · a：</text>
  <text x="70" y="228" fill="#f1f5f9" font-size="13">kx - mg = m(5g) ⟹ kx = 6mg ⟹ <strong style="color:#00e676; font-size:14px;">x = 6mg / k</strong>  ➔ ✅ 選 (E)</text>
</svg>'''

    ex10_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 垂直彈射裝置情境配置</div>
        ''' + ex10_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 鉛直分量與動力學分析並列</div>
        ''' + ex10_svg_fbd + '''
      </div>
    </div>'''

    problems[21]['diagrams'] = [
        { 'label': '📐 原始題圖 (彈射裝置)', 'svg': ex10_svg_raw },
        { 'label': '💡 鉛直動力學與伸長量推導', 'svg': ex10_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex10_svg_dual }
    ]
    problems[21]['svg'] = ex10_svg_raw
    problems[21]['related'] = [
        { 'id': 'problem1', 'title': '範例 1：彈簧伸長與外力', 'badge': '虎克定律' },
        { 'id': 'practice', 'title': '自主測驗：37°-53° 經典懸吊', 'badge': '雙繩彈簧' },
        { 'id': 'exercise11', 'title': '類題 11：套裝雙彈簧特性', 'badge': '彈簧組合' }
    ]
    problems[21]['solutions'] = [
        {
            'title': '【重點解析・雙對稱彈力鉛直分量與牛頓第二定律】（102指考標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・兩對稱彈簧之鉛直向上合拉力</strong>：<br>設每個彈簧伸長量為 $x$，彈力量值為 $F_s = kx$。<br>兩彈簧對稱分佈且與鉛垂線夾角皆為 $\\theta = 60^\\circ$，其鉛直向上合力為：$$F_{\\text{up}} = 2 \\cdot (kx \\cos 60^\\circ) = 2 \\cdot kx \\cdot \\frac{1}{2} = \\mathbf{kx}$$',
                '📌 <strong>重點二・列出牛頓第二定律動力方程式</strong>：<br>質點 $m$ 受到向上彈力合力 $kx$ 與向下重力 $mg$，具有向上加速度 $a = 5g$：$$\\Sigma F_y = m \\cdot a \\implies kx - mg = m(5g)$$',
                '⚡ <strong>重點三・解得每個彈簧之伸長量</strong>：$$kx = 6mg \\implies \\mathbf{x = \\frac{6mg}{k}} \\quad \\text{✅ 選 (E)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 23 (Index 22): 類題 11 套裝雙彈簧 F-x 特性圖與彈力常數 (q-22)
    # ========================================================
    problems[22]['answer'] = '(C) 200 N/m'

    ex11_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Fig A: Nested Springs -->
  <g transform="translate(30, 20)">
    <rect x="0" y="0" width="220" height="235" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="110" y="24" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">圖 (A) 套裝組合彈簧</text>
    <!-- Ground -->
    <line x1="20" y1="210" x2="200" y2="210" stroke="#64748b" stroke-width="3"/>
    <!-- Outer Large Spring: taller from y=210 to y=60 (height 150) -->
    <path d="M 90,210 L 90,190 L 130,175 L 70,155 L 130,135 L 70,115 L 130,95 L 70,75 L 110,60" fill="none" stroke="#00e5ff" stroke-width="3"/>
    <text x="155" y="110" fill="#00e5ff" font-size="11" font-weight="bold">大彈簧</text>
    <!-- Inner Small Spring: from y=210 to y=110 (height 100) -->
    <path d="M 100,210 L 100,195 L 115,185 L 85,170 L 115,155 L 85,140 L 115,125 L 100,110" fill="none" stroke="#facc15" stroke-width="2.5"/>
    <text x="155" y="160" fill="#facc15" font-size="11" font-weight="bold">小彈簧</text>
    <!-- 0.2m difference label -->
    <line x1="60" y1="60" x2="60" y2="110" stroke="#ff5252" stroke-width="1.5"/>
    <text x="50" y="90" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="end">0.2 m</text>
  </g>

  <!-- Fig B: F-x Curve -->
  <g transform="translate(280, 20)">
    <rect x="0" y="0" width="230" height="235" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e676" stroke-width="1.5"/>
    <text x="115" y="24" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">圖 (B) F - x 特性曲線圖</text>
    <!-- Axes -->
    <line x1="40" y1="190" x2="200" y2="190" stroke="#64748b" stroke-width="2"/>
    <text x="195" y="205" fill="#94a3b8" font-size="10.5">x (m)</text>
    <line x1="40" y1="190" x2="40" y2="45" stroke="#64748b" stroke-width="2"/>
    <text x="35" y="40" fill="#94a3b8" font-size="10.5">F (N)</text>
    <!-- Points: (0,0) to (100, 140) [x=0.2, F=20], then to (160, 60) [x=0.3, F=50] -->
    <line x1="40" y1="190" x2="110" y2="140" stroke="#00e5ff" stroke-width="2.5"/>
    <line x1="110" y1="140" x2="170" y2="70" stroke="#00e676" stroke-width="3"/>
    <circle cx="110" cy="140" r="4" fill="#00e5ff"/>
    <circle cx="170" cy="70" r="4" fill="#00e676"/>
    <text x="110" y="132" fill="#00e5ff" font-size="10" font-weight="bold">(0.2, 20)</text>
    <text x="170" y="62" fill="#00e676" font-size="10" font-weight="bold">(0.3, 50)</text>
    <text x="75" y="180" fill="#00e5ff" font-size="9.5">僅壓大彈簧</text>
    <text x="145" y="115" fill="#00e676" font-size="9.5">兩彈簧並聯</text>
  </g>
</svg>'''

    ex11_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="20" width="480" height="235" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="50" y="50" fill="#38bdf8" font-size="13" font-weight="bold">💡 兩階段斜率分析與等效並聯公式：</text>

  <!-- Stage 1 -->
  <text x="50" y="85" fill="#00e5ff" font-size="12" font-weight="bold">階段一（0 ≤ x ≤ 0.2 m）：僅大彈簧受壓縮</text>
  <text x="70" y="108" fill="#f1f5f9" font-size="12">外力完全由大彈簧承受 ⟹ 斜率即為大彈簧力常數：</text>
  <text x="70" y="130" fill="#00e5ff" font-size="13" font-weight="bold">k_大 = ΔF / Δx = 20 / 0.2 = 100 N/m</text>

  <!-- Stage 2 -->
  <text x="50" y="165" fill="#00e676" font-size="12" font-weight="bold">階段二（0.2 m ≤ x ≤ 0.3 m）：大、小彈簧同時受壓（並聯）</text>
  <text x="70" y="188" fill="#f1f5f9" font-size="12">組合總彈力常數為斜率：k_等效 = (50 - 20) / (0.3 - 0.2) = 300 N/m</text>

  <!-- Final subtraction -->
  <rect x="50" y="200" width="440" height="42" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.5"/>
  <text x="70" y="226" fill="#facc15" font-size="13" font-weight="bold">k_小 = k_等效 - k_大 = 300 - 100 = 200 N/m ➔ ✅ 選 (C)</text>
</svg>'''

    ex11_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 套裝彈簧情境與特性曲線</div>
        ''' + ex11_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 兩階段斜率計算分析並列</div>
        ''' + ex11_svg_fbd + '''
      </div>
    </div>'''

    problems[22]['diagrams'] = [
        { 'label': '📐 原始題圖 (套裝雙彈簧)', 'svg': ex11_svg_raw },
        { 'label': '💡 兩階段斜率計算解析', 'svg': ex11_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex11_svg_dual }
    ]
    problems[22]['svg'] = ex11_svg_raw
    problems[22]['related'] = [
        { 'id': 'exercise2', 'title': '類題 2：雙彈簧水平並聯推移', 'badge': '並聯等效' },
        { 'id': 'problem1', 'title': '範例 1：彈簧伸長量與外力圖', 'badge': 'F-x圖' },
        { 'id': 'exercise10', 'title': '類題 10：雙彈簧垂直彈射裝置', 'badge': '雙彈簧' }
    ]
    problems[22]['solutions'] = [
        {
            'title': '【重點解析・F-x 特性圖分段斜率與並聯力常數】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・階段一求大彈簧力常數 $k_{\\text{大}}$</strong>：<br>大彈簧比小彈簧長 $0.2\\text{ m}$，故當 $0 \\le x \\le 0.2\\text{ m}$ 時只有大彈簧被壓縮。<br>由圖(B)對應點 $(0.2\\text{ m}, 20\\text{ N})$，大彈簧之力常數為圖線斜率：$$k_{\\text{大}} = \\frac{\\Delta F}{\\Delta x} = \\frac{20 - 0}{0.2 - 0} = \\mathbf{100\\text{ N/m}}$$',
                '📌 <strong>重點二・階段二求組合等效力常數 $k_{\\text{等效}}$</strong>：<br>當壓縮量超過 $0.2\\text{ m}$ 時，大、小彈簧同時受壓（等效<strong>並聯</strong>）。<br>在 $x = 0.2\\text{ m} \\sim 0.3\\text{ m}$ 區間，外力由 $20\\text{ N}$ 增加至 $50\\text{ N}$：$$k_{\\text{等效}} = \\frac{\\Delta F}{\\Delta x} = \\frac{50 - 20}{0.3 - 0.2} = \\frac{30}{0.1} = \\mathbf{300\\text{ N/m}}$$',
                '⚡ <strong>重點三・並聯關係求小彈簧力常數 $k_{\\text{小}}$</strong>：<br>並聯等效力常數為各彈簧之和：$$k_{\\text{等效}} = k_{\\text{大}} + k_{\\text{小}} \\implies k_{\\text{小}} = 300 - 100 = \\mathbf{200\\text{ N/m}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 24 (Index 23): 類題 12 繩索應力應變與極限強度綜合題 (q-23)
    # ========================================================
    problems[23]['answer'] = '(1) 尼龍繩 ； (2) 碳纖維繩 ； (3) 5 × 10⁻⁶ m²'

    ex12_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Stress-Strain Curve Graph -->
  <g transform="translate(30, 20)">
    <rect x="0" y="0" width="220" height="235" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="110" y="24" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">應力 T vs 應變 S 曲線</text>
    <!-- Axes -->
    <line x1="35" y1="200" x2="195" y2="200" stroke="#64748b" stroke-width="2"/>
    <text x="190" y="215" fill="#94a3b8" font-size="10">S = x/L</text>
    <line x1="35" y1="200" x2="35" y2="45" stroke="#64748b" stroke-width="2"/>
    <text x="30" y="40" fill="#94a3b8" font-size="10">T = F/A</text>
    <!-- Curve: linear up to T1, then curve to Tm, then break -->
    <line x1="35" y1="200" x2="105" y2="120" stroke="#00e5ff" stroke-width="2.5"/>
    <path d="M 105,120 Q 140,80 170,70" fill="none" stroke="#facc15" stroke-width="2.5"/>
    <circle cx="105" cy="120" r="3.5" fill="#00e5ff"/>
    <text x="100" y="112" fill="#00e5ff" font-size="9.5">線性上限 T₁</text>
    <circle cx="170" cy="70" r="4" fill="#ff5252"/>
    <text x="170" y="62" fill="#ff5252" font-size="10" font-weight="bold">極限強度 Tm</text>
  </g>

  <!-- Table Summary Card -->
  <g transform="translate(270, 20)">
    <rect x="0" y="0" width="240" height="235" rx="8" fill="rgba(15, 23, 42, 0.6)" stroke="#00e676" stroke-width="1.5"/>
    <text x="120" y="24" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">材料參數對照表</text>
    <rect x="15" y="40" width="210" height="180" rx="6" fill="#1e293b" stroke="#64748b" stroke-width="1"/>
    <text x="25" y="65" fill="#94a3b8" font-size="11">材質　　力常數 k　　極限 Tm</text>
    <line x1="20" y1="75" x2="220" y2="75" stroke="#64748b" stroke-width="1"/>
    <text x="25" y="98" fill="#38bdf8" font-size="11">尼龍繩　k₀ (最軟)　　620 MPa</text>
    <text x="25" y="122" fill="#f1f5f9" font-size="11">棉繩　　2k₀　　　　 230 MPa</text>
    <text x="25" y="146" fill="#facc15" font-size="11">蜘蛛絲　3k₀　　　　 1000 MPa</text>
    <text x="25" y="170" fill="#f1f5f9" font-size="11">鋼索　　52k₀　　　　1330 MPa</text>
    <text x="25" y="195" fill="#00e676" font-size="11" font-weight="bold">碳纖維　77k₀ (最硬)　3430 MPa</text>
  </g>
</svg>'''

    ex12_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="20" width="490" height="240" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="#00e676" stroke-width="1.5"/>
  <text x="45" y="48" fill="#00e676" font-size="13" font-weight="bold">💡 三小題核心判斷推導：</text>

  <!-- Subquestion 1 -->
  <text x="45" y="80" fill="#38bdf8" font-size="12" font-weight="bold">(1) 微小伸長量下所需拉力最小（最易伸長）：</text>
  <text x="65" y="100" fill="#f1f5f9" font-size="11.5">F = kx ⟹ k 越小拉力越小 ⟹ 表中 k₀ 最小 ➔ <strong style="color:#38bdf8;">尼龍繩</strong></text>

  <!-- Subquestion 2 -->
  <text x="45" y="132" fill="#facc15" font-size="12" font-weight="bold">(2) 承受最大單位面積極限拉力（極限強度最高）：</text>
  <text x="65" y="152" fill="#f1f5f9" font-size="11.5">極限強度 Tm 代表斷裂前最大應力 ⟹ 表中 Tm = 3430 最高 ➔ <strong style="color:#facc15;">碳纖維繩</strong></text>

  <!-- Subquestion 3 -->
  <text x="45" y="184" fill="#00e676" font-size="12" font-weight="bold">(3) 登山者繩索安全截面積計算：</text>
  <text x="65" y="206" fill="#f1f5f9" font-size="11">最大拉力 F = 3200 N，Tm = 620 × 10⁶ N/m²</text>
  <text x="65" y="228" fill="#00e676" font-size="12" font-weight="bold">A ≥ F / Tm = 3200 / (620 × 10⁶) ≈ 5.16 × 10⁻⁶ m² ≈ 5 × 10⁻⁶ m²</text>
</svg>'''

    ex12_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 應力應變圖與材料特性表</div>
        ''' + ex12_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 應力定義與截面積運算並列</div>
        ''' + ex12_svg_fbd + '''
      </div>
    </div>'''

    problems[23]['diagrams'] = [
        { 'label': '📐 原始題圖 (應力應變曲線)', 'svg': ex12_svg_raw },
        { 'label': '💡 應力定義與截面積解析', 'svg': ex12_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': ex12_svg_dual }
    ]
    problems[23]['svg'] = ex12_svg_raw
    problems[23]['related'] = [
        { 'id': 'exercise4', 'title': '類題 4：自重彈簧非均勻伸長', 'badge': '應變分析' },
        { 'id': 'problem1', 'title': '範例 1：彈簧外力與伸長量', 'badge': '虎克定律' },
        { 'id': 'exercise11', 'title': '類題 11：套裝雙彈簧特性', 'badge': '力學性質' }
    ]
    problems[23]['solutions'] = [
        {
            'title': '【重點解析・應力應變物理意涵與材料強度綜合計算】（104學測標準解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>(1) 微小伸長下所需拉力最小之材質</strong>：<br>在彈性限度內遵守虎克定律 $F = kx$。在相同長度與粗細下，拉力 $F$ 與力常數 $k$ 成正比。力常數 $k$ 越小則越易拉伸，表中力常數最小者為 <strong>【尼龍繩】</strong>（$k = k_0$）。',
                '📌 <strong>(2) 承受最大單位面積極限拉力之材質</strong>：<br>單位面積所能承受之最大拉力即為<strong>「極限強度 $T_m$」</strong>。對照表格，$T_m$ 最高者為 <strong>【碳纖維繩】</strong>（$3430\\text{ MPa}$）。',
                '⚡ <strong>(3) 登山者繩索截面積計算</strong>：<br>登山者重 $80\\text{ kgw}$，安全倍率為 $4$ 倍 $\\implies$ 繩索須承受拉力：$$F = 4 \\times 80\\text{ kgw} \\approx 3200\\text{ N}$$極限強度 $T_m = 620\\text{ MPa} = 620 \\times 10^6\\text{ N/m}^2$。<br>由應力定義 $T = \\frac{F}{A} \\le T_m$：$$A \\ge \\frac{F}{T_m} = \\frac{3200}{620 \\times 10^6} \\approx \\mathbf{5.16 \\times 10^{-6}\\text{ m}^2} \\approx \\mathbf{5 \\times 10^{-6}\\text{ m}^2}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 25 (Index 24): 力矩 1 正三角形板三力對頂點之合力矩 (q-24)
    # ========================================================
    problems[24]['answer'] = '(C) (√3 / 2) Fa'

    torque1_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Equilateral triangle ABC: side = a (e.g. 200px) -->
  <!-- A at (270, 50), B at (170, 223), C at (370, 223) -->
  <polygon points="270,50 170,223 370,223" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>

  <!-- Vertices -->
  <circle cx="270" cy="50" r="6" fill="#facc15"/>
  <text x="270" y="38" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">支點 A</text>

  <circle cx="170" cy="223" r="5" fill="#38bdf8"/>
  <text x="150" y="235" fill="#38bdf8" font-size="13" font-weight="bold">B</text>

  <circle cx="370" cy="223" r="5" fill="#38bdf8"/>
  <text x="385" y="235" fill="#38bdf8" font-size="13" font-weight="bold">C</text>

  <!-- Force F1 along AB (from A towards B) -->
  <line x1="250" y1="85" x2="190" y2="188" stroke="#ff5252" stroke-width="3.5" marker-end="url(#arr-ex1-red)"/>
  <text x="195" y="130" fill="#ff5252" font-size="12" font-weight="bold">F₁ = F</text>

  <!-- Force F2 along BC (from B towards C) -->
  <line x1="190" y1="240" x2="350" y2="240" stroke="#00e676" stroke-width="3.5" marker-end="url(#arr-ex1-green)"/>
  <text x="270" y="260" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">F₂ = F</text>

  <!-- Force F3 along CA (from C towards A) -->
  <line x1="350" y1="188" x2="290" y2="85" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="345" y="130" fill="#facc15" font-size="12" font-weight="bold">F₃ = F</text>

  <!-- Height h from A to BC -->
  <line x1="270" y1="50" x2="270" y2="223" stroke="#f1f5f9" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="275" y="150" fill="#f1f5f9" font-size="11" font-weight="bold">力臂 d = (√3/2) a</text>
</svg>'''

    torque1_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="20" width="480" height="235" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="#facc15" stroke-width="1.5"/>
  <text x="50" y="50" fill="#facc15" font-size="13" font-weight="bold">💡 以任一頂點 A 為支點之力矩剖析：</text>

  <!-- Force 1 & 3 through A -->
  <text x="50" y="85" fill="#ff5252" font-size="12" font-weight="bold">1. 作用力 F₁ (沿 AB) 與 F₃ (沿 CA)：</text>
  <text x="70" y="108" fill="#f1f5f9" font-size="12">此二力的作用線均直接穿過頂點 A ⟹ 力臂 d₁ = 0, d₃ = 0</text>
  <text x="70" y="128" fill="#94a3b8" font-size="12">因此產生的力矩：τ₁ = 0, τ₃ = 0</text>

  <!-- Force 2 along BC -->
  <text x="50" y="160" fill="#00e676" font-size="12" font-weight="bold">2. 作用力 F₂ (沿對邊 BC)：</text>
  <text x="70" y="182" fill="#f1f5f9" font-size="12">頂點 A 到對邊 BC 的垂直距離即為正三角形的高：</text>
  <text x="70" y="202" fill="#00e676" font-size="13" font-weight="bold">力臂 d = h = a · sin 60° = (√3 / 2) a</text>

  <!-- Conclusion -->
  <rect x="50" y="215" width="440" height="32" rx="4" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="236" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">合力矩量值：τ = F₂ · d = (√3 / 2) F a ➔ ✅ 選 (C)</text>
</svg>'''

    torque1_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 正三角形板三循環力圖</div>
        ''' + torque1_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 頂點支點力臂與合力矩解析</div>
        ''' + torque1_svg_fbd + '''
      </div>
    </div>'''

    problems[24]['diagrams'] = [
        { 'label': '📐 原始題圖 (正三角形板)', 'svg': torque1_svg_raw },
        { 'label': '💡 頂點支點力矩計算解析', 'svg': torque1_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque1_svg_dual }
    ]
    problems[24]['svg'] = torque1_svg_raw
    problems[24]['related'] = [
        { 'id': 'torque2', 'title': '力矩 2：傾斜細桿兩端質點合力矩', 'badge': '支點力矩' },
        { 'id': 'problem7', 'title': '範例 7：高架工作車抗翻覆臨界', 'badge': '力臂計算' },
        { 'id': 'torque3', 'title': '力矩 3：均質桿件傾斜力矩', 'badge': '力矩平衡' }
    ]
    problems[24]['solutions'] = [
        {
            'title': '【重點解析・對稱三角形力臂計算與力矩定義】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・選定任一頂點為參考支點</strong>：<br>對稱性極佳，任選頂點 A 為支點。',
                '📌 <strong>重點二・分析通過支點的作用力</strong>：<br>三力分別沿邊長 AB、BC、CA 方向作用：<br>① 沿 AB 之作用力：其作用線穿過頂點 A，力臂為 $0$，故力矩 $\\tau_1 = 0$。<br>② 沿 CA 之作用力：其作用線穿過頂點 A，力臂為 $0$，故力矩 $\\tau_3 = 0$。',
                '⚡ <strong>重點三・計算對邊作用力之合力矩</strong>：<br>頂點 A 至對邊 BC 之垂直距離即為邊長為 $a$ 的正三角形之高：$$d = a \\sin 60^\\circ = \\frac{\\sqrt{3}}{2}a$$因此對頂點 A 的合力矩量值為：$$\\tau_{\\text{合}} = F \\cdot d = \\mathbf{\\frac{\\sqrt{3}}{2}Fa} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 26 (Index 25): 力矩 2 傾斜細桿兩端質點對中心力矩 (q-25)
    # ========================================================
    problems[25]['answer'] = '(B) (Wd / 2) sinθ'

    torque2_svg_raw = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Vertical Reference Line -->
  <line x1="270" y1="30" x2="270" y2="250" stroke="#64748b" stroke-width="1.8" stroke-dasharray="4,4"/>
  <text x="270" y="25" fill="#64748b" font-size="11" text-anchor="middle">鉛垂線</text>

  <!-- Rod length d: tilted at angle theta to vertical -->
  <!-- Center O at (270, 140). d = 220px, half = 110px. theta = 30 deg -->
  <!-- dx = 110*sin30 = 55, dy = 110*cos30 = 95.2 -->
  <!-- Left-top (2W): (270-55, 140-95.2) = (215, 45) -->
  <!-- Right-bottom (3W): (270+55, 140+95.2) = (325, 235) -->
  <line x1="215" y1="45" x2="325" y2="235" stroke="#facc15" stroke-width="5" stroke-linecap="round"/>

  <!-- Pivot O in center -->
  <circle cx="270" cy="140" r="6" fill="#38bdf8"/>
  <text x="285" y="145" fill="#38bdf8" font-size="14" font-weight="bold">O</text>

  <!-- Angle theta arcs -->
  <path d="M 270,90 A 50,50 0 0,0 245,97" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text x="250" y="85" fill="#fff" font-size="12">θ</text>

  <!-- Left Mass 2W at (215, 45) -->
  <circle cx="215" cy="45" r="14" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="215" y="50" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="middle">2W</text>
  <!-- 2W gravity down -->
  <line x1="215" y1="45" x2="215" y2="105" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="185" y="80" fill="#ff5252" font-size="11" font-weight="bold">2W (下)</text>
  <!-- Lever arm: horizontal distance to O = 55 -->
  <line x1="215" y1="140" x2="270" y2="140" stroke="#00e5ff" stroke-width="1.5" stroke-dasharray="2,2"/>
  <text x="242" y="132" fill="#00e5ff" font-size="10.5" text-anchor="middle">½d sinθ</text>

  <!-- Right Mass 3W at (325, 235) -->
  <circle cx="325" cy="235" r="16" fill="#1e293b" stroke="#00e676" stroke-width="2.5"/>
  <text x="325" y="240" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">3W</text>
  <!-- 3W gravity down -->
  <line x1="325" y1="235" x2="325" y2="280" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="350" y="260" fill="#ff5252" font-size="11" font-weight="bold">3W (下)</text>
  <!-- Lever arm: horizontal distance to O = 55 -->
  <line x1="270" y1="140" x2="325" y2="140" stroke="#00e676" stroke-width="1.5" stroke-dasharray="2,2"/>
  <text x="298" y="132" fill="#00e676" font-size="10.5" text-anchor="middle">½d sinθ</text>
</svg>'''

    torque2_svg_fbd = '''<svg viewBox="0 0 540 280" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="20" width="480" height="235" rx="10" fill="rgba(15, 23, 42, 0.7)" stroke="#00e676" stroke-width="1.5"/>
  <text x="50" y="50" fill="#00e676" font-size="13" font-weight="bold">💡 力矩旋轉方向與合力矩剖析：</text>

  <!-- 3W Torque -->
  <text x="50" y="85" fill="#00e676" font-size="12" font-weight="bold">1. 質點 3W 之力矩（右下）：</text>
  <text x="70" y="108" fill="#f1f5f9" font-size="12">重力在支點右側向下 ⟹ 產生<strong>順時鐘 (↻)</strong> 力矩：</text>
  <text x="70" y="128" fill="#00e676" font-size="13" font-weight="bold">τ₁ = 3W · (½ d · sin θ) ↻</text>

  <!-- 2W Torque -->
  <text x="50" y="160" fill="#00e5ff" font-size="12" font-weight="bold">2. 質點 2W 之力矩（左上）：</text>
  <text x="70" y="182" fill="#f1f5f9" font-size="12">重力在支點左側向下 ⟹ 產生<strong>逆時鐘 (↺)</strong> 力矩：</text>
  <text x="70" y="202" fill="#00e5ff" font-size="13" font-weight="bold">τ₂ = 2W · (½ d · sin θ) ↺</text>

  <!-- Conclusion -->
  <rect x="50" y="215" width="440" height="32" rx="4" fill="#1e293b" stroke="#facc15" stroke-width="1.2"/>
  <text x="270" y="236" fill="#facc15" font-size="13" font-weight="bold" text-anchor="middle">合力矩量值：τ = τ₁ - τ₂ = (3W - 2W) · ½d sinθ = (Wd / 2) sinθ ➔ ✅ (B)</text>
</svg>'''

    torque2_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 傾斜細桿雙質點力矩圖</div>
        ''' + torque2_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 順逆力矩抵消運算並列</div>
        ''' + torque2_svg_fbd + '''
      </div>
    </div>'''

    problems[25]['diagrams'] = [
        { 'label': '📐 原始題圖 (傾斜細桿)', 'svg': torque2_svg_raw },
        { 'label': '💡 順逆力矩抵消解析', 'svg': torque2_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque2_svg_dual }
    ]
    problems[25]['svg'] = torque2_svg_raw
    problems[25]['related'] = [
        { 'id': 'torque1', 'title': '力矩 1：正三角形板循環力合力矩', 'badge': '力臂分解' },
        { 'id': 'problem8', 'title': '範例 8：水平輕棒懸重樞鈕力', 'badge': '力矩變化' },
        { 'id': 'torque3', 'title': '力矩 3：均質桿件傾斜力矩', 'badge': '桿件力矩' }
    ]
    problems[25]['solutions'] = [
        {
            'title': '【重點解析・重力垂直力臂與順逆力矩抵消】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・計算兩端重力對支點 O 之力臂</strong>：<br>桿長為 $d$，中點 O 為轉軸，故 O 到兩端質點之桿長距離均為 $\\frac{d}{2}$。<br>細桿與鉛直方向夾角為 $\\theta$。因重力沿鉛垂線向下，其作用線至支點 O 的水平垂直距離（力臂）為：$$\\text{力臂 } \\ell = \\frac{d}{2} \\sin\\theta$$',
                '📌 <strong>重點二・判斷兩質點力矩之旋轉方向</strong>：<br>① 右側質點（重 $3W$）：在支點右側受向下重力，產生<strong>順時鐘 ($\\circlearrowright$)</strong> 之力矩：$$\\tau_1 = 3W \\cdot \\left(\\frac{d}{2}\\sin\\theta\\right)$$② 左側質點（重 $2W$）：在支點左側受向下重力，產生<strong>逆時鐘 ($\\circlearrowleft$)</strong> 之力矩：$$\\tau_2 = 2W \\cdot \\left(\\frac{d}{2}\\sin\\theta\\right)$$',
                '⚡ <strong>重點三・兩相反力矩相消得合力矩</strong>：<br>合力矩量值等於順逆力矩相減：$$\\tau_{\\text{合}} = \\tau_1 - \\tau_2 = (3W - 2W) \\cdot \\left(\\frac{d}{2}\\sin\\theta\\right) = \\mathbf{\\frac{Wd}{2}\\sin\\theta} \\quad \\text{✅ 選 (B)}$$'
            ]
        }
    ]


    # ========================================================
    # Enrich Problem 27 (Index 26): 力矩 3 87聯考雙質點細桿重力合力矩 (q-26)
    # ========================================================
    problems[26]['options'] = [
        '(A) $0$',
        '(B) $\\frac{1}{2}mgd \\sin \\theta$',
        '(C) $mgd \\sin \\theta$',
        '(D) $\\frac{3}{2}mgd \\sin \\theta$',
        '(E) $\\frac{1}{2}mgd \\cos \\theta$'
    ]
    problems[26]['answer'] = '(B) (1/2) mgd sinθ'

    torque3_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Vertical Reference Line -->
  <line x1="270" y1="25" x2="270" y2="295" stroke="#64748b" stroke-width="1.8" stroke-dasharray="4,4"/>
  <text x="270" y="20" fill="#64748b" font-size="11" text-anchor="middle">鉛垂線</text>

  <!-- Rod length d: tilted at angle theta to vertical -->
  <line x1="210" y1="56" x2="330" y2="264" stroke="#94a3b8" stroke-width="4.5" stroke-linecap="round"/>
  <text x="235" y="105" fill="#94a3b8" font-size="12">½ d</text>
  <text x="305" y="215" fill="#94a3b8" font-size="12">½ d</text>

  <!-- Pivot O in center -->
  <circle cx="270" cy="160" r="6" fill="#facc15"/>
  <text x="288" y="165" fill="#facc15" font-size="14" font-weight="bold">O (轉軸)</text>

  <!-- Angle theta arc -->
  <path d="M 270,105 A 55,55 0 0,0 242,112" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text x="248" y="100" fill="#fff" font-size="12">θ</text>

  <!-- Top-left Mass m at (210, 56) -->
  <circle cx="210" cy="56" r="13" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="210" y="61" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">m</text>
  <!-- Gravity mg down -->
  <line x1="210" y1="56" x2="210" y2="125" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="175" y="95" fill="#ff5252" font-size="11" font-weight="bold">W₁ = mg</text>
  <!-- Lever arm: horizontal distance to O = 60 -->
  <line x1="210" y1="160" x2="270" y2="160" stroke="#00e5ff" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="210" y1="56" x2="210" y2="160" stroke="#64748b" stroke-width="1" stroke-dasharray="2,2"/>
  <text x="240" y="152" fill="#00e5ff" font-size="10.5" text-anchor="middle">½d sinθ</text>

  <!-- Bottom-right Mass 2m at (330, 264) -->
  <circle cx="330" cy="264" fill="#1e293b" stroke="#00e676" stroke-width="2.5"/>
  <text x="330" y="270" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">2m</text>
  <!-- Gravity 2mg down -->
  <line x1="330" y1="264" x2="330" y2="318" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="350" y="295" fill="#ff5252" font-size="11" font-weight="bold">W₂ = 2mg</text>
  <!-- Lever arm: horizontal distance to O = 60 -->
  <line x1="270" y1="160" x2="330" y2="160" stroke="#00e676" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="330" y1="160" x2="330" y2="264" stroke="#64748b" stroke-width="1" stroke-dasharray="2,2"/>
  <text x="300" y="152" fill="#00e676" font-size="10.5" text-anchor="middle">½d sinθ</text>
</svg>'''

    torque3_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="20" width="490" height="280" rx="10" fill="rgba(15, 23, 42, 0.75)" stroke="#00e676" stroke-width="1.5"/>
  <text x="45" y="52" fill="#00e676" font-size="14" font-weight="bold">💡 【87 聯考】以中點 O 為支點之合力矩運算：</text>

  <text x="45" y="90" fill="#00e676" font-size="13" font-weight="bold">1. 質點 2m（右下）之順時針力矩：</text>
  <text x="65" y="115" fill="#f1f5f9" font-size="12.5">重力 2mg 在轉軸右側向下 ⟹ 產生順時針 (↻) 力矩：</text>
  <text x="65" y="138" fill="#00e676" font-size="13.5" font-weight="bold">τ₁ = (2mg) · (½ d · sin θ) = mgd · sin θ (↻)</text>

  <text x="45" y="175" fill="#00e5ff" font-size="13" font-weight="bold">2. 質點 m（左上）之逆時針力矩：</text>
  <text x="65" y="200" fill="#f1f5f9" font-size="12.5">重力 mg 在轉軸左側向下 ⟹ 產生逆時針 (↺) 力矩：</text>
  <text x="65" y="223" fill="#00e5ff" font-size="13.5" font-weight="bold">τ₂ = (mg) · (½ d · sin θ) = ½ mgd · sin θ (↺)</text>

  <rect x="45" y="245" width="450" height="42" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.5"/>
  <text x="270" y="272" fill="#facc15" font-size="13.5" font-weight="bold" text-anchor="middle">合力矩量值：τ = τ₁ - τ₂ = ½ mgd · sin θ ➔ ✅ 選 (B)</text>
</svg>'''

    torque3_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 雙質點細桿傾角幾何圖</div>
        ''' + torque3_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 順逆力矩拆解運算並列</div>
        ''' + torque3_svg_fbd + '''
      </div>
    </div>'''

    problems[26]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙質點細桿)', 'svg': torque3_svg_raw },
        { 'label': '💡 順逆力矩拆解解析', 'svg': torque3_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque3_svg_dual }
    ]
    problems[26]['svg'] = torque3_svg_raw
    problems[26]['related'] = [
        { 'id': 'torque2', 'title': '力矩 2：傾斜細桿兩端質點合力矩', 'badge': '力矩對照' },
        { 'id': 'torque1', 'title': '力矩 1：正三角形板循環力合力矩', 'badge': '力臂分解' },
        { 'id': 'torque5', 'title': '力矩 5：任意角度維持平衡懸掛點', 'badge': '重心隨遇' }
    ]
    problems[26]['solutions'] = [
        {
            'title': '【重點解析・重力垂直力臂與兩質點力矩相消】（87聯考大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・計算兩質點重力對支點 O 之垂直力臂</strong>：<br>桿長為 $d$，中點 O 為轉軸，故轉軸至兩端質點之桿長皆為 $\\frac{d}{2}$。<br>細桿與鉛垂線夾角為 $\\theta$，鉛直向下之重力其作用線至支點 O 的垂直水平距離即為力臂：$$\\text{力臂 } \\ell = \\frac{d}{2} \\sin\\theta$$',
                '📌 <strong>重點二・判斷兩重力之旋轉方向</strong>：<br>① 下方質點（質量 $2m$）：位於支點右側，重力向下，使桿繞 O 產生<strong>順時針 (\\circlearrowright)</strong> 力矩：$$\\tau_1 = (2mg) \\cdot \\left(\\frac{d}{2}\\sin\\theta\\right) = mgd \\sin\\theta$$② 上方質點（質量 $m$）：位於支點左側，重力向下，使桿繞 O 產生<strong>逆時針 (\\circlearrowleft)</strong> 力矩：$$\\tau_2 = (mg) \\cdot \\left(\\frac{d}{2}\\sin\\theta\\right) = \\frac{1}{2}mgd \\sin\\theta$$',
                '⚡ <strong>重點三・兩相反力矩相消得合力矩</strong>：<br>因兩力矩方向相反，合力矩量值等於兩者相減：$$\\tau_{\\text{合}} = \\tau_1 - \\tau_2 = mgd \\sin\\theta - \\frac{1}{2}mgd \\sin\\theta = \\mathbf{\\frac{1}{2}mgd \\sin\\theta} \\quad \\text{✅ 選 (B)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 28 (Index 27): 力矩 4 98指考圓輪推上階梯臨界力矩 (q-27)
    # ========================================================
    problems[27]['answer'] = '(1) C<br>(2) A<br>(3) B'

    torque4_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ground -->
  <line x1="30" y1="260" x2="340" y2="260" stroke="#64748b" stroke-width="2"/>
  <!-- Step -->
  <line x1="340" y1="260" x2="340" y2="200" stroke="#94a3b8" stroke-width="2.5"/>
  <line x1="340" y1="200" x2="510" y2="200" stroke="#94a3b8" stroke-width="2.5"/>
  <polygon points="340,260 340,200 510,200 510,260" fill="rgba(30, 41, 59, 0.6)"/>
  <line x1="365" y1="200" x2="365" y2="260" stroke="#facc15" stroke-width="1.5"/>
  <text x="375" y="235" fill="#facc15" font-size="12" font-weight="bold">階高 h</text>

  <!-- Wheel Body: R = 90px, Center at (255, 170) -->
  <circle cx="255" cy="170" r="90" fill="rgba(0, 229, 255, 0.08)" stroke="#00e5ff" stroke-width="3"/>
  <circle cx="255" cy="170" r="5" fill="#facc15"/>
  <text x="238" y="165" fill="#facc15" font-size="13" font-weight="bold">圓心 O</text>

  <!-- Horizontal Force F -->
  <line x1="255" y1="170" x2="335" y2="170" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="290" y="155" fill="#facc15" font-size="13" font-weight="bold">水平外力 F</text>

  <!-- Step Corner A at (340, 200) -->
  <circle cx="340" cy="200" r="6" fill="#00e676"/>
  <text x="350" y="195" fill="#00e676" font-size="14" font-weight="bold">A (階梯角)</text>

  <!-- Gravity W -->
  <line x1="255" y1="170" x2="255" y2="245" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="260" y="235" fill="#ff5252" font-size="12" font-weight="bold">重力 W</text>

  <!-- Radius line from O to A -->
  <line x1="255" y1="170" x2="340" y2="200" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="290" y="195" fill="#94a3b8" font-size="11">半徑 R</text>
</svg>'''

    torque4_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="15" width="490" height="290" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#facc15" stroke-width="1.5"/>
  <text x="45" y="42" fill="#facc15" font-size="13.5" font-weight="bold">💡 【98 指考】圓輪推上階梯臨界力矩剖析：</text>

  <text x="45" y="72" fill="#38bdf8" font-size="12.5" font-weight="bold">問題 (1) 未脫離地面時受力：</text>
  <text x="65" y="93" fill="#f1f5f9" font-size="12">外力 F、重力 W、地面正向力 N、階梯支持力 N' ➔ 共 4 個力 ✅ 選 (C)</text>

  <text x="45" y="125" fill="#00e676" font-size="12.5" font-weight="bold">問題 (2) 分力平衡方程式：</text>
  <text x="65" y="146" fill="#f1f5f9" font-size="12">水平向左支持分力與 F 平衡：N' cosθ = F</text>
  <text x="65" y="166" fill="#f1f5f9" font-size="12">鉛直向上支持分力與 N, W 平衡：N + N' sinθ = W ➔ ✅ 選 (A)</text>

  <text x="45" y="198" fill="#facc15" font-size="12.5" font-weight="bold">問題 (3) 以階梯角 A 為支點之臨界脫離力矩：</text>
  <text x="65" y="219" fill="#f1f5f9" font-size="12">臨界脫離地面時 N = 0。外力力臂 d_F = R - h；重力力臂 d_W = √(2Rh - h²)</text>

  <rect x="45" y="240" width="450" height="50" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="260" fill="#00e676" font-size="12.5" font-weight="bold" text-anchor="middle">力矩平衡：F · (R - h) = W · √(h(2R - h))</text>
  <text x="270" y="280" fill="#facc15" font-size="13" font-weight="bold" text-anchor="middle">F_min = W · √(h(2R - h)) / (R - h) ➔ ✅ 選 (B)</text>
</svg>'''

    torque4_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 圓輪爬階原始幾何圖</div>
        ''' + torque4_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 受力平衡與臨界脫離力矩並列</div>
        ''' + torque4_svg_fbd + '''
      </div>
    </div>'''

    problems[27]['diagrams'] = [
        { 'label': '📐 原始題圖 (圓輪爬階)', 'svg': torque4_svg_raw },
        { 'label': '💡 臨界脫離力矩解析', 'svg': torque4_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque4_svg_dual }
    ]
    problems[27]['svg'] = torque4_svg_raw
    problems[27]['related'] = [
        { 'id': 'problem7', 'title': '範例 7：高架起重車翻覆臨界', 'badge': '力矩翻轉' },
        { 'id': 'problem11', 'title': '範例 11：木箱滑動與傾倒臨界', 'badge': '臨界正向力' },
        { 'id': 'torque6', 'title': '力矩 6：均質木棒懸重臨界翹起', 'badge': '臨界支點' }
    ]
    problems[27]['solutions'] = [
        {
            'title': '【重點解析・圓輪推上階梯三大子題完整剖析】（98指考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>問題 (1)・尚未脫離地面時受力個數分析</strong>：<br>圓輪受力包含：<br>① 外力 $F$（施於圓心向右）<br>② 重力 $W$（鉛直向下通過圓心）<br>③ 地面正向力 $N$（鉛直向上）<br>④ 階梯頂點 A 之支持力 $N^{\\prime}$（沿接觸法線通過圓心，指向左上方）<br>因輪子光滑，地面與階梯角皆無摩擦力。故共受 <strong>4 個力</strong> 作用 $\\implies$ <strong>✅ 選 (C)</strong>。',
                '📌 <strong>問題 (2)・建立分力平衡方程式</strong>：<br>設階梯角支持力 $N^{\\prime}$ 與水平方向夾角為 $\\theta$：<br>幾何關係：$O$ 至 $A$ 之高差為 $R - h$，斜邊為 $R$，故 $\\sin\\theta = \\frac{R-h}{R}$，$\\cos\\theta = \\frac{\\sqrt{h(2R-h)}}{R}$。<br>① 水平方向合力為零：$$N^{\\prime} \\cos\\theta = F$$② 鉛直方向合力為零：$$N + N^{\\prime} \\sin\\theta = W$$故選 <strong>✅ (A)</strong>。',
                '⚡ <strong>問題 (3)・以階梯角 A 為支點求最小推力 $F_{\\min}$</strong>：<br>當圓輪恰脫離地面之瞬間，地面正向力 $N = 0$。<br>以接觸點 A 為支點，支持力 $N^{\\prime}$ 通過支點不產生力矩：<br>① 水平外力 $F$ 之力臂為垂直距離：$$d_F = R - h \\quad (\\circlearrowleft \\text{ 逆時針力矩})$$② 重力 $W$ 之力臂為水平距離：$$d_W = \\sqrt{R^2 - (R - h)^2} = \\sqrt{h(2R - h)} \\quad (\\circlearrowright \\text{ 順時針力矩})$$由力矩平衡 $\\sum \\tau_A = 0$：$$F \\cdot (R - h) = W \\cdot \\sqrt{h(2R - h)} \\implies \\mathbf{F_{\\min} = W\\frac{\\sqrt{h(2R - h)}}{R - h}} \\quad \\text{✅ 選 (B)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 29 (Index 28): 力矩 5 任意角度維持平衡之懸掛支點 (q-28)
    # ========================================================
    problems[28]['options'] = [
        '(A) $\\dfrac{W_1}{W_1 + W_2}L$',
        '(B) $\\dfrac{W_2}{W_1 + W_2}L$',
        '(C) $\\dfrac{W_1}{W_2}L$',
        '(D) $\\dfrac{W_2}{W_1}L$',
        '(E) $\\dfrac{1}{2}L$'
    ]
    problems[28]['answer'] = '(A) [W₁ / (W₁ + W₂)] L'

    torque5_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ceiling support -->
  <line x1="280" y1="20" x2="360" y2="20" stroke="#64748b" stroke-width="2.5"/>
  <line x1="320" y1="20" x2="320" y2="130" stroke="#facc15" stroke-width="2"/>
  <text x="328" y="75" fill="#facc15" font-size="11" font-weight="bold">繩張力 T</text>

  <!-- Rod L tilted at theta to horizontal -->
  <line x1="120" y1="210" x2="420" y2="90" stroke="#94a3b8" stroke-width="5" stroke-linecap="round"/>
  <line x1="120" y1="210" x2="220" y2="210" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <path d="M 160,210 A 40,40 0 0,0 156,195" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="170" y="202" fill="#fff" font-size="11">θ</text>

  <!-- Suspension Pivot O at (320, 130) -->
  <circle cx="320" cy="130" r="5" fill="#facc15"/>
  <text x="312" y="152" fill="#facc15" font-size="13" font-weight="bold">O (懸掛支點)</text>

  <!-- Mass W1 at (120, 210) -->
  <circle cx="120" cy="210" r="14" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="120" y="215" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">W₁</text>
  <line x1="120" y1="210" x2="120" y2="270" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="130" y="255" fill="#ff5252" font-size="11" font-weight="bold">W₁ (下)</text>

  <!-- Mass W2 at (420, 90) -->
  <circle cx="420" cy="90" r="16" fill="#1e293b" stroke="#00e676" stroke-width="2.5"/>
  <text x="420" y="95" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">W₂</text>
  <line x1="420" y1="90" x2="420" y2="155" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="430" y="140" fill="#ff5252" font-size="11" font-weight="bold">W₂ (下)</text>

  <!-- Distances -->
  <text x="210" y="160" fill="#00e5ff" font-size="11">距離 (L - x)</text>
  <text x="365" y="100" fill="#00e676" font-size="11">距離 x</text>
</svg>'''

    torque5_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="15" width="490" height="270" rx="10" fill="rgba(15, 23, 42, 0.75)" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="45" y="45" fill="#00e5ff" font-size="13.5" font-weight="bold">💡 任意角度 θ 恆能平衡之物理條件剖析：</text>

  <text x="45" y="80" fill="#f1f5f9" font-size="12.5">設質點 W₂ 與懸掛點 O 之距離為 x，則 W₁ 距 O 點為 (L - x)。</text>

  <text x="45" y="112" fill="#00e676" font-size="12.5" font-weight="bold">以懸掛點 O 為支點之力矩平衡方程式：</text>
  <text x="65" y="137" fill="#f1f5f9" font-size="12">W₁ 之逆時針力矩 = W₂ 之順時針力矩</text>
  <text x="65" y="162" fill="#facc15" font-size="13.5" font-weight="bold">W₁ · (L - x) · cos θ = W₂ · x · cos θ</text>

  <text x="45" y="196" fill="#38bdf8" font-size="12.5" font-weight="bold">角度因子 cos θ 相消（隨遇平衡特性）：</text>
  <text x="65" y="218" fill="#f1f5f9" font-size="12">不論傾角 θ 為何，cos θ 皆可約去 ⟹ W₁(L - x) = W₂ x ⟹ (W₁ + W₂)x = W₁ L</text>

  <rect x="45" y="235" width="450" height="38" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="259" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">O 點與 W₂ 之距離：x = [W₁ / (W₁ + W₂)] L ➔ ✅ 選 (A)</text>
</svg>'''

    torque5_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 懸掛細桿傾角幾何圖</div>
        ''' + torque5_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 隨遇平衡力矩與重心定位並列</div>
        ''' + torque5_svg_fbd + '''
      </div>
    </div>'''

    problems[28]['diagrams'] = [
        { 'label': '📐 原始題圖 (懸掛細桿)', 'svg': torque5_svg_raw },
        { 'label': '💡 隨遇平衡與重心定位解析', 'svg': torque5_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque5_svg_dual }
    ]
    problems[28]['svg'] = torque5_svg_raw
    problems[28]['related'] = [
        { 'id': 'torque2', 'title': '力矩 2：傾斜細桿兩端質點合力矩', 'badge': '力臂分解' },
        { 'id': 'torque3', 'title': '力矩 3：均質桿件傾斜力矩', 'badge': '桿件力矩' },
        { 'id': 'torque7', 'title': '力矩 7：均勻直尺力矩平衡', 'badge': '重心支點' }
    ]
    problems[28]['solutions'] = [
        {
            'title': '【重點解析・任意角度維持隨遇平衡之支點條件】（聯考經典滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・設定未知數與各力之力臂</strong>：<br>設 O 點與質點 $W_2$ 間的距離為 $x$，則 O 點與質點 $W_1$ 間的距離為 $(L - x)$。<br>細桿與水平方向夾角為 $\\theta$，兩質點重力垂直向下，對懸掛支點 O 的水平垂直距離（力臂）分別為：$$d_1 = (L - x)\\cos\\theta \\quad \\text{與} \\quad d_2 = x\\cos\\theta$$',
                '📌 <strong>重點二・建立以 O 點為支點之力矩平衡方程式</strong>：<br>以懸掛點 O 為轉軸，繩張力通過支點不產生力矩：$$\\sum \\tau_O = 0 \\implies W_1 \\cdot (L - x)\\cos\\theta = W_2 \\cdot x\\cos\\theta$$',
                '⚡ <strong>重點三・消去角度因子求得重心位置</strong>：<br>題意說明「<strong>不論傾斜角度 $\\theta$ 為何，細桿恆能維持靜力平衡</strong>」：<br>因 $0^\\circ < \\theta < 90^\\circ$，$\\cos\\theta \\ne 0$，兩邊同除以 $\\cos\\theta$ 得：$$W_1(L - x) = W_2 x \\implies W_1 L - W_1 x = W_2 x$$$$(W_1 + W_2)x = W_1 L \\implies \\mathbf{x = \\frac{W_1}{W_1 + W_2}L} \\quad \\text{✅ 選 (A)}$$<br><em>物理觀點</em>：此平衡位置恰為兩質點系統之<strong>「重心（質心）」</strong>。當懸掛點與重心重合時，重力合力通過支點，故能維持<strong>隨遇平衡</strong>。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 30 (Index 29): 力矩 6 均質木棒懸重臨界翹起力矩 (q-29)
    # ========================================================
    problems[29]['options'] = [
        '(A) $\\dfrac{1}{6}W$',
        '(B) $\\dfrac{1}{4}W$',
        '(C) $\\dfrac{1}{3}W$',
        '(D) $\\dfrac{1}{2}W$',
        '(E) $\\dfrac{2}{3}W$'
    ]
    problems[29]['answer'] = '(D) 1/2 W'

    torque6_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Table surface -->
  <rect x="40" y="180" width="280" height="90" fill="rgba(30, 41, 59, 0.7)" stroke="#475569" stroke-width="2"/>
  <text x="140" y="230" fill="#64748b" font-size="13" font-weight="bold">水平桌面</text>

  <!-- Table Edge P at x = 320 -->
  <circle cx="320" cy="180" r="5" fill="#facc15"/>
  <text x="310" y="205" fill="#facc15" font-size="12" font-weight="bold">桌緣 P</text>

  <!-- Uniform Rod: length 360px from x = 80 to x = 440 -->
  <rect x="80" y="162" width="360" height="18" rx="3" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>
  <text x="190" y="155" fill="#94a3b8" font-size="11">桌面內：⅔ L</text>
  <text x="370" y="155" fill="#38bdf8" font-size="11">伸出：⅓ L</text>

  <!-- Rod Center of Mass at x = 260 -->
  <circle cx="260" cy="171" r="5" fill="#ff5252"/>
  <line x1="260" y1="171" x2="260" y2="245" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="235" y="230" fill="#ff5252" font-size="12" font-weight="bold">W (棒重)</text>

  <!-- Hanging Weight at right end x = 440 -->
  <circle cx="440" cy="171" r="4" fill="#00e676"/>
  <line x1="440" y1="171" x2="440" y2="225" stroke="#00e676" stroke-width="1.8"/>
  <rect x="428" y="225" width="24" height="24" rx="3" fill="#1e293b" stroke="#00e676" stroke-width="2"/>
  <text x="440" y="241" fill="#00e676" font-size="11" font-weight="bold" text-anchor="middle">w</text>
</svg>'''

    torque6_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="15" width="490" height="270" rx="10" fill="rgba(15, 23, 42, 0.75)" stroke="#facc15" stroke-width="1.5"/>
  <text x="45" y="45" fill="#facc15" font-size="13.5" font-weight="bold">💡 均質木棒恰不翹起之臨界力矩平衡：</text>

  <text x="45" y="80" fill="#38bdf8" font-size="12.5" font-weight="bold">1. 臨界翹起之正向力作用點：</text>
  <text x="65" y="103" fill="#f1f5f9" font-size="12">木棒恰不翹起時，桌面對木棒之正向力全部集中於【桌緣 P 點】。</text>

  <text x="45" y="135" fill="#00e676" font-size="12.5" font-weight="bold">2. 計算各力對桌緣 P 點之力臂：</text>
  <text x="65" y="158" fill="#f1f5f9" font-size="12">木棒重心在全棒中點（距右端 ½L），距桌緣 P 之力臂：d₁ = ½L - ⅓L = ⅙L</text>
  <text x="65" y="180" fill="#f1f5f9" font-size="12">右端懸掛砝碼距桌緣 P 之力臂：d₂ = ⅓L</text>

  <rect x="45" y="205" width="450" height="60" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="228" fill="#00e676" font-size="12.5" font-weight="bold" text-anchor="middle">以桌緣 P 為支點列力矩平衡：W · (⅙ L) = w · (⅓ L)</text>
  <text x="270" y="252" fill="#facc15" font-size="13.5" font-weight="bold" text-anchor="middle">砝碼重量：w = W · (⅙ / ⅓) = ½ W ➔ ✅ 選 (D)</text>
</svg>'''

    torque6_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 木棒置桌伸出題圖</div>
        ''' + torque6_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 桌緣臨界支點槓桿平衡並列</div>
        ''' + torque6_svg_fbd + '''
      </div>
    </div>'''

    problems[29]['diagrams'] = [
        { 'label': '📐 原始題圖 (均質木棒置桌)', 'svg': torque6_svg_raw },
        { 'label': '💡 桌緣臨界力矩解析', 'svg': torque6_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque6_svg_dual }
    ]
    problems[29]['svg'] = torque6_svg_raw
    problems[29]['related'] = [
        { 'id': 'problem7', 'title': '範例 7：高架起重車翻覆臨界', 'badge': '力矩翻轉' },
        { 'id': 'torque7', 'title': '力矩 7：均勻直尺力矩平衡', 'badge': '直尺槓桿' },
        { 'id': 'problem11', 'title': '範例 11：木箱滑動與傾倒臨界', 'badge': '臨界正向力' }
    ]
    problems[29]['solutions'] = [
        {
            'title': '【重點解析・均質木棒桌緣臨界翹起力矩求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・均質木棒之重心幾何定位</strong>：<br>木棒為均質，故重心位於全棒幾何中心（距左端 $\\frac{1}{2}L$、距右端 $\\frac{1}{2}L$ 處）。<br>木棒伸出桌面 $\\frac{1}{3}L$，故桌緣 P 距離木棒右端為 $\\frac{1}{3}L$。',
                '📌 <strong>重點二・判斷臨界翹起時正向力作用點</strong>：<br>在右端懸掛砝碼使木棒「恰不翹起」之臨界狀態下，桌面對木棒的支持力向右側邊緣集中，其合力作用點恰在<strong>【桌緣 P 處】</strong>（此時桌緣左側之桌面正向力皆降為 $0$）。',
                '⚡ <strong>重點三・以桌緣 P 為支點列力矩平衡方程式</strong>：<br>① 木棒重心在桌緣 P 左側，力臂為：$$d_1 = \\frac{1}{2}L - \\frac{1}{3}L = \\frac{1}{6}L \\quad (\\circlearrowleft \\text{ 逆時針力矩，防止翹起})$$② 右端砝碼在桌緣 P 右側，力臂為：$$d_2 = \\frac{1}{3}L \\quad (\\circlearrowright \\text{ 順時針力矩，促使翹起})$$對桌緣 P 取力矩 $\\sum \\tau_P = 0$：$$W \\cdot \\left(\\frac{1}{6}L\\right) = w \\cdot \\left(\\frac{1}{3}L\\right) \\implies \\mathbf{w = \\frac{1}{2}W} \\quad \\text{✅ 選 (D)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 31 (Index 30): 力矩 7 107指考均勻直尺力矩平衡 (q-30)
    # ========================================================
    problems[30]['options'] = [
        '(A) $20\\text{ g}$',
        '(B) $30\\text{ g}$',
        '(C) $50\\text{ g}$',
        '(D) $60\\text{ g}$',
        '(E) $70\\text{ g}$'
    ]
    problems[30]['answer'] = '(C) 50 g'

    torque7_svg_raw = '''<svg viewBox="0 0 600 300" style="max-width: 540px;" xmlns="http://www.w3.org/2000/svg">
  <!-- Ruler Body -->
  <rect x="75" y="130" width="450" height="24" rx="3" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>

  <!-- Ticks -->
  <line x1="75" y1="130" x2="75" y2="142" stroke="#64748b" stroke-width="1.5"/>
  <text x="75" y="122" fill="#64748b" font-size="10" text-anchor="middle">0</text>
  <line x1="225" y1="130" x2="225" y2="140" stroke="#64748b" stroke-width="1.5"/>
  <text x="225" y="122" fill="#64748b" font-size="10" text-anchor="middle">10</text>
  <line x1="300" y1="130" x2="300" y2="146" stroke="#ff5252" stroke-width="2"/>
  <text x="300" y="122" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">15 (重心)</text>
  <line x1="375" y1="130" x2="375" y2="146" stroke="#00e676" stroke-width="2"/>
  <text x="375" y="122" fill="#00e676" font-size="11" font-weight="bold" text-anchor="middle">20 (支點)</text>
  <line x1="450" y1="130" x2="450" y2="146" stroke="#00e5ff" stroke-width="2"/>
  <text x="450" y="122" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="middle">25</text>
  <line x1="525" y1="130" x2="525" y2="142" stroke="#64748b" stroke-width="1.5"/>
  <text x="525" y="122" fill="#64748b" font-size="10" text-anchor="middle">30 cm</text>

  <!-- Ruler Center of Mass at 15 cm -> x = 300 -->
  <circle cx="300" cy="142" r="5" fill="#ff5252"/>
  <line x1="300" y1="154" x2="300" y2="225" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="300" y="242" fill="#ff5252" font-size="12" font-weight="bold" text-anchor="middle">W (直尺重)</text>

  <!-- Fulcrum Wedge at 20 cm -> x = 375 -->
  <polygon points="375,154 360,185 390,185" fill="#00e676" stroke="#059669" stroke-width="1.5"/>
  <rect x="350" y="185" width="50" height="15" rx="2" fill="#334155"/>
  <line x1="375" y1="154" x2="375" y2="90" stroke="#00e676" stroke-width="2" marker-end="url(#arr-ex1-green)"/>
  <text x="385" y="102" fill="#00e676" font-size="12" font-weight="bold">N</text>

  <!-- Object at 25 cm -> x = 450 -->
  <rect x="435" y="106" width="30" height="24" rx="3" fill="#1e293b" stroke="#00e5ff" stroke-width="2"/>
  <text x="450" y="122" fill="#00e5ff" font-size="10.5" font-weight="bold" text-anchor="middle">50g</text>
  <line x1="450" y1="154" x2="450" y2="225" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="450" y="242" fill="#ff5252" font-size="12" font-weight="bold" text-anchor="middle">50 gw</text>
</svg>'''

    torque7_svg_fbd = '''<svg viewBox="0 0 600 300" style="max-width: 540px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="15" width="550" height="270" rx="10" fill="rgba(15, 23, 42, 0.75)" stroke="#00e676" stroke-width="1.5"/>
  <text x="45" y="45" fill="#00e676" font-size="13.5" font-weight="bold">💡 【107 指考】均勻直尺力矩平衡運算：</text>

  <text x="45" y="80" fill="#38bdf8" font-size="12.5" font-weight="bold">1. 判定直尺之重心位置：</text>
  <text x="65" y="103" fill="#f1f5f9" font-size="12">均勻直尺全長 30 cm ⟹ 重心位於幾何中心 x = 15 cm 處。</text>

  <text x="45" y="135" fill="#facc15" font-size="12.5" font-weight="bold">2. 以 20 cm 支撐點為支點，計算各力力臂：</text>
  <text x="65" y="158" fill="#f1f5f9" font-size="12">直尺重力 W 之力臂：d₁ = 20 - 15 = 5 cm（在支點左方，產生逆時針力矩）</text>
  <text x="65" y="180" fill="#f1f5f9" font-size="12">小物體 (50 gw) 之力臂：d₂ = 25 - 20 = 5 cm（在支點右方，產生順時針力矩）</text>

  <rect x="45" y="205" width="510" height="60" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.2"/>
  <text x="300" y="228" fill="#facc15" font-size="12.5" font-weight="bold" text-anchor="middle">槓桿原理：W · d₁ = 50 gw · d₂ ⟹ M · (5 cm) = 50 g · (5 cm)</text>
  <text x="300" y="252" fill="#00e676" font-size="13.5" font-weight="bold" text-anchor="middle">直尺質量：M = 50 g ➔ ✅ 選 (C)</text>
</svg>'''

    torque7_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 均勻直尺刻度支撐題圖</div>
        ''' + torque7_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 支撐點支點槓桿平衡並列</div>
        ''' + torque7_svg_fbd + '''
      </div>
    </div>'''

    problems[30]['diagrams'] = [
        { 'label': '📐 原始題圖 (均勻直尺)', 'svg': torque7_svg_raw },
        { 'label': '💡 槓桿力矩平衡解析', 'svg': torque7_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': torque7_svg_dual }
    ]
    problems[30]['svg'] = torque7_svg_raw
    problems[30]['related'] = [
        { 'id': 'torque6', 'title': '力矩 6：均質木棒懸重臨界翹起', 'badge': '重心力臂' },
        { 'id': 'torque5', 'title': '力矩 5：任意角度維持平衡懸掛點', 'badge': '重心隨遇' },
        { 'id': 'exercise5', 'title': '類題 5：雙彈簧吊重平衡', 'badge': '力矩槓桿' }
    ]
    problems[30]['solutions'] = [
        {
            'title': '【重點解析・均勻直尺重心判定與槓桿原理求解】（107指考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・均勻直尺重心判定</strong>：<br>直尺為均勻材質，總長度為 $30\\text{ cm}$，故其重心必位於幾何中心處：$$x_{\\text{重心}} = \\frac{30\\text{ cm}}{2} = 15\\text{ cm}$$設直尺質量為 $M$（重力為 $W = M\\text{ gw}$）。',
                '📌 <strong>重點二・以 20 cm 支撐點為參考支點計算力臂</strong>：<br>支撐點位於 $x = 20\\text{ cm}$ 處（支撐反力 $N$ 通過支點不產生力矩）：<br>① 直尺重力 $W$ 位於 $x = 15\\text{ cm}$（支點左方），力臂為：$$d_1 = 20\\text{ cm} - 15\\text{ cm} = 5\\text{ cm} \\quad (\\circlearrowleft \\text{ 逆時針力矩})$$② 小物體重力 $50\\text{ gw}$ 位於 $x = 25\\text{ cm}$（支點右方），力臂為：$$d_2 = 25\\text{ cm} - 20\\text{ cm} = 5\\text{ cm} \\quad (\\circlearrowright \\text{ 順時針力矩})$$',
                '⚡ <strong>重點三・列出力矩平衡方程式求解直尺質量</strong>：<br>直尺維持水平靜力平衡，順時針力矩等於逆時針力矩：$$W \\cdot d_1 = 50\\text{ gw} \\cdot d_2$$$$M \\cdot (5\\text{ cm}) = 50\\text{ g} \\cdot (5\\text{ cm}) \\implies \\mathbf{M = 50\\text{ g}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 32 (Index 31): 平衡 1 光滑斜面受力方向與正向力剖析 (q-31)
    # ========================================================
    problems[31]['answer'] = '(1) A<br>(2) C'

    equil1_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <polygon points="60,250 460,250 60,90" fill="rgba(30, 41, 59, 0.7)" stroke="#64748b" stroke-width="2"/>
  <path d="M 400,250 A 60,60 0 0,0 420,234" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text x="390" y="242" fill="#fff" font-size="12">θ</text>

  <g transform="translate(240, 178) rotate(-21.8)">
    <rect x="-35" y="-25" width="70" height="50" rx="4" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
    <text x="0" y="6" fill="#00e5ff" font-size="14" font-weight="bold" text-anchor="middle">W</text>
  </g>

  <line x1="240" y1="178" x2="240" y2="265" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="248" y="255" fill="#ff5252" font-size="12" font-weight="bold">重力 W</text>

  <line x1="240" y1="178" x2="160" y2="146" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="145" y="135" fill="#00e676" font-size="11" font-weight="bold">F₁ (沿斜面)</text>

  <line x1="240" y1="178" x2="150" y2="178" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="125" y="195" fill="#facc15" font-size="11" font-weight="bold">F₂ (水平)</text>

  <line x1="240" y1="178" x2="275" y2="90" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arr-ex1-cyan)"/>
  <text x="285" y="105" fill="#38bdf8" font-size="12" font-weight="bold">法線正向力 N</text>
</svg>'''

    equil1_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="40" y="42" fill="#38bdf8" font-size="13.5" font-weight="bold">💡 光滑斜面兩外力狀態下之正向力剖析：</text>

  <text x="40" y="75" fill="#00e676" font-size="12.5" font-weight="bold">問題 (1) 施力 F₁ 沿斜面向上：</text>
  <text x="60" y="98" fill="#f1f5f9" font-size="12">重力分解：垂直斜面分力 W cosθ，平行斜面分力 W sinθ</text>
  <text x="60" y="120" fill="#00e676" font-size="13" font-weight="bold">垂直斜面合力為零 ⟹ N₁ = W cosθ ➔ ✅ 選 (A)</text>

  <text x="40" y="155" fill="#facc15" font-size="12.5" font-weight="bold">問題 (2) 施力 F₂ 沿水平方向：</text>
  <text x="60" y="178" fill="#f1f5f9" font-size="12">外力 F₂、重力 W、正向力 N₂ 三力構成直角封閉三角形（N₂ 為斜邊）：</text>
  <text x="60" y="200" fill="#facc15" font-size="13" font-weight="bold">N₂ cosθ = W ⟹ N₂ = W / cosθ = W secθ ➔ ✅ 選 (C)</text>

  <rect x="40" y="222" width="460" height="48" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.2"/>
  <text x="270" y="242" fill="#94a3b8" font-size="11.5" text-anchor="middle">💡 關鍵結論：沿斜面拉 N₁ &lt; W（減載）；水平推 N₂ &gt; W（增壓負擔）</text>
  <text x="270" y="260" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">N₁ = W cosθ ； N₂ = W / cosθ</text>
</svg>'''

    equil1_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 光滑斜面外力情境圖</div>
        ''' + equil1_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 兩受力狀態正向力對照並列</div>
        ''' + equil1_svg_fbd + '''
      </div>
    </div>'''

    problems[31]['diagrams'] = [
        { 'label': '📐 原始題圖 (光滑斜面)', 'svg': equil1_svg_raw },
        { 'label': '💡 正向力受力分解解析', 'svg': equil1_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil1_svg_dual }
    ]
    problems[31]['svg'] = equil1_svg_raw
    problems[31]['related'] = [
        { 'id': 'problem9', 'title': '範例 9：斜面靜止與等速下滑受力', 'badge': '斜面受力' },
        { 'id': 'exercise7', 'title': '類題 7：光滑斜面跨滑輪平衡', 'badge': '斜面滑輪' },
        { 'id': 'equil2', 'title': '平衡 2：雙斜面跨滑輪平衡比值', 'badge': '斜面平衡' }
    ]
    problems[31]['solutions'] = [
        {
            'title': '【重點解析・光滑斜面受力方向對正向力之深刻影響】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>問題 (1)・沿斜面向上施力 $F_1$ 之正向力剖析</strong>：<br>物體受三力作用：外力 $F_1$（沿斜面向上）、重力 $W$（鉛直向下）、斜面正向力 $N_1$（垂直斜面向上）。<br>將重力沿斜面方向與垂直斜面方向分解：<br>① 平行斜面：$F_1 = W \\sin\\theta$<br>② 垂直斜面：合力為零 $\\implies \\mathbf{N_1 = W \\cos\\theta} \\quad \\text{✅ 選 (A)}$<br><em>結論</em>：此時斜面支持力小於物重 $W$（減載效果）。',
                '⚡ <strong>問題 (2)・沿水平方向施力 $F_2$ 之正向力剖析</strong>：<br>物體受三力作用：水平外力 $F_2$、重力 $W$、垂直斜面正向力 $N_2$。<br>由三力平衡之封閉向量直角三角形可知，正向力 $N_2$ 為直角三角形之斜邊：<br>鉛直方向分力平衡：$$N_2 \\cos\\theta = W \\implies \\mathbf{N_2 = \\frac{W}{\\cos\\theta} = W \\sec\\theta} \\quad \\text{✅ 選 (C)}$$<br><em>結論</em>：水平推力會將物體壓向斜面，導致正向力增大且大於物重 $W$（增壓負擔）。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 33 (Index 32): 平衡 2 雙斜面跨滑輪平衡比值推導 (q-32)
    # ========================================================
    problems[32]['options'] = [
        '(A) $\\dfrac{\\sin\\theta_1}{\\sin\\theta_2}$',
        '(B) $\\dfrac{\\sin\\theta_2}{\\sin\\theta_1}$',
        '(C) $\\dfrac{\\cos\\theta_1}{\\cos\\theta_2}$',
        '(D) $\\dfrac{\\cos\\theta_2}{\\cos\\theta_1}$',
        '(E) $\\dfrac{\\tan\\theta_1}{\\tan\\theta_2}$'
    ]
    problems[32]['answer'] = '(B) sinθ₂ / sinθ₁'

    equil2_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <polygon points="40,240 500,240 270,70" fill="rgba(30, 41, 59, 0.7)" stroke="#64748b" stroke-width="2"/>
  <path d="M 100,240 A 60,60 0 0,0 120,215" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text x="125" y="235" fill="#fff" font-size="12">θ₁</text>

  <path d="M 440,240 A 60,60 0 0,1 420,215" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text x="400" y="235" fill="#fff" font-size="12">θ₂</text>

  <circle cx="270" cy="70" r="14" fill="#334155" stroke="#facc15" stroke-width="2"/>
  <circle cx="270" cy="70" r="4" fill="#facc15"/>

  <line x1="165" y1="148" x2="258" y2="62" stroke="#facc15" stroke-width="2"/>
  <line x1="282" y1="62" x2="375" y2="148" stroke="#facc15" stroke-width="2"/>

  <g transform="translate(165, 148) rotate(-36.5)">
    <rect x="-24" y="-18" width="48" height="36" rx="4" fill="#1e293b" stroke="#00e5ff" stroke-width="2"/>
    <text x="0" y="5" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">W₁</text>
  </g>
  <line x1="165" y1="148" x2="165" y2="215" stroke="#ff5252" stroke-width="2.2" marker-end="url(#arr-ex1-red)"/>
  <text x="145" y="205" fill="#ff5252" font-size="11" font-weight="bold">W₁</text>

  <g transform="translate(375, 148) rotate(36.5)">
    <rect x="-24" y="-18" width="48" height="36" rx="4" fill="#1e293b" stroke="#00e676" stroke-width="2"/>
    <text x="0" y="5" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">W₂</text>
  </g>
  <line x1="375" y1="148" x2="375" y2="215" stroke="#ff5252" stroke-width="2.2" marker-end="url(#arr-ex1-red)"/>
  <text x="385" y="205" fill="#ff5252" font-size="11" font-weight="bold">W₂</text>
</svg>'''

    equil2_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="45" fill="#00e676" font-size="13.5" font-weight="bold">💡 雙斜面輕繩張力傳遞與下滑力平衡剖析：</text>

  <text x="40" y="80" fill="#00e5ff" font-size="12.5" font-weight="bold">1. 左側物體 W₁ 之沿斜面平衡：</text>
  <text x="60" y="103" fill="#f1f5f9" font-size="12">沿斜面向下之重力分力與輕繩向上拉力 T 平衡：</text>
  <text x="60" y="125" fill="#00e5ff" font-size="13" font-weight="bold">T = W₁ · sin θ₁</text>

  <text x="40" y="158" fill="#facc15" font-size="12.5" font-weight="bold">2. 右側物體 W₂ 之沿斜面平衡：</text>
  <text x="60" y="180" fill="#f1f5f9" font-size="12">沿斜面向下之重力分力亦與輕繩向上拉力 T 平衡：</text>
  <text x="60" y="202" fill="#facc15" font-size="13" font-weight="bold">T = W₂ · sin θ₂</text>

  <rect x="40" y="222" width="460" height="48" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="242" fill="#f1f5f9" font-size="12" text-anchor="middle">由繩張力相等：W₁ · sin θ₁ = W₂ · sin θ₂</text>
  <text x="270" y="260" fill="#00e676" font-size="13.5" font-weight="bold" text-anchor="middle">重量比值：W₁ / W₂ = sin θ₂ / sin θ₁ ➔ ✅ 選 (B)</text>
</svg>'''

    equil2_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 雙斜面跨滑輪題圖</div>
        ''' + equil2_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 繩張力與重力下滑分力平衡並列</div>
        ''' + equil2_svg_fbd + '''
      </div>
    </div>'''

    problems[32]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙斜面跨滑輪)', 'svg': equil2_svg_raw },
        { 'label': '💡 繩張力與下滑平衡解析', 'svg': equil2_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil2_svg_dual }
    ]
    problems[32]['svg'] = equil2_svg_raw
    problems[32]['related'] = [
        { 'id': 'exercise7', 'title': '類題 7：光滑斜面跨滑輪雙物體平衡', 'badge': '滑輪系統' },
        { 'id': 'equil1', 'title': '平衡 1：光滑斜面正向力剖析', 'badge': '斜面分力' },
        { 'id': 'problem9', 'title': '範例 9：斜面受力平衡', 'badge': '斜面平衡' }
    ]
    problems[32]['solutions'] = [
        {
            'title': '【重點解析・雙斜面輕繩張力傳遞與下滑平衡方程式】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・同一直線輕繩張力處處相等</strong>：<br>滑輪為輕質且光滑，輕繩兩端之張力量值恆相等，設為 $T$。',
                '📌 <strong>重點二・分別對兩物體建立沿斜面平衡式</strong>：<br>雙斜面均為光滑，物體無摩擦力：<br>① 對左側物體（重 $W_1$、斜角 $\\theta_1$）：$$T = W_1 \\sin\\theta_1$$② 對右側物體（重 $W_2$、斜角 $\\theta_2$）：$$T = W_2 \\sin\\theta_2$$',
                '⚡ <strong>重點三・聯立求解重量比值</strong>：<br>由繩張力相等建立等式：$$W_1 \\sin\\theta_1 = W_2 \\sin\\theta_2 \\implies \\mathbf{\\frac{W_1}{W_2} = \\frac{\\sin\\theta_2}{\\sin\\theta_1}} \\quad \\text{✅ 選 (B)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 34 (Index 33): 平衡 3 斜向推力與地面全作用力 (q-33)
    # ========================================================
    problems[33]['options'] = [
        '(A) $W + F\\sin 30^\\circ$',
        '(B) $F\\cos 30^\\circ$',
        '(C) $\\sqrt{W^2 + F^2}$',
        '(D) $\\sqrt{\\left(W + \\frac{1}{2}F\\right)^2 + \\left(\\frac{\\sqrt{3}}{2}F\\right)^2}$（即 $\\sqrt{W^2 + WF + F^2}$）',
        '(E) $W$'
    ]
    problems[33]['answer'] = '(D) √(W² + WF + F²)'

    equil3_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="40" y1="230" x2="500" y2="230" stroke="#64748b" stroke-width="2.5"/>
  <rect x="40" y="230" width="460" height="45" fill="rgba(30, 41, 59, 0.4)"/>

  <rect x="225" y="130" width="90" height="100" rx="4" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="270" y="185" fill="#00e5ff" font-size="16" font-weight="bold" text-anchor="middle">W</text>

  <line x1="140" y1="105" x2="225" y2="155" stroke="#facc15" stroke-width="3.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="155" y="100" fill="#facc15" font-size="13" font-weight="bold">推力 F (30°)</text>
  <line x1="140" y1="105" x2="210" y2="105" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <path d="M 180,105 A 40,40 0 0,1 195,115" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="200" y="118" fill="#fff" font-size="11">30°</text>

  <line x1="270" y1="180" x2="270" y2="275" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="280" y="265" fill="#ff5252" font-size="12" font-weight="bold">W</text>

  <line x1="270" y1="230" x2="200" y2="155" stroke="#00e676" stroke-width="3" marker-end="url(#arr-ex1-green)"/>
  <text x="175" y="165" fill="#00e676" font-size="13" font-weight="bold">全作用力 R</text>
</svg>'''

    equil3_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#facc15" stroke-width="1.5"/>
  <text x="40" y="42" fill="#facc15" font-size="13.5" font-weight="bold">💡 地面全作用力（正向力 N 與靜摩擦力 fs 合力）解析：</text>

  <text x="40" y="75" fill="#38bdf8" font-size="12.5" font-weight="bold">1. 分解外力與建立直角分量平衡：</text>
  <text x="60" y="98" fill="#f1f5f9" font-size="12">水平向右推力分量：Fx = F · cos 30° = (√3 / 2) F</text>
  <text x="60" y="120" fill="#f1f5f9" font-size="12">鉛直向下推力分量：Fy = F · sin 30° = (1 / 2) F</text>

  <text x="40" y="152" fill="#00e676" font-size="12.5" font-weight="bold">2. 地面分量受力：</text>
  <text x="60" y="174" fill="#f1f5f9" font-size="12">水平靜摩擦力向左：fs = Fx = (√3 / 2) F</text>
  <text x="60" y="196" fill="#f1f5f9" font-size="12">地面正向力向上：N = W + Fy = W + (1 / 2) F</text>

  <rect x="40" y="215" width="460" height="55" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="235" fill="#f1f5f9" font-size="11.5" text-anchor="middle">全作用力 R = √(N² + fs²) = √[(W + ½F)² + (√3/2 F)²]</text>
  <text x="270" y="255" fill="#00e676" font-size="13.5" font-weight="bold" text-anchor="middle">R = √(W² + WF + F²) ➔ ✅ 選 (D)</text>
</svg>'''

    equil3_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 斜向推力原情境圖</div>
        ''' + equil3_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 地面全作用力合成解析並列</div>
        ''' + equil3_svg_fbd + '''
      </div>
    </div>'''

    problems[33]['diagrams'] = [
        { 'label': '📐 原始題圖 (斜向推力)', 'svg': equil3_svg_raw },
        { 'label': '💡 地面全作用力解析', 'svg': equil3_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil3_svg_dual }
    ]
    problems[33]['svg'] = equil3_svg_raw
    problems[33]['related'] = [
        { 'id': 'problem9', 'title': '範例 9：斜面地面全作用力', 'badge': '全接觸力' },
        { 'id': 'exercise6', 'title': '類題 6：兩分力垂直與反向合力', 'badge': '正交分解' },
        { 'id': 'problem10', 'title': '範例 10：梯子靠牆地面接觸力', 'badge': '接觸力合成' }
    ]
    problems[33]['solutions'] = [
        {
            'title': '【重點解析・「地面全作用力」物理定義與正交分量合成】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・嚴格辨析「地面全作用力」之定義</strong>：<br>地面對木塊的作用力包含兩部分：鉛直向上之<strong>正向力 $N$</strong> 與水平向左之<strong>靜摩擦力 $f_s$</strong>。<br>「地面作用力 $\\vec{R}$」即為兩者之向量和：$$\\vec{R} = \\vec{N} + \\vec{f}_s \\implies R = \\sqrt{N^2 + f_s^2}$$',
                '📌 <strong>重點二・將斜向外力 $F$ 正交分解求分量</strong>：<br>外力 $F$ 與水平夾角為 $30^\\circ$ 斜向下推：<br>① 水平分力：$F_x = F\\cos 30^\\circ = \\frac{\\sqrt{3}}{2}F$（向右）<br>② 鉛直分力：$F_y = F\\sin 30^\\circ = \\frac{1}{2}F$（向下）<br>由木塊靜力平衡條件：<br>水平方向：$f_s = F_x = \\frac{\\sqrt{3}}{2}F$<br>鉛直方向：$N = W + F_y = W + \\frac{1}{2}F$',
                '⚡ <strong>重點三・合成求地面全作用力之量值</strong>：<br>代入勾股定理：$$R = \\sqrt{\\left(W + \\frac{1}{2}F\\right)^2 + \\left(\\frac{\\sqrt{3}}{2}F\\right)^2}$$$$= \\sqrt{W^2 + 2 \\cdot W \\cdot \\frac{1}{2}F + \\frac{1}{4}F^2 + \\frac{3}{4}F^2} = \\mathbf{\\sqrt{W^2 + WF + F^2}} \\quad \\text{✅ 選 (D)}$$<br><em>等效速解法</em>：由三力平衡 $\\vec{R} + \\vec{W} + \\vec{F} = 0 \\implies \\vec{R} = -(\\vec{W} + \\vec{F})$。因此 $R$ 之量值等於重力 $W$ 與外力 $F$ 之合力（夾角 $60^\\circ$），由餘弦定理直接得 $\\sqrt{W^2 + F^2 + 2WF\\cos 60^\\circ} = \\sqrt{W^2 + WF + F^2}$。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 35 (Index 34): 平衡 4 天花板三繩吊球張力 (q-34)
    # ========================================================
    problems[34]['options'] = [
        '(A) $\\dfrac{1}{2}mg$',
        '(B) $\\dfrac{1}{\\sqrt{3}}mg$',
        '(C) $mg$',
        '(D) $2mg$'
    ]
    problems[34]['answer'] = '(C) mg'

    equil4_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="60" y1="40" x2="480" y2="40" stroke="#64748b" stroke-width="2.5"/>

  <circle cx="130" cy="40" r="5" fill="#facc15"/>
  <text x="120" y="30" fill="#facc15" font-size="13" font-weight="bold">A</text>
  <circle cx="410" cy="40" r="5" fill="#facc15"/>
  <text x="415" y="30" fill="#facc15" font-size="13" font-weight="bold">B</text>

  <line x1="130" y1="52" x2="410" y2="52" stroke="#64748b" stroke-width="1" stroke-dasharray="3,3"/>
  <text x="270" y="65" fill="#64748b" font-size="11" text-anchor="middle">相距 √3 l</text>

  <line x1="130" y1="40" x2="270" y2="120" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="180" y="95" fill="#00e5ff" font-size="12" font-weight="bold">繩 AC = l</text>

  <line x1="410" y1="40" x2="270" y2="120" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="345" y="95" fill="#00e5ff" font-size="12" font-weight="bold">繩 BC = l</text>

  <circle cx="270" cy="120" r="5" fill="#facc15"/>
  <text x="282" y="125" fill="#facc15" font-size="13" font-weight="bold">C</text>

  <line x1="270" y1="120" x2="270" y2="220" stroke="#facc15" stroke-width="2"/>
  <text x="280" y="170" fill="#facc15" font-size="11" font-weight="bold">繩 CD</text>

  <circle cx="270" cy="235" r="15" fill="#1e293b" stroke="#ff5252" stroke-width="2.5"/>
  <text x="270" y="240" fill="#ff5252" font-size="12" font-weight="bold" text-anchor="middle">D (m)</text>
  <line x1="270" y1="250" x2="270" y2="285" stroke="#ff5252" stroke-width="2" marker-end="url(#arr-ex1-red)"/>
  <text x="285" y="280" fill="#ff5252" font-size="11" font-weight="bold">mg</text>
</svg>'''

    equil4_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e5ff" font-size="13.5" font-weight="bold">💡 等腰幾何角度推導與結點 C 受力平衡：</text>

  <text x="40" y="75" fill="#facc15" font-size="12.5" font-weight="bold">1. 幾何邊長判定懸繩夾角：</text>
  <text x="60" y="98" fill="#f1f5f9" font-size="12">等腰 △ABC 底邊長 √3 l，兩腰長皆為 l。過 C 作垂直高線平分底邊：</text>
  <text x="60" y="120" fill="#facc15" font-size="13" font-weight="bold">cos θ = (½ · √3 l) / l = √3 / 2 ⟹ θ = 30°（與天花板夾角）</text>

  <text x="40" y="152" fill="#00e676" font-size="12.5" font-weight="bold">2. 結點 C 鉛直受力平衡：</text>
  <text x="60" y="174" fill="#f1f5f9" font-size="12">兩斜繩張力對稱相等 TAC = TBC = T；向上垂直分量總和平衡重力 mg：</text>
  <text x="60" y="196" fill="#00e676" font-size="13" font-weight="bold">2 · T · sin 30° = mg ⟹ 2 · T · (½) = mg</text>

  <rect x="40" y="215" width="460" height="52" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.2"/>
  <text x="270" y="235" fill="#f1f5f9" font-size="12" text-anchor="middle">頂角 ∠ACB = 120°，兩繩與鉛垂夾角皆為 60°（構成正三角形受力封閉圈）</text>
  <text x="270" y="255" fill="#facc15" font-size="13.5" font-weight="bold" text-anchor="middle">繩 AC 張力：TAC = mg ➔ ✅ 選 (C)</text>
</svg>'''

    equil4_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 懸繩三釘幾何圖</div>
        ''' + equil4_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 結點受力平衡與角度對照並列</div>
        ''' + equil4_svg_fbd + '''
      </div>
    </div>'''

    problems[34]['diagrams'] = [
        { 'label': '📐 原始題圖 (天花板三繩吊球)', 'svg': equil4_svg_raw },
        { 'label': '💡 結點受力平衡解析', 'svg': equil4_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil4_svg_dual }
    ]
    problems[34]['svg'] = equil4_svg_raw
    problems[34]['related'] = [
        { 'id': 'problem3', 'title': '範例 3：三線拉銅環拉密定理', 'badge': '拉密定理' },
        { 'id': 'practice', 'title': '自主測驗：37-53 雙繩懸吊張力', 'badge': '節點平衡' },
        { 'id': 'exercise7', 'title': '類題 7：跨滑輪雙物體平衡', 'badge': '繩索張力' }
    ]
    problems[34]['solutions'] = [
        {
            'title': '【重點解析・等腰三角形幾何角辨識與結點共點力平衡】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・利用三角形邊長幾何求出繩與水平線夾角</strong>：<br>天花板兩固定釘相距 $AB = \\sqrt{3}l$，兩懸繩長 $AC = l, BC = l$。<br>$\\triangle ABC$ 為等腰三角形，作高線垂直底邊 $AB$ 於中點 $H$：$$AH = \\frac{\\sqrt{3}}{2}l$$在直角 $\\triangle AHC$ 中：$$\\cos\\angle CAH = \\frac{AH}{AC} = \\frac{\\frac{\\sqrt{3}}{2}l}{l} = \\frac{\\sqrt{3}}{2} \\implies \\angle CAH = 30^\\circ$$因此兩繩與天花板水平夾角皆為 $30^\\circ$，頂角 $\\angle ACB = 120^\\circ$。',
                '📌 <strong>重點二・分析結點 C 之共點力平衡</strong>：<br>結點 C 連接三條輕繩：<br>① 向下繩 CD：懸掛小球，張力 $T_{CD} = mg$<br>② 斜向繩 AC 與 BC：由左右對稱性，張力必相等 $T_{AC} = T_{BC} = T$',
                '⚡ <strong>重點三・鉛直方向受力平衡列式求解</strong>：<br>兩斜繩向上鉛直分力之和平衡向下重力：$$2 \\cdot T \\sin 30^\\circ = mg \\implies 2 \\cdot T \\cdot \\frac{1}{2} = mg$$$$\\mathbf{T_{AC} = mg} \\quad \\text{✅ 選 (C)}$$<br><em>向量封閉圖觀點</em>：兩繩張力與鉛垂線各夾 $60^\\circ$，三力間之夾角皆為 $120^\\circ$，構成<strong>正三角形封閉力圈</strong>，故三力量值皆相等且等於 $mg$。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 36 (Index 35): 平衡 5 雙光滑斜板圓球支持力 (q-35)
    # ========================================================
    problems[35]['options'] = [
        '(A) $N_甲 = (\\sqrt{3} - 1)W, \\quad N_乙 = \\dfrac{\\sqrt{6} - \\sqrt{2}}{2}W$',
        '(B) $N_甲 = (\\sqrt{3} - 1)W, \\quad N_乙 = \\dfrac{3\\sqrt{2} - \\sqrt{6}}{2}W$',
        '(C) $N_甲 = \\dfrac{\\sqrt{3}}{2}W, \\quad N_乙 = \\dfrac{\\sqrt{2}}{2}W$',
        '(D) $N_甲 = (\\sqrt{3} + 1)W, \\quad N_乙 = \\dfrac{3\\sqrt{2} + \\sqrt{6}}{2}W$'
    ]
    problems[35]['answer'] = '(B) N甲 = (√3 - 1)W, N乙 = (3√2 - √6)/2 W'

    equil5_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="50" y1="250" x2="490" y2="250" stroke="#64748b" stroke-width="2"/>

  <line x1="220" y1="250" x2="80" y2="70" stroke="#00e5ff" stroke-width="4"/>
  <text x="90" y="90" fill="#00e5ff" font-size="13" font-weight="bold">甲板 (60°)</text>
  <path d="M 180,250 A 40,40 0 0,1 190,225" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="185" y="240" fill="#fff" font-size="11">60°</text>

  <line x1="220" y1="250" x2="400" y2="70" stroke="#00e676" stroke-width="4"/>
  <text x="380" y="90" fill="#00e676" font-size="13" font-weight="bold">乙板 (45°)</text>
  <path d="M 260,250 A 40,40 0 0,0 250,230" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="255" y="240" fill="#fff" font-size="11">45°</text>

  <circle cx="235" cy="145" r="65" fill="rgba(30, 41, 59, 0.7)" stroke="#facc15" stroke-width="2.5"/>
  <circle cx="235" cy="145" r="4" fill="#facc15"/>
  <text x="235" y="135" fill="#facc15" font-size="13" font-weight="bold" text-anchor="middle">球心 O</text>

  <line x1="235" y1="145" x2="235" y2="240" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="245" y="225" fill="#ff5252" font-size="12" font-weight="bold">重力 W</text>

  <line x1="178" y1="178" x2="235" y2="145" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="165" y="165" fill="#00e5ff" font-size="12" font-weight="bold">N_甲</text>

  <line x1="281" y1="191" x2="235" y2="145" stroke="#00e676" stroke-width="2.5"/>
  <text x="290" y="180" fill="#00e676" font-size="12" font-weight="bold">N_乙</text>
</svg>'''

    equil5_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 雙板法線角判定與三力平衡聯立求解：</text>

  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 判定兩板支持力之法線方向夾角：</text>
  <text x="60" y="94" fill="#f1f5f9" font-size="12">甲板傾角 60° ⟹ 法線支持力 N_甲 與水平夾角 30°（斜向右上）</text>
  <text x="60" y="114" fill="#f1f5f9" font-size="12">乙板傾角 45° ⟹ 法線支持力 N_乙 與水平夾角 45°（斜向左上）</text>

  <text x="40" y="145" fill="#00e5ff" font-size="12.5" font-weight="bold">2. 水平方向平衡聯立：</text>
  <text x="60" y="167" fill="#f1f5f9" font-size="12">N_甲 · cos 30° = N_乙 · cos 45° ⟹ N_乙 = √(3/2) N_甲</text>

  <text x="40" y="195" fill="#38bdf8" font-size="12.5" font-weight="bold">3. 鉛直方向平衡求解支持力：</text>
  <text x="60" y="217" fill="#f1f5f9" font-size="12">N_甲 · sin 30° + N_乙 · sin 45° = W ⟹ ½ N_甲 (1 + √3) = W</text>

  <rect x="40" y="232" width="460" height="42" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="248" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">N_甲 = (√3 - 1) W</text>
  <text x="270" y="265" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">N_乙 = ½ (3√2 - √6) W ➔ ✅ 選 (B)</text>
</svg>'''

    equil5_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 雙斜板架圓球題圖</div>
        ''' + equil5_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 法線受力聯立求解並列</div>
        ''' + equil5_svg_fbd + '''
      </div>
    </div>'''

    problems[35]['diagrams'] = [
        { 'label': '📐 原始題圖 (雙斜板圓球)', 'svg': equil5_svg_raw },
        { 'label': '💡 法線支持力平衡解析', 'svg': equil5_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil5_svg_dual }
    ]
    problems[35]['svg'] = equil5_svg_raw
    problems[35]['related'] = [
        { 'id': 'problem5', 'title': '範例 5：雙球系統正向力分析', 'badge': '球體平衡' },
        { 'id': 'problem3', 'title': '範例 3：三線拉銅環拉密定理', 'badge': '拉密定理' },
        { 'id': 'equil1', 'title': '平衡 1：光滑斜面正向力剖析', 'badge': '法向支持力' }
    ]
    problems[35]['solutions'] = [
        {
            'title': '【重點解析・雙斜板接觸法線角判定與三力平衡聯立】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・判定甲、乙兩板支持力之法線方向夾角</strong>：<br>圓球受三力平衡：鉛直向下之重力 $W$、甲板支持力 $N_\\text{甲}$、乙板支持力 $N_\\text{乙}$。<br>支持力必沿接觸點法線指向圓心：<br>① 甲板與水平夾角為 $60^\\circ$ $\\implies$ 其法線 $N_\\text{甲}$ 與水平夾角為 $90^\\circ - 60^\\circ = 30^\\circ$（斜向右上）<br>② 乙板與水平夾角為 $45^\\circ$ $\\implies$ 其法線 $N_\\text{乙}$ 與水平夾角為 $90^\\circ - 45^\\circ = 45^\\circ$（斜向左上）',
                '📌 <strong>重點二・建立水平與鉛直平衡方程式</strong>：<br>① 水平方向合力為零：$$N_\\text{甲}\\cos 30^\\circ = N_\\text{乙}\\cos 45^\\circ \\implies N_\\text{甲}\\frac{\\sqrt{3}}{2} = N_\\text{乙}\\frac{\\sqrt{2}}{2} \\implies N_\\text{乙} = \\sqrt{\\frac{3}{2}}N_\\text{甲}$$② 鉛直方向合力為零：$$N_\\text{甲}\\sin 30^\\circ + N_\\text{乙}\\sin 45^\\circ = W$$',
                '⚡ <strong>重點三・代入聯立並有理化求解</strong>：<br>將 $N_\\text{乙} = \\sqrt{\\frac{3}{2}}N_\\text{甲}$ 代入鉛直平衡式：$$\\frac{1}{2}N_\\text{甲} + \\frac{\\sqrt{2}}{2}\\left(\\sqrt{\\frac{3}{2}}N_\\text{甲}\\right) = W \\implies \\frac{1 + \\sqrt{3}}{2}N_\\text{甲} = W$$$$N_\\text{甲} = \\frac{2}{\\sqrt{3} + 1}W = \\frac{2(\\sqrt{3} - 1)}{(\\sqrt{3} + 1)(\\sqrt{3} - 1)}W = \\mathbf{(\\sqrt{3} - 1)W}$$再求 $N_\\text{乙}$：$$N_\\text{乙} = \\sqrt{\\frac{3}{2}}(\\sqrt{3} - 1)W = \\frac{\\sqrt{3}}{\\sqrt{2}}(\\sqrt{3} - 1)W = \\frac{3 - \\sqrt{3}}{\\sqrt{2}}W = \\mathbf{\\frac{3\\sqrt{2} - \\sqrt{6}}{2}W} \\quad \\text{✅ 選 (B)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 37 (Index 36): 平衡 6 雙端水平懸掛彈簧吊重平衡 (q-36)
    # ========================================================
    problems[36]['options'] = [
        '(A) $300\\text{ g}$',
        '(B) $150\\text{ g}$',
        '(C) $120\\text{ g}$',
        '(D) $100\\text{ g}$',
        '(E) $50\\text{ g}$'
    ]
    problems[36]['answer'] = '(C) 120 g'

    equil6_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="90" y1="50" x2="450" y2="50" stroke="#64748b" stroke-width="2.5"/>
  <circle cx="110" cy="50" r="5" fill="#facc15"/>
  <text x="100" y="40" fill="#facc15" font-size="13" font-weight="bold">A</text>
  <circle cx="430" cy="50" r="5" fill="#facc15"/>
  <text x="435" y="40" fill="#facc15" font-size="13" font-weight="bold">B</text>

  <line x1="110" y1="30" x2="430" y2="30" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="270" y="25" fill="#64748b" font-size="11" text-anchor="middle">兩端水平相距 40 cm</text>

  <line x1="110" y1="50" x2="430" y2="50" stroke="#475569" stroke-width="2" stroke-dasharray="4,4"/>

  <line x1="110" y1="50" x2="270" y2="170" stroke="#00e5ff" stroke-width="3"/>
  <text x="175" y="100" fill="#00e5ff" font-size="12" font-weight="bold">伸長後 L = 25 cm</text>

  <line x1="430" y1="50" x2="270" y2="170" stroke="#00e5ff" stroke-width="3"/>
  <text x="365" y="100" fill="#00e5ff" font-size="12" font-weight="bold">L = 25 cm</text>

  <line x1="270" y1="50" x2="270" y2="170" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="278" y="115" fill="#facc15" font-size="11" font-weight="bold">垂降 h = 15 cm</text>

  <circle cx="270" cy="170" r="5" fill="#facc15"/>

  <rect x="250" y="195" width="40" height="36" rx="4" fill="#1e293b" stroke="#00e676" stroke-width="2.5"/>
  <text x="270" y="218" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">M</text>
  <line x1="270" y1="170" x2="270" y2="195" stroke="#facc15" stroke-width="2"/>
  <line x1="270" y1="231" x2="270" y2="270" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="282" y="265" fill="#ff5252" font-size="12" font-weight="bold">W = Mg</text>
</svg>'''

    equil6_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 彈簧對稱拉伸幾何與中央懸重力平衡剖析：</text>

  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 原彈簧常數 k₀ 與兩半分割彈簧常數 k：</text>
  <text x="60" y="94" fill="#f1f5f9" font-size="12">原彈簧：k₀ = 100 gw / 10 cm = 10 gw/cm。中央懸掛分成兩半（各長 L₀ = 20 cm）：</text>
  <text x="60" y="114" fill="#facc15" font-size="12.5" font-weight="bold">長度減半 ⟹ 彈力常數加倍：k = 2 k₀ = 20 gw/cm</text>

  <text x="40" y="145" fill="#00e5ff" font-size="12.5" font-weight="bold">2. 直角幾何（3:4:5）求伸長量與彈力 F：</text>
  <text x="60" y="167" fill="#f1f5f9" font-size="12">拉伸後長度：L = √(20² + 15²) = 25 cm ⟹ 伸長量 Δx = 25 - 20 = 5 cm</text>
  <text x="60" y="187" fill="#00e5ff" font-size="12.5" font-weight="bold">單側彈簧彈力：F = k · Δx = 20 gw/cm × 5 cm = 100 gw</text>

  <rect x="40" y="210" width="460" height="60" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="232" fill="#f1f5f9" font-size="12" text-anchor="middle">兩側向上鉛直分量共同支撐物重：W = 2 · F · sin φ = 2 · (100 gw) · (15/25)</text>
  <text x="270" y="254" fill="#00e676" font-size="14" font-weight="bold" text-anchor="middle">物體質量：M = 120 g ➔ ✅ 選 (C)</text>
</svg>'''

    equil6_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 兩端懸掛彈簧吊重題圖</div>
        ''' + equil6_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 分割彈簧常數與受力平衡並列</div>
        ''' + equil6_svg_fbd + '''
      </div>
    </div>'''

    problems[36]['diagrams'] = [
        { 'label': '📐 原始題圖 (彈簧吊重)', 'svg': equil6_svg_raw },
        { 'label': '💡 彈簧分割與受力平衡解析', 'svg': equil6_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil6_svg_dual }
    ]
    problems[36]['svg'] = equil6_svg_raw
    problems[36]['related'] = [
        { 'id': 'problem1', 'title': '範例 1：彈簧對折與力常數加倍', 'badge': '虎克定律' },
        { 'id': 'problem4', 'title': '範例 4：垂直彈簧懸吊受力', 'badge': '彈簧平衡' },
        { 'id': 'practice', 'title': '自主測驗：37-53 懸吊系統', 'badge': '對稱平衡' }
    ]
    problems[36]['solutions'] = [
        {
            'title': '【重點解析・彈簧對折分割常數加倍與 3:4:5 幾何平衡求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・計算原彈簧力常數與分割後力常數</strong>：<br>原彈簧長 $40\\text{ cm}$，掛 $100\\text{ g}$ 伸長 $10\\text{ cm}$：$$k_0 = \\frac{100\\text{ gw}}{10\\text{ cm}} = 10\\text{ gw/cm}$$將彈簧兩端固定於相距 $40\\text{ cm}$ 處並於中央懸物，彈簧被分成左右兩段對稱半簧，每段原長：$$L_0 = \\frac{40\\text{ cm}}{2} = 20\\text{ cm}$$因彈簧長度減半，力常數加倍：$$k = 2 k_0 = 2 \\times 10\\text{ gw/cm} = 20\\text{ gw/cm}$$',
                '📌 <strong>重點二・直角幾何計算每段彈簧之伸長量與彈力</strong>：<br>兩固定端水平半距為 $20\\text{ cm}$，中央物體垂降 $15\\text{ cm}$。<br>由勾股定理（$3:4:5$ 直角三角形），拉伸後彈簧長度為：$$L = \\sqrt{20^2 + 15^2} = 25\\text{ cm}$$每半彈簧之伸長量：$$\\Delta x = L - L_0 = 25\\text{ cm} - 20\\text{ cm} = 5\\text{ cm}$$單側彈力為：$$F = k \\cdot \\Delta x = 20\\text{ gw/cm} \\times 5\\text{ cm} = 100\\text{ gw}$$',
                '⚡ <strong>重點三・鉛直受力平衡求物體質量</strong>：<br>彈簧與水平線夾角之正弦值為：$$\\sin\\phi = \\frac{15}{25} = \\frac{3}{5}$$兩側彈簧向上鉛直分力共同支撐懸掛重物：$$W = 2 \\cdot F\\sin\\phi = 2 \\times 100\\text{ gw} \\times \\frac{3}{5} = \\mathbf{120\\text{ gw}} \\implies \\mathbf{M = 120\\text{ g}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 38 (Index 37): 平衡 8 88聯考對摺細繩張開最大距離 (q-37)
    # ========================================================
    problems[37]['options'] = [
        '(A) $50\\text{ cm}$',
        '(B) $50\\sqrt{2}\\text{ cm}$',
        '(C) $50\\sqrt{3}\\text{ cm}$',
        '(D) $100\\text{ cm}$',
        '(E) $60\\text{ cm}$'
    ]
    problems[37]['answer'] = '(C) 50√3 cm'

    equil8_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <circle cx="130" cy="70" r="7" fill="#facc15"/>
  <text x="110" y="65" fill="#facc15" font-size="12" font-weight="bold">左手</text>
  <circle cx="410" cy="70" r="7" fill="#facc15"/>
  <text x="425" y="65" fill="#facc15" font-size="12" font-weight="bold">右手</text>

  <line x1="130" y1="50" x2="410" y2="50" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="270" y="42" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">最大張開距離 d_max</text>

  <line x1="130" y1="70" x2="270" y2="150" stroke="#00e5ff" stroke-width="3"/>
  <text x="180" y="125" fill="#00e5ff" font-size="12" font-weight="bold">繩長 50 cm</text>

  <line x1="410" y1="70" x2="270" y2="150" stroke="#00e5ff" stroke-width="3"/>
  <text x="350" y="125" fill="#00e5ff" font-size="12" font-weight="bold">繩長 50 cm</text>

  <line x1="130" y1="70" x2="270" y2="70" stroke="#64748b" stroke-width="1" stroke-dasharray="3,3"/>
  <path d="M 160,70 A 30,30 0 0,1 155,85" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="170" y="85" fill="#fff" font-size="11">θ</text>

  <circle cx="270" cy="150" r="5" fill="#facc15"/>
  <rect x="250" y="170" width="40" height="34" rx="4" fill="#1e293b" stroke="#ff5252" stroke-width="2.5"/>
  <text x="270" y="192" fill="#ff5252" font-size="12" font-weight="bold" text-anchor="middle">30 N</text>
  <line x1="270" y1="150" x2="270" y2="170" stroke="#facc15" stroke-width="2"/>
  <line x1="270" y1="204" x2="270" y2="245" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="282" y="240" fill="#ff5252" font-size="11" font-weight="bold">W = 30 N</text>
</svg>'''

    equil8_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#facc15" stroke-width="1.5"/>
  <text x="40" y="42" fill="#facc15" font-size="13.5" font-weight="bold">💡 【88 聯考】細繩極限張力與最大張開距離剖析：</text>

  <text x="40" y="72" fill="#38bdf8" font-size="12.5" font-weight="bold">1. 判定細繩最大安全張力 T_max 與對摺長度：</text>
  <text x="60" y="94" fill="#f1f5f9" font-size="12">「重量大於 30 N 扯斷」⟹ 最大耐受張力 T_max = 30 N；對摺後兩段各長 ℓ = 50 cm</text>

  <text x="40" y="125" fill="#00e676" font-size="12.5" font-weight="bold">2. 鉛直平衡求最小水平夾角 θ_min：</text>
  <text x="60" y="147" fill="#f1f5f9" font-size="12">兩繩向上分量平衡重力：2 · T · sin θ = W ⟹ 2 · (30) · sin θ = 30 N</text>
  <text x="60" y="167" fill="#00e676" font-size="13" font-weight="bold">sin θ ≥ 1/2 ⟹ θ_min = 30°（夾角越小繩張力越大，臨界為 30°）</text>

  <rect x="40" y="195" width="460" height="70" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.2"/>
  <text x="270" y="218" fill="#f1f5f9" font-size="12" text-anchor="middle">兩端最大水平相距：d_max = 2 · ℓ · cos θ_min</text>
  <text x="270" y="240" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">d_max = 2 × 50 cm × cos 30° = 100 × (√3/2) = 50√3 cm</text>
  <text x="270" y="258" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">✅ 選 (C)</text>
</svg>'''

    equil8_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 對摺細繩張開題圖</div>
        ''' + equil8_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 極限張力與最大距離並列</div>
        ''' + equil8_svg_fbd + '''
      </div>
    </div>'''

    problems[37]['diagrams'] = [
        { 'label': '📐 原始題圖 (對摺細繩)', 'svg': equil8_svg_raw },
        { 'label': '💡 極限張力與幾何解析', 'svg': equil8_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil8_svg_dual }
    ]
    problems[37]['svg'] = equil8_svg_raw
    problems[37]['related'] = [
        { 'id': 'equil4', 'title': '平衡 4：天花板三繩吊球張力', 'badge': '懸繩幾何' },
        { 'id': 'problem3', 'title': '範例 3：三線拉銅環拉密定理', 'badge': '極限張力' },
        { 'id': 'equil6', 'title': '平衡 6：雙端水平懸掛彈簧吊重', 'badge': '對稱懸掛' }
    ]
    problems[37]['solutions'] = [
        {
            'title': '【重點解析・細繩極限張力與對摺懸吊最大開距求解】（88聯考大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・判定細繩之極限張力與對摺長度</strong>：<br>由題意「下端掛大於 $30\\text{ N}$ 會扯斷」，得知該細繩所能承受之最大張力為：$$T_{\\max} = 30\\text{ N}$$全長 $100\\text{ cm}$ 對摺後，兩邊之繩長皆為：$$\\ell = \\frac{100\\text{ cm}}{2} = 50\\text{ cm}$$',
                '📌 <strong>重點二・鉛直方向受力平衡求最小水平夾角 $\\theta_{\\min}$</strong>：<br>設細繩與水平線夾角為 $\\theta$，掛物重 $W = 30\\text{ N}$：$$2 T \\sin\\theta = W \\implies T = \\frac{30\\text{ N}}{2\\sin\\theta} = \\frac{15}{\\sin\\theta}$$細繩不被扯斷之條件為 $T \\le T_{\\max} = 30\\text{ N}$：$$\\frac{15}{\\sin\\theta} \\le 30 \\implies \\sin\\theta \\ge \\frac{1}{2} \\implies \\theta \\ge 30^\\circ$$因此細繩與水平線夾角之最小值為 $\\theta_{\\min} = 30^\\circ$（角度越小繩張力越大）。',
                '⚡ <strong>重點三・計算兩手最大相距拉開距離 $d_{\\max}$</strong>：<br>雙手相距即為兩段細繩之水平投影長度和：$$d = 2 \\cdot \\ell \\cos\\theta$$當 $\\theta = 30^\\circ$ 時，$d$ 達最大值：$$\\mathbf{d_{\\max} = 2 \\times 50\\text{ cm} \\times \\cos 30^\\circ = 100 \\times \\frac{\\sqrt{3}}{2} = 50\\sqrt{3}\\text{ cm}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 39 (Index 38): 平衡 9 光滑鉛直壁懸球繩張力 (q-38)
    # ========================================================
    problems[38]['options'] = [
        '(A) $W\\sin\\theta$',
        '(B) $W\\cos\\theta$',
        '(C) $W\\sec\\theta$（即 $\\dfrac{W}{\\cos\\theta}$）',
        '(D) $W\\csc\\theta$'
    ]
    problems[38]['answer'] = '(C) W secθ'

    equil9_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="180" y1="30" x2="180" y2="270" stroke="#64748b" stroke-width="3"/>
  <rect x="150" y="30" width="30" height="240" fill="rgba(30, 41, 59, 0.5)"/>
  <text x="140" y="150" fill="#64748b" font-size="12" font-weight="bold" transform="rotate(-90 140 150)">光滑鉛直壁</text>

  <circle cx="180" cy="50" r="5" fill="#facc15"/>

  <circle cx="240" cy="154" r="60" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <circle cx="240" cy="154" r="4" fill="#00e5ff"/>
  <text x="250" y="150" fill="#00e5ff" font-size="12" font-weight="bold">球心 O</text>

  <line x1="180" y1="50" x2="240" y2="154" stroke="#facc15" stroke-width="2.5"/>
  <text x="220" y="90" fill="#facc15" font-size="12" font-weight="bold">繩張力 T</text>

  <path d="M 180,90 A 40,40 0 0,0 195,85" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="190" y="105" fill="#fff" font-size="11">θ</text>

  <line x1="240" y1="154" x2="240" y2="245" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="248" y="235" fill="#ff5252" font-size="12" font-weight="bold">重力 W</text>

  <line x1="180" y1="154" x2="235" y2="154" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="195" y="145" fill="#00e676" font-size="11" font-weight="bold">正向力 N</text>
</svg>'''

    equil9_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e5ff" font-size="13.5" font-weight="bold">💡 鉛直壁懸球封閉直角三角形解析：</text>

  <text x="40" y="75" fill="#facc15" font-size="12.5" font-weight="bold">1. 圓球共點力平衡分析：</text>
  <text x="60" y="98" fill="#f1f5f9" font-size="12">球受三力平衡：鉛直向下之重力 W、水平向右之壁面正向力 N、沿繩向左上之張力 T</text>
  <text x="60" y="120" fill="#f1f5f9" font-size="12">因牆面光滑無摩擦，三力延長線必共點於球心 O，構成直角封閉力三角形。</text>

  <text x="40" y="152" fill="#00e676" font-size="12.5" font-weight="bold">2. 直角三角形函數對應：</text>
  <text x="60" y="174" fill="#f1f5f9" font-size="12">鉛直鄰邊為重力 W，斜邊為繩張力 T，夾角為 θ：</text>
  <text x="60" y="196" fill="#00e676" font-size="13" font-weight="bold">T · cos θ = W ⟹ T = W / cos θ = W sec θ</text>

  <rect x="40" y="215" width="460" height="52" rx="6" fill="#1e293b" stroke="#facc15" stroke-width="1.2"/>
  <text x="270" y="235" fill="#94a3b8" font-size="12" text-anchor="middle">（附：水平正向力為 N = T · sin θ = W tan θ）</text>
  <text x="270" y="255" fill="#facc15" font-size="13.5" font-weight="bold" text-anchor="middle">繩張力量值：T = W sec θ ➔ ✅ 選 (C)</text>
</svg>'''

    equil9_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 垂直壁懸球題圖</div>
        ''' + equil9_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 直角向量封閉三角形並列</div>
        ''' + equil9_svg_fbd + '''
      </div>
    </div>'''

    problems[38]['diagrams'] = [
        { 'label': '📐 原始題圖 (垂直壁懸球)', 'svg': equil9_svg_raw },
        { 'label': '💡 直角封閉力三角形解析', 'svg': equil9_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil9_svg_dual }
    ]
    problems[38]['svg'] = equil9_svg_raw
    problems[38]['related'] = [
        { 'id': 'equil1', 'title': '平衡 1：光滑斜面正向力剖析', 'badge': '三力直角' },
        { 'id': 'equil10', 'title': '平衡 10：斜面與鉛直板夾球受力', 'badge': '擋板接觸' },
        { 'id': 'problem10', 'title': '範例 10：梯子靠光滑牆', 'badge': '光滑壁面' }
    ]
    problems[38]['solutions'] = [
        {
            'title': '【重點解析・光滑鉛直壁懸球共點三力直角三角形速解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・圓球三力共點受力分析</strong>：<br>圓球受三力達到靜力平衡：<br>① 重力 $W$：鉛直向下作用於球心<br>② 光滑壁正向力 $N$：垂直壁面水平向右通過球心<br>③ 輕繩拉力 $T$：沿繩方向向左上方作用，作用線通過球心<br>三力交於球心，構成<strong>直角封閉力三角形</strong>。',
                '📌 <strong>重點二・判定向量三角形之幾何角度</strong>：<br>繩與鉛垂線之夾角為 $\\theta$，鉛直邊對應重力 $W$，斜邊對應繩張力 $T$。',
                '⚡ <strong>重點三・三角函數關係求解繩張力</strong>：<br>由鉛直方向力平衡：$$T \\cos\\theta = W \\implies \\mathbf{T = \\frac{W}{\\cos\\theta} = W \\sec\\theta} \\quad \\text{✅ 選 (C)}$$<br><em>補充</em>：水平正向力為 $N = T \\sin\\theta = W \\tan\\theta$。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 40 (Index 39): 平衡 10 斜面與鉛直板夾球受力分析 (q-39)
    # ========================================================
    problems[39]['options'] = [
        '(A) 斜面對小球的作用力一定大於 $W$',
        '(B) 擋板對小球的作用力一定大於 $W$',
        '(C) 當斜角 $\\alpha$ 增加時，斜面對小球的作用力變大',
        '(D) 當斜角 $\\alpha$ 增加時，擋板對小球的作用力變大',
        '(E) 斜面對小球的作用力方向必與斜面垂直'
    ]
    problems[39]['answer'] = '(B) 擋板對小球的作用力一定大於 W'

    equil10_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <polygon points="60,250 480,250 60,110" fill="rgba(30, 41, 59, 0.7)" stroke="#64748b" stroke-width="2"/>
  <path d="M 400,250 A 60,60 0 0,0 420,235" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="390" y="242" fill="#fff" font-size="11">α</text>

  <line x1="280" y1="90" x2="280" y2="250" stroke="#facc15" stroke-width="4"/>
  <text x="288" y="115" fill="#facc15" font-size="12" font-weight="bold">鉛直擋板</text>

  <circle cx="225" cy="155" r="55" fill="rgba(30, 41, 59, 0.8)" stroke="#00e5ff" stroke-width="2.5"/>
  <circle cx="225" cy="155" r="4" fill="#00e5ff"/>
  <text x="225" y="145" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">球心 O</text>

  <line x1="225" y1="155" x2="225" y2="245" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="235" y="235" fill="#ff5252" font-size="12" font-weight="bold">重力 W</text>

  <line x1="280" y1="155" x2="230" y2="155" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-ex2-gold)"/>
  <text x="255" y="145" fill="#facc15" font-size="11" font-weight="bold">N₁ (擋板)</text>

  <line x1="180" y1="210" x2="222" y2="160" stroke="#00e676" stroke-width="2.8" marker-end="url(#arr-ex1-green)"/>
  <text x="175" y="180" fill="#00e676" font-size="11" font-weight="bold">N₂ (斜面)</text>
</svg>'''

    equil10_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#facc15" stroke-width="1.5"/>
  <text x="40" y="42" fill="#facc15" font-size="13.5" font-weight="bold">💡 鉛直擋板與斜面夾球受力直角三角形剖析：</text>

  <text x="40" y="72" fill="#00e676" font-size="12.5" font-weight="bold">1. 三力構成封閉直角三角形：</text>
  <text x="60" y="94" fill="#f1f5f9" font-size="12">鉛直向下的重力 W、水平向左的擋板支持力 N₁、垂直斜面向上的正向力 N₂</text>
  <text x="60" y="114" fill="#00e676" font-size="13" font-weight="bold">N₂ · cos α = W ⟹ N₂ = W / cos α ； N₁ = W · tan α</text>

  <text x="40" y="145" fill="#ff5252" font-size="12.5" font-weight="bold">2. 選項 (B) 錯誤核心關鍵分析：</text>
  <text x="60" y="167" fill="#f1f5f9" font-size="12">擋板對球作用力 N₁ = W tan α：</text>
  <text x="60" y="187" fill="#ff5252" font-size="12.5" font-weight="bold">當傾角 α &lt; 45° 時，tan α &lt; 1 ⟹ N₁ &lt; W（並非一定大於 W！）</text>

  <rect x="40" y="210" width="460" height="60" rx="6" fill="#1e293b" stroke="#ff5252" stroke-width="1.2"/>
  <text x="270" y="232" fill="#f1f5f9" font-size="12" text-anchor="middle">僅當 α &gt; 45° 時 N₁ 才大於 W，故選項 (B) 宣稱「一定大於 W」顯然錯誤</text>
  <text x="270" y="254" fill="#ff5252" font-size="13.5" font-weight="bold" text-anchor="middle">何者錯誤 ➔ ✅ 選 (B)</text>
</svg>'''

    equil10_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 斜面擋板夾球題圖</div>
        ''' + equil10_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 受力直角三角形與反例剖析並列</div>
        ''' + equil10_svg_fbd + '''
      </div>
    </div>'''

    problems[39]['diagrams'] = [
        { 'label': '📐 原始題圖 (斜面擋板夾球)', 'svg': equil10_svg_raw },
        { 'label': '💡 直角力三角形與反例解析', 'svg': equil10_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil10_svg_dual }
    ]
    problems[39]['svg'] = equil10_svg_raw
    problems[39]['related'] = [
        { 'id': 'equil9', 'title': '平衡 9：光滑鉛直壁懸球繩張力', 'badge': '直角三角' },
        { 'id': 'equil5', 'title': '平衡 5：雙光滑斜板圓球支持力', 'badge': '雙板支持' },
        { 'id': 'equil1', 'title': '平衡 1：光滑斜面受力方向', 'badge': '法向正力' }
    ]
    problems[39]['solutions'] = [
        {
            'title': '【重點解析・斜面擋板夾球共點力平衡與定性分析】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・小球受力分析與直角三角形關係</strong>：<br>小球受三力平衡：鉛直向下之重力 $W$、擋板水平支持力 $N_1$（向左）、斜面正向力 $N_2$（垂直斜面向上）。<br>三力構成直角封閉力三角形，其中斜面正向力 $N_2$ 與鉛垂線夾角即為斜面傾角 $\\alpha$：$$N_2 = \\frac{W}{\\cos\\alpha} = W\\sec\\alpha \\qquad N_1 = W\\tan\\alpha$$',
                '📌 <strong>重點二・逐項嚴謹檢視各選項</strong>：<br>• <strong>(A) 正確</strong>：因 $0^\\circ < \\alpha < 90^\\circ$ 且 $\\cos\\alpha < 1$，故 $N_2 = \\frac{W}{\\cos\\alpha} > W$ 恆成立。<br>• <strong>(C)、(D) 正確</strong>：當 $\\alpha$ 增大時，$\\cos\\alpha$ 變小 $\\implies N_2$ 變大；$\\tan\\alpha$ 變大 $\\implies N_1$ 變大。<br>• <strong>(E) 正確</strong>：接觸面光滑無摩擦力，斜面對小球之作用力必沿法線方向垂直於斜面。',
                '⚡ <strong>重點三・抓出錯誤選項 (B) 之反例</strong>：<br>擋板對球作用力 $N_1 = W\\tan\\alpha$：<br>當 $\\alpha < 45^\\circ$ 時（例如 $\\alpha = 30^\\circ$），$\\tan 30^\\circ = \\frac{1}{\\sqrt{3}} < 1 \\implies N_1 = \\frac{1}{\\sqrt{3}}W < W$！<br>只有當 $\\alpha > 45^\\circ$ 時，$N_1$ 才會大於 $W$。<br>因此選項 (B) 敘述「擋板對小球的作用力一定大於 $W$」<strong>顯然錯誤</strong> ➔ <strong>✅ 選 (B)</strong>。'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 41 (Index 40): 平衡 11 大球面輕繩懸小球支持力 (q-40)
    # ========================================================
    problems[40]['options'] = [
        '(A) $\\dfrac{W}{\\sin\\theta}$',
        '(B) $\\dfrac{W}{\\cos\\theta}$',
        '(C) $\\dfrac{W}{2\\sin\\theta}$',
        '(D) $\\dfrac{W}{2\\cos\\theta}$',
        '(E) $\\dfrac{W}{\\tan\\theta}$'
    ]
    problems[40]['answer'] = '(D) W / (2 cosθ)'

    equil11_svg_raw = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <circle cx="270" cy="240" r="130" fill="rgba(30, 41, 59, 0.6)" stroke="#64748b" stroke-width="2"/>
  <circle cx="270" cy="240" r="4" fill="#64748b"/>
  <text x="270" y="258" fill="#64748b" font-size="11" text-anchor="middle">大球球心 O (半徑 R)</text>

  <line x1="270" y1="40" x2="270" y2="240" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <circle cx="270" cy="40" r="5" fill="#facc15"/>
  <text x="282" y="45" fill="#facc15" font-size="12" font-weight="bold">懸點 A</text>

  <line x1="270" y1="40" x2="354" y2="140" stroke="#facc15" stroke-width="2.5"/>
  <text x="325" y="85" fill="#facc15" font-size="11" font-weight="bold">繩長 L = R</text>

  <line x1="270" y1="240" x2="354" y2="140" stroke="#00e5ff" stroke-width="2" stroke-dasharray="2,2"/>
  <text x="325" y="200" fill="#00e5ff" font-size="11">半徑 R</text>

  <circle cx="354" cy="140" r="12" fill="#1e293b" stroke="#00e676" stroke-width="2.5"/>
  <text x="375" y="145" fill="#00e676" font-size="12" font-weight="bold">B (小球)</text>

  <line x1="354" y1="140" x2="396" y2="90" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="405" y="95" fill="#00e676" font-size="12" font-weight="bold">正向力 N</text>

  <line x1="354" y1="140" x2="354" y2="205" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="362" y="195" fill="#ff5252" font-size="11" font-weight="bold">W</text>

  <path d="M 270,180 A 60,60 0 0,1 308,194" fill="none" stroke="#fff" stroke-width="1.2"/>
  <text x="282" y="190" fill="#fff" font-size="11">θ</text>
</svg>'''

    equil11_svg_fbd = '''<svg viewBox="0 0 540 300" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="270" rx="10" fill="rgba(15, 23, 42, 0.8)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 幾何三角形相似比與等腰三角形解題速算：</text>

  <text x="40" y="72" fill="#38bdf8" font-size="12.5" font-weight="bold">1. 受力三角形與幾何 △OBA 相似比：</text>
  <text x="60" y="94" fill="#f1f5f9" font-size="12">小球受三力：正向力 N（沿 OB）、繩張力 T（沿 BA）、重力 W（鉛直向下，平行 AO）</text>
  <text x="60" y="114" fill="#38bdf8" font-size="12.5" font-weight="bold">相似比：N / OB = T / BA = W / AO</text>

  <text x="40" y="145" fill="#facc15" font-size="12.5" font-weight="bold">2. 利用等腰幾何（OB = BA = R）求解：</text>
  <text x="60" y="167" fill="#f1f5f9" font-size="12">繩長等於球半徑 ⟹ OB = BA = R ⟹ N = T（大球支持力必等於繩張力）</text>
  <text x="60" y="187" fill="#facc15" font-size="12.5" font-weight="bold">等腰 △OBA 底邊 AO = 2 · R · cos θ ⟹ N / R = W / (2R cos θ)</text>

  <rect x="40" y="210" width="460" height="60" rx="6" fill="#1e293b" stroke="#00e676" stroke-width="1.2"/>
  <text x="270" y="232" fill="#f1f5f9" font-size="12" text-anchor="middle">消去半徑 R：N = W / (2 cos θ)</text>
  <text x="270" y="254" fill="#00e676" font-size="13.5" font-weight="bold" text-anchor="middle">正向力量值：N = W / (2 cos θ) ➔ ✅ 選 (D)</text>
</svg>'''

    equil11_svg_dual = '''<div class="dual-diagram-comparison-grid">
      <div class="dual-diagram-pane">
        <div class="pane-tag">📐 大球面懸球幾何題圖</div>
        ''' + equil11_svg_raw + '''
      </div>
      <div class="dual-diagram-pane">
        <div class="pane-tag">💡 幾何受力相似比推導並列</div>
        ''' + equil11_svg_fbd + '''
      </div>
    </div>'''

    problems[40]['diagrams'] = [
        { 'label': '📐 原始題圖 (大球面懸球)', 'svg': equil11_svg_raw },
        { 'label': '💡 相似力三角形推導解析', 'svg': equil11_svg_fbd },
        { 'label': '⚖️ 原圖與圖解並列', 'svg': equil11_svg_dual }
    ]
    problems[40]['svg'] = equil11_svg_raw
    problems[40]['related'] = [
        { 'id': 'equil9', 'title': '平衡 9：光滑鉛直壁懸球繩張力', 'badge': '圓球平衡' },
        { 'id': 'problem5', 'title': '範例 5：雙球系統正向力分析', 'badge': '幾何相似' },
        { 'id': 'equil4', 'title': '平衡 4：天花板三繩吊球張力', 'badge': '等腰三角形' }
    ]
    problems[40]['solutions'] = [
        {
            'title': '【重點解析・大球面懸球幾何相似三角形與等腰性質求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・共點三力與空間幾何三角形相似比</strong>：<br>置於光滑大球表面之小球受三力作用：<br>① 大球對小球之支持力 $N$：沿接觸法線通過球心，方向沿 $\\vec{OB}$ 向外<br>② 輕繩張力 $T$：沿繩方向指向懸掛點，方向沿 $\\vec{BA}$<br>③ 小球重力 $W$：鉛直向下作用，方向平行 $\\vec{AO}$<br>三力封閉向量三角形與幾何 $\\triangle OBA$ 嚴格相似：$$\\frac{N}{OB} = \\frac{T}{BA} = \\frac{W}{AO}$$',
                '📌 <strong>重點二・等腰幾何性質（$OB = BA = R$）導出 $N = T$</strong>：<br>題意說明「<strong>繩長與大球半徑相等</strong>」，即 $BA = OB = R$。<br>由相似比立即可得：$$\\frac{N}{R} = \\frac{T}{R} \\implies N = T$$即大球對小球之正向力必與繩張力量值完全相等！',
                '⚡ <strong>重點三・求出底邊 $AO$ 長度並代入相似比求解</strong>：<br>在等腰 $\\triangle OBA$ 中，兩腰皆為 $R$，底角 $\\angle AOB = \\theta$（即 $OB$ 與鉛垂線之夾角）。<br>過 $B$ 作底邊 $AO$ 之垂線，將底邊平分，得底邊長度：$$AO = 2 \\cdot R \\cos\\theta$$代入相似比例式：$$\\frac{N}{OB} = \\frac{W}{AO} \\implies \\frac{N}{R} = \\frac{W}{2R \\cos\\theta}$$$$\\mathbf{N = \\frac{W}{2\\cos\\theta}} \\quad \\text{✅ 選 (D)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 42 (Index 41): 平衡 12 兩球夾壓縮彈簧平衡形變量 (q-41)
    # ========================================================
    problems[41]['options'] = [
        '(A) $\\frac{W}{k}$',
        '(B) $\\frac{\\sqrt{3}W}{k}$',
        '(C) $\\frac{W}{\\sqrt{3}k}$',
        '(D) $\\frac{W}{2k}$',
        '(E) $\\frac{\\sqrt{3}W}{2k}$'
    ]
    problems[41]['answer'] = '(C) W / (√3 k)'

    equil12_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="180" y1="35" x2="360" y2="35" stroke="#64748b" stroke-width="2.5"/>
  <circle cx="270" cy="35" r="5" fill="#facc15"/>
  <text x="270" y="25" fill="#facc15" font-size="13" font-weight="bold" text-anchor="middle">固定頂點 O</text>
  <line x1="270" y1="35" x2="270" y2="240" stroke="#475569" stroke-width="1.5" stroke-dasharray="4,4"/>
  <path d="M 245 80 A 50 50 0 0 1 295 80" fill="none" stroke="#facc15" stroke-width="1.5"/>
  <text x="270" y="100" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">60° (半角 30°)</text>
  <line x1="270" y1="35" x2="190" y2="200" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="215" y="125" fill="#00e5ff" font-size="12" font-weight="bold">L</text>
  <line x1="270" y1="35" x2="350" y2="200" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="320" y="125" fill="#00e5ff" font-size="12" font-weight="bold">L</text>
  <path d="M 190 200 L 205 192 L 220 208 L 235 192 L 250 208 L 265 192 L 280 208 L 295 192 L 310 208 L 325 192 L 335 208 L 350 200" fill="none" stroke="#00e676" stroke-width="2.5"/>
  <text x="270" y="185" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">彈簧 (k, 壓縮量 x)</text>
  <circle cx="190" cy="200" r="14" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="190" y="205" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">A</text>
  <line x1="190" y1="214" x2="190" y2="265" stroke="#ff5252" stroke-width="2.2" marker-end="url(#arr-ex1-red)"/>
  <text x="190" y="282" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">重 W</text>
  <circle cx="350" cy="200" r="14" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="350" y="205" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">B</text>
  <line x1="350" y1="214" x2="350" y2="265" stroke="#ff5252" stroke-width="2.2" marker-end="url(#arr-ex1-red)"/>
  <text x="350" y="282" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">重 W</text>
</svg>'''

    equil12_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="230" height="275" rx="8" fill="rgba(15, 23, 42, 0.7)" stroke="#334155" stroke-width="1.2"/>
  <text x="135" y="45" fill="#facc15" font-size="12.5" font-weight="bold" text-anchor="middle">球 A 隔離受力圖</text>
  <circle cx="135" cy="130" r="14" fill="#1e293b" stroke="#00e5ff" stroke-width="2"/>
  <text x="135" y="135" fill="#00e5ff" font-size="11" font-weight="bold" text-anchor="middle">A</text>
  <line x1="135" y1="144" x2="135" y2="215" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="145" y="190" fill="#ff5252" font-size="12" font-weight="bold">W</text>
  <line x1="121" y1="130" x2="50" y2="130" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="80" y="120" fill="#00e676" font-size="12" font-weight="bold">F = kx</text>
  <line x1="135" y1="116" x2="175" y2="55" stroke="#00e5ff" stroke-width="2.5" marker-end="url(#arr-ex1-cyan)"/>
  <text x="165" y="90" fill="#00e5ff" font-size="12" font-weight="bold">T</text>
  <line x1="135" y1="116" x2="135" y2="55" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="145" y="75" fill="#facc15" font-size="11">30°</text>

  <rect x="270" y="20" width="250" height="275" rx="8" fill="rgba(15, 23, 42, 0.7)" stroke="#00e676" stroke-width="1.2"/>
  <text x="395" y="45" fill="#00e676" font-size="12.5" font-weight="bold" text-anchor="middle">封閉直角向量三角形</text>
  <line x1="430" y1="75" x2="430" y2="200" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="440" y="145" fill="#ff5252" font-size="12.5" font-weight="bold">W</text>
  <line x1="430" y1="200" x2="358" y2="200" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="395" y="222" fill="#00e676" font-size="12.5" font-weight="bold" text-anchor="middle">F = kx</text>
  <line x1="358" y1="200" x2="430" y2="75" stroke="#00e5ff" stroke-width="2.5" marker-end="url(#arr-ex1-cyan)"/>
  <text x="380" y="125" fill="#00e5ff" font-size="12.5" font-weight="bold">T</text>
  <text x="415" y="105" fill="#facc15" font-size="12" font-weight="bold">30°</text>

  <rect x="290" y="235" width="210" height="45" rx="5" fill="#0f172a" stroke="#facc15" stroke-width="1"/>
  <text x="395" y="255" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">tan 30° = F / W = 1 / √3</text>
  <text x="395" y="272" fill="#00e5ff" font-size="11.5" font-weight="bold" text-anchor="middle">x = W / (√3 k) ✅ (C)</text>
</svg>'''

    problems[41]['diagrams'] = [
        {'label': '📐 原始題圖 (兩球夾彈簧)', 'svg': equil12_svg_raw},
        {'label': '💡 球A隔離與直角向量三角形', 'svg': equil12_svg_fbd}
    ]
    problems[41]['svg'] = equil12_svg_raw
    problems[41]['related'] = [
        {'id': 'equil6', 'title': '平衡 6：雙端水平懸掛彈簧吊重', 'badge': '彈簧平衡'},
        {'id': 'equil4', 'title': '平衡 4：天花板三繩吊球張力', 'badge': '三力共點'},
        {'id': 'problem2', 'title': '範例 2：直角三角形三角比', 'badge': '向量封閉'}
    ]
    problems[41]['solutions'] = [
        {
            'title': '【重點解析・隔離體受力平衡與直角三角形三角比求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・隔離球 A 受力分析與對稱性</strong>：<br>因系統左右完全對稱，兩懸繩夾角 $60^\\circ$ 均勻分佈於鉛直線兩側，故每條繩與鉛直線夾角皆為 $\\theta = 30^\\circ$。<br>隔離左側球 $A$，受三力作用：<br>① 鉛直向下之重力 $W$<br>② 彈簧向左之推力 $F = kx$（彈簧處於壓縮狀態，向兩端施加彈力）<br>③ 輕繩斜向右上方之張力 $T$，方向與鉛垂線夾 $30^\\circ$',
                '📐 <strong>重點二・共點三力向量封閉直角三角形</strong>：<br>球 $A$ 靜止平衡，重力 $W$（向下）、彈力 $F$（水平向左）與張力 $T$（斜向上）構成直角三角形：$$\\tan 30^\\circ = \\frac{\\text{水平力 } F}{\\text{鉛直力 } W} = \\frac{kx}{W}$$',
                '⚡ <strong>重點三・代入特殊角求彈簧壓縮量 $x$</strong>：<br>由 $\\tan 30^\\circ = \\frac{1}{\\sqrt{3}}$：$$\\frac{1}{\\sqrt{3}} = \\frac{kx}{W} \\implies \\mathbf{x = \\frac{W}{\\sqrt{3}k} = \\frac{\\sqrt{3}W}{3k}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 43 (Index 42): 平衡 13 斜面雙外力平衡與正向力 (q-42)
    # ========================================================
    problems[42]['options'] = [
        '(A) $1\\,W$',
        '(B) $\\sqrt{2}\\,W$',
        '(C) $\\frac{3}{2}\\,W$',
        '(D) $2\\,W$',
        '(E) $\\frac{5}{2}\\,W$'
    ]
    problems[42]['answer'] = '(D) 2 W'

    equil13_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <polygon points="70,260 450,260 450,75" fill="rgba(30, 41, 59, 0.5)" stroke="#64748b" stroke-width="2"/>
  <text x="120" y="250" fill="#facc15" font-size="13" font-weight="bold">θ (53°)</text>
  <g transform="translate(260, 168) rotate(-26)">
    <rect x="-30" y="-35" width="60" height="35" rx="4" fill="#1e293b" stroke="#facc15" stroke-width="2.5"/>
    <text x="0" y="-13" fill="#facc15" font-size="13" font-weight="bold" text-anchor="middle">2W</text>
  </g>
  <line x1="260" y1="150" x2="260" y2="245" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="270" y="235" fill="#ff5252" font-size="13" font-weight="bold">重力 2W</text>
  <line x1="260" y1="150" x2="180" y2="111" stroke="#00e5ff" stroke-width="2.8" marker-end="url(#arr-ex1-cyan)"/>
  <text x="165" y="98" fill="#00e5ff" font-size="12.5" font-weight="bold">平行拉力 W</text>
  <line x1="260" y1="150" x2="350" y2="150" stroke="#facc15" stroke-width="2.8" marker-end="url(#arr-ex1-yellow)"/>
  <text x="355" y="145" fill="#facc15" font-size="12.5" font-weight="bold">水平推力 W</text>
  <line x1="260" y1="150" x2="225" y2="78" stroke="#00e676" stroke-width="2.8" marker-end="url(#arr-ex1-green)"/>
  <text x="210" y="70" fill="#00e676" font-size="13" font-weight="bold">正向力 N</text>
</svg>'''

    equil13_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 四力平衡正交分解與正向力求解：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 沿斜面方向力平衡（求斜面傾角 θ）：</text>
  <text x="60" y="95" fill="#f1f5f9" font-size="12">沿斜面向上合力 = 沿斜面向下分力：</text>
  <text x="60" y="117" fill="#00e5ff" font-size="12.5" font-weight="bold">W + W cosθ = 2W sinθ  ⟹  1 + cosθ = 2 sinθ</text>
  <text x="60" y="138" fill="#f1f5f9" font-size="12">平方求解得：sinθ = 4/5 (0.8)，cosθ = 3/5 (0.6)（即傾角 θ = 53°）</text>
  <text x="40" y="172" fill="#00e676" font-size="12.5" font-weight="bold">2. 垂直斜面方向力平衡（求斜面正向力 N）：</text>
  <text x="60" y="195" fill="#f1f5f9" font-size="12">正向力 N 平衡重力與水平推力之垂直斜面分量：</text>
  <text x="60" y="217" fill="#facc15" font-size="12.5" font-weight="bold">N = 2W cosθ + W sinθ</text>
  <text x="60" y="240" fill="#f1f5f9" font-size="12">代入數值：N = 2W × (3/5) + W × (4/5) = (6/5)W + (4/5)W = 2W</text>
  <rect x="60" y="255" width="420" height="35" rx="6" fill="#0f172a" stroke="#00e676" stroke-width="1.5"/>
  <text x="270" y="278" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">⚡ 結論：斜面正向力 N = 2W  ✅ (D)</text>
</svg>'''

    problems[42]['diagrams'] = [
        {'label': '📐 原始題圖 (雙外力斜面)', 'svg': equil13_svg_raw},
        {'label': '💡 正交分解與正向力推導', 'svg': equil13_svg_fbd}
    ]
    problems[42]['svg'] = equil13_svg_raw
    problems[42]['related'] = [
        {'id': 'equil1', 'title': '平衡 1：光滑斜面正向力剖析', 'badge': '斜面力平衡'},
        {'id': 'equil3', 'title': '平衡 3：斜向推力與地面全作用力', 'badge': '正交分解'},
        {'id': 'problem1', 'title': '範例 1：共點三力向量三角形', 'badge': '靜力平衡'}
    ]
    problems[42]['solutions'] = [
        {
            'title': '【重點解析・斜面正交分解與四力平衡精準求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・物體受力完整列出</strong>：<br>置於光滑斜面上的物體（重 $2W$）共受四力作用靜止：<br>① 重力：量值 $2W$，方向鉛直向下<br>② 平行斜面向上外力：量值 $W$<br>③ 水平向右推力：量值 $W$<br>④ 光滑斜面正向力：量值 $N$，方向垂直斜面向上',
                '📐 <strong>重點二・沿斜面方向力平衡求傾角 $\\theta$</strong>：<br>以平行斜面方向列平衡方程式：$$W + W \\cos\\theta = 2W \\sin\\theta \\implies 1 + \\cos\\theta = 2\\sin\\theta$$利用三角恆等式 $\\cos^2\\theta = 1 - \\sin^2\\theta$：$$(2\\sin\\theta - 1)^2 = 1 - \\sin^2\\theta \\implies 5\\sin^2\\theta - 4\\sin\\theta = 0$$解得 $\\sin\\theta = \\frac{4}{5}$，$\\cos\\theta = \\frac{3}{5}$（對應特殊角 $\\theta = 53^\\circ$）。',
                '⚡ <strong>重點三・垂直斜面方向力平衡求解正向力 $N$</strong>：<br>垂直斜面方向之分力平衡：$$N = 2W \\cos\\theta + W \\sin\\theta$$代入數值：$$N = 2W \\times \\frac{3}{5} + W \\times \\frac{4}{5} = \\frac{6}{5}W + \\frac{4}{5}W = \\frac{10}{5}W = 2W$$$$\\mathbf{N = 2W} \\quad \\text{✅ 選 (D)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 44 (Index 43): 平衡 14 掛畫細繩張力極限與最短長度 (q-43)
    # ========================================================
    problems[43]['options'] = [
        '(A) $\\frac{2}{\\sqrt{3}}\\text{ m}$',
        '(B) $\\frac{3}{2}\\text{ m}$',
        '(C) $2\\text{ m}$',
        '(D) $\\frac{5}{2}\\text{ m}$',
        '(E) $2\\sqrt{3}\\text{ m}$'
    ]
    problems[43]['answer'] = '(A) 2 / √3 m'

    equil14_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <circle cx="270" cy="50" r="5" fill="#facc15"/>
  <text x="270" y="40" fill="#facc15" font-size="12.5" font-weight="bold" text-anchor="middle">掛鉤 (H)</text>
  <rect x="150" y="160" width="240" height="130" rx="4" fill="#1e293b" stroke="#64748b" stroke-width="2.5"/>
  <text x="270" y="230" fill="#cbd5e1" font-size="13" font-weight="bold" text-anchor="middle">畫作本體（含框重 W = 1 kgw）</text>
  <circle cx="190" cy="160" r="4" fill="#00e676"/>
  <text x="180" y="150" fill="#00e676" font-size="11.5" font-weight="bold">釘子 A</text>
  <circle cx="350" cy="160" r="4" fill="#00e676"/>
  <text x="360" y="150" fill="#00e676" font-size="11.5" font-weight="bold">釘子 B</text>
  <line x1="190" y1="175" x2="350" y2="175" stroke="#facc15" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="270" y="190" fill="#facc15" font-size="11" text-anchor="middle">兩釘固定相距 d = 1 m</text>
  <line x1="270" y1="50" x2="190" y2="160" stroke="#00e5ff" stroke-width="2.8"/>
  <text x="215" y="100" fill="#00e5ff" font-size="12" font-weight="bold">L / 2</text>
  <line x1="270" y1="50" x2="350" y2="160" stroke="#00e5ff" stroke-width="2.8"/>
  <text x="320" y="100" fill="#00e5ff" font-size="12" font-weight="bold">L / 2</text>
  <line x1="270" y1="50" x2="270" y2="160" stroke="#475569" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="255" y="85" fill="#facc15" font-size="11.5">θ</text>
  <text x="280" y="85" fill="#facc15" font-size="11.5">θ</text>
  <line x1="270" y1="240" x2="270" y2="285" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="280" y="280" fill="#ff5252" font-size="12" font-weight="bold">W = 1 kgw</text>
</svg>'''

    equil14_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e5ff" font-size="13.5" font-weight="bold">💡 細繩最大耐張力與最短長度幾何極限剖析：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 鉛直方向受力平衡方程式：</text>
  <text x="60" y="95" fill="#f1f5f9" font-size="12">兩側繩張力 T 對稱，鉛垂方向合力支撐畫作重力 W：</text>
  <text x="60" y="117" fill="#00e5ff" font-size="12.5" font-weight="bold">2T cosθ = W = 1 kgw  ⟹  cosθ = 1 / (2T)</text>
  <text x="40" y="150" fill="#00e676" font-size="12.5" font-weight="bold">2. 張力不超過最大耐張限度（T ≤ 1 kgw）：</text>
  <text x="60" y="173" fill="#f1f5f9" font-size="12">繩子最短時，張力達到最大承受極限 T_max = 1 kgw：</text>
  <text x="60" y="195" fill="#facc15" font-size="12.5" font-weight="bold">cosθ_max = 1 / (2 × 1) = 1/2  ⟹  θ_max = 60°</text>
  <text x="40" y="228" fill="#facc15" font-size="12.5" font-weight="bold">3. 幾何直角三角形求繩長 L_min：</text>
  <text x="60" y="248" fill="#f1f5f9" font-size="12">半邊水平距離為 d/2 = 0.5 m：sin 60° = (d/2) / (L/2) = 1 / L</text>
  <text x="60" y="270" fill="#00e676" font-size="12.5" font-weight="bold">L_min = 1 / sin 60° = 1 / (√3 / 2) = 2 / √3 m  ✅ (A)</text>
</svg>'''

    problems[43]['diagrams'] = [
        {'label': '📐 原始題圖 (對稱掛畫)', 'svg': equil14_svg_raw},
        {'label': '💡 極限張力與幾何長度剖析', 'svg': equil14_svg_fbd}
    ]
    problems[43]['svg'] = equil14_svg_raw
    problems[43]['related'] = [
        {'id': 'equil8', 'title': '平衡 8：88聯考對摺細繩極限張力', 'badge': '最大張力'},
        {'id': 'equil4', 'title': '平衡 4：天花板對稱吊球張力', 'badge': '對稱平衡'},
        {'id': 'problem4', 'title': '範例 4：雙繩懸吊系統受力平衡', 'badge': '張力三角'}
    ]
    problems[43]['solutions'] = [
        {
            'title': '【重點解析・對稱懸吊張力極限與幾何最短繩長推導】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・鉛直方向受力平衡列式</strong>：<br>畫作重 $W = 1\\text{ kgw}$，兩側細繩對稱拉緊，設每邊張力為 $T$，細繩與鉛垂線之夾角為 $\\theta$。<br>由鉛直方向合力為零：$$2T \\cos\\theta = W = 1\\text{ kgw} \\implies T = \\frac{1}{2\\cos\\theta}$$細繩長度越短，夾角 $\\theta$ 越大，$\\cos\\theta$ 越小，繩張力 $T$ 越巨大。',
                '📐 <strong>重點二・耐張極限求臨界夾角 $\\theta$</strong>：<br>細繩所能承受之最大張力為 $T_{\\max} = 1\\text{ kgw}$。<br>令張力達到極限 $T = 1\\text{ kgw}$，可得最大夾角 $\\theta_{\\max}$：$$\\cos\\theta_{\\max} = \\frac{1}{2 \\times 1} = \\frac{1}{2} \\implies \\theta_{\\max} = 60^\\circ$$此時細繩與水平釘子連線夾角為 $30^\\circ$。',
                '⚡ <strong>重點三・直角三角形幾何求最短繩長 $L_{\\min}$</strong>：<br>兩釘間距 $d = 1\\text{ m}$，半邊橫向距為 $\\frac{d}{2} = 0.5\\text{ m}$，單側繩長為 $\\frac{L}{2}$。<br>由直角幾何：$$\\sin\\theta = \\frac{d/2}{L/2} = \\frac{d}{L} \\implies \\sin 60^\\circ = \\frac{1}{L}$$$$\\mathbf{L_{\\min} = \\frac{1}{\\sin 60^\\circ} = \\frac{1}{\\frac{\\sqrt{3}}{2}} = \\frac{2}{\\sqrt{3}}\\text{ m}} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 45 (Index 44): 平衡 15 均勻懸繩最低點張力與長度比 (q-44)
    # ========================================================
    problems[44]['options'] = [
        '(A) $T_C = \\frac{12}{25}W,\\quad AC : BC = 9 : 16$',
        '(B) $T_C = \\frac{12}{25}W,\\quad AC : BC = 3 : 4$',
        '(C) $T_C = \\frac{7}{12}W,\\quad AC : BC = 9 : 16$',
        '(D) $T_C = \\frac{5}{12}W,\\quad AC : BC = 16 : 9$',
        '(E) $T_C = \\frac{25}{12}W,\\quad AC : BC = 3 : 4$'
    ]
    problems[44]['answer'] = '(A) Tc = 12/25 W, AC:BC = 9:16'

    equil15_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="80" y1="30" x2="80" y2="280" stroke="#64748b" stroke-width="3"/>
  <line x1="460" y1="30" x2="460" y2="280" stroke="#64748b" stroke-width="3"/>
  <path d="M 80 70 Q 200 220 240 220 Q 300 220 460 90" fill="none" stroke="#00e5ff" stroke-width="3.5"/>
  <circle cx="80" cy="70" r="5" fill="#facc15"/>
  <text x="60" y="65" fill="#facc15" font-size="13" font-weight="bold">A</text>
  <line x1="80" y1="70" x2="80" y2="150" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <line x1="80" y1="70" x2="135" y2="145" stroke="#facc15" stroke-width="1.5"/>
  <text x="95" y="115" fill="#facc15" font-size="12" font-weight="bold">53°</text>
  <circle cx="460" cy="90" r="5" fill="#facc15"/>
  <text x="475" y="85" fill="#facc15" font-size="13" font-weight="bold">B</text>
  <line x1="460" y1="90" x2="460" y2="170" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <line x1="460" y1="90" x2="400" y2="170" stroke="#facc15" stroke-width="1.5"/>
  <text x="430" y="135" fill="#facc15" font-size="12" font-weight="bold">37°</text>
  <circle cx="240" cy="220" r="5" fill="#00e676"/>
  <text x="240" y="245" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">最低點 C（切線水平）</text>
  <text x="145" y="170" fill="#00e5ff" font-size="12" font-weight="bold">AC 段 (W₁)</text>
  <text x="340" y="180" fill="#00e5ff" font-size="12" font-weight="bold">BC 段 (W₂)</text>
</svg>'''

    equil15_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 隔離 AC、BC 段受力三角形與長度比剖析：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 最低點 C 特性：切線呈水平，張力 T_C 方向為純水平！</text>
  <text x="40" y="105" fill="#00e5ff" font-size="12.5" font-weight="bold">2. 隔離 AC 段（重 W₁）與 BC 段（重 W₂）之三力平衡：</text>
  <text x="60" y="128" fill="#f1f5f9" font-size="12">AC 段：tan 53° = T_C / W₁ = 4/3  ⟹  W₁ = (3/4) T_C</text>
  <text x="60" y="150" fill="#f1f5f9" font-size="12">BC 段：tan 37° = T_C / W₂ = 3/4  ⟹  W₂ = (4/3) T_C</text>
  <text x="40" y="185" fill="#00e676" font-size="12.5" font-weight="bold">3. 繩總重 W 與最低點張力 T_C：</text>
  <text x="60" y="208" fill="#facc15" font-size="12.5" font-weight="bold">W = W₁ + W₂ = (3/4 + 4/3) T_C = (25/12) T_C  ⟹  T_C = (12/25) W</text>
  <text x="40" y="242" fill="#facc15" font-size="12.5" font-weight="bold">4. 粗繩均勻分佈，長度比等於重量比：</text>
  <text x="60" y="265" fill="#00e5ff" font-size="12.5" font-weight="bold">AC 長度 : BC 長度 = W₁ : W₂ = (3/4) : (4/3) = 9 : 16  ✅ (A)</text>
</svg>'''

    problems[44]['diagrams'] = [
        {'label': '📐 原始題圖 (懸粗繩切線角)', 'svg': equil15_svg_raw},
        {'label': '💡 隔離AC/BC段與張力分析', 'svg': equil15_svg_fbd}
    ]
    problems[44]['svg'] = equil15_svg_raw
    problems[44]['related'] = [
        {'id': 'equil8', 'title': '平衡 8：88聯考對摺細繩最大距離', 'badge': '懸繩平衡'},
        {'id': 'equil9', 'title': '平衡 9：光滑鉛直壁懸球繩張力', 'badge': '三力平衡'},
        {'id': 'exercise4', 'title': '類題 4：懸繩張力與重力平衡', 'badge': '分段隔離'}
    ]
    problems[44]['solutions'] = [
        {
            'title': '【重點解析・以最低點切線純水平特性隔離兩段求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・繩子最低點 $C$ 關鍵物理特性</strong>：<br>懸掛粗繩在最低點 $C$ 處之切線必為<strong>水平方向</strong>，因此 $C$ 點兩側繩張力 $T_C$ 必為<strong>純水平向左與純水平向右</strong>！',
                '📐 <strong>重點二・隔離 $AC$ 段與 $BC$ 段列出三力平衡</strong>：<br>① 隔離 $AC$ 段（重 $W_1$）：受 $C$ 點水平張力 $T_C$（向右）、重力 $W_1$（向下）、$A$ 點張力 $T_A$（與鉛直線夾 $53^\\circ$）。<br>由力三角形：$$\\tan 53^\\circ = \\frac{T_C}{W_1} = \\frac{4}{3} \\implies W_1 = \\frac{3}{4}T_C$$② 隔離 $BC$ 段（重 $W_2$）：受 $C$ 點水平張力 $T_C$（向左）、重力 $W_2$（向下）、$B$ 點張力 $T_B$（與鉛直線夾 $37^\\circ$）。<br>由力三角形：$$\\tan 37^\\circ = \\frac{T_C}{W_2} = \\frac{3}{4} \\implies W_2 = \\frac{4}{3}T_C$$',
                '⚡ <strong>重點三・總重 $W$ 運算與長度比</strong>：<br>繩子總重為兩段之和：$$W = W_1 + W_2 = \\left(\\frac{3}{4} + \\frac{4}{3}\\right)T_C = \\frac{25}{12}T_C \\implies \\mathbf{T_C = \\frac{12}{25}W}$$因粗繩均勻分佈，兩段長度比即為重量比：$$\\mathbf{AC : BC} = W_1 : W_2 = \\frac{3}{4} : \\frac{4}{3} = \\mathbf{9 : 16} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 46 (Index 45): 平衡 16 動態拉起過程懸繩張力變化 (q-45)
    # ========================================================
    problems[45]['options'] = [
        '(A) 逐漸變小',
        '(B) 逐漸變大',
        '(C) 保持不變',
        '(D) 先變小再變大',
        '(E) 先變大再變小'
    ]
    problems[45]['answer'] = '(D) 先變小再變大'

    equil16_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <circle cx="200" cy="50" r="5" fill="#facc15"/>
  <text x="185" y="45" fill="#facc15" font-size="13" font-weight="bold">樞紐 P</text>
  <line x1="200" y1="50" x2="200" y2="280" stroke="#475569" stroke-width="1.2" stroke-dasharray="3,3"/>
  <line x1="200" y1="50" x2="270" y2="150" stroke="#00e5ff" stroke-width="2.8"/>
  <text x="215" y="95" fill="#facc15" font-size="12" font-weight="bold">ϕ</text>
  <text x="245" y="90" fill="#00e5ff" font-size="12.5" font-weight="bold">T (PQ)</text>
  <circle cx="270" cy="150" r="5" fill="#facc15"/>
  <text x="285" y="150" fill="#facc15" font-size="13" font-weight="bold">Q</text>
  <line x1="270" y1="150" x2="400" y2="105" stroke="#00e676" stroke-width="2.8" marker-end="url(#arr-ex1-green)"/>
  <text x="390" y="95" fill="#00e676" font-size="12.5" font-weight="bold">拉力 F</text>
  <line x1="270" y1="150" x2="380" y2="150" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="330" y="142" fill="#00e676" font-size="11.5" font-weight="bold">θ (固定)</text>
  <line x1="270" y1="150" x2="270" y2="230" stroke="#ff5252" stroke-width="2.5"/>
  <rect x="250" y="230" width="40" height="35" rx="4" fill="#1e293b" stroke="#ff5252" stroke-width="2"/>
  <text x="270" y="253" fill="#ff5252" font-size="13" font-weight="bold" text-anchor="middle">W</text>
</svg>'''

    equil16_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e5ff" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e5ff" font-size="13.5" font-weight="bold">💡 動態力三角形向量軌跡（垂線段最短原理）：</text>
  <line x1="160" y1="80" x2="160" y2="240" stroke="#ff5252" stroke-width="3" marker-end="url(#arr-ex1-red)"/>
  <text x="140" y="165" fill="#ff5252" font-size="13" font-weight="bold" text-anchor="middle">W (固定)</text>
  <line x1="160" y1="240" x2="330" y2="140" stroke="#00e676" stroke-width="2" stroke-dasharray="4,4"/>
  <text x="340" y="135" fill="#00e676" font-size="12.5" font-weight="bold">F 作用線 (方向固定)</text>
  <line x1="210" y1="210" x2="160" y2="80" stroke="#64748b" stroke-width="1.8"/>
  <text x="195" y="135" fill="#64748b" font-size="11">T(初)</text>
  <line x1="247" y1="189" x2="160" y2="80" stroke="#facc15" stroke-width="2.8" marker-end="url(#arr-ex1-yellow)"/>
  <text x="215" y="115" fill="#facc15" font-size="12" font-weight="bold">T_min ⊥ F</text>
  <rect x="238" y="180" width="10" height="10" fill="none" stroke="#facc15" stroke-width="1.2" transform="rotate(30, 243, 185)"/>
  <line x1="295" y1="161" x2="160" y2="80" stroke="#00e5ff" stroke-width="2" marker-end="url(#arr-ex1-cyan)"/>
  <text x="260" y="100" fill="#00e5ff" font-size="11">T(後)</text>
  <rect x="340" y="170" width="165" height="115" rx="6" fill="#0f172a" stroke="#facc15" stroke-width="1.2"/>
  <text x="422" y="195" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">📌 幾何極值分析</text>
  <text x="350" y="218" fill="#f1f5f9" font-size="11">① 頂點到直線連線</text>
  <text x="350" y="235" fill="#00e676" font-size="11.5" font-weight="bold">以垂線段長度為最短！</text>
  <text x="350" y="255" fill="#00e5ff" font-size="11">② 隨 ϕ 漸增：</text>
  <text x="350" y="273" fill="#facc15" font-size="12" font-weight="bold">T 必先變小後變大 ✅ (D)</text>
</svg>'''

    problems[45]['diagrams'] = [
        {'label': '📐 原始題圖 (動態施力拉起)', 'svg': equil16_svg_raw},
        {'label': '💡 動態向量三角形與垂線最短', 'svg': equil16_svg_fbd}
    ]
    problems[45]['svg'] = equil16_svg_raw
    problems[45]['related'] = [
        {'id': 'problem10', 'title': '範例 10：動態三力平衡極值', 'badge': '垂線最短'},
        {'id': 'exercise7', 'title': '類題 7：定滑輪拉動物體張力變化', 'badge': '動態平衡'},
        {'id': 'exercise8', 'title': '類題 8：三力閉合外接圓幾何', 'badge': '幾何軌跡'}
    ]
    problems[45]['solutions'] = [
        {
            'title': '【重點解析・動態力三角形封閉法則與垂線段最短原理】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・節點 $Q$ 共點三力動態平衡</strong>：<br>隔離中點 $Q$，受三力作用維持靜平衡：<br>① 重物向下拉力：量值為 $W$，大小與方向恆定鉛直向下<br>② 外力 $F$：施力方向恆定（與水平夾角 $\\theta$ 固定，指向右上方）<br>③ 上段繩張力 $T$：沿線段 $QP$ 指向懸點 $P$，其與鉛垂線夾角 $\\phi$ 逐漸增大',
                '📐 <strong>重點二・建構動態向量三角形</strong>：<br>三力平衡向量封閉：$$\\vec{W} + \\vec{F} + \\vec{T} = 0$$① 先繪製恆定之重力向量 $\\vec{W}$（固定長度之鉛垂線段）<br>② 從 $\\vec{W}$ 之末端引出一條射線，代表外力 $\\vec{F}$ 的作用線（方向固定）<br>③ 張力向量 $\\vec{T}$ 必須從射線上某點連回 $\\vec{W}$ 之起點以構成封閉三角形',
                '⚡ <strong>重點三・幾何極值判定（垂線段最短定理）</strong>：<br>由固定頂點到一固定直線的所有連線段中，以<strong>垂直線段</strong>之長度為最短！<br>① 當繩張力 $\\vec{T}$ 垂直於外力 $\\vec{F}$（即 $\\vec{T} \\perp \\vec{F}$）時，張力具有極小值 $T_{\\min} = W \\cos\\theta$<br>② 初始時夾角 $\\phi$ 較小，隨著 $\\phi$ 逐漸變大，張力向量逐步由鈍角接近直角、再變為銳角<br>③ 故張力量值必然呈現：<strong>先變小，通過垂直極小值後再變大</strong>！$$\\mathbf{\\text{先變小再變大}} \\quad \\text{✅ 選 (D)}$$'
            ]
        }
    ]


    # ========================================================
    # Enrich Problem 47 (Index 46): 平衡 17 碗內雙球受力與支持力剖析 (q-46)
    # ========================================================
    problems[46]['options'] = [
        '(A) 二球間：$\\frac{W}{\\sqrt{3}}$，球對碗壁：$\\frac{2W}{\\sqrt{3}}$',
        '(B) 二球間：$\\frac{2W}{\\sqrt{3}}$，球對碗壁：$\\frac{W}{\\sqrt{3}}$',
        '(C) 二球間：$\\frac{W}{2}$，球對碗壁：$\\sqrt{3}W$',
        '(D) 二球間：$\\frac{\\sqrt{3}W}{2}$，球對碗壁：$W$',
        '(E) 二球間：$W$，球對碗壁：$2W$'
    ]
    problems[46]['answer'] = '(A) 二球間：W/√3，球對碗壁：2W/√3'

    equil17_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <path d="M 90 70 A 180 180 0 0 0 450 70" fill="rgba(15, 23, 42, 0.6)" stroke="#64748b" stroke-width="3"/>
  <circle cx="270" cy="70" r="4" fill="#facc15"/>
  <text x="270" y="58" fill="#facc15" font-size="12.5" font-weight="bold" text-anchor="middle">碗心 O (內半徑 3r)</text>
  <circle cx="210" cy="174" r="60" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <circle cx="210" cy="174" r="4" fill="#00e5ff"/>
  <text x="210" y="179" fill="#00e5ff" font-size="14" font-weight="bold" text-anchor="middle">A</text>
  <circle cx="330" cy="174" r="60" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <circle cx="330" cy="174" r="4" fill="#00e5ff"/>
  <text x="330" y="179" fill="#00e5ff" font-size="14" font-weight="bold" text-anchor="middle">B</text>
  <line x1="270" y1="70" x2="210" y2="174" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="270" y1="70" x2="330" y2="174" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="210" y1="174" x2="330" y2="174" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <path d="M 252 101 A 36 36 0 0 1 288 101" fill="none" stroke="#facc15" stroke-width="1.5"/>
  <text x="270" y="125" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">60° (各 30°)</text>
  <text x="220" y="115" fill="#facc15" font-size="11">2r</text>
  <text x="310" y="115" fill="#facc15" font-size="11">2r</text>
  <text x="270" y="165" fill="#facc15" font-size="11" text-anchor="middle">2r</text>
  <line x1="210" y1="174" x2="210" y2="245" stroke="#ff5252" stroke-width="2.2" marker-end="url(#arr-ex1-red)"/>
  <text x="210" y="260" fill="#ff5252" font-size="11.5" font-weight="bold" text-anchor="middle">重 W</text>
  <line x1="330" y1="174" x2="330" y2="245" stroke="#ff5252" stroke-width="2.2" marker-end="url(#arr-ex1-red)"/>
  <text x="330" y="260" fill="#ff5252" font-size="11.5" font-weight="bold" text-anchor="middle">重 W</text>
</svg>'''

    equil17_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="235" height="290" rx="8" fill="rgba(15, 23, 42, 0.75)" stroke="#334155" stroke-width="1.2"/>
  <text x="137" y="40" fill="#facc15" font-size="13" font-weight="bold" text-anchor="middle">球 B 隔離體受三力平衡</text>
  <circle cx="137" cy="140" r="28" fill="#1e293b" stroke="#00e5ff" stroke-width="2"/>
  <text x="137" y="145" fill="#00e5ff" font-size="13" font-weight="bold" text-anchor="middle">B</text>
  <line x1="137" y1="140" x2="137" y2="225" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="147" y="200" fill="#ff5252" font-size="12" font-weight="bold">W</text>
  <line x1="137" y1="140" x2="215" y2="140" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="180" y="130" fill="#00e676" font-size="12" font-weight="bold">X (互推力)</text>
  <line x1="137" y1="140" x2="85" y2="50" stroke="#facc15" stroke-width="2.8" marker-end="url(#arr-ex1-yellow)"/>
  <text x="75" y="85" fill="#facc15" font-size="12.5" font-weight="bold">Y (碗壁力)</text>
  <line x1="137" y1="140" x2="137" y2="50" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="120" y="80" fill="#facc15" font-size="11.5">30°</text>

  <rect x="270" y="15" width="250" height="290" rx="8" fill="rgba(15, 23, 42, 0.75)" stroke="#00e676" stroke-width="1.2"/>
  <text x="395" y="40" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">封閉直角向量三角形</text>
  <line x1="360" y1="65" x2="360" y2="185" stroke="#ff5252" stroke-width="2.8" marker-end="url(#arr-ex1-red)"/>
  <text x="345" y="130" fill="#ff5252" font-size="12.5" font-weight="bold">W</text>
  <line x1="360" y1="185" x2="430" y2="185" stroke="#00e676" stroke-width="2.8" marker-end="url(#arr-ex1-green)"/>
  <text x="395" y="205" fill="#00e676" font-size="12.5" font-weight="bold" text-anchor="middle">X = Y sin 30°</text>
  <line x1="430" y1="185" x2="360" y2="65" stroke="#facc15" stroke-width="2.8" marker-end="url(#arr-ex1-yellow)"/>
  <text x="410" y="120" fill="#facc15" font-size="12.5" font-weight="bold">Y</text>
  <text x="375" y="90" fill="#facc15" font-size="11.5">30°</text>

  <rect x="285" y="220" width="220" height="70" rx="6" fill="#0f172a" stroke="#facc15" stroke-width="1"/>
  <text x="395" y="242" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">Y cos 30° = W ⟹ Y = 2W / √3</text>
  <text x="395" y="262" fill="#00e676" font-size="12" font-weight="bold" text-anchor="middle">X = Y sin 30° = W / √3</text>
  <text x="395" y="280" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">比值 X : Y = 1 : 2  ✅ (A)</text>
</svg>'''

    problems[46]['diagrams'] = [
        {'label': '📐 原始題圖 (碗內雙球)', 'svg': equil17_svg_raw},
        {'label': '💡 球B受力與直角力三角形', 'svg': equil17_svg_fbd}
    ]
    problems[46]['svg'] = equil17_svg_raw
    problems[46]['related'] = [
        {'id': 'problem5', 'title': '範例 5：容器內雙球接觸正向力分析', 'badge': '雙球堆疊'},
        {'id': 'equil5', 'title': '平衡 5：雙光滑斜板圓球支持力', 'badge': '接觸支持力'},
        {'id': 'equil11', 'title': '平衡 11：大球面輕繩懸小球支持力', 'badge': '球面幾何'}
    ]
    problems[46]['solutions'] = [
        {
            'title': '【重點解析・碗心幾何等邊三角形與共點三力直角三角形求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・連心線幾何構成等邊三角形</strong>：<br>碗內半徑為 $3r$，小球半徑為 $r$。碗心為 $O$。<br>① 兩小球球心到碗心 $O$ 之距離皆為：$$3r - r = 2r$$② 兩球水平相切，兩球心間距為 $r + r = 2r$。<br>故碗心 $O$ 與兩球心構成<strong>邊長均為 $2r$ 之等邊正三角形</strong>！<br>頂角 $60^\\circ$ 被鉛垂線對稱平分，故球心與碗心之連線與鉛垂線之夾角為 $\\theta = 30^\\circ$。',
                '📐 <strong>重點二・隔離右球 B 進行受力分析</strong>：<br>球 $B$ 處於靜平衡，共受三力作用：<br>① 重力 $W$：方向鉛直向下<br>② 左球 $A$ 對球 $B$ 之水平互推力 $X$：方向水平向右<br>③ 碗壁對球 $B$ 之正向支持力 $Y$：沿法線指向碗心 $O$，即斜向左上方，與鉛垂直線夾 $30^\\circ$',
                '⚡ <strong>重點三・構成封閉直角三角形計算求解</strong>：<br>三力合力為零，水平與鉛直平衡方程式：$$Y \\cos 30^\\circ = W \\implies Y \\times \\frac{\\sqrt{3}}{2} = W \\implies \\mathbf{Y = \\frac{2W}{\\sqrt{3}} = \\frac{2\\sqrt{3}}{3}W}$$二球間推力：$$X = Y \\sin 30^\\circ = \\frac{2W}{\\sqrt{3}} \\times \\frac{1}{2} = \\mathbf{\\frac{W}{\\sqrt{3}} = \\frac{\\sqrt{3}}{3}W} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 48 (Index 47): 平衡 18 光滑大碗內三球接觸平衡 (q-47)
    # ========================================================
    problems[47]['options'] = [
        '(A) (1) $\\frac{\\sqrt{3}}{3}W$；(2) $\\frac{\\sqrt{3}}{3}W$；(3) $\\sqrt{3}W$',
        '(B) (1) $\\frac{\\sqrt{3}}{2}W$；(2) $\\frac{1}{2}W$；(3) $3W$',
        '(C) (1) $\\frac{\\sqrt{3}}{3}W$；(2) $\\frac{\\sqrt{3}}{2}W$；(3) $2\\sqrt{3}W$',
        '(D) (1) $\\frac{1}{2}W$；(2) $\\frac{\\sqrt{3}}{3}W$；(3) $\\sqrt{3}W$',
        '(E) (1) $\\sqrt{3}W$；(2) $\\sqrt{3}W$；(3) $3W$'
    ]
    problems[47]['answer'] = '(A) (1) √3/3 W；(2) √3/3 W；(3) √3 W'

    equil18_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <path d="M 90 110 A 180 180 0 0 0 450 110" fill="rgba(15, 23, 42, 0.6)" stroke="#64748b" stroke-width="3"/>
  <circle cx="270" cy="110" r="4" fill="#facc15"/>
  <text x="270" y="95" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">碗心 O (兼 C 球球心)</text>
  <circle cx="270" cy="110" r="60" fill="rgba(30, 41, 59, 0.5)" stroke="#00e676" stroke-width="2.5"/>
  <text x="270" y="115" fill="#00e676" font-size="14" font-weight="bold" text-anchor="middle">C (重 W)</text>
  <circle cx="210" cy="214" r="60" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="210" y="219" fill="#00e5ff" font-size="14" font-weight="bold" text-anchor="middle">A</text>
  <circle cx="330" cy="214" r="60" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="330" y="219" fill="#00e5ff" font-size="14" font-weight="bold" text-anchor="middle">B</text>
  <line x1="270" y1="110" x2="210" y2="214" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="270" y1="110" x2="330" y2="214" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="210" y1="214" x2="330" y2="214" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="165" y1="292" x2="210" y2="214" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-ex1-yellow)"/>
  <text x="160" y="260" fill="#facc15" font-size="12" font-weight="bold">N_A</text>
  <line x1="375" y1="292" x2="330" y2="214" stroke="#facc15" stroke-width="2.5" marker-end="url(#arr-ex1-yellow)"/>
  <text x="375" y="260" fill="#facc15" font-size="12" font-weight="bold">N_B</text>
</svg>'''

    equil18_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 三球堆疊平衡三層受力剖析：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 整體系統 (A+B+C) 鉛直平衡 ⟹ 求碗壁支持力 N：</text>
  <text x="60" y="95" fill="#f1f5f9" font-size="12">碗壁對 A、B 兩球之正向力通過球心 C，與鉛垂線各夾 30°：</text>
  <text x="60" y="117" fill="#00e5ff" font-size="12.5" font-weight="bold">2 N_B cos 30° = 3W  ⟹  2 N_B × (√3 / 2) = 3W  ⟹  N_A = N_B = √3 W  (第3小題)</text>
  <text x="40" y="150" fill="#00e676" font-size="12.5" font-weight="bold">2. 隔離頂層 C 球 ⟹ 求球間推力 F_BC：</text>
  <text x="60" y="173" fill="#f1f5f9" font-size="12">C 球重 W，受下方 A、B 球斜向支撐，方向與鉛垂線各夾 30°：</text>
  <text x="60" y="195" fill="#facc15" font-size="12.5" font-weight="bold">2 F_BC cos 30° = W  ⟹  F_BC = W / (2 × √3 / 2) = (√3 / 3) W  (第1小題)</text>
  <text x="40" y="228" fill="#facc15" font-size="12.5" font-weight="bold">3. 隔離底層 B 球水平平衡 ⟹ 求兩底球互推力 F_AB：</text>
  <text x="60" y="248" fill="#f1f5f9" font-size="12">F_AB = (N_B - F_BC) sin 30° = (√3 W - √3/3 W) × 1/2 = (2√3/3 W) × 1/2</text>
  <text x="60" y="270" fill="#00e676" font-size="12.5" font-weight="bold">F_AB = (√3 / 3) W  (第2小題)  ⟹  三小題依序：(√3/3)W, (√3/3)W, √3W  ✅ (A)</text>
</svg>'''

    problems[47]['diagrams'] = [
        {'label': '📐 原始題圖 (碗內三球堆疊)', 'svg': equil18_svg_raw},
        {'label': '💡 三層受力分解與逐步推導', 'svg': equil18_svg_fbd}
    ]
    problems[47]['svg'] = equil18_svg_raw
    problems[47]['related'] = [
        {'id': 'equil17', 'title': '平衡 17：碗內雙球受力與支持力', 'badge': '碗內球體'},
        {'id': 'problem5', 'title': '範例 5：多球堆疊平衡受力', 'badge': '整體隔離'},
        {'id': 'equil19', 'title': '平衡 19：三圓柱堆疊繫鋼繩平衡', 'badge': '三體平衡'}
    ]
    problems[47]['solutions'] = [
        {
            'title': '【重點解析・三體系統整體法與兩層隔離法完整推導】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・整體法求碗壁正向支持力 $N_A$、$N_B$（第3小題）</strong>：<br>將三球 $A$、$B$、$C$ 視為一整體，總重量為 $3W$。<br>碗壁對 $A$、$B$ 兩球施支持力 $N_A = N_B$，通過球心且與鉛垂線各夾角 $\\theta = 30^\\circ$。<br>整體鉛直合力為零：$$2N_B \\cos 30^\\circ = 3W \\implies 2N_B \\times \\frac{\\sqrt{3}}{2} = 3W \\implies \\mathbf{N_A = N_B = \\sqrt{3}W}$$',
                '📐 <strong>重點二・隔離頂層球 C 求球間推力 $F_{BC}$（第1小題）</strong>：<br>頂部球 $C$ 僅受自重 $W$ 及底層 $A$、$B$ 兩球之斜向上支持力 $F_{AC} = F_{BC}$，方向與鉛垂線夾 $30^\\circ$：$$2F_{BC} \\cos 30^\\circ = W \\implies 2F_{BC} \\times \\frac{\\sqrt{3}}{2} = W \\implies \\mathbf{F_{BC} = \\frac{W}{\\sqrt{3}} = \\frac{\\sqrt{3}}{3}W}$$',
                '⚡ <strong>重點三・隔離底層球 B 水平平衡求 $F_{AB}$（第2小題）</strong>：<br>球 $B$ 受碗壁正向力 $N_B$ 向內上方（水平分量向左 $N_B \\sin 30^\\circ$）、球 $C$ 壓迫力 $F_{BC}$ 向外下方（水平分量向右 $F_{BC} \\sin 30^\\circ$）、及球 $A$ 向右推力 $F_{AB}$：$$F_{AB} = (N_B - F_{BC}) \\sin 30^\\circ = \\left(\\sqrt{3}W - \\frac{\\sqrt{3}}{3}W\\right) \\times \\frac{1}{2} = \\frac{2\\sqrt{3}}{3}W \\times \\frac{1}{2} = \\mathbf{\\frac{\\sqrt{3}}{3}W}$$三小題依序為：$\\mathbf{\\frac{\\sqrt{3}}{3}W,\\; \\frac{\\sqrt{3}}{3}W,\\; \\sqrt{3}W} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 49 (Index 48): 平衡 19 三圓柱堆疊繫鋼繩平衡張力 (q-48)
    # ========================================================
    problems[48]['options'] = [
        '(A) (1) $\\frac{500}{3}\\text{ kgw}$；(2) $\\frac{400}{3}\\text{ kgw}$',
        '(B) (1) $\\frac{400}{3}\\text{ kgw}$；(2) $\\frac{500}{3}\\text{ kgw}$',
        '(C) (1) $200\\text{ kgw}$；(2) $160\\text{ kgw}$',
        '(D) (1) $\\frac{250}{3}\\text{ kgw}$；(2) $\\frac{200}{3}\\text{ kgw}$',
        '(E) (1) $250\\text{ kgw}$；(2) $200\\text{ kgw}$'
    ]
    problems[48]['answer'] = '(A) (1) 500/3 kgw；(2) 400/3 kgw'

    equil19_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="50" y1="260" x2="490" y2="260" stroke="#64748b" stroke-width="2.5"/>
  <line x1="190" y1="210" x2="350" y2="210" stroke="#facc15" stroke-width="2.5"/>
  <text x="270" y="202" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">鋼繩長 160 cm (張力 T)</text>
  <circle cx="190" cy="210" r="50" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="190" y="215" fill="#00e5ff" font-size="13" font-weight="bold" text-anchor="middle">A (100 kgw)</text>
  <circle cx="350" cy="210" r="50" fill="rgba(30, 41, 59, 0.7)" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="350" y="215" fill="#00e5ff" font-size="13" font-weight="bold" text-anchor="middle">B (100 kgw)</text>
  <circle cx="270" cy="150" r="50" fill="rgba(30, 41, 59, 0.7)" stroke="#00e676" stroke-width="2.5"/>
  <text x="270" y="155" fill="#00e676" font-size="13" font-weight="bold" text-anchor="middle">C (200 kgw)</text>
  <line x1="190" y1="210" x2="270" y2="150" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="220" y="175" fill="#cbd5e1" font-size="11.5">100 cm</text>
  <line x1="350" y1="210" x2="270" y2="150" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="315" y="175" fill="#cbd5e1" font-size="11.5">100 cm</text>
  <line x1="270" y1="150" x2="270" y2="210" stroke="#475569" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="275" y="185" fill="#475569" font-size="11">60 cm</text>
  <text x="230" y="225" fill="#facc15" font-size="11">80 cm</text>
  <text x="310" y="225" fill="#facc15" font-size="11">80 cm</text>
</svg>'''

    equil19_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 3:4:5 直角幾何與圓柱隔離平衡剖析：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 幾何連心線尺寸（3:4:5 特殊直角三角形）：</text>
  <text x="60" y="95" fill="#f1f5f9" font-size="12">斜邊（AC 連心線）= 2R = 100 cm，半底邊 = 160/2 = 80 cm：</text>
  <text x="60" y="117" fill="#00e5ff" font-size="12.5" font-weight="bold">高 h = √(100² - 80²) = 60 cm ⟹ cos 53° = 3/5 (0.6), sin 53° = 4/5 (0.8)</text>
  <text x="40" y="150" fill="#00e676" font-size="12.5" font-weight="bold">2. 隔離頂部 C 圓柱（鉛直平衡求 F_AC）：</text>
  <text x="60" y="173" fill="#f1f5f9" font-size="12">2 · F_AC · cos 53° = W_C = 200 kgw ⟹ 2 · F_AC · (3/5) = 200</text>
  <text x="60" y="195" fill="#facc15" font-size="12.5" font-weight="bold">F_AC = 200 / (6/5) = 500 / 3 kgw  (第1小題答案)</text>
  <text x="40" y="228" fill="#facc15" font-size="12.5" font-weight="bold">3. 隔離底部 B 圓柱（水平平衡求鋼繩張力 T）：</text>
  <text x="60" y="248" fill="#f1f5f9" font-size="12">鋼繩向左拉力 T 平衡 C 圓柱向右下推力之水平分量：</text>
  <text x="60" y="270" fill="#00e676" font-size="12.5" font-weight="bold">T = F_BC · sin 53° = (500 / 3) × (4 / 5) = 400 / 3 kgw  (第2小題) ✅ (A)</text>
</svg>'''

    problems[48]['diagrams'] = [
        {'label': '📐 原始題圖 (三柱堆疊)', 'svg': equil19_svg_raw},
        {'label': '💡 3:4:5幾何與鋼繩張力推導', 'svg': equil19_svg_fbd}
    ]
    problems[48]['svg'] = equil19_svg_raw
    problems[48]['related'] = [
        {'id': 'equil18', 'title': '平衡 18：光滑大碗內三球接觸平衡', 'badge': '三體堆疊'},
        {'id': 'problem5', 'title': '範例 5：多球堆疊接觸支持力', 'badge': '正交分解'},
        {'id': 'torque2', 'title': '力矩 2：水平地面圓柱推動平衡', 'badge': '受力平衡'}
    ]
    problems[48]['solutions'] = [
        {
            'title': '【重點解析・圓心幾何 3:4:5 特殊比與隔離體水平鉛直求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・圓心連線幾何與特殊角判定</strong>：<br>三圓柱半徑均為 $R = 50\\text{ cm}$。<br>① $A$、$C$ 兩圓心距離為斜邊：$2R = 100\\text{ cm}$<br>② $A$、$B$ 兩圓心相距 $160\\text{ cm}$，對稱分佈使 $C$ 到 $A$ 水平距為半底邊：$$\\frac{160\\text{ cm}}{2} = 80\\text{ cm}$$③ 由勾股定理求高：$$h = \\sqrt{100^2 - 80^2} = 60\\text{ cm}$$連心線與鉛垂線之夾角為特殊角 $53^\\circ$：$$\\cos 53^\\circ = \\frac{60}{100} = \\frac{3}{5},\\quad \\sin 53^\\circ = \\frac{80}{100} = \\frac{4}{5}$$',
                '📐 <strong>重點二・隔離頂部圓柱 C 求相互作用力 $F_{AC}$（第1小題）</strong>：<br>頂層 $C$ 柱重 $200\\text{ kgw}$，受 $A$、$B$ 兩側對稱支撐力 $F_{AC} = F_{BC}$：$$2F_{AC} \\cos 53^\\circ = 200 \\implies 2F_{AC} \\times \\frac{3}{5} = 200 \\implies \\mathbf{F_{AC} = \\frac{500}{3}\\text{ kgw}}$$',
                '⚡ <strong>重點三・隔離底層圓柱 B 求鋼繩張力 $T$（第2小題）</strong>：<br>底層 $B$ 柱水平方向受鋼繩向左張力 $T$ 與頂柱 $C$ 施加之斜推力水平分量：$$T = F_{BC} \\sin 53^\\circ = \\frac{500}{3} \\times \\frac{4}{5} = \\mathbf{\\frac{400}{3}\\text{ kgw}} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 50 (Index 49): 平衡 20 雙物體懸掛施水平力與彈簧恢復力 (q-49)
    # ========================================================
    problems[49]['options'] = [
        '(A) (1) $5W$；(2) $45^\\circ$',
        '(B) (1) $4W$；(2) $37^\\circ$',
        '(C) (1) $5W$；(2) $53^\\circ$',
        '(D) (1) $\\frac{5}{3}W$；(2) $45^\\circ$',
        '(E) (1) $3W$；(2) $30^\\circ$'
    ]
    problems[49]['answer'] = '(A) (1) 5W；(2) 45°'

    equil20_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <line x1="140" y1="35" x2="260" y2="35" stroke="#64748b" stroke-width="2.5"/>
  <circle cx="200" cy="35" r="4" fill="#facc15"/>
  <text x="200" y="25" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">固定點 O</text>
  <line x1="200" y1="35" x2="200" y2="120" stroke="#475569" stroke-width="1.2" stroke-dasharray="3,3"/>
  <path d="M 200 35 L 206 46 L 218 52 L 208 64 L 220 70 L 210 82 L 222 88 L 225 100" fill="none" stroke="#00e676" stroke-width="2.5"/>
  <text x="180" y="70" fill="#facc15" font-size="12" font-weight="bold">37°</text>
  <text x="235" y="75" fill="#00e676" font-size="12" font-weight="bold">彈簧 (恢復力 F)</text>
  <circle cx="225" cy="100" r="14" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="225" y="105" fill="#00e5ff" font-size="12" font-weight="bold" text-anchor="middle">A</text>
  <text x="245" y="112" fill="#ff5252" font-size="11" font-weight="bold">重 W</text>
  <line x1="225" y1="100" x2="225" y2="200" stroke="#475569" stroke-width="1.2" stroke-dasharray="3,3"/>
  <line x1="225" y1="100" x2="288" y2="164" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="235" y="140" fill="#facc15" font-size="12" font-weight="bold">θ (45°)</text>
  <rect x="274" y="150" width="28" height="28" rx="4" fill="#1e293b" stroke="#facc15" stroke-width="2.5"/>
  <text x="288" y="169" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">B</text>
  <text x="288" y="196" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">重 3W</text>
  <line x1="302" y1="164" x2="385" y2="164" stroke="#00e676" stroke-width="2.8" marker-end="url(#arr-ex1-green)"/>
  <text x="395" y="169" fill="#00e676" font-size="13" font-weight="bold">拉力 S</text>
</svg>'''

    equil20_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 整體系統與隔離體雙階段平衡剖析：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 整體系統 (A + B) 平衡（總重 W + 3W = 4W）：</text>
  <text x="60" y="95" fill="#f1f5f9" font-size="12">鉛直方向：F · cos 37° = 4W  ⟹  F · (4/5) = 4W  ⟹  F = 5W (第1小題答案)</text>
  <text x="60" y="117" fill="#00e5ff" font-size="12.5" font-weight="bold">水平方向求拉力 S：S = F · sin 37° = 5W · (3/5) = 3W</text>
  <text x="40" y="155" fill="#00e676" font-size="12.5" font-weight="bold">2. 隔離物體 B 受三力作用平衡：</text>
  <text x="60" y="178" fill="#f1f5f9" font-size="12">鉛直分量：T_AB · cos θ = 3W（重力）</text>
  <text x="60" y="200" fill="#f1f5f9" font-size="12">水平分量：T_AB · sin θ = S = 3W（拉力）</text>
  <text x="40" y="235" fill="#facc15" font-size="12.5" font-weight="bold">3. 水平與鉛直分量相比求夾角 θ：</text>
  <text x="60" y="258" fill="#00e676" font-size="12.5" font-weight="bold">tan θ = S / 3W = 3W / 3W = 1  ⟹  θ = 45°  (第2小題答案)  ✅ (A)</text>
</svg>'''

    problems[49]['diagrams'] = [
        {'label': '📐 原始題圖 (雙物體懸吊)', 'svg': equil20_svg_raw},
        {'label': '💡 整體與隔離雙階段受力推導', 'svg': equil20_svg_fbd}
    ]
    problems[49]['svg'] = equil20_svg_raw
    problems[49]['related'] = [
        {'id': 'equil6', 'title': '平衡 6：雙端水平懸掛彈簧吊重', 'badge': '彈簧平衡'},
        {'id': 'problem4', 'title': '範例 4：細繩與彈簧懸吊平衡', 'badge': '整體隔離'},
        {'id': 'exercise2', 'title': '類題 2：彈性繩多重力受力系統', 'badge': '分段平衡'}
    ]
    problems[49]['solutions'] = [
        {
            'title': '【重點解析・整體法求彈簧外力與隔離法求繩角】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・整體系統（$A + B$）鉛直平衡求彈簧恢復力 $F$（第1小題）</strong>：<br>將物體 $A$（重 $W$）與物體 $B$（重 $3W$）視為一整體，總重為：$$W_{\\text{總}} = W + 3W = 4W$$頂部彈簧恢復力 $F$ 與鉛垂線夾角為 $37^\\circ$。系統在鉛直方向受力平衡：$$F \\cos 37^\\circ = 4W \\implies F \\times \\frac{4}{5} = 4W \\implies \\mathbf{F = 5W}$$',
                '📐 <strong>重點二・整體水平平衡求水平外力 $S$</strong>：<br>系統水平方向僅受水平拉力 $S$ 與彈簧向左拉力之水平分量：$$S = F \\sin 37^\\circ = 5W \\times \\frac{3}{5} = 3W$$',
                '⚡ <strong>重點三・隔離物體 B 求解繩角 $\\theta$（第2小題）</strong>：<br>隔離物體 $B$（重 $3W$），受重力 $3W$ 向下、水平拉力 $S = 3W$ 向右、及繩張力 $T_{AB}$ 向左上方（與鉛垂線夾角 $\\theta$）：$$\\tan\\theta = \\frac{\\text{水平力 } S}{\\text{鉛直重力 } 3W} = \\frac{3W}{3W} = 1 \\implies \\mathbf{\\theta = 45^\\circ} \\quad \\text{✅ 選 (A)}$$'
            ]
        }
    ]

    # ========================================================
    # Enrich Problem 51 (Index 50): 平衡 21 均勻平板雙支柱支撐與臨界蹺起力矩 (q-50)
    # ========================================================
    problems[50]['options'] = [
        '(A) (1) $3.5\\text{ m}$；(2) $3.3\\text{ m}$',
        '(B) (1) $3.0\\text{ m}$；(2) $3.0\\text{ m}$',
        '(C) (1) $2.5\\text{ m}$；(2) $2.88\\text{ m}$',
        '(D) (1) $2.0\\text{ m}$；(2) $2.5\\text{ m}$',
        '(E) (1) $1.5\\text{ m}$；(2) $2.0\\text{ m}$'
    ]
    problems[50]['answer'] = '(C) (1) 2.5 m；(2) 2.88 m'

    equil21_svg_raw = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="70" y="140" width="400" height="18" rx="3" fill="#1e293b" stroke="#00e5ff" stroke-width="2.5"/>
  <text x="270" y="130" fill="#00e5ff" font-size="12.5" font-weight="bold" text-anchor="middle">均勻平板長 15 m (重 400 N)</text>
  <circle cx="270" cy="149" r="4" fill="#ff5252"/>
  <text x="270" y="178" fill="#ff5252" font-size="11" font-weight="bold" text-anchor="middle">重心 G</text>
  <line x1="270" y1="149" x2="270" y2="220" stroke="#ff5252" stroke-width="2.5" marker-end="url(#arr-ex1-red)"/>
  <text x="282" y="210" fill="#ff5252" font-size="11.5" font-weight="bold">W = 400 N</text>
  <polygon points="163,158 153,200 173,200" fill="#64748b"/>
  <text x="163" y="215" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">A</text>
  <polygon points="377,158 367,200 387,200" fill="#facc15"/>
  <text x="377" y="215" fill="#facc15" font-size="12" font-weight="bold" text-anchor="middle">B (轉軸)</text>
  <line x1="163" y1="110" x2="377" y2="110" stroke="#facc15" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="270" y="102" fill="#facc15" font-size="11" text-anchor="middle">A、B 間距 8 m (距重心各 4 m)</text>
  <circle cx="430" cy="115" r="9" fill="#00e676"/>
  <line x1="430" y1="124" x2="430" y2="140" stroke="#00e676" stroke-width="2"/>
  <line x1="430" y1="140" x2="430" y2="195" stroke="#00e676" stroke-width="2.5" marker-end="url(#arr-ex1-green)"/>
  <text x="430" y="100" fill="#00e676" font-size="11.5" font-weight="bold" text-anchor="middle">小孩 640 N</text>
  <text x="430" y="210" fill="#00e676" font-size="11" text-anchor="middle">x = 2.5 m</text>
</svg>'''

    equil21_svg_fbd = '''<svg viewBox="0 0 540 320" style="max-width: 500px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="15" width="500" height="290" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#00e676" stroke-width="1.5"/>
  <text x="40" y="42" fill="#00e676" font-size="13.5" font-weight="bold">💡 平板蹺起臨界力矩平衡雙情境推導：</text>
  <text x="40" y="72" fill="#facc15" font-size="12.5" font-weight="bold">1. 小孩向外走極限距離 x（平板恰蹺起 ⟹ N_A = 0）：</text>
  <text x="60" y="95" fill="#f1f5f9" font-size="12">以支柱 B 為轉軸列力矩平衡（逆力矩 = 順力矩）：</text>
  <text x="60" y="117" fill="#00e5ff" font-size="12.5" font-weight="bold">400 N × 4 m = 640 N × x  ⟹  x = 1600 / 640 = 2.5 m  (第1小題)</text>
  <text x="40" y="155" fill="#00e676" font-size="12.5" font-weight="bold">2. 小孩安全走到最右端端點，支柱 B 距右端距離 y：</text>
  <text x="60" y="178" fill="#f1f5f9" font-size="12">小孩在最右端力臂為 y；重心距最右端 7.5 m，重心距 B 力臂為 (7.5 - y)：</text>
  <text x="60" y="200" fill="#facc15" font-size="12.5" font-weight="bold">400 × (7.5 - y) = 640 × y  ⟹  3000 - 400 y = 640 y</text>
  <text x="40" y="235" fill="#facc15" font-size="12.5" font-weight="bold">3. 求解支柱 B 距端點位置 y：</text>
  <text x="60" y="258" fill="#00e676" font-size="12.5" font-weight="bold">1040 y = 3000  ⟹  y = 3000 / 1040 = 75 / 26 ≈ 2.88 m  (第2小題)  ✅ (C)</text>
</svg>'''

    problems[50]['diagrams'] = [
        {'label': '📐 原始題圖 (均勻平板支撐)', 'svg': equil21_svg_raw},
        {'label': '💡 臨界蹺起力矩平衡剖析', 'svg': equil21_svg_fbd}
    ]
    problems[50]['svg'] = equil21_svg_raw
    problems[50]['related'] = [
        {'id': 'torque6', 'title': '力矩 6：均質木棒懸重臨界翹起力矩', 'badge': '臨界翹起'},
        {'id': 'torque7', 'title': '力矩 7：107指考均勻直尺力矩平衡', 'badge': '力矩平衡'},
        {'id': 'problem7', 'title': '範例 7：高架工作車翻覆臨界力矩', 'badge': '轉軸取定'}
    ]
    problems[50]['solutions'] = [
        {
            'title': '【重點解析・蹺起臨界支持力為零與支點力矩平衡精準求解】（大考標準滿分解）',
            'type': 'textbook',
            'steps': [
                '📌 <strong>重點一・幾何尺寸與重心力臂判定</strong>：<br>均勻平板長度 $L = 15\\text{ m}$，板重 $W = 400\\text{ N}$ 作用於幾何中心 $G$（距左右兩端各 $7.5\\text{ m}$）。<br>兩對稱支柱相距 $8\\text{ m}$，故重心 $G$ 距支柱 $A$ 與 $B$ 均為：$$\\frac{8\\text{ m}}{2} = 4\\text{ m}$$',
                '📐 <strong>重點二・第 (1) 小題求小孩向外走極限距離 $x$</strong>：<br>小孩向右越過 $B$ 點時，平板有繞 $B$ 點順時針旋轉之趨勢。當恰好蹺起時，支柱 $A$ 之支持力減至零：$N_A = 0$。<br>以支柱 $B$ 為轉軸列力矩平衡（板重逆時針力矩 = 小孩順時針力矩）：$$W_{\\text{板}} \\times \\overline{GB} = W_{\\text{孩}} \\times x$$$$400\\text{ N} \\times 4\\text{ m} = 640\\text{ N} \\times x \\implies \\mathbf{x = \\frac{1600}{640} = 2.5\\text{ m}}$$',
                '⚡ <strong>重點三・第 (2) 小題求安全走到最右端時支柱 $B$ 位置 $y$</strong>：<br>設支柱 $B$ 移至距最右端 $y$ 處。小孩站於最右端端點，其對 $B$ 之力臂為 $y$。<br>平板重心 $G$ 距最右端仍為 $7.5\\text{ m}$，故重心 $G$ 對支柱 $B$ 之力臂為 $(7.5 - y)$。<br>以支柱 $B$ 為轉軸列力矩平衡：$$400 \\times (7.5 - y) = 640 \\times y$$$$3000 - 400y = 640y \\implies 1040y = 3000 \\implies \\mathbf{y = \\frac{3000}{1040} = \\frac{75}{26} \\approx 2.88\\text{ m}} \\quad \\text{✅ 選 (C)}$$'
            ]
        }
    ]
    out_path = os.path.join(base_dir, 'physics_problems_data.js')
    print(f"Writing to {out_path}...")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('const PHYSICS_PROBLEMS_DATA = ' + json.dumps(problems, ensure_ascii=False, indent=2) + ';\n')
    print("Done! Data updated successfully.")

if __name__ == '__main__':
    main()
