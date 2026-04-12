"""增强版思维导图生成模块 - 基于Pretext框架，包含详细笔记内容"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path
from typing import List, Dict, Any
import json

from models.paper import Paper
from llm.factory import LLMProviderFactory
from utils.helpers import sanitize_filename


class MindMapGeneratorV2:
    """增强版思维导图生成器 - Pretext框架 + 详细笔记"""
    
    def __init__(self, llm_config=None):
        print(f"[DEBUG] MindMapGeneratorV2 初始化, llm_config={llm_config}")
        self.llm = None
        if llm_config:
            try:
                self.llm = LLMProviderFactory.create(llm_config)
                print(f"[DEBUG] LLM 创建成功: {self.llm}")
            except Exception as e:
                print(f"[DEBUG] LLM 创建失败: {e}")
                self.llm = None
    
    def generate(self, paper: Paper, note: str = None, use_markmap: bool = False) -> str:
        """生成思维导图
        
        Args:
            paper: 论文对象
            note: 论文笔记（可选）
            use_markmap: 是否使用markmap格式（默认使用D3.js）
            
        Returns:
            str: 思维导图HTML文件路径
        """
        print(f"[DEBUG] MindMapGeneratorV2.generate called, use_markmap={use_markmap}, has_llm={self.llm is not None}")
        
        if use_markmap:
            print(f"开始生成Markmap思维导图: {paper.title}")
            
            # 1. 使用LLM优化笔记内容，使其更适合思维导图展示
            if self.llm and note:
                print("[DEBUG] 使用LLM优化笔记内容...")
                optimized_note = self._optimize_note_for_mindmap(note, paper.title)
            else:
                print(f"[DEBUG] 跳过LLM优化, llm={self.llm is not None}, note={note is not None}")
                optimized_note = note or paper.abstract or paper.title
            
            # 2. 使用优化后的内容生成markmap
            output_path = self._generate_markmap_html(optimized_note, paper.title)
            print(f"Markmap思维导图生成完成: {output_path}")
        else:
            print(f"开始生成Pretext思维导图: {paper.title}")
            
            # 1. 构建思维导图数据结构
            if self.llm and note:
                mindmap_data = self._generate_with_llm(paper, note)
            else:
                mindmap_data = self._generate_pretext_structure(paper, note)
            
            # 2. 生成可视化HTML
            output_path = self._generate_html(mindmap_data, paper.title)
            
            print(f"Pretext思维导图生成完成: {output_path}")
        
        return output_path
    
    def _optimize_note_for_mindmap(self, note: str, title: str) -> str:
        """使用LLM优化笔记内容，使其更适合思维导图展示
        
        Args:
            note: 原始笔记内容
            title: 论文标题
            
        Returns:
            str: 优化后的Markdown内容
        """
        print("使用LLM优化笔记内容用于思维导图...")
        
        prompt = f"""请将以下学术论文笔记转换为适合思维导图展示的Markdown格式。

要求：
1. 保持原有的层级结构（# ## ###）
2. 精简每个要点的内容，保留核心信息
3. 使用简洁的关键词和短句
4. 确保逻辑清晰，层次分明
5. 不要添加新的内容，只优化现有内容的呈现方式
6. 总字数控制在2000字以内

原始笔记：
{note[:3000]}

