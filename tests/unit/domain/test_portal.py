"""
Unit Tests for Portal Domain Model
==================================
"""

import unittest
from domain.models.portal import Portal, PortalStatus, PortalType


class TestPortalDomain(unittest.TestCase):
    """Test Portal domain model"""

    def setUp(self):
        self.valid_portal = Portal(
            id="test",
            name="Test Portal",
            port=8080,
            type=PortalType.SETUP,
            status=PortalStatus.STOPPED,
            description="Test portal",
            module_path="test.module"
        )

    def test_portal_creation(self):
        """Test portal can be created with valid data"""
        self.assertEqual(self.valid_portal.id, "test")
        self.assertEqual(self.valid_portal.port, 8080)
        self.assertEqual(self.valid_portal.type, PortalType.SETUP)

    def test_portal_is_active(self):
        """Test is_active method"""
        self.assertFalse(self.valid_portal.is_active())

        self.valid_portal.status = PortalStatus.RUNNING
        self.assertTrue(self.valid_portal.is_active())

    def test_portal_can_start(self):
        """Test can_start method"""
        # Can start when stopped
        self.valid_portal.status = PortalStatus.STOPPED
        self.assertTrue(self.valid_portal.can_start())

        # Can start when in error
        self.valid_portal.status = PortalStatus.ERROR
        self.assertTrue(self.valid_portal.can_start())

        # Cannot start when running
        self.valid_portal.status = PortalStatus.RUNNING
        self.assertFalse(self.valid_portal.can_start())

    def test_portal_validation(self):
        """Test portal validation"""
        # Valid portal
        self.assertTrue(self.valid_portal.validate())

        # Invalid: no name
        invalid_portal = Portal(
            id="test",
            name="",
            port=8080,
            type=PortalType.SETUP,
            status=PortalStatus.STOPPED,
            description="Test",
            module_path="test.module"
        )
        self.assertFalse(invalid_portal.validate())

        # Invalid: port too low
        invalid_portal.name = "Test"
        invalid_portal.port = 80
        self.assertFalse(invalid_portal.validate())

        # Invalid: port too high
        invalid_portal.port = 70000
        self.assertFalse(invalid_portal.validate())


if __name__ == "__main__":
    unittest.main()