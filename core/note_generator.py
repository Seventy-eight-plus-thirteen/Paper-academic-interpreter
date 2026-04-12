"""笔记生成模块（优化版中文Wiki风格）"""
from typing import List
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.paper import Paper, Section
from llm.factory import LLMProviderFactory


class NoteGenerator:
    """笔记生成器 - 优化版中文Wiki风格"""
    
    def __init__(self, llm_config):
        self.llm = LLMProviderFactory.create(llm_config)
    
    def generate(self, paper: Paper) -> str:
        """生成优化版中文Wiki风格的完整Markdown笔记
        
        Args:
            paper: 论文对象
            
        Returns:
            str: 优化后的中文Markdown笔记
        """
        print(f"开始生成优化版中文笔记: {paper.title}")
        
        # 构建优化prompt
        prompt = self._build_optimization_prompt(paper)
        
        try:
            messages = [
                {"role": "system", "content": "你是一位专业的学术论文分析专家，擅长将英文论文转换为结构清晰、内容丰富的中文Wiki笔记。"},
                {"role": "user", "content": prompt}
            ]
            
            note = self.llm.chat(messages, max_tokens=6000, temperature=0.3)
            print("笔记生成完成")
            
            # 后处理优化
            note = self._post_optimize(note)
            
            return note
        except Exception as e:
            print(f"笔记生成失败: {e}")
            return self._generate_fallback_note(paper)
    
    def _build_optimization_prompt(self, paper: Paper) -> str:
        """构建笔记优化prompt"""
        
        # 收集论文内容
        sections_text = ""
        for i, section in enumerate(paper.sections[:10], 1):  # 限制章节数量
            sections_text += f"\n\n## 章节{i}: {section.title}\n{section.content[:1500]}"
        
        prompt = f"""【重要】请将以下英文论文转换为中文Wiki笔记。必须全部使用中文！

## 论文信息（原文）

**标题**: {paper.title}
**作者**: {', '.join(paper.authors) if paper.authors else '未知'}
**摘要**: {paper.abstract[:2000] if paper.abstract else '无摘要'}

**论文章节内容**:
{sections_text}

---

## 【要求】输出格式（全部使用中文）

# [中文标题]

## 论文基本信息

- **标题**: {paper.title}
- **作者**: {', '.join(paper.authors) if paper.authors else '未知'}
- **期刊/会议**: [发表信息]
- **时间**: [发表时间]

---

## 摘要

### 研究背景
[用中文介绍研究背景和问题]

### 研究方法
- **数据来源**: [中文描述]
- **样本规模**: [中文描述]
- **方法**: [中文描述]

### 主要成果
- [中文描述关键结果1]
- [中文描述关键结果2]

### 研究意义
[中文描述研究的意义和价值]

---

## 1. 引言

### 1.1 研究背景
[用中文描述领域现状和存在的问题]

### 1.2 研究动机
[用中文描述为什么需要这项研究]

### 1.3 研究目标
1. [中文目标1]
2. [中文目标2]

---

## 2. 材料与方法

### 2.1 数据集
[用中文描述数据]

### 2.2 方法
[用中文描述方法]

---

## 3. 实验结果

### 3.1 主要结果
[用中文描述结果，使用Markdown表格展示对比数据]

### 3.2 结果分析
[用中文解读结果]

---

## 4. 讨论

### 4.1 方法优势
[用中文分析优势]

### 4.2 方法局限
[用中文描述局限性]

### 4.3 未来方向
[用中文描述未来研究方向]

---

## 5. 结论

### 5.1 主要贡献
[用中文总结贡献]

### 5.2 临床意义
[用中文说明意义]

---

## 附录：关键术语

| 术语 | 定义 |
|------|------|
| [术语1] | [中文定义] |
| [术语2] | [中文定义] |

---

## 【强制要求】

1. **必须使用中文**：除了专有名词（如KNHIS、AUROC、AF）和英文缩写外，全部使用中文
2. **禁止英文段落**：不要出现大段的英文内容
3. **删除空标题**：不要生成只有标题没有内容的章节（如果内容太少，我会尝试补充）
4. **深化解释**：对每个结果提供详细的中文解释
5. **使用表格**：对比数据使用Markdown表格
6. **结构清晰**：使用 1.1, 1.2 等层级编号
7. **内容充实**：每个要点都要有详细的中文说明

请直接输出中文笔记内容："""

        return prompt
    
    def _post_optimize(self, note: str) -> str:
        """笔记后处理优化 - 只删除真正空的章节"""
        print("开始笔记后处理优化...")
        
        lines = note.split('\n')
        optimized_lines = []
        
        # 跟踪状态
        seen_sections = set()
        current_section_buffer = []
        current_section_content = []
        
        skip_patterns = [
            "[详细描述]",
            "[具体实现]",
            "[在此插入",
            "[待补充]",
            "[公式将在此处插入",
            "[图表将在此处插入",
            "[关键数据将在此处插入",
            "[局限性将在此处插入",
            "内容概述",
            "### 内容概述",
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 跳过包含跳过模式的行
            should_skip = False
            for pattern in skip_patterns:
                if pattern in stripped:
                    should_skip = True
                    break
            
            if should_skip:
                i += 1
                continue
            
            # 检测章节标题（只检测一级和二级标题）
            is_section_header = (stripped.startswith('# ') or stripped.startswith('## ')) and not stripped.startswith('## 标签')
            
            if is_section_header:
                # 处理之前的章节
                if current_section_buffer:
                    # 检查是否为空章节（没有任何非空内容）
                    has_any_content = any(
                        l.strip() and not l.strip().startswith('- [[')
                        for l in current_section_content
                    )
                    
                    if has_any_content:
                        # 有内容，保留章节
                        section_key = current_section_buffer[0].strip().lower().replace('#', '').strip()[:30]
                        if section_key not in seen_sections:
                            seen_sections.add(section_key)
                            optimized_lines.extend(current_section_buffer)
                            optimized_lines.extend(current_section_content)
                    else:
                        # 真正空的章节，删除
                        print(f"  删除空章节: {current_section_buffer[0].strip()[:50]}")
                
                current_section_buffer = [line]
                current_section_content = []
                i += 1
                continue
            
            # 收集内容
            if current_section_buffer:
                current_section_content.append(line)
            else:
                optimized_lines.append(line)
            
            i += 1
        
        # 处理最后一个章节
        if current_section_buffer:
            has_any_content = any(
                l.strip() and not l.strip().startswith('- [[')
                for l in current_section_content
            )
            
            if has_any_content:
                optimized_lines.extend(current_section_buffer)
                optimized_lines.extend(current_section_content)
            else:
                print(f"  删除空章节: {current_section_buffer[0].strip()[:50]}")
        
        # 最终清理
        optimized_note = '\n'.join(optimized_lines)
        
        # 删除多余的空行
        while '\n\n\n' in optimized_note:
            optimized_note = optimized_note.replace('\n\n\n', '\n\n')
        
        # 删除文档末尾的空内容
        lines = optimized_note.split('\n')
        while lines and (not lines[-1].strip() or lines[-1].strip().startswith('#') or lines[-1].strip().startswith('- [[')):
            lines.pop()
        
        optimized_note = '\n'.join(lines)
        
        print(f"后处理完成，原始行数: {len(note.split(chr(10)))}, 优化后行数: {len(optimized_note.split(chr(10)))}")
        return optimized_note
    
    def _generate_fallback_note(self, paper: Paper) -> str:
        """生成备用笔记（当LLM失败时使用）"""
        note = f"# {paper.title}\n\n"
        note += "## 论文基本信息\n\n"
        note += f"- **标题**: {paper.title}\n"
        if paper.authors:
            note += f"- **作者**: {', '.join(paper.authors)}\n"
        if paper.abstract:
            note += f"\n## 摘要\n\n{paper.abstract}\n"
        
        note += "\n## 主要内容\n\n"
        for section in paper.sections:
            note += f"\n### {section.title}\n\n"
            note += f"{section.content[:500]}\n"
        
        return note
