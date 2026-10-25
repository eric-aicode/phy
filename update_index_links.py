import re

def update_index():
    for fn in ['index.html', 'topic_catalog.html']:
        path = rf'g:\我的雲端硬碟\00學測中心\靜力學_向量封閉三角形\{fn}'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = re.sub(
            r'href=[\"\'](problem\d+|exercise\d+|torque\d+|equil\d+|frict\d+)\.html[\"\']',
            r'href="viewer.html?id=\1"',
            content
        )
        new_content = re.sub(
            r'data-href=[\"\'](problem\d+|exercise\d+|torque\d+|equil\d+|frict\d+)\.html[\"\']',
            r'data-href="viewer.html?id=\1"',
            new_content
        )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {fn} links to viewer.html?id=...")

if __name__ == '__main__':
    update_index()