请直接输出优化后的Markdown内容，不需要任何解释。"""

        try:
            messages = [{"role": "user", "content": prompt}]
            optimized = self.llm.chat(messages, max_tokens=2000, temperature=0.3)
            print("笔记优化完成")
            return optimized
        except Exception as e:
            print(f"笔记优化失败，使用原始内容: {e}")
            return note
    
    def _generate_markmap_html(self, note: str, title: str) -> str:
        """使用markmap生成思维导图HTML
        
        Args:
            note: Markdown格式的笔记内容
            title: 论文标题
            
        Returns:
            str: HTML文件路径
        """
        safe_title = sanitize_filename(title[:50])
        
        output_dir = Path("outputs/mindmaps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{safe_title}_markmap.html"
        print(f"[DEBUG] 生成markmap文件: {output_file}")
        
        # 清理note内容，确保是有效的Markdown
        cleaned_note = self._clean_markdown_for_markmap(note)
        print(f"[DEBUG] 清理后的note长度: {len(cleaned_note)}")
        
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markmap - {title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        #header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 15px 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        #header h1 {{
            margin: 0;
            font-size: 1.3em;
            color: #2c3e50;
        }}
        
        #header p {{
            margin: 5px 0 0 0;
            font-size: 0.85em;
            color: #7f8c8d;
        }}
        
        #markmap-container {{
            width: 100%;
            height: calc(100vh - 80px);
            background: white;
            position: relative;
            overflow: hidden;
        }}
        
        .markmap {{
            width: 100%;
            height: 100%;
            transform-origin: center center;
            transition: transform 0.3s ease;
        }}
        
        .markmap svg {{
            width: 100%;
            height: 100%;
        }}
        
        #zoom-controls {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 1000;
        }}
        
        #zoom-controls button {{
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 6px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        #zoom-controls button:hover {{
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        #zoom-controls button:active {{
            transform: scale(0.95);
        }}
        
        #zoom-level {{
            text-align: center;
            font-size: 12px;
            color: #666;
            font-weight: 500;
            padding: 5px 0;
        }}
        
        #fit-screen-btn {{
            width: auto !important;
            padding: 8px 12px !important;
            font-size: 12px !important;
            white-space: nowrap;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.17.2"></script>
</head>
<body>
    <div id="header">
        <h1>🧠 Markmap 思维导图</h1>
        <p>{title}</p>
    </div>
    
    <div id="markmap-container">
        <div class="markmap" id="markmap-content">
{cleaned_note}
        </div>
        
        <div id="zoom-controls">
            <button onclick="zoomIn()" title="放大">+</button>
            <div id="zoom-level">100%</div>
            <button onclick="zoomOut()" title="缩小">−</button>
            <button id="fit-screen-btn" onclick="fitToScreen()" title="适应屏幕">适应</button>
            <button onclick="resetZoom()" title="重置">⟲</button>
        </div>
    </div>
    
    <script>
        let currentZoom = 1;
        const minZoom = 0.3;
        const maxZoom = 3;
        const zoomStep = 0.2;
        
        function updateZoom() {{
            const markmapContent = document.getElementById('markmap-content');
            markmapContent.style.transform = `scale(${{currentZoom}})`;
            document.getElementById('zoom-level').textContent = Math.round(currentZoom * 100) + '%';
        }}
        
        function zoomIn() {{
            if (currentZoom < maxZoom) {{
                currentZoom += zoomStep;
                updateZoom();
            }}
        }}
        
        function zoomOut() {{
            if (currentZoom > minZoom) {{
                currentZoom -= zoomStep;
                updateZoom();
            }}
        }}
        
        function resetZoom() {{
            currentZoom = 1;
            updateZoom();
        }}
        
        function fitToScreen() {{
            // 计算适合的缩放比例
            const container = document.getElementById('markmap-container');
            const content = document.getElementById('markmap-content');
            const svg = content.querySelector('svg');
            
            if (svg) {{
                const containerWidth = container.clientWidth - 100; // 留边距
                const containerHeight = container.clientHeight - 100;
                const svgWidth = svg.clientWidth || svg.getBoundingClientRect().width;
                const svgHeight = svg.clientHeight || svg.getBoundingClientRect().height;
                
                if (svgWidth > 0 && svgHeight > 0) {{
                    const scaleX = containerWidth / svgWidth;
                    const scaleY = containerHeight / svgHeight;
                    currentZoom = Math.min(scaleX, scaleY, 1); // 不超过100%
                    currentZoom = Math.max(currentZoom, minZoom);
                    updateZoom();
                }}
            }}
        }}
        
        // 鼠标滚轮缩放
        document.getElementById('markmap-container').addEventListener('wheel', function(e) {{
            if (e.ctrlKey || e.metaKey) {{
                e.preventDefault();
                if (e.deltaY < 0) {{
                    zoomIn();
                }} else {{
                    zoomOut();
                }}
            }}
        }});
        
        // 键盘快捷键
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey || e.metaKey) {{
                switch(e.key) {{
                    case '=':
                    case '+':
                        e.preventDefault();
                        zoomIn();
                        break;
                    case '-':
                        e.preventDefault();
                        zoomOut();
                        break;
                    case '0':
                        e.preventDefault();
                        resetZoom();
                        break;
                }}
            }}
        }});
        
        // 自动初始化markmap
        window.addEventListener('load', function() {{
            console.log('Markmap loaded successfully');
            // 延迟适应屏幕，等待markmap渲染完成
            setTimeout(fitToScreen, 500);
        }});
    </script>
</body>
</html>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def _clean_markdown_for_markmap(self, note: str) -> str:
        """清理Markdown内容，使其适合markmap显示
        
        Args:
            note: 原始笔记内容
            
        Returns:
            str: 清理后的Markdown
        """
        if not note:
            return "# 暂无内容\\n\\n- 等待生成笔记..."
        
        lines = note.split('\\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过空行但保留一个
            if not stripped:
                if cleaned_lines and cleaned_lines[-1] != '':
                    cleaned_lines.append('')
                continue
            
            # 跳过Obsidian链接
            if stripped.startswith('- [[') or stripped.startswith('[[#'):
                continue
            
            # 跳过标签行
            if stripped.startswith('## 标签') or stripped.startswith('# Tags'):
                continue
            
            # 跳过相关链接行
            if stripped.startswith('## 相关链接') or stripped.startswith('# Links'):
                continue
            
            # 跳过模板化内容
            skip_patterns = [
                "由于缺少具体论文内容",
                "[详细描述]",
                "[具体实现]",
                "[对论文的贡献]",
                "[在此插入",
                "[待补充]",
            ]
            should_skip = False
            for pattern in skip_patterns:
                if pattern in stripped:
                    should_skip = True
                    break
            if should_skip:
                continue
            
            cleaned_lines.append(line)
        
        # 移除末尾的空行
        while cleaned_lines and cleaned_lines[-1] == '':
            cleaned_lines.pop()
        
        result = '\\n'.join(cleaned_lines)
        
        # 确保内容以标题开头
        if not result.strip().startswith('#'):
            result = "# 论文笔记\\n\\n" + result
        
        return result
    
    def _generate_with_llm(self, paper: Paper, note: str) -> Dict:
        """使用LLM生成思维导图结构，包含详细笔记内容"""
        prompt = f"""请基于以下论文笔记，生成一个专业、详细的思维导图结构。

