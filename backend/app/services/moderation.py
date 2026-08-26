"""
Content Moderation Service.
"""
from typing import List, Dict, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_
import re
import logging

from ..models.moderation import Lexicon, LexiconCategory, LexiconSeverity
from ..models.work import Work

logger = logging.getLogger(__name__)


class ModerationService:
    """Content moderation service."""
    
    def __init__(self, db: Session):
        self.db = db
        self._lexicon_cache: Optional[Dict[str, List[Dict]]] = None
        self._cache_enabled = True
    
    def _load_lexicon(self) -> Dict[str, List[Dict]]:
        """Load keyword library (cached)"""
        if self._lexicon_cache is not None and self._cache_enabled:
            return self._lexicon_cache
        
        lexicons = self.db.query(Lexicon).filter(
            Lexicon.enabled == True
        ).all()
        
        lexicon_dict: Dict[str, List[Dict]] = {
            LexiconCategory.VIOLENCE.value: [],
            LexiconCategory.PORNOGRAPHY.value: [],
            LexiconCategory.ILLEGAL.value: [],
            LexiconCategory.OTHER.value: [],
        }
        
        for lex in lexicons:
            lexicon_dict[lex.category.value].append({
                'word': lex.word.lower(),  # Convert to lowercase
                'severity': lex.severity.value,
                'id': lex.id,
            })
        
        if self._cache_enabled:
            self._lexicon_cache = lexicon_dict
        
        logger.info(f"Loaded {len(lexicons)} lexicon entries")
        return lexicon_dict
    
    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        return text.lower().strip()
    
    def _check_text_for_keywords(
        self, 
        text: str, 
        lexicon_dict: Dict[str, List[Dict]]
    ) -> Dict[str, any]:
        """
        Check keywords in text
        
        Returns:
        {
            'found_tags': ['violence', 'pornography'],  # Detected tags
            'flagged_keywords': [{'word': 'xxx', 'category': 'violence', 'severity': 'high'}],  # Flagged keywords
            'has_violation': True/False
        }
        """
        if not text:
            return {
                'found_tags': [],
                'flagged_keywords': [],
                'has_violation': False
            }
        
        normalized_text = self._normalize_text(text)
        found_tags: Set[str] = set()
        flagged_keywords: List[Dict] = []
        
        #
        for category, words_list in lexicon_dict.items():
            for word_entry in words_list:
                word = word_entry['word']
                severity = word_entry['severity']
                
                # "ass" "class")
                pattern = r'\b' + re.escape(word) + r'\b'
                if re.search(pattern, normalized_text, re.IGNORECASE):
                    found_tags.add(category)
                    flagged_keywords.append({
                        'word': word,
                        'category': category,
                        'severity': severity,
                        'lexicon_id': word_entry['id']
                    })
        
        return {
            'found_tags': list(found_tags),
            'flagged_keywords': flagged_keywords,
            'has_violation': len(found_tags) > 0
        }
    
    def check_nsfw(
        self, 
        prompt: str, 
        negative_prompt: Optional[str] = None,
        work_id: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Check if content contains NSFW keywords
        
        Args:
            prompt: Main prompt
            negative_prompt: Negative prompt (optional)
            work_id: Work ID (optional, for logging)
        
        Returns:
            {
                'is_violation': bool,  # Is violation
                'nsfw_tags': List[str],  # Detected tags ['violence', 'pornography', 'illegal']
                'flagged_keywords': List[Dict],  # Flagged keywords
                'confidence': str,  # 'high', 'medium', 'low'
            }
        """
        try:
            #
            lexicon_dict = self._load_lexicon()
            
            # prompt
            prompt_result = self._check_text_for_keywords(prompt, lexicon_dict)
            
            # negative_prompt()
            negative_result = {
                'found_tags': [],
                'flagged_keywords': [],
                'has_violation': False
            }
            if negative_prompt:
                negative_result = self._check_text_for_keywords(negative_prompt, lexicon_dict)
            
            #
            all_tags = set(prompt_result['found_tags'] + negative_result['found_tags'])
            all_keywords = prompt_result['flagged_keywords'] + negative_result['flagged_keywords']
            
            has_high_severity = any(kw.get('severity') == LexiconSeverity.HIGH.value for kw in all_keywords)
            has_medium_severity = any(kw.get('severity') == LexiconSeverity.MEDIUM.value for kw in all_keywords)
            
            if has_high_severity:
                confidence = 'high'
            elif has_medium_severity:
                confidence = 'medium'
            elif all_keywords:
                confidence = 'low'
            else:
                confidence = 'none'
            
            result = {
                'is_violation': len(all_tags) > 0,
                'nsfw_tags': list(all_tags),
                'flagged_keywords': all_keywords,
                'confidence': confidence,
            }
            
            if work_id:
                logger.info(f"NSFW check for work {work_id}: violation={result['is_violation']}, tags={result['nsfw_tags']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in NSFW check: {str(e)}", exc_info=True)
            return {
                'is_violation': False,
                'nsfw_tags': [],
                'flagged_keywords': [],
                'confidence': 'none',
                'error': str(e)
            }
    
    def invalidate_cache(self):
        """Clear cache (called when keyword library is updated)"""
        self._lexicon_cache = None
        logger.info("Lexicon cache invalidated")


def get_moderation_service(db: Session) -> ModerationService:
    return ModerationService(db)
