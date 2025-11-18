"""
Standard Notes integration
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import httpx


class StandardNotesClient:
    """Client for Standard Notes API"""

    def __init__(self, server_url: str, email: str, password: str):
        self.server_url = server_url.rstrip('/')
        self.email = email
        self.password = password
        self.session_token = None
        self.access_token = None
        self.refresh_token = None

    async def authenticate(self) -> bool:
        """Authenticate with Standard Notes"""
        try:
            async with httpx.AsyncClient() as client:
                # Get auth parameters
                params_response = await client.get(
                    f"{self.server_url}/v1/auth/params",
                    params={"email": self.email}
                )

                if params_response.status_code != 200:
                    logger.error(f"Failed to get auth params: {params_response.text}")
                    return False

                params = params_response.json()

                # For Standard Notes, we need to generate the password hash
                # This is a simplified version - real implementation would use
                # the proper SN encryption library
                import hashlib
                import base64

                # Generate keys (simplified - use proper SN crypto in production)
                pw_cost = params.get("pw_cost", 110000)
                pw_salt = params.get("pw_salt", "")

                # Create password hash
                pw_hash = hashlib.pbkdf2_hmac(
                    'sha512',
                    self.password.encode(),
                    pw_salt.encode(),
                    pw_cost
                )
                password_hash = base64.b64encode(pw_hash).decode()

                # Sign in
                sign_in_response = await client.post(
                    f"{self.server_url}/v1/auth/sign_in",
                    json={
                        "email": self.email,
                        "password": password_hash,
                        "api": "20200115"
                    }
                )

                if sign_in_response.status_code != 200:
                    logger.error(f"Failed to sign in: {sign_in_response.text}")
                    return False

                auth_data = sign_in_response.json()
                self.session_token = auth_data.get("token")
                self.access_token = auth_data.get("access_token")
                self.refresh_token = auth_data.get("refresh_token")

                logger.info("Successfully authenticated with Standard Notes")
                return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    async def get_notes(self, sync_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Get notes from Standard Notes

        Args:
            sync_token: Optional sync token for incremental sync

        Returns:
            Dictionary with notes and sync_token
        """
        if not self.session_token and not self.access_token:
            if not await self.authenticate():
                return {"notes": [], "sync_token": None}

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token or self.session_token}"
                }

                # Build sync request
                request_data = {
                    "api": "20200115",
                    "cursor_token": sync_token
                } if sync_token else {
                    "api": "20200115"
                }

                response = await client.post(
                    f"{self.server_url}/v1/items/sync",
                    json=request_data,
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Failed to sync notes: {response.text}")
                    return {"notes": [], "sync_token": None}

                data = response.json()

                # Filter for notes only
                all_items = data.get("retrieved_items", [])
                notes = [
                    item for item in all_items
                    if item.get("content_type") == "Note" and not item.get("deleted")
                ]

                logger.info(f"Retrieved {len(notes)} notes from Standard Notes")

                return {
                    "notes": notes,
                    "sync_token": data.get("cursor_token"),
                    "total_items": len(all_items)
                }

        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            return {"notes": [], "sync_token": None}

    async def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags from Standard Notes"""
        if not self.session_token and not self.access_token:
            if not await self.authenticate():
                return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token or self.session_token}"
                }

                response = await client.post(
                    f"{self.server_url}/v1/items/sync",
                    json={"api": "20200115"},
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get tags: {response.text}")
                    return []

                data = response.json()
                all_items = data.get("retrieved_items", [])

                tags = [
                    item for item in all_items
                    if item.get("content_type") == "Tag" and not item.get("deleted")
                ]

                logger.info(f"Retrieved {len(tags)} tags from Standard Notes")
                return tags

        except Exception as e:
            logger.error(f"Failed to get tags: {e}")
            return []

    def parse_note(self, note_item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a Standard Notes item into a normalized format"""
        content = note_item.get("content", {})

        # Handle encrypted content (simplified - use proper SN crypto in production)
        if isinstance(content, str):
            # Content is encrypted or in old format
            title = f"Note {note_item.get('uuid', '')[:8]}"
            text = ""
        else:
            title = content.get("title", "Untitled")
            text = content.get("text", "")

        return {
            "id": note_item.get("uuid"),
            "title": title,
            "content": text,
            "created_at": note_item.get("created_at"),
            "updated_at": note_item.get("updated_at"),
            "content_type": note_item.get("content_type"),
            "tags": [],  # Will be populated separately
            "metadata": {
                "standard_notes_uuid": note_item.get("uuid"),
                "content_type": note_item.get("content_type"),
            }
        }


async def sync_standard_notes(
    server_url: str,
    email: str,
    password: str,
    last_sync_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sync notes from Standard Notes

    Args:
        server_url: Standard Notes server URL
        email: User email
        password: User password
        last_sync_token: Optional token for incremental sync

    Returns:
        Dictionary with synced notes and new sync token
    """
    client = StandardNotesClient(server_url, email, password)

    # Authenticate
    if not await client.authenticate():
        return {
            "success": False,
            "error": "Authentication failed",
            "notes": [],
            "sync_token": None
        }

    # Get notes
    result = await client.get_notes(last_sync_token)

    # Parse notes
    parsed_notes = [
        client.parse_note(note)
        for note in result["notes"]
    ]

    return {
        "success": True,
        "notes": parsed_notes,
        "sync_token": result["sync_token"],
        "count": len(parsed_notes)
    }
