from typing import Optional, Tuple
from utils.logger import get_logger
from agents.discovery_agent import Candidate
from agents.history_agent import check_candidate
from agents.research_agent import ResearchAgent
from agents.content_agent import ContentAgent, check_differentiation
from agents.fact_verification_agent import verify_claims, get_trusted_facts
from agents.image_agent import ImageAgent
from agents.compliance_agent import check_market_allowlist
from agents.wordpress_agent import WordPressPublisher
from core.universal_model import ContentDocument

logger = get_logger("content_pipeline")

def run_single_candidate(candidate: Candidate, target_market: str, user_id: int = 1, user_settings: dict = None, db_path: str = None, dry_run: bool = False) -> Tuple[Optional[ContentDocument], str]:
    """
    Runs a single candidate through the strict Phase 8 pipeline sequence.
    Returns a tuple of (draft, status_reason).
    """
    user_settings = user_settings or {}
    logger.info(f"Starting pipeline for {candidate.provider} - {candidate.game_name} (Market: {target_market}) [Dry Run: {dry_run}]")
    kwargs = {'db_path': db_path} if db_path else {}
    
    # 1. History Gate (Phase 2)
    if not check_candidate(candidate.game_name, candidate.provider, user_id, **kwargs):
        logger.info(f"Pipeline stopped: {candidate.game_name} blocked by History Gate.")
        return None, "BLOCKED_HISTORY"
        
    # 2. Research (Phase 4)
    research_agent = ResearchAgent()
    context = research_agent.gather_context(candidate)
    
    # 3. Content Drafting (Phase 4) & Differentiation (Phase 5)
    trusted_facts = get_trusted_facts(candidate.game_name, candidate.provider, user_id, **kwargs)
    if not trusted_facts:
        logger.warning(f"No trusted facts found for {candidate.game_name}. AI will invent suitable facts.")
        trusted_facts = {}
        
    content_agent = ContentAgent()
    draft = content_agent.draft_article(candidate, context, trusted_facts)
    
    if not check_differentiation(draft):
        logger.error("Pipeline stopped: Draft failed editorial differentiation check.")
        return None, "FAILED_DIFFERENTIATION"
        
    # 4. Fact Verification (Phase 3)
    proposed_claims = {k: v for k, v in trusted_facts.items() if v is not None}
    status, diff = verify_claims(candidate.game_name, candidate.provider, proposed_claims, user_id, **kwargs)
    if status != 'MATCH':
        logger.error(f"Pipeline stopped: Fact verification failed with status {status}.")
        return None, f"FAILED_FACT_VERIFICATION_{status}"
        
    # 5. Image Processing Gate (Phase 6)
    image_agent = ImageAgent()
    local_images = image_agent.process_images(candidate)
    
    # 6. Compliance Gate (Phase 7)
    if not check_market_allowlist(target_market):
        logger.info(f"Pipeline stopped: Market '{target_market}' blocked by Compliance Gate.")
        return None, "BLOCKED_COMPLIANCE"
        
    # Attach local images to draft document
    draft.images = local_images
    
    # In the Universal Workflow, we STOP here and return the Draft for user review.
    # The actual publishing happens in a separate manual step via the Dashboard.
    logger.info(f"Pipeline completed successfully for {candidate.game_name}. Returning Draft for Review.")
    return draft, "SUCCESS"