【输入内容】
论文标题: {paper.title}

笔记内容:
{note[:8000]}

【输出要求】

## 1. 结构规范
必须严格遵循Pretext框架的5个阶段:
1. 📖 预读阶段 - 快速了解基本信息和核心观点
2. 🏗️ 结构分析 - 整体框架和各部分主要内容
3. 🔍 深度阅读 - 核心概念和技术实现细节
4. 💡 批判思考 - 创新点、局限性和对比分析
5. 🚀 延伸思考 - 应用场景、未来方向和领域影响

## 2. 节点命名规则（极其重要，必须严格遵守）

### ❌ 严格禁止使用的节点名称:
- 要点1、要点2、要点3...
- 内容1、内容2、内容3...
- 信息A、信息B、信息C...
- 发现1、发现2、发现3...
- 关键1、关键2、关键3...
- 任何数字编号或字母编号的占位符
- 主题分类、详细点1、详细点2等泛化名称
- 临床意义、诊断要点（作为叶子节点名称时禁止，必须展开为具体内容）

### ✅ 必须使用的节点名称:
- 具体的概念名称（如"自注意力机制"、"TNM分期"）
- 专业术语（如"残差连接"、"EGFR突变"）
- 方法/技术名称（如"Transformer架构"、"免疫组化"）
- 分类/类别名称（如"上皮性肿瘤"、"神经内分泌肿瘤"）
- 从原文中提取的关键主题词

### 命名示例:
医学领域正确示例:
- ✅ 临床表现诊断、影像学检查方法、组织病理学分类、TNM分期系统、靶向治疗策略
- ❌ 要点1、内容概述、关键发现

技术领域正确示例:
- ✅ Transformer架构、自注意力机制、多头注意力、位置编码
- ❌ 方法1、技术细节、实现方式

## 3. 内容深度要求（极其重要）

### 医学领域内容深度标准:
每个诊断/治疗/检查相关节点必须包含以下维度的详细内容：

#### 对于"临床表现"类节点：
- description: 必须列举具体症状（如"咳嗽、咯血、胸痛、呼吸困难"）
- note: 必须包含：发病机制、典型体征、严重程度分级、与其他疾病的鉴别要点

#### 对于"影像学检查"类节点：
- description: 必须说明检查目的和适用场景
- note: 必须包含：检查方法细节、典型影像表现、诊断标准、敏感性和特异性数据

#### 对于"病理诊断"类节点：
- description: 必须说明诊断方法和标本类型
- note: 必须包含：病理特征描述、分级标准、免疫组化标志物、分子病理特征

#### 对于"治疗策略"类节点：
- description: 必须说明治疗方案和适用人群
- note: 必须包含：具体药物/手术方式、剂量/疗程、疗效数据、副作用管理

### 禁止内容模板:
❌ "该要点的临床应用价值"
❌ "诊断时需要注意的关键点"
❌ "相关内容"
❌ "补充信息"
❌ "详细说明"

### 正确内容示例:
✅ "临床意义：该指标升高提示肿瘤负荷增加，可用于疗效监测和预后评估。正常值<10ng/mL，>100ng/mL提示广泛转移"
✅ "诊断要点：①年龄>40岁吸烟者；②持续性咳嗽>2周；③CT显示肺门肿块伴纵隔淋巴结肿大；④需与肺结核、肺炎鉴别"

## 4. 内容提取规则

### 从原文提取节点名称的方法:
1. 识别章节标题中的核心概念
2. 提取关键段落的第一句主题句
3. 找出重复出现的重要术语
4. 识别方法、技术、分类的具体名称
5. 使用专业领域内的标准命名

### 描述内容生成规则:
- 描述必须是具体的，不是泛泛的
- 从原文摘录关键信息
- 使用准确的数字、数据、术语
- 保持医学/技术准确性
- 每个note字段至少50-100字的具体内容

## 5. JSON输出格式

