"""
Partner and API Key Management for the API Gateway.

This module handles:
- Partner registration and management
- API key generation and validation
- Service access control per partner
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import secrets
import time


class Service(str, Enum):
    """Available backend services."""
    USERS = "users"
    POSTS = "posts"
    COMMENTS = "comments"
    TODOS = "todos"
    ALBUMS = "albums"
    PHOTOS = "photos"


@dataclass
class Partner:
    """Represents an external partner with API access."""
    id: str
    name: str
    api_key: str
    allowed_services: set[Service]
    rate_limit: int  # requests per minute
    is_active: bool = True
    created_at: float = field(default_factory=time.time)
    
    def can_access(self, service: Service) -> bool:
        """Check if partner can access a specific service."""
        return self.is_active and service in self.allowed_services


class PartnerStore:
    """
    In-memory store for partner management.
    In production, this would be backed by a database.
    """
    
    def __init__(self):
        self._partners: dict[str, Partner] = {}
        self._api_key_index: dict[str, str] = {}  # api_key -> partner_id
        self._initialize_demo_partners()
    
    def _initialize_demo_partners(self):
        """Create demo partners for testing."""
        # Partner 1: Full access partner (premium tier)
        self.create_partner(
            partner_id="partner-001",
            name="Premium Partner Inc.",
            allowed_services={Service.USERS, Service.POSTS, Service.COMMENTS, 
                           Service.TODOS, Service.ALBUMS, Service.PHOTOS},
            rate_limit=100,
            api_key="premium-key-001"
        )
        
        # Partner 2: Limited access partner (basic tier)
        self.create_partner(
            partner_id="partner-002",
            name="Basic Partner Ltd.",
            allowed_services={Service.USERS, Service.POSTS},
            rate_limit=30,
            api_key="basic-key-002"
        )
        
        # Partner 3: Read-only social data partner
        self.create_partner(
            partner_id="partner-003",
            name="Social Analytics Co.",
            allowed_services={Service.POSTS, Service.COMMENTS},
            rate_limit=50,
            api_key="social-key-003"
        )
    
    def create_partner(
        self,
        partner_id: str,
        name: str,
        allowed_services: set[Service],
        rate_limit: int = 60,
        api_key: Optional[str] = None
    ) -> Partner:
        """Create a new partner with an API key."""
        if api_key is None:
            api_key = f"key-{secrets.token_hex(16)}"
        
        partner = Partner(
            id=partner_id,
            name=name,
            api_key=api_key,
            allowed_services=allowed_services,
            rate_limit=rate_limit
        )
        
        self._partners[partner_id] = partner
        self._api_key_index[api_key] = partner_id
        return partner
    
    def get_by_api_key(self, api_key: str) -> Optional[Partner]:
        """Look up a partner by their API key."""
        partner_id = self._api_key_index.get(api_key)
        if partner_id:
            return self._partners.get(partner_id)
        return None
    
    def get_by_id(self, partner_id: str) -> Optional[Partner]:
        """Look up a partner by their ID."""
        return self._partners.get(partner_id)
    
    def list_partners(self) -> list[Partner]:
        """List all registered partners."""
        return list(self._partners.values())
    
    def deactivate_partner(self, partner_id: str) -> bool:
        """Deactivate a partner's access."""
        partner = self._partners.get(partner_id)
        if partner:
            partner.is_active = False
            return True
        return False


# Global partner store instance
partner_store = PartnerStore()
