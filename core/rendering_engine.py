from typing import List, Dict, Any, Optional
from core.universal_model import ContentDocument, Section

class RenderingEngine:
    @staticmethod
    def render_classic_html(doc: ContentDocument, image_assignments: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Renders ContentDocument into standard, semantic WordPress HTML.
        Supports section_id-based image assignments and strict fallback rules.
        """
        if doc.html_content is not None:
            return doc.html_content

        html = []
        assignments = image_assignments or []
        
        # Maps section_id or heading to assigned images
        assigned_by_sec: Dict[str, List[Dict[str, Any]]] = {}
        for assign in assignments:
            s_id = assign.get("section_id", "")
            if s_id:
                assigned_by_sec.setdefault(s_id, []).append(assign)
                
        rendered_sec_ids = set()

        def format_img_tag(assign: Dict[str, Any]) -> str:
            src = assign.get("url") or assign.get("file_path", "")
            align = assign.get("alignment", "center")
            size = assign.get("size", "large")
            w = assign.get("custom_width") or assign.get("width")
            h = assign.get("custom_height") or assign.get("height")
            
            style_str = ""
            if w: style_str += f' width="{w}"'
            if h: style_str += f' height="{h}"'

            align_class = f"align{align}" if align != "full_width" else "aligncenter size-full"
            return f'<p style="text-align:{align};"><img src="{src}" alt="Article Image" class="{align_class} size-{size} wp-image"{style_str} /></p>'

        # Featured image
        if 'featured' in doc.images and doc.images['featured']:
            html.append(f'<p style="text-align:center;"><img src="{doc.images["featured"]}" alt="{doc.title} Featured" class="aligncenter size-full wp-image" /></p>')
            
        if doc.introduction:
            html.append(f"<p>{doc.introduction}</p>")
            
        # Section renderer
        def render_section(section: Section, level: int = 2):
            sec_html = []
            sec_id = section.section_id
            if sec_id: rendered_sec_ids.add(sec_id)

            sec_assigns = []
            if sec_id in assigned_by_sec:
                sec_assigns = assigned_by_sec[sec_id]
            else:
                # Fallback check by heading name
                for assign in assignments:
                    if assign.get("section_name", "").lower().strip() == section.heading.lower().strip():
                        sec_assigns.append(assign)
                        if sec_id: rendered_sec_ids.add(sec_id)

            before_heading_imgs = [format_img_tag(a) for a in sec_assigns if a.get("position") == "before_heading"]
            after_heading_imgs = [format_img_tag(a) for a in sec_assigns if a.get("position") == "after_heading"]
            after_para_imgs = [format_img_tag(a) for a in sec_assigns if a.get("position") in ["after_paragraph", "between_paragraphs", "end_of_section", None]]

            sec_html.extend(before_heading_imgs)
            sec_html.append(f"<h{level}>{section.heading}</h{level}>")
            sec_html.extend(after_heading_imgs)

            if section.content:
                content = section.content.strip()
                if not content.startswith('<p>') and not content.startswith('<ul>') and not content.startswith('<ol>'):
                    p_break = '</p><p>'
                    content = f"<p>{content.replace(chr(10) + chr(10), p_break)}</p>"
                sec_html.append(content)

            sec_html.extend(after_para_imgs)

            for sub in section.subsections:
                sec_html.append(render_section(sub, level=min(level + 1, 6)))

            return "\n".join(sec_html)

        for section in doc.sections:
            html.append(render_section(section))

        # Check unrendered / missing section assignments
        for assign in assignments:
            s_id = assign.get("section_id", "")
            fallback = assign.get("fallback_behavior", "do_not_publish")
            if s_id and s_id not in rendered_sec_ids:
                if fallback == "end_of_article":
                    html.append(format_img_tag(assign))
                # Note: if fallback == "do_not_publish", image is NOT rendered! (Orphaned image safeguard)

        if doc.faqs:
            html.append("<h2>FAQs</h2>")
            for faq in doc.faqs:
                html.append(f"<h3>{faq.question}</h3>\n<p>{faq.answer}</p>")

        if doc.conclusion:
            html.append("<h2>Conclusion</h2>")
            content = doc.conclusion.strip()
            if not content.startswith('<p>'):
                p_break = '</p><p>'
                content = f"<p>{content.replace(chr(10) + chr(10), p_break)}</p>"
            html.append(content)

        html.append('<hr/>\n<p><strong>Responsible Gambling Notice:</strong> Please gamble responsibly. Only bet what you can afford to lose. If you need help, seek professional advice.</p>')

        return "\n\n".join(html)
