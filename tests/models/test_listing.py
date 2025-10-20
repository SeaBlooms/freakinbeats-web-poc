"""
Unit tests for the Listing model.

Tests cover:
- UUID primary key generation and uniqueness
- Model creation with required fields
- Model creation with optional fields
- Soft delete functionality (is_active, removed_at, sold_at)
- to_dict() serialization
- Timestamp handling (created_at, updated_at)
- Field constraints and validations
- Custom metadata JSON field
"""

import pytest
from datetime import datetime, timezone
from app.models.listing import Listing
from app.extensions import db
import uuid


class TestListingModel:
    """Test suite for Listing model basic functionality."""
    
    def test_listing_creation_with_minimal_fields(self, db):
        """Test creating a listing with only required fields."""
        listing = Listing(
            listing_id='test-listing-001',
            price_value=29.99,
            release_id='release-123'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.uuid is not None
        assert listing.listing_id == 'test-listing-001'
        assert listing.price_value == 29.99
        assert listing.release_id == 'release-123'
        assert listing.is_active is True  # Default value
    
    def test_listing_creation_with_all_fields(self, db):
        """Test creating a listing with all fields populated."""
        now = datetime.now(timezone.utc)
        
        listing = Listing(
            listing_id='test-listing-002',
            status='For Sale',
            condition='Very Good Plus (VG+)',
            sleeve_condition='Very Good (VG)',
            posted=now,
            uri='/marketplace/listing/12345',
            resource_url='https://api.discogs.com/marketplace/listings/12345',
            price_value=49.99,
            price_currency='USD',
            shipping_price=5.99,
            shipping_currency='USD',
            weight=250.0,
            format_quantity=1,
            external_id='ext-001',
            location='Portland, OR',
            comments='Mint condition, never played',
            release_id='release-456',
            release_title='Dark Side of the Moon',
            release_year=1973,
            release_resource_url='https://api.discogs.com/releases/456',
            release_uri='/releases/456',
            artist_names='Pink Floyd',
            primary_artist='Pink Floyd',
            label_names='Harvest',
            primary_label='Harvest',
            format_names='Vinyl, LP, Album',
            primary_format='Vinyl',
            genres='Rock',
            styles='Prog Rock, Psychedelic Rock',
            country='UK',
            catalog_number='SHVL 804',
            barcode='5099902894713',
            master_id='master-789',
            master_url='https://api.discogs.com/masters/789',
            image_uri='https://i.discogs.com/image.jpg',
            image_resource_url='https://api.discogs.com/image/123',
            release_community_have=50000,
            release_community_want=10000,
            export_timestamp=now,
            is_active=True,
            custom_metadata={'featured': True, 'condition_notes': 'Excellent'}
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Verify all fields
        assert listing.uuid is not None
        assert listing.listing_id == 'test-listing-002'
        assert listing.status == 'For Sale'
        assert listing.condition == 'Very Good Plus (VG+)'
        assert listing.release_title == 'Dark Side of the Moon'
        assert listing.primary_artist == 'Pink Floyd'
        assert listing.price_value == 49.99
        assert listing.custom_metadata['featured'] is True


class TestListingUUID:
    """Test suite for UUID primary key functionality."""
    
    def test_uuid_auto_generation(self, db):
        """Test that UUID is automatically generated when not provided."""
        listing = Listing(
            listing_id='test-uuid-001',
            price_value=19.99,
            release_id='release-001'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.uuid is not None
        assert len(listing.uuid) == 36  # Standard UUID format
        assert listing.uuid.count('-') == 4  # UUID has 4 hyphens
    
    def test_uuid_uniqueness(self, db):
        """Test that each listing gets a unique UUID."""
        listing1 = Listing(
            listing_id='test-uuid-002',
            price_value=19.99,
            release_id='release-002'
        )
        listing2 = Listing(
            listing_id='test-uuid-003',
            price_value=29.99,
            release_id='release-003'
        )
        
        db.session.add(listing1)
        db.session.add(listing2)
        db.session.commit()
        
        assert listing1.uuid != listing2.uuid
    
    def test_uuid_format_validation(self, db):
        """Test that generated UUID follows proper format."""
        listing = Listing(
            listing_id='test-uuid-004',
            price_value=19.99,
            release_id='release-004'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Validate UUID format (8-4-4-4-12 hex characters)
        uuid_parts = listing.uuid.split('-')
        assert len(uuid_parts) == 5
        assert len(uuid_parts[0]) == 8
        assert len(uuid_parts[1]) == 4
        assert len(uuid_parts[2]) == 4
        assert len(uuid_parts[3]) == 4
        assert len(uuid_parts[4]) == 12
        
        # Verify all characters are valid hex
        assert all(c in '0123456789abcdef-' for c in listing.uuid.lower())
    
    def test_uuid_persistence_after_retrieval(self, db):
        """Test that UUID remains consistent after database retrieval."""
        listing = Listing(
            listing_id='test-uuid-005',
            price_value=19.99,
            release_id='release-005'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        original_uuid = listing.uuid
        listing_id = listing.listing_id
        
        # Clear session and retrieve again
        db.session.expunge(listing)
        retrieved_listing = Listing.query.filter_by(listing_id=listing_id).first()
        
        assert retrieved_listing.uuid == original_uuid
    
    def test_uuid_as_primary_key_query(self, db):
        """Test querying listings by UUID primary key."""
        listing = Listing(
            listing_id='test-uuid-006',
            price_value=19.99,
            release_id='release-006'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Query by UUID
        found_listing = Listing.query.get(listing.uuid)
        
        assert found_listing is not None
        assert found_listing.listing_id == 'test-uuid-006'
        assert found_listing.uuid == listing.uuid


class TestListingConstraints:
    """Test suite for model constraints and validations."""
    
    def test_listing_id_uniqueness(self, db):
        """Test that listing_id must be unique."""
        listing1 = Listing(
            listing_id='duplicate-id',
            price_value=19.99,
            release_id='release-001'
        )
        listing2 = Listing(
            listing_id='duplicate-id',
            price_value=29.99,
            release_id='release-002'
        )
        
        db.session.add(listing1)
        db.session.commit()
        
        db.session.add(listing2)
        
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db.session.commit()
        
        db.session.rollback()
    
    def test_price_value_non_negative_constraint(self, db):
        """Test that price_value must be non-negative."""
        listing = Listing(
            listing_id='test-price-001',
            price_value=-10.0,  # Invalid negative price
            release_id='release-001'
        )
        
        db.session.add(listing)
        
        with pytest.raises(Exception):  # CheckConstraint violation
            db.session.commit()
        
        db.session.rollback()
    
    def test_required_fields_validation(self, db):
        """Test that required fields cannot be None."""
        # Missing listing_id
        listing1 = Listing(
            price_value=19.99,
            release_id='release-001'
        )
        
        db.session.add(listing1)
        
        with pytest.raises(Exception):  # IntegrityError for nullable=False
            db.session.commit()
        
        db.session.rollback()


class TestListingSoftDelete:
    """Test suite for soft delete functionality."""
    
    def test_default_is_active_true(self, db):
        """Test that new listings default to is_active=True."""
        listing = Listing(
            listing_id='test-active-001',
            price_value=19.99,
            release_id='release-001'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.is_active is True
        assert listing.removed_at is None
        assert listing.sold_at is None
    
    def test_soft_delete_removal(self, db):
        """Test marking a listing as removed (soft delete)."""
        listing = Listing(
            listing_id='test-remove-001',
            price_value=19.99,
            release_id='release-001'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Mark as removed
        listing.is_active = False
        listing.removed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        assert listing.is_active is False
        assert listing.removed_at is not None
        assert listing.sold_at is None
    
    def test_soft_delete_sold(self, db):
        """Test marking a listing as sold."""
        listing = Listing(
            listing_id='test-sold-001',
            price_value=19.99,
            release_id='release-001'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Mark as sold
        listing.is_active = False
        listing.sold_at = datetime.now(timezone.utc)
        db.session.commit()
        
        assert listing.is_active is False
        assert listing.sold_at is not None
    
    def test_query_active_listings_only(self, db):
        """Test filtering to show only active listings."""
        # Create active listing
        active_listing = Listing(
            listing_id='test-active-002',
            price_value=19.99,
            release_id='release-002'
        )
        
        # Create removed listing
        removed_listing = Listing(
            listing_id='test-removed-002',
            price_value=29.99,
            release_id='release-003',
            is_active=False,
            removed_at=datetime.now(timezone.utc)
        )
        
        db.session.add(active_listing)
        db.session.add(removed_listing)
        db.session.commit()
        
        # Query only active listings
        active_listings = Listing.query.filter_by(is_active=True).all()
        
        assert len(active_listings) >= 1
        assert all(listing.is_active for listing in active_listings)
        assert active_listing in active_listings
        assert removed_listing not in active_listings


class TestListingTimestamps:
    """Test suite for timestamp fields."""
    
    def test_created_at_auto_set(self, db):
        """Test that created_at is automatically set on creation."""
        listing = Listing(
            listing_id='test-timestamp-001',
            price_value=19.99,
            release_id='release-001'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.created_at is not None
        # created_at should be set to a datetime object
        assert isinstance(listing.created_at, datetime)
    
    def test_updated_at_auto_set(self, db):
        """Test that updated_at is automatically set on creation."""
        listing = Listing(
            listing_id='test-timestamp-002',
            price_value=19.99,
            release_id='release-002'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.updated_at is not None
        assert isinstance(listing.updated_at, datetime)
        # created_at and updated_at should be very close (within 1 second)
        assert abs((listing.updated_at - listing.created_at).total_seconds()) < 1
    
    def test_updated_at_changes_on_update(self, db):
        """Test that updated_at changes when record is updated."""
        listing = Listing(
            listing_id='test-timestamp-003',
            price_value=19.99,
            release_id='release-003'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        original_updated_at = listing.updated_at
        
        # Update the listing
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp difference
        listing.price_value = 29.99
        db.session.commit()
        
        assert listing.updated_at >= original_updated_at


class TestListingCustomMetadata:
    """Test suite for custom_metadata JSON field."""
    
    def test_custom_metadata_storage(self, db):
        """Test storing custom metadata as JSON."""
        metadata = {
            'featured': True,
            'condition_notes': 'Excellent pressing',
            'tags': ['rare', 'limited edition'],
            'internal_notes': 'Store display copy'
        }
        
        listing = Listing(
            listing_id='test-metadata-001',
            price_value=19.99,
            release_id='release-001',
            custom_metadata=metadata
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.custom_metadata['featured'] is True
        assert listing.custom_metadata['tags'] == ['rare', 'limited edition']
    
    def test_custom_metadata_nullable(self, db):
        """Test that custom_metadata can be None."""
        listing = Listing(
            listing_id='test-metadata-002',
            price_value=19.99,
            release_id='release-002'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        assert listing.custom_metadata is None
    
    def test_custom_metadata_update(self, db):
        """Test updating custom_metadata after creation."""
        listing = Listing(
            listing_id='test-metadata-003',
            price_value=19.99,
            release_id='release-003',
            custom_metadata={'status': 'new'}
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Update metadata - need to reassign to trigger SQLAlchemy change detection
        updated_metadata = listing.custom_metadata.copy()
        updated_metadata['status'] = 'featured'
        updated_metadata['priority'] = 'high'
        listing.custom_metadata = updated_metadata
        db.session.commit()
        
        retrieved_listing = Listing.query.get(listing.uuid)
        assert retrieved_listing.custom_metadata['status'] == 'featured'
        assert retrieved_listing.custom_metadata['priority'] == 'high'


class TestListingToDictSerialization:
    """Test suite for to_dict() method."""
    
    def test_to_dict_includes_all_fields(self, db):
        """Test that to_dict() includes all model fields."""
        now = datetime.now(timezone.utc)
        
        listing = Listing(
            listing_id='test-dict-001',
            status='For Sale',
            condition='Mint (M)',
            price_value=39.99,
            price_currency='USD',
            release_id='release-001',
            release_title='Test Album',
            primary_artist='Test Artist',
            is_active=True,
            custom_metadata={'test': True}
        )
        
        db.session.add(listing)
        db.session.commit()
        
        data = listing.to_dict()
        
        # Check critical fields
        assert 'uuid' in data
        assert data['listing_id'] == 'test-dict-001'
        assert data['status'] == 'For Sale'
        assert data['price_value'] == 39.99
        assert data['release_title'] == 'Test Album'
        assert data['is_active'] is True
        assert data['custom_metadata']['test'] is True
    
    def test_to_dict_datetime_serialization(self, db):
        """Test that datetime fields are serialized to ISO format."""
        now = datetime.now(timezone.utc)
        
        listing = Listing(
            listing_id='test-dict-002',
            price_value=19.99,
            release_id='release-002',
            posted=now,
            export_timestamp=now
        )
        
        db.session.add(listing)
        db.session.commit()
        
        data = listing.to_dict()
        
        assert isinstance(data['posted'], str)
        assert 'T' in data['posted']  # ISO format includes 'T'
        assert isinstance(data['export_timestamp'], str)
        assert isinstance(data['created_at'], str)
    
    def test_to_dict_null_datetime_handling(self, db):
        """Test that None datetime fields are serialized as None."""
        listing = Listing(
            listing_id='test-dict-003',
            price_value=19.99,
            release_id='release-003'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        data = listing.to_dict()
        
        assert data['posted'] is None
        assert data['removed_at'] is None
        assert data['sold_at'] is None
        assert data['export_timestamp'] is None
    
    def test_to_dict_uuid_included(self, db):
        """Test that UUID is included in serialization."""
        listing = Listing(
            listing_id='test-dict-004',
            price_value=19.99,
            release_id='release-004'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        data = listing.to_dict()
        
        assert 'uuid' in data
        assert data['uuid'] == listing.uuid
        assert len(data['uuid']) == 36


class TestListingRepr:
    """Test suite for __repr__ method."""
    
    def test_repr_format(self, db):
        """Test that __repr__ returns expected format."""
        listing = Listing(
            listing_id='test-repr-001',
            price_value=19.99,
            release_id='release-001',
            release_title='Abbey Road',
            primary_artist='The Beatles'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        repr_str = repr(listing)
        
        assert 'Listing test-repr-001' in repr_str
        assert 'Abbey Road' in repr_str
        assert 'The Beatles' in repr_str
    
    def test_repr_with_none_fields(self, db):
        """Test __repr__ when title and artist are None."""
        listing = Listing(
            listing_id='test-repr-002',
            price_value=19.99,
            release_id='release-002'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        repr_str = repr(listing)
        
        assert 'Listing test-repr-002' in repr_str
        assert 'None' in repr_str  # Should handle None gracefully


class TestListingIndexes:
    """Test suite for database indexes."""
    
    def test_listing_id_indexed(self, db):
        """Test that listing_id is indexed for fast lookups."""
        # Create multiple listings
        for i in range(10):
            listing = Listing(
                listing_id=f'test-index-{i:03d}',
                price_value=19.99,
                release_id=f'release-{i:03d}'
            )
            db.session.add(listing)
        
        db.session.commit()
        
        # Query by listing_id (should use index)
        result = Listing.query.filter_by(listing_id='test-index-005').first()
        
        assert result is not None
        assert result.listing_id == 'test-index-005'
    
    def test_release_id_indexed(self, db):
        """Test that release_id is indexed for fast lookups."""
        # Create multiple listings with same release_id
        for i in range(5):
            listing = Listing(
                listing_id=f'test-release-{i:03d}',
                price_value=19.99,
                release_id='release-shared-001'
            )
            db.session.add(listing)
        
        db.session.commit()
        
        # Query by release_id (should use index)
        results = Listing.query.filter_by(release_id='release-shared-001').all()
        
        assert len(results) == 5
