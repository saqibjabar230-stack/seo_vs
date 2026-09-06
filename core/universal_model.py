from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FAQ(BaseModel):
    question: str
    answer: str

class Section(BaseModel):
    section_id: str = "" # Unique stable UUID identifier
    heading: str
    content: str # Can contain paragraphs, lists, tables (safe HTML/Markdown)
    required: bool = True
    content_type: str = "paragraph" # paragraph, bullet_list, table, faq, how_to
    ai_instruction: Optional[str] = None
    subsections: List['Section'] = Field(default_factory=list)

class SeoMetadata(BaseModel):
    focus_keyword: str
    meta_description: str
    meta_title: Optional[str] = None

class ContentDocument(BaseModel):
    """
    Universal Content Model
    This represents the purely structured format of an article, completely disconnected from WordPress formatting.
    """
    title: str
    slug: str = ""
    seo_metadata: SeoMetadata
    
    introduction: str
    sections: List[Section]
    conclusion: str
    html_content: Optional[str] = None
    faqs: List[FAQ] = Field(default_factory=list)
    
    # Internal metadata
    images: Dict[str, str] = Field(default_factory=dict) # e.g., {'featured': '/path', 'section_id': '/path'}
    custom_fields: Dict[str, Any] = Field(default_factory=dict) # Catch-all for Appyn data, etc.
    categories: List[str] = Field(default_factory=list)

# --- Template & Section Pydantic Schemas ---

class TemplateSectionSchema(BaseModel):
    id: Optional[str] = None # UUID section_id
    name: str
    order: int = 1
    required: bool = True
    content_type: str = "paragraph"
    ai_instruction: Optional[str] = None

class ContentTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    mode: str = "custom" # "default" or "custom"
    is_default: bool = False
    sections: List[TemplateSectionSchema] = Field(default_factory=list)

class ContentTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    mode: str
    is_default: bool
    version: int
    sections: List[TemplateSectionSchema]

# --- Image Management Schemas ---

class ImageAssignmentCreate(BaseModel):
    image_id: str
    section_id: str # Stable UUID reference
    template_id: Optional[int] = None
    job_id: Optional[str] = None
    draft_id: Optional[int] = None
    position: str = "after_heading" # before_heading, after_heading, before_paragraph, after_paragraph, between_paragraphs, end_of_section
    alignment: str = "center" # left, center, right, full_width
    size: str = "large" # small, medium, large, full_width, custom
    custom_width: Optional[int] = None
    custom_height: Optional[int] = None
    fallback_behavior: str = "do_not_publish" # do_not_publish, nearest_section, end_of_article

class ImageSettingsSchema(BaseModel):
    default_width: int = 800
    alignment: str = "center"
    quality: str = "high"
    fallback_behavior: str = "do_not_publish"

# --- Validation Result Schema ---

class ContentValidationResult(BaseModel):
    is_valid: bool
    checks_passed: int
    total_checks: int = 12
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

# --- Website Profile Schema ---

class WebsiteProfileSchema(BaseModel):
    id: Optional[int] = None
    name: str
    site_url: str
    username: str
    app_password: str
    default_template_id: Optional[int] = None
    editor_type: str = "classic"
    seo_plugin: str = "none"
    default_categories: List[str] = Field(default_factory=list)
    default_tags: List[str] = Field(default_factory=list)
    default_author: Optional[str] = None
