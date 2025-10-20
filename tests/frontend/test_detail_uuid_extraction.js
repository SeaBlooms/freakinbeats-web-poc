/**
 * Unit tests for VinylDetail.getUuidFromUrl()
 * 
 * Tests UUID extraction from various URL patterns to ensure
 * robust parsing of detail page routes.
 * 
 * Run with: npm test (after setting up Jest)
 * Or: jest tests/frontend/test_detail_uuid_extraction.js
 */

describe('VinylDetail.getUuidFromUrl()', () => {
    let vinylDetail;
    let originalLocation;

    beforeEach(() => {
        // Save original location
        originalLocation = window.location;
        
        // Mock window.location with configurable pathname
        delete window.location;
        window.location = { pathname: '' };
    });

    afterEach(() => {
        // Restore original location
        window.location = originalLocation;
    });

    test('extracts UUID from standard detail URL', () => {
        window.location.pathname = '/detail/550e8400-e29b-41d4-a716-446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-e29b-41d4-a716-446655440000');
    });

    test('extracts UUID with lowercase hex characters', () => {
        window.location.pathname = '/detail/abcdef01-2345-6789-abcd-ef0123456789';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('abcdef01-2345-6789-abcd-ef0123456789');
    });

    test('extracts UUID from URL with trailing slash', () => {
        window.location.pathname = '/detail/550e8400-e29b-41d4-a716-446655440000/';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-e29b-41d4-a716-446655440000');
    });

    test('extracts UUID from URL with query parameters', () => {
        window.location.pathname = '/detail/550e8400-e29b-41d4-a716-446655440000';
        window.location.search = '?ref=email&campaign=promo';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-e29b-41d4-a716-446655440000');
    });

    test('extracts UUID from nested path structure', () => {
        window.location.pathname = '/shop/vinyl/detail/550e8400-e29b-41d4-a716-446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-e29b-41d4-a716-446655440000');
    });

    test('returns null for URL without UUID', () => {
        window.location.pathname = '/detail/';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('returns null for home page', () => {
        window.location.pathname = '/';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('returns null for invalid UUID format (too short)', () => {
        window.location.pathname = '/detail/550e8400';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('returns null for invalid UUID format (wrong separators)', () => {
        window.location.pathname = '/detail/550e8400_e29b_41d4_a716_446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('returns null for URL with integer ID (legacy format)', () => {
        window.location.pathname = '/detail/12345';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('returns null for malformed URL path', () => {
        window.location.pathname = '/details/550e8400-e29b-41d4-a716-446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('handles UUID with uppercase hex characters', () => {
        window.location.pathname = '/detail/550E8400-E29B-41D4-A716-446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550E8400-E29B-41D4-A716-446655440000');
    });

    test('handles UUID with mixed case hex characters', () => {
        window.location.pathname = '/detail/550e8400-E29b-41D4-a716-446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-E29b-41D4-a716-446655440000');
    });

    test('returns null for URL with UUID-like string but invalid characters', () => {
        window.location.pathname = '/detail/550g8400-e29b-41d4-a716-446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('returns null for empty pathname', () => {
        window.location.pathname = '';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('extracts first UUID when multiple UUIDs in path', () => {
        window.location.pathname = '/detail/550e8400-e29b-41d4-a716-446655440000/related/abcdef01-2345-6789-abcd-ef0123456789';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-e29b-41d4-a716-446655440000');
    });

    test('handles URL with hash fragment', () => {
        window.location.pathname = '/detail/550e8400-e29b-41d4-a716-446655440000';
        window.location.hash = '#reviews';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('550e8400-e29b-41d4-a716-446655440000');
    });

    test('returns null for URL with spaces in path', () => {
        window.location.pathname = '/detail/550e8400 e29b 41d4 a716 446655440000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBeNull();
    });

    test('handles RFC 4122 NIL UUID (all zeros)', () => {
        window.location.pathname = '/detail/00000000-0000-0000-0000-000000000000';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('00000000-0000-0000-0000-000000000000');
    });

    test('handles RFC 4122 MAX UUID (all Fs)', () => {
        window.location.pathname = '/detail/ffffffff-ffff-ffff-ffff-ffffffffffff';
        vinylDetail = new VinylDetail();
        
        expect(vinylDetail.uuid).toBe('ffffffff-ffff-ffff-ffff-ffffffffffff');
    });
});