```json
{{
  "name": "论文标题（简洁）",
  "description": "论文核心贡献的准确描述（50-100字）",
  "type": "root",
  "children": [
    {{
      "name": "📖 预读阶段",
      "description": "该阶段的核心内容概述",
      "type": "branch",
      "note": "详细笔记内容（100-200字）",
      "children": [
        {{
          "name": "【具体概念名称，禁止用要点1】",
          "description": "具体描述（来自原文，包含关键数据/症状/方法）",
          "type": "leaf",
          "note": "详细笔记（50-100字，包含机制/标准/数据）",
          "children": [
            {{
              "name": "【具体子概念】",
              "description": "具体细节（如具体症状、检查参数）",
              "type": "detail",
              "note": "详细说明（如正常值范围、诊断标准）"
            }}
          ]
        }}
      ]
    }}
  ]
}}
```

## 6. 质量检查清单（生成后必须自检）

- [ ] 所有节点名称都是具体概念，没有"要点X"等占位符
- [ ] 每个描述字段都有具体内容，不是泛泛而谈
- [ ] 每个note字段至少50-100字的具体内容
- [ ] 没有出现"该要点的临床应用价值"等模板化描述
- [ ] 医学内容包含具体症状/检查/数据
- [ ] 专业术语使用准确
- [ ] 层次结构清晰（5个阶段 → 3-4个子主题 → 2-3个要点）
- [ ] 内容来自原文，不是编造
- [ ] JSON格式正确，可以解析

## 7. 生成步骤

步骤1: 仔细阅读笔记，识别所有核心概念、专业术语和关键数据
步骤2: 将概念组织成5个Pretext阶段
步骤3: 为每个节点命名（使用具体术语，禁止占位符）
步骤4: 填写描述和笔记（必须包含具体数据/症状/标准，禁止模板化描述）
步骤5: 质量检查（确保没有"要点X"等违规名称，确保内容具体充实）

【严格禁止】
1. 如果检测到节点名称包含"要点"、"内容"、"信息"、"发现"、"关键"等泛化词汇 + 数字，必须重新生成！
2. 如果检测到description或note字段使用"该要点的临床应用价值"、"诊断时需要注意的关键点"等模板化内容，必须重新生成！
3. 如果节点内容少于30字，必须扩展补充！

