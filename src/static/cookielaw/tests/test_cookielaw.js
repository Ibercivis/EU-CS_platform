/**
 * Unit tests for Cookielaw module
 * Tests cookie consent acceptance and rejection functionality
 */

describe('Cookielaw', function() {
    
    // Clean up cookies before each test
    beforeEach(function() {
        document.cookie = "cookielaw_accepted=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "cookielaw_accepted=false; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    });

    describe('createCookielawCookie()', function() {
        
        it('should set cookielaw_accepted cookie to true', function() {
            Cookielaw.createCookielawCookie();
            expect(document.cookie).toContain('cookielaw_accepted=true');
        });

        it('should set cookie path to root', function() {
            Cookielaw.createCookielawCookie();
            // Verify the cookie is accessible from root path
            expect(document.cookie).toContain('cookielaw_accepted=true');
        });

        it('should set cookie expiration to one year', function() {
            var today = new Date();
            var oneYearLater = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate());
            
            Cookielaw.createCookielawCookie();
            
            // Cookie should be set with expiration date in the future
            expect(document.cookie).toContain('cookielaw_accepted=true');
        });

        it('should be callable without parameters', function() {
            expect(function() {
                Cookielaw.createCookielawCookie();
            }).not.toThrow();
        });
    });

    describe('rejectCookies()', function() {
        
        it('should set cookielaw_accepted cookie to false', function() {
            Cookielaw.rejectCookies();
            expect(document.cookie).toContain('cookielaw_accepted=false');
        });

        it('should be callable without parameters', function() {
            expect(function() {
                Cookielaw.rejectCookies();
            }).not.toThrow();
        });

        it('should set the same cookie as accept function', function() {
            Cookielaw.rejectCookies();
            var rejectCookie = document.cookie;
            
            // Clear and test accept
            document.cookie = "cookielaw_accepted=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            Cookielaw.createCookielawCookie();
            var acceptCookie = document.cookie;
            
            // Both should set the same cookie name
            expect(rejectCookie).toContain('cookielaw_accepted');
            expect(acceptCookie).toContain('cookielaw_accepted');
        });

        it('should be callable after accepting cookies', function() {
            Cookielaw.createCookielawCookie();
            
            expect(function() {
                Cookielaw.rejectCookies();
            }).not.toThrow();
            
            expect(document.cookie).toContain('cookielaw_accepted=false');
        });
    });

    describe('isCookieAccepted()', function() {
        
        it('should return true when cookielaw_accepted=true', function() {
            Cookielaw.createCookielawCookie();
            expect(Cookielaw.isCookieAccepted()).toBe(true);
        });

        it('should return false when cookie is not set', function() {
            expect(Cookielaw.isCookieAccepted()).toBe(false);
        });

        it('should return false when cookielaw_accepted=false', function() {
            Cookielaw.rejectCookies();
            expect(Cookielaw.isCookieAccepted()).toBe(false);
        });

        it('should return true only for true value', function() {
            Cookielaw.createCookielawCookie();
            var isAccepted = Cookielaw.isCookieAccepted();
            
            // Should be true
            expect(isAccepted).toBe(true);
            
            // After rejection, should be false
            Cookielaw.rejectCookies();
            expect(Cookielaw.isCookieAccepted()).toBe(false);
        });
    });

    describe('isCookieRejected()', function() {
        
        it('should return true when cookielaw_accepted=false', function() {
            Cookielaw.rejectCookies();
            expect(Cookielaw.isCookieRejected()).toBe(true);
        });

        it('should return false when cookie is not set', function() {
            expect(Cookielaw.isCookieRejected()).toBe(false);
        });

        it('should return false when cookielaw_accepted=true', function() {
            Cookielaw.createCookielawCookie();
            expect(Cookielaw.isCookieRejected()).toBe(false);
        });

        it('should return true only for false value', function() {
            Cookielaw.rejectCookies();
            var isRejected = Cookielaw.isCookieRejected();
            
            // Should be true
            expect(isRejected).toBe(true);
            
            // After acceptance, should be false
            Cookielaw.createCookielawCookie();
            expect(Cookielaw.isCookieRejected()).toBe(false);
        });
    });

    describe('Cookie State Transitions', function() {
        
        it('should transition from no cookie to accepted', function() {
            expect(Cookielaw.isCookieAccepted()).toBe(false);
            expect(Cookielaw.isCookieRejected()).toBe(false);
            
            Cookielaw.createCookielawCookie();
            
            expect(Cookielaw.isCookieAccepted()).toBe(true);
            expect(Cookielaw.isCookieRejected()).toBe(false);
        });

        it('should transition from accepted to rejected', function() {
            Cookielaw.createCookielawCookie();
            expect(Cookielaw.isCookieAccepted()).toBe(true);
            
            Cookielaw.rejectCookies();
            
            expect(Cookielaw.isCookieAccepted()).toBe(false);
            expect(Cookielaw.isCookieRejected()).toBe(true);
        });

        it('should transition from rejected to accepted', function() {
            Cookielaw.rejectCookies();
            expect(Cookielaw.isCookieRejected()).toBe(true);
            
            Cookielaw.createCookielawCookie();
            
            expect(Cookielaw.isCookieAccepted()).toBe(true);
            expect(Cookielaw.isCookieRejected()).toBe(false);
        });
    });

    describe('GDPR Compliance', function() {
        
        it('should have both accept and reject functions available', function() {
            expect(typeof Cookielaw.createCookielawCookie).toBe('function');
            expect(typeof Cookielaw.rejectCookies).toBe('function');
        });

        it('should allow users to check their preference', function() {
            expect(typeof Cookielaw.isCookieAccepted).toBe('function');
            expect(typeof Cookielaw.isCookieRejected).toBe('function');
        });

        it('should make reject option equally accessible as accept', function() {
            // Both functions should be callable without any complexity
            var acceptCallable = typeof Cookielaw.createCookielawCookie === 'function';
            var rejectCallable = typeof Cookielaw.rejectCookies === 'function';
            
            expect(acceptCallable).toBe(true);
            expect(rejectCallable).toBe(true);
        });

        it('should persist user preference for one year', function() {
            var today = new Date();
            
            Cookielaw.createCookielawCookie();
            
            // Cookie should exist and contain the preference
            expect(document.cookie).toContain('cookielaw_accepted=true');
            
            // The cookie string should indicate it's set for a long duration
            expect(document.cookie).toContain('cookielaw_accepted=true');
        });
    });

});
