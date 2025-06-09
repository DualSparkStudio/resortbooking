// Luxury Resort Main JavaScript File

(function($) {
    'use strict';

    // Document Ready
    $(document).ready(function() {
        initializeComponents();
        setupEventListeners();
        handleNavigation();
        initializeAnimations();
    });

    // Initialize Components
    function initializeComponents() {
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });

        // Initialize date inputs with today as minimum
        initializeDateInputs();

        // Initialize form validations
        initializeFormValidation();

        // Initialize smooth scrolling
        initializeSmoothScrolling();

        // Initialize lazy loading for images
        initializeLazyLoading();
    }

    // Setup Event Listeners
    function setupEventListeners() {
        // Mobile menu toggle
        $('.navbar-toggler').on('click', function() {
            $(this).toggleClass('active');
        });

        // Search functionality
        setupSearchHandlers();

        // Booking form handlers
        setupBookingHandlers();

        // Contact form handlers
        setupContactFormHandlers();

        // Admin panel handlers
        setupAdminHandlers();

        // Window resize handler
        $(window).on('resize', function() {
            handleResponsiveElements();
        });

        // Scroll handlers
        $(window).on('scroll', function() {
            handleScrollEffects();
        });
    }

    // Navigation Handling
    function handleNavigation() {
        // Add active class to current page nav item
        var currentPath = window.location.pathname;
        $('.nav-link').each(function() {
            var href = $(this).attr('href');
            if (href && currentPath.includes(href) && href !== '/') {
                $(this).addClass('active');
            }
        });

        // Navbar background on scroll
        $(window).scroll(function() {
            if ($(this).scrollTop() > 50) {
                $('.luxury-nav').addClass('scrolled');
            } else {
                $('.luxury-nav').removeClass('scrolled');
            }
        });
    }

    // Initialize Animations
    function initializeAnimations() {
        // Animate elements on scroll
        $(window).scroll(function() {
            $('.animate-on-scroll').each(function() {
                var elementTop = $(this).offset().top;
                var elementBottom = elementTop + $(this).outerHeight();
                var viewportTop = $(window).scrollTop();
                var viewportBottom = viewportTop + $(window).height();

                if (elementBottom > viewportTop && elementTop < viewportBottom) {
                    $(this).addClass('animate-fade-in-up');
                }
            });
        });

        // Counter animation
        $('.luxury-stat-number').each(function() {
            var $this = $(this);
            var countTo = parseInt($this.text().replace(/[^\d]/g, ''));
            
            $({ countNum: 0 }).animate({
                countNum: countTo
            }, {
                duration: 2000,
                easing: 'swing',
                step: function() {
                    $this.text(Math.floor(this.countNum).toLocaleString());
                },
                complete: function() {
                    $this.text(countTo.toLocaleString());
                }
            });
        });
    }

    // Date Input Initialization
    function initializeDateInputs() {
        var today = new Date().toISOString().split('T')[0];
        $('input[type="date"]').attr('min', today);

        // Check-in/Check-out date validation
        $('input[name="check_in_date"], #checkIn').on('change', function() {
            var checkInDate = new Date($(this).val());
            var checkOutInput = $('input[name="check_out_date"], #checkOut');
            
            if (checkInDate) {
                checkInDate.setDate(checkInDate.getDate() + 1);
                var minCheckOut = checkInDate.toISOString().split('T')[0];
                checkOutInput.attr('min', minCheckOut);
                
                if (checkOutInput.val() && checkOutInput.val() <= $(this).val()) {
                    checkOutInput.val(minCheckOut);
                }
            }
        });
    }

    // Form Validation
    function initializeFormValidation() {
        // Bootstrap form validation
        var forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });

        // Custom validation rules
        setupCustomValidation();
    }

    // Custom Validation Rules
    function setupCustomValidation() {
        // Email validation
        $('input[type="email"]').on('blur', function() {
            var email = $(this).val();
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                $(this).addClass('is-invalid');
                showValidationMessage($(this), 'Please enter a valid email address.');
            } else {
                $(this).removeClass('is-invalid').addClass('is-valid');
                hideValidationMessage($(this));
            }
        });

        // Phone validation
        $('input[type="tel"]').on('blur', function() {
            var phone = $(this).val();
            var phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            
            if (phone && !phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''))) {
                $(this).addClass('is-invalid');
                showValidationMessage($(this), 'Please enter a valid phone number.');
            } else {
                $(this).removeClass('is-invalid').addClass('is-valid');
                hideValidationMessage($(this));
            }
        });

        // Password strength validation
        $('input[type="password"]').on('input', function() {
            if ($(this).attr('name') === 'password') {
                validatePasswordStrength($(this));
            }
        });
    }

    // Password Strength Validation
    function validatePasswordStrength(input) {
        var password = input.val();
        var strength = 0;
        var feedback = [];

        // Length check
        if (password.length >= 8) strength += 20;
        else feedback.push('At least 8 characters');

        // Uppercase check
        if (/[A-Z]/.test(password)) strength += 20;
        else feedback.push('One uppercase letter');

        // Lowercase check
        if (/[a-z]/.test(password)) strength += 20;
        else feedback.push('One lowercase letter');

        // Number check
        if (/\d/.test(password)) strength += 20;
        else feedback.push('One number');

        // Special character check
        if (/[^a-zA-Z0-9]/.test(password)) strength += 20;
        else feedback.push('One special character');

        // Update strength indicator
        var strengthBar = input.siblings('.password-strength').find('.progress-bar');
        var strengthText = input.siblings('.password-strength').find('small');

        if (strengthBar.length) {
            strengthBar.css('width', strength + '%');
            
            if (strength < 40) {
                strengthBar.removeClass().addClass('progress-bar bg-danger');
                strengthText.text('Weak password - ' + feedback.join(', '));
            } else if (strength < 80) {
                strengthBar.removeClass().addClass('progress-bar bg-warning');
                strengthText.text('Medium strength');
            } else {
                strengthBar.removeClass().addClass('progress-bar bg-success');
                strengthText.text('Strong password');
            }
        }
    }

    // Search Handlers
    function setupSearchHandlers() {
        // Room search functionality
        $('#roomSearch').on('input', function() {
            var searchTerm = $(this).val().toLowerCase();
            $('.room-card').each(function() {
                var roomName = $(this).find('.card-title').text().toLowerCase();
                var roomDescription = $(this).find('.card-text').text().toLowerCase();
                
                if (roomName.includes(searchTerm) || roomDescription.includes(searchTerm)) {
                    $(this).closest('.col-lg-4').show();
                } else {
                    $(this).closest('.col-lg-4').hide();
                }
            });
        });

        // Quick search form
        $('.quick-search-form').on('submit', function(e) {
            e.preventDefault();
            performQuickSearch();
        });
    }

    // Booking Handlers
    function setupBookingHandlers() {
        // Room availability check
        $('#checkAvailability').on('click', function() {
            checkRoomAvailability();
        });

        // Guest count validation
        $('select[name="num_guests"], #guests').on('change', function() {
            var maxOccupancy = $(this).data('max-occupancy') || 10;
            var selectedGuests = parseInt($(this).val());
            
            if (selectedGuests > maxOccupancy) {
                showNotification('warning', 'This room type has a maximum occupancy of ' + maxOccupancy + ' guests.');
                $(this).val(maxOccupancy);
            }
        });

        // Booking form submission
        $('.booking-form').on('submit', function() {
            showLoadingState($(this));
        });

        // Price calculation
        setupPriceCalculation();
    }

    // Price Calculation
    function setupPriceCalculation() {
        $('input[name="check_in_date"], input[name="check_out_date"], #checkIn, #checkOut').on('change', function() {
            calculateBookingPrice();
        });
    }

    // Calculate Booking Price
    function calculateBookingPrice() {
        var checkIn = $('input[name="check_in_date"], #checkIn').val();
        var checkOut = $('input[name="check_out_date"], #checkOut').val();
        var pricePerNight = parseFloat($('#pricePerNight').data('price') || 0);

        if (checkIn && checkOut && pricePerNight) {
            var startDate = new Date(checkIn);
            var endDate = new Date(checkOut);
            var nights = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));

            if (nights > 0) {
                var subtotal = nights * pricePerNight;
                var taxes = subtotal * 0.12; // 12% tax
                var total = subtotal + taxes;

                // Update price display
                updatePriceDisplay(nights, subtotal, taxes, total);
            }
        }
    }

    // Update Price Display
    function updatePriceDisplay(nights, subtotal, taxes, total) {
        $('#nightsCount').text(nights);
        $('#subtotalAmount').text(formatCurrency(subtotal));
        $('#taxAmount').text(formatCurrency(taxes));
        $('#totalAmount').text(formatCurrency(total));
        
        // Show price breakdown
        $('.price-breakdown').show();
    }

    // Contact Form Handlers
    function setupContactFormHandlers() {
        $('.contact-form').on('submit', function(e) {
            var form = $(this);
            
            // Basic validation
            if (!validateContactForm(form)) {
                e.preventDefault();
                return false;
            }
            
            showLoadingState(form);
        });
    }

    // Validate Contact Form
    function validateContactForm(form) {
        var isValid = true;
        var requiredFields = form.find('[required]');
        
        requiredFields.each(function() {
            if (!$(this).val().trim()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid').addClass('is-valid');
            }
        });
        
        return isValid;
    }

    // Admin Panel Handlers
    function setupAdminHandlers() {
        // Data table enhancements
        if ($('.admin-table').length) {
            initializeAdminTables();
        }

        // Chart initialization
        if ($('#bookingChart').length) {
            initializeBookingChart();
        }

        // Bulk actions
        setupBulkActions();
    }

    // Initialize Admin Tables
    function initializeAdminTables() {
        $('.admin-table').each(function() {
            var table = $(this);
            
            // Add search functionality
            var searchInput = $('<input type="text" class="form-control mb-3" placeholder="Search table...">');
            table.before(searchInput);
            
            searchInput.on('input', function() {
                var searchTerm = $(this).val().toLowerCase();
                table.find('tbody tr').each(function() {
                    var rowText = $(this).text().toLowerCase();
                    $(this).toggle(rowText.includes(searchTerm));
                });
            });
        });
    }

    // Bulk Actions Setup
    function setupBulkActions() {
        // Select all functionality
        $('input[type="checkbox"][id="selectAll"]').on('change', function() {
            var isChecked = $(this).prop('checked');
            var checkboxes = $(this).closest('table').find('tbody input[type="checkbox"]');
            checkboxes.prop('checked', isChecked);
            updateBulkActionButtons();
        });

        // Individual checkbox handling
        $('table tbody input[type="checkbox"]').on('change', function() {
            updateBulkActionButtons();
        });
    }

    // Update Bulk Action Buttons
    function updateBulkActionButtons() {
        var selectedCount = $('table tbody input[type="checkbox"]:checked').length;
        $('.bulk-action-btn').prop('disabled', selectedCount === 0);
        $('.selected-count').text(selectedCount);
    }

    // Smooth Scrolling
    function initializeSmoothScrolling() {
        $('a[href^="#"]').on('click', function(e) {
            var target = $(this.getAttribute('href'));
            
            if (target.length) {
                e.preventDefault();
                $('html, body').stop().animate({
                    scrollTop: target.offset().top - 100
                }, 1000);
            }
        });
    }

    // Lazy Loading
    function initializeLazyLoading() {
        if ('IntersectionObserver' in window) {
            var imageObserver = new IntersectionObserver(function(entries, observer) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        var img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(function(img) {
                imageObserver.observe(img);
            });
        }
    }

    // Responsive Element Handling
    function handleResponsiveElements() {
        var windowWidth = $(window).width();
        
        // Mobile-specific adjustments
        if (windowWidth < 768) {
            $('.sticky-top').removeClass('sticky-top').addClass('was-sticky');
        } else {
            $('.was-sticky').removeClass('was-sticky').addClass('sticky-top');
        }
    }

    // Scroll Effects
    function handleScrollEffects() {
        var scrollTop = $(window).scrollTop();
        var windowHeight = $(window).height();

        // Parallax effect for hero sections
        $('.hero-section').css('transform', 'translateY(' + scrollTop * 0.5 + 'px)');

        // Fade in elements
        $('.fade-in-on-scroll').each(function() {
            var elementTop = $(this).offset().top;
            if (elementTop < scrollTop + windowHeight - 100) {
                $(this).addClass('fade-in');
            }
        });
    }

    // Room Availability Check
    function checkRoomAvailability() {
        var checkIn = $('#checkIn').val();
        var checkOut = $('#checkOut').val();
        var roomType = $('#roomType').val();

        if (!checkIn || !checkOut) {
            showNotification('warning', 'Please select check-in and check-out dates.');
            return;
        }

        // Show loading state
        $('#checkAvailability').html('<i class="fas fa-spinner fa-spin me-2"></i>Checking...').prop('disabled', true);

        // Simulate API call (replace with actual implementation)
        setTimeout(function() {
            $('#checkAvailability').html('<i class="fas fa-search me-2"></i>Check Availability').prop('disabled', false);
            showNotification('success', 'Rooms are available for your selected dates!');
        }, 2000);
    }

    // Quick Search Performance
    function performQuickSearch() {
        var formData = $('.quick-search-form').serialize();
        
        // Redirect to rooms page with search parameters
        window.location.href = '/rooms?' + formData;
    }

    // Utility Functions
    function showLoadingState(element) {
        var submitBtn = element.find('button[type="submit"]');
        submitBtn.prop('disabled', true);
        
        var originalText = submitBtn.html();
        submitBtn.data('original-text', originalText);
        submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
    }

    function hideLoadingState(element) {
        var submitBtn = element.find('button[type="submit"]');
        submitBtn.prop('disabled', false);
        submitBtn.html(submitBtn.data('original-text'));
    }

    function showNotification(type, message, duration = 5000) {
        var alertClass = 'alert-' + type;
        var icon = getNotificationIcon(type);
        
        var notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 100px; right: 20px; z-index: 9999; max-width: 400px;" role="alert">
                <i class="${icon} me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(notification);
        
        // Auto-dismiss after duration
        setTimeout(function() {
            notification.fadeOut(function() {
                $(this).remove();
            });
        }, duration);
    }

    function getNotificationIcon(type) {
        var icons = {
            'success': 'fas fa-check-circle',
            'danger': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    function showValidationMessage(element, message) {
        var feedback = element.siblings('.invalid-feedback');
        if (feedback.length === 0) {
            feedback = $('<div class="invalid-feedback"></div>');
            element.after(feedback);
        }
        feedback.text(message);
    }

    function hideValidationMessage(element) {
        element.siblings('.invalid-feedback').remove();
    }

    function formatCurrency(amount) {
        return '$' + amount.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Public API
    window.LuxuryResort = {
        showNotification: showNotification,
        formatCurrency: formatCurrency,
        checkAvailability: checkRoomAvailability,
        calculatePrice: calculateBookingPrice
    };

    // Initialize everything when DOM is ready
    $(document).ready(function() {
        // Add loading class to body initially
        $('body').addClass('loading');
        
        // Remove loading class when everything is loaded
        $(window).on('load', function() {
            $('body').removeClass('loading');
        });
    });

})(jQuery);

// Additional standalone functions

// Image gallery functionality
function initializeImageGallery() {
    $('.gallery-image').on('click', function() {
        var src = $(this).attr('src');
        var alt = $(this).attr('alt');
        
        var modal = $(`
            <div class="modal fade" id="imageModal" tabindex="-1">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${alt}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${src}" class="img-fluid" alt="${alt}">
                        </div>
                    </div>
                </div>
            </div>
        `);
        
        $('body').append(modal);
        modal.modal('show');
        
        modal.on('hidden.bs.modal', function() {
            modal.remove();
        });
    });
}

// Star rating functionality
function initializeStarRating() {
    $('.star-rating').each(function() {
        var rating = $(this).data('rating');
        var stars = '';
        
        for (var i = 1; i <= 5; i++) {
            if (i <= rating) {
                stars += '<i class="fas fa-star text-warning"></i>';
            } else {
                stars += '<i class="far fa-star text-muted"></i>';
            }
        }
        
        $(this).html(stars);
    });
}

// Cookie consent handling
function initializeCookieConsent() {
    if (!localStorage.getItem('cookieConsent')) {
        var cookieBanner = $(`
            <div class="cookie-consent position-fixed bottom-0 start-0 end-0 bg-dark text-white p-3" style="z-index: 9999;">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <p class="mb-0">We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.</p>
                        </div>
                        <div class="col-md-4 text-end">
                            <button class="btn btn-luxury btn-sm me-2" id="acceptCookies">Accept</button>
                            <button class="btn btn-outline-light btn-sm" id="declineCookies">Decline</button>
                        </div>
                    </div>
                </div>
            </div>
        `);
        
        $('body').append(cookieBanner);
        
        $('#acceptCookies').on('click', function() {
            localStorage.setItem('cookieConsent', 'accepted');
            cookieBanner.fadeOut();
        });
        
        $('#declineCookies').on('click', function() {
            localStorage.setItem('cookieConsent', 'declined');
            cookieBanner.fadeOut();
        });
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Social sharing
function shareOnSocial(platform, url, text) {
    var shareUrls = {
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
        twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
        whatsapp: `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`
    };
    
    if (shareUrls[platform]) {
        window.open(shareUrls[platform], '_blank', 'width=600,height=400');
    }
}

// Export functionality
function exportData(data, filename, type = 'csv') {
    var content = '';
    var mimeType = '';
    
    if (type === 'csv') {
        content = convertToCSV(data);
        mimeType = 'text/csv';
    } else if (type === 'json') {
        content = JSON.stringify(data, null, 2);
        mimeType = 'application/json';
    }
    
    var blob = new Blob([content], { type: mimeType });
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + '.' + type;
    link.click();
}

function convertToCSV(data) {
    if (!data.length) return '';
    
    var headers = Object.keys(data[0]);
    var csv = headers.join(',') + '\n';
    
    data.forEach(function(row) {
        var values = headers.map(function(header) {
            var value = row[header] || '';
            return '"' + value.toString().replace(/"/g, '""') + '"';
        });
        csv += values.join(',') + '\n';
    });
    
    return csv;
}

// Initialize additional features when document is ready
$(document).ready(function() {
    initializeImageGallery();
    initializeStarRating();
    initializeCookieConsent();
});
