// Cookie Law consent management
var Cookielaw = (function() {
    return {
        createCookielawCookie: function() {
            // Set cookie to accept cookies
            var expirationDate = new Date();
            expirationDate.setFullYear(expirationDate.getFullYear() + 1);
            document.cookie = "cookielaw_accepted=true; path=/; expires=" + expirationDate.toUTCString();
        },
        
        rejectCookies: function() {
            // Set cookie to reject cookies
            var expirationDate = new Date();
            expirationDate.setFullYear(expirationDate.getFullYear() + 1);
            document.cookie = "cookielaw_accepted=false; path=/; expires=" + expirationDate.toUTCString();
        },
        
        isCookieAccepted: function() {
            return document.cookie.indexOf('cookielaw_accepted=true') !== -1;
        },
        
        isCookieRejected: function() {
            return document.cookie.indexOf('cookielaw_accepted=false') !== -1;
        }
    };
})();