请输出完整的JSON格式思维导图结构:"""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个思维导图设计专家，擅长将复杂的论文内容转化为清晰的结构化思维导图。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm.chat(messages)
            
            # 解析JSON
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            mindmap_data = json.loads(json_str.strip())
            
            # 后处理：验证和修复节点名称
            mindmap_data = self._post_process_mindmap(mindmap_data)
            
            return mindmap_data
            
        except Exception as e:
            print(f"LLM生成思维导图失败: {e}，回退到规则方法")
            return self._generate_pretext_structure(paper)
    
    def _generate_pretext_structure(self, paper: Paper, note: str = None) -> Dict:
        """基于Pretext框架生成4层深度思维导图结构（智能提取内容）"""
        
        # 优先使用笔记内容
        content_source = note if note else paper.abstract
        
        # 提取关键主题和概念
        extracted_topics = self._extract_topics_from_content(content_source)
        
        # 构建5个Pretext阶段
        stage_configs = [
            ("📖 预读阶段", "快速了解论文背景和核心问题"),
            ("🏗️ 结构分析", "论文整体框架和方法概述"),
            ("🔍 深度阅读", "核心方法和技术实现细节"),
            ("💡 批判思考", "创新点、局限性和对比分析"),
            ("🚀 延伸思考", "应用场景、未来方向和领域影响")
        ]
        
        structure_children = []
        
        for stage_name, stage_desc in stage_configs:
            # 为每个阶段分配主题
            stage_topics = self._assign_topics_to_stage(extracted_topics, stage_name)
            
            if not stage_topics:
                # 如果没有匹配的主题，从摘要生成
                stage_topics = self._generate_topics_from_abstract(
                    paper.abstract, stage_name
                )
            
            # 创建阶段分支
            stage_children = []
            for topic in stage_topics[:4]:  # 每个阶段最多4个主题
                topic_children = self._generate_topic_children(topic)
                stage_children.append({
                    "name": topic['name'][:30],
                    "description": topic['description'][:100],
                    "type": "leaf",
                    "note": topic.get('detail', topic['description'])[:200],
                    "children": topic_children
                })
            
            if stage_children:
                structure_children.append({
                    "name": stage_name,
                    "description": stage_desc,
                    "type": "branch",
                    "note": f"包含 {len(stage_children)} 个核心主题",
                    "children": stage_children
                })
        
        # 如果没有提取到任何内容，使用基于摘要的智能生成
        if not structure_children:
            structure_children = self._generate_structure_from_abstract(paper.abstract)
        
        return {
            "name": paper.title[:60],
            "description": paper.abstract[:150] if paper.abstract else "论文思维导图",
            "type": "root",
            "children": structure_children[:5]
        }
    
    def _extract_topics_from_content(self, content: str) -> List[Dict]:
        """从内容中提取关键主题"""
        if not content:
            return []
        
        topics = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测标题行（以#开头）
            if line.startswith('#'):
                # 提取标题文本
                title = line.lstrip('#').strip()
                if title and len(title) < 50:
                    topics.append({
                        'name': title,
                        'description': '',
                        'detail': '',
                        'source': 'heading'
                    })
            
            # 检测要点（以-或*开头）
            elif line.startswith(('- ', '* ')):
                point = line[2:].strip()
                # 提取关键短语（通常是前半句）
                if ':' in point or '：' in point:
                    parts = point.replace('：', ':').split(':', 1)
                    name = parts[0].strip()[:30]
                    desc = parts[1].strip()[:100]
                else:
                    # 提取前15个字符作为名称
                    name = point[:30] if len(point) > 30 else point
                    desc = point[:100]
                
                if name and len(name) > 3:
                    topics.append({
                        'name': name,
                        'description': desc,
                        'detail': point[:200],
                        'source': 'bullet'
                    })
            
            # 检测编号列表（1. 2. 等）
            elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                point = line[2:].strip()
                if point and len(point) > 5:
                    topics.append({
                        'name': point[:30],
                        'description': point[:100],
                        'detail': point[:200],
                        'source': 'numbered'
                    })
        
        # 去重
        seen_names = set()
        unique_topics = []
        for topic in topics:
            if topic['name'] not in seen_names:
                seen_names.add(topic['name'])
                unique_topics.append(topic)
        
        return unique_topics[:20]  # 最多20个主题
    
    def _assign_topics_to_stage(self, topics: List[Dict], stage_name: str) -> List[Dict]:
        """根据阶段名称分配主题"""
        stage_keywords = {
            "📖 预读阶段": ['背景', '问题', '动机', '挑战', 'introduction', 'abstract', 'related'],
            "🏗️ 结构分析": ['方法', '架构', '模型', '框架', 'method', 'architecture', 'model'],
            "🔍 深度阅读": ['实现', '细节', '算法', '技术', 'implementation', 'algorithm'],
            "💡 批判思考": ['创新', '优势', '局限', '对比', 'contribution', 'comparison'],
            "🚀 延伸思考": ['应用', '未来', '展望', '影响', 'application', 'future', 'conclusion']
        }
        
        keywords = stage_keywords.get(stage_name, [])
        assigned = []
        
        for topic in topics:
            text = (topic['name'] + ' ' + topic['description']).lower()
            if any(kw in text for kw in keywords):
                assigned.append(topic)
        
        # 如果匹配太少，均匀分配
        if len(assigned) < 2 and topics:
            idx = hash(stage_name) % max(len(topics), 1)
            assigned = topics[idx:idx+3]
        
        return assigned[:4]
    
    def _generate_topics_from_abstract(self, abstract: str, stage_name: str) -> List[Dict]:
        """从摘要生成主题"""
        if not abstract:
            return []
        
        # 将摘要分割成句子
        import re
        sentences = re.split(r'[。！？.!?]', abstract)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        topics = []
        stage_keywords = {
            "📖 预读阶段": 0,
            "🏗️ 结构分析": 1,
            "🔍 深度阅读": 2,
            "💡 批判思考": 3,
            "🚀 延伸思考": 4
        }
        
        stage_idx = stage_keywords.get(stage_name, 0)
        
        # 根据阶段选择不同的句子
        for i, sent in enumerate(sentences):
            if i % 5 == stage_idx:  # 均匀分配到不同阶段
                # 提取关键短语作为名称
                words = sent.split()
                if len(words) >= 3:
                    name = ' '.join(words[:4]) if len(words) > 4 else sent[:20]
                else:
                    name = sent[:20]
                
                topics.append({
                    'name': name,
                    'description': sent[:100],
                    'detail': sent[:200]
                })
        
        return topics[:3]
    
    def _generate_topic_children(self, topic: Dict) -> List[Dict]:
        """为主题生成子节点"""
        children = []
        detail = topic.get('detail', '')
        
        # 从detail中提取子主题
        if detail:
            # 分割成子要点
            sub_points = detail.split('，')
            for i, point in enumerate(sub_points[:2]):
                point = point.strip()
                if len(point) > 5:
                    children.append({
                        "name": point[:25] if len(point) > 25 else point,
                        "description": point[:60],
                        "type": "detail",
                        "note": point[:120]
                    })
        
        # 如果没有提取到子主题，创建默认的
        if not children:
            children = [
                {
                    "name": "关键概念",
                    "description": topic['description'][:60] if topic.get('description') else "核心内容",
                    "type": "detail",
                    "note": topic.get('detail', '详细说明')[:120]
                },
                {
                    "name": "应用价值",
                    "description": "实际应用意义",
                    "type": "detail",
                    "note": "在相关领域的重要性和应用场景"
                }
            ]
        
        return children
    
    def _generate_structure_from_abstract(self, abstract: str) -> List[Dict]:
        """基于摘要生成默认结构"""
        if not abstract:
            return []
        
        # 提取关键句子
        import re
        sentences = re.split(r'[。！？.!?]', abstract)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        # 分配到5个阶段
        stages = [
            ("📖 预读阶段", "研究背景与问题"),
            ("🏗️ 结构分析", "方法框架概述"),
            ("🔍 深度阅读", "技术实现细节"),
            ("💡 批判思考", "创新点与优势"),
            ("🚀 延伸思考", "应用与展望")
        ]
        
        structure = []
        for i, (stage_name, stage_desc) in enumerate(stages):
            # 为每个阶段选择句子
            if i < len(sentences):
                sent = sentences[i]
                # 提取关键短语
                words = sent.split()[:4]
                name = ' '.join(words) if words else f"主题{i+1}"
                
                children = [
                    {
                        "name": name[:25],
                        "description": sent[:80],
                        "type": "leaf",
                        "note": sent[:150],
                        "children": [
                            {
                                "name": "核心内容",
                                "description": sent[:50],
                                "type": "detail",
                                "note": sent[:100]
                            }
                        ]
                    }
                ]
                
                structure.append({
                    "name": stage_name,
                    "description": stage_desc,
                    "type": "branch",
                    "note": sent[:100],
                    "children": children
                })
        
        return structure
    
    def _post_process_mindmap(self, data: Dict) -> Dict:
        """后处理思维导图，修复占位符名称和模板化内容"""
        import re
        
        # 定义占位符模式
        placeholder_patterns = [
            r'^要点\d+$',
            r'^内容\d+$',
            r'^信息\w*\d*$',
            r'^发现\d+$',
            r'^关键\d+$',
            r'^主题分类$',
            r'^详细点\d+$',
        ]
        
        # 定义模板化内容模式
        template_patterns = [
            r'该要点的临床应用价值',
            r'诊断时需要注意的关键点',
            r'相关内容$',
            r'补充信息$',
            r'详细说明$',
            r'详细内容$',
            r'待补充',
            r'暂无',
        ]
        
        def is_placeholder(name: str) -> bool:
            """检查是否是占位符名称"""
            for pattern in placeholder_patterns:
                if re.match(pattern, name):
                    return True
            return False
        
        def is_template_content(content: str) -> bool:
            """检查是否是模板化内容"""
            if not content or len(content) < 10:
                return True
            for pattern in template_patterns:
                if re.search(pattern, content):
                    return True
            return False
        
        def extract_better_name(node: Dict) -> str:
            """从节点内容提取更好的名称"""
            # 尝试从description提取
            desc = node.get('description', '')
            if desc and len(desc) > 5:
                # 提取前10个字符作为名称
                return desc[:10] + "..." if len(desc) > 10 else desc
            
            # 尝试从note提取
            note = node.get('note', '')
            if note and len(note) > 5:
                return note[:10] + "..." if len(note) > 10 else note
            
            # 默认返回
            return "相关内容"
        
        def extract_better_content(node: Dict, field: str) -> str:
            """从节点其他字段提取更好的内容"""
            # 尝试从name提取
            name = node.get('name', '')
            if name and len(name) > 3:
                return f"关于{name}的具体内容需要从原文中提取详细描述。"
            
            # 尝试从其他字段提取
            for key in ['description', 'note']:
                if key != field:
                    value = node.get(key, '')
                    if value and len(value) > 20 and not is_template_content(value):
                        return value
            
            return ""
        
        def process_node(node: Dict, parent_name: str = ""):
            """递归处理节点"""
            name = node.get('name', '')
            
            # 检查并修复占位符名称
            if is_placeholder(name):
                better_name = extract_better_name(node)
                print(f"修复占位符名称: '{name}' -> '{better_name}'")
                node['name'] = better_name
            
            # 检查并修复模板化description
            description = node.get('description', '')
            if is_template_content(description):
                better_desc = extract_better_content(node, 'description')
                if better_desc:
                    print(f"修复模板化description: '{description[:30]}...' -> '{better_desc[:30]}...'")
                    node['description'] = better_desc
                else:
                    # 使用父节点名称生成描述
                    if parent_name:
                        node['description'] = f"{name}是{parent_name}的重要组成部分，具体内容详见相关文献。"
            
            # 检查并修复模板化note
            note = node.get('note', '')
            if is_template_content(note):
                better_note = extract_better_content(node, 'note')
                if better_note:
                    print(f"修复模板化note: '{note[:30]}...' -> '{better_note[:30]}...'")
                    node['note'] = better_note
                else:
                    # 使用description扩展
                    if description and len(description) > 10:
                        node['note'] = f"{description} 建议进一步查阅原文获取更详细的信息和数据。"
            
            # 处理子节点
            for child in node.get('children', []):
                process_node(child, name)
        
        process_node(data)
        return data
    
    def _generate_html(self, mindmap_data: Dict, title: str) -> str:
        """生成思维导图HTML，包含详细内容面板"""
        safe_title = sanitize_filename(title[:50])
        
        output_dir = Path("outputs/mindmaps")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{safe_title}_pretext_mindmap.html"
        
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pretext思维导图 - {title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        body {{
            margin: 0;
            font-family: 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
            background: var(--bg-gradient);
            overflow: hidden;
            display: flex;
        }}
        
        #mindmap-container {{
            flex: 1;
            height: 100vh;
            position: relative;
        }}
        
        #mindmap {{
            width: 100%;
            height: 100%;
        }}
        
        #detail-panel {{
            width: 350px;
            height: 100vh;
            background: white;
            box-shadow: -4px 0 20px rgba(0,0,0,0.1);
            padding: 20px;
            overflow-y: auto;
            box-sizing: border-box;
        }}
        
        #detail-panel h2 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 1.3em;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
        }}
        
        #detail-panel .section {{
            margin-bottom: 20px;
        }}
        
        #detail-panel .section h3 {{
            margin: 0 0 8px 0;
            color: var(--primary-color);
            font-size: 1em;
        }}
        
        #detail-panel .section p {{
            margin: 0;
            color: #555;
            font-size: 0.9em;
            line-height: 1.6;
        }}
        
        #detail-panel .note-box {{
            background: #f8f9fa;
            border-left: 4px solid var(--primary-color);
            padding: 12px;
            margin-top: 10px;
            border-radius: 4px;
        }}
        
        #detail-panel .note-box h4 {{
            margin: 0 0 5px 0;
            color: #666;
            font-size: 0.85em;
        }}
        
        #detail-panel .note-box p {{
            margin: 0;
            color: #333;
            font-size: 0.9em;
        }}
        
        .node-circle {{
            fill: #fff;
            stroke: var(--primary-color);
            stroke-width: 3px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .node:hover .node-circle {{
            r: 10;
            fill: var(--primary-color);
        }}
        
        .node.selected .node-circle {{
            fill: var(--secondary-color);
            stroke: var(--secondary-color);
            r: 10;
        }}
        
        .node text {{
            font-size: 13px;
            font-weight: 500;
            text-shadow: 0 1px 3px rgba(255,255,255,0.9);
            cursor: pointer;
        }}
        
        .link {{
            fill: none;
            stroke: rgba(255,255,255,0.6);
            stroke-width: 2px;
        }}
        
        #title {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        #title h1 {{
            margin: 0;
            font-size: 1.3em;
            color: #2c3e50;
        }}
        
        #title p {{
            margin: 5px 0 0 0;
            font-size: 0.85em;
            color: #7f8c8d;
        }}
        
        #controls {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        #controls button {{
            margin: 3px;
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            background: var(--primary-color);
            color: white;
            cursor: pointer;
            font-size: 11px;
        }}
        
        #controls button:hover {{
            background: var(--secondary-color);
        }}
        
        .empty-state {{
            text-align: center;
            color: #999;
            margin-top: 50px;
        }}
        
        .empty-state i {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div id="mindmap-container">
        <div id="title">
            <h1>📚 Pretext思维导图</h1>
            <p>{title}</p>
        </div>
        
        <div id="controls">
            <button onclick="expandAll()">展开全部</button>
            <button onclick="collapseAll()">收起全部</button>
            <button onclick="resetZoom()">重置视图</button>
        </div>
        
        <div id="mindmap"></div>
    </div>
    
    <div id="detail-panel">
        <h2>📋 节点详情</h2>
        <div id="detail-content">
            <div class="empty-state">
                <p>点击左侧思维导图的节点<br>查看详细内容</p>
            </div>
        </div>
    </div>
    
    <script>
        const data = {json.dumps(mindmap_data, ensure_ascii=False)};
        
        const containerWidth = document.getElementById('mindmap-container').clientWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#mindmap").append("svg")
            .attr("width", containerWidth)
            .attr("height", height)
            .call(d3.zoom().on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }}));
        
        const g = svg.append("g")
            .attr("transform", "translate(80, " + height / 2 + ")");
        
        let i = 0;
        const duration = 750;
        let root;
        let selectedNode = null;
        
        const tree = d3.tree().size([height - 150, containerWidth - 400]);
        
        root = d3.hierarchy(data, d => d.children);
        root.x0 = height / 2;
        root.y0 = 0;
        
        // 初始收起第三层
        if (root.children) {{
            root.children.forEach(child => {{
                if (child.children) {{
                    child.children.forEach(collapse);
                }}
            }});
        }}
        
        update(root);
        
        // 默认选中根节点
        selectNode(root);
        
        function collapse(d) {{
            if (d.children) {{
                d._children = d.children;
                d._children.forEach(collapse);
                d.children = null;
            }}
        }}
        
        function expand(d) {{
            if (d._children) {{
                d.children = d._children;
                d._children.forEach(expand);
                d._children = null;
            }}
        }}
        
        function selectNode(d) {{
            // 移除所有节点的选中状态
            d3.selectAll(".node").classed("selected", false);
            
            // 设置新的选中状态 - 通过id选择
            selectedNode = d;
            d3.selectAll(".node").filter(n => n === d).classed("selected", true);
            
            // 更新详情面板
            updateDetailPanel(d.data);
        }}
        
        function updateDetailPanel(data) {{
            const panel = document.getElementById('detail-content');
            
            let html = `
                <div class="section">
                    <h3>📝 标题</h3>
                    <p>${{data.name}}</p>
                </div>
            `;
            
            if (data.description) {{
                html += `
                    <div class="section">
                        <h3>📖 描述</h3>
                        <p>${{data.description}}</p>
                    </div>
                `;
            }}
            
            if (data.note) {{
                html += `
                    <div class="note-box">
                        <h4>📌 笔记摘录</h4>
                        <p>${{data.note}}</p>
                    </div>
                `;
            }}
            
            if (data.type) {{
                const typeLabels = {{
                    'root': '根节点',
                    'branch': '分支节点',
                    'leaf': '叶节点',
                    'concept': '概念',
                    'method': '方法',
                    'result': '结果',
                    'insight': '洞察'
                }};
                html += `
                    <div class="section">
                        <h3>🏷️ 类型</h3>
                        <p>${{typeLabels[data.type] || data.type}}</p>
                    </div>
                `;
            }}
            
            panel.innerHTML = html;
        }}
        
        function update(source) {{
            const treeData = tree(root);
            
            const nodes = treeData.descendants();
            const links = treeData.links();
            
            nodes.forEach(d => {{ d.y = d.depth * 200; }});
            
            const node = g.selectAll('g.node')
                .data(nodes, d => d.id || (d.id = ++i));
            
            const nodeEnter = node.enter().append('g')
                .attr('class', 'node')
                .attr("transform", d => "translate(" + source.y0 + "," + source.x0 + ")")
                .on('click', (event, d) => {{
                    selectNode(d);
                    click(event, d);
                }});
            
            nodeEnter.append('circle')
                .attr('class', 'node-circle')
                .attr('r', 1e-6)
                .style("fill", d => d._children ? "#764ba2" : "#fff");
            
            nodeEnter.append('text')
                .attr("dy", ".35em")
                .attr("x", d => d.children || d._children ? -13 : 13)
                .attr("text-anchor", d => d.children || d._children ? "end" : "start")
                .text(d => d.data.name)
                .style("fill-opacity", 1e-6);
            
            const nodeUpdate = node.merge(nodeEnter);
            
            nodeUpdate.transition()
                .duration(duration)
                .attr("transform", d => "translate(" + d.y + "," + d.x + ")");
            
            nodeUpdate.select('circle.node-circle')
                .attr('r', d => d.depth === 0 ? 10 : 7)
                .style("fill", d => d._children ? "#764ba2" : "#fff")
                .attr('cursor', 'pointer');
            
            nodeUpdate.select('text')
                .style("fill-opacity", 1);
            
            const nodeExit = node.exit().transition()
                .duration(duration)
                .attr("transform", d => "translate(" + source.y + "," + source.x + ")")
                .remove();
            
            nodeExit.select('circle')
                .attr('r', 1e-6);
            
            nodeExit.select('text')
                .style("fill-opacity", 1e-6);
            
            const link = g.selectAll('path.link')
                .data(links, d => d.target.id);
            
            const linkEnter = link.enter().insert('path', "g")
                .attr("class", "link")
                .attr('d', d => {{
                    const o = {{x: source.x0, y: source.y0}};
                    return diagonal(o, o);
                }});
            
            const linkUpdate = link.merge(linkEnter);
            
            linkUpdate.transition()
                .duration(duration)
                .attr('d', d => diagonal(d.source, d.target));
            
            const linkExit = link.exit().transition()
                .duration(duration)
                .attr('d', d => {{
                    const o = {{x: source.x, y: source.y}};
                    return diagonal(o, o);
                }})
                .remove();
            
            nodes.forEach(d => {{
                d.x0 = d.x;
                d.y0 = d.y;
            }});
        }}
        
        function diagonal(s, d) {{
            return `M ${{s.y}} ${{s.x}}
                    C ${{(s.y + d.y) / 2}} ${{s.x}},
                      ${{(s.y + d.y) / 2}} ${{d.x}},
                      ${{d.y}} ${{d.x}}`;
        }}
        
        function click(event, d) {{
            if (d.children) {{
                d._children = d.children;
                d.children = null;
            }} else {{
                d.children = d._children;
                d._children = null;
            }}
            update(d);
        }}
        
        function expandAll() {{
            // 递归展开所有节点
            function expandRecursive(d) {{
                if (d._children) {{
                    d.children = d._children;
                    d._children = null;
                }}
                if (d.children) {{
                    d.children.forEach(expandRecursive);
                }}
            }}
            expandRecursive(root);
            update(root);
        }}
        
        function collapseAll() {{
            // 递归收起所有非根节点
            function collapseRecursive(d) {{
                if (d.children) {{
                    d._children = d.children;
                    d._children.forEach(collapseRecursive);
                    d.children = null;
                }}
            }}
            if (root.children) {{
                root.children.forEach(collapseRecursive);
            }}
            update(root);
        }}
        
        function resetZoom() {{
            // 使用正确的D3.js v7 zoom API
            const zoom = d3.zoom().on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(80, height / 2).scale(1)
            );
        }}
    </script>
</body>
</html>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
