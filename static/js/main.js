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

        // Enhanced navbar background on scroll with smooth transitions
        var lastScrollTop = 0;
        var navbar = $('.luxury-nav');
        
        $(window).scroll(function() {
            var scrollTop = $(this).scrollTop();
            
            // Add/remove scrolled class for styling
            if (scrollTop > 50) {
                navbar.addClass('scrolled');
            } else {
                navbar.removeClass('scrolled');
            }
            
            // Hide/show navbar on scroll direction (optional enhancement)
            if (scrollTop > lastScrollTop && scrollTop > 200) {
                // Scrolling down - hide navbar
                navbar.addClass('navbar-hidden');
            } else {
                // Scrolling up - show navbar
                navbar.removeClass('navbar-hidden');
            }
            
            lastScrollTop = scrollTop;
        });

        // Smooth scroll for anchor links
        $('a[href^="#"]').on('click', function(e) {
            var target = $(this.getAttribute('href'));
            if (target.length) {
                e.preventDefault();
                $('html, body').stop().animate({
                    scrollTop: target.offset().top - navbar.outerHeight()
                }, 800, 'easeInOutQuart');
            }
        });

        // Add parallax effect to hero section
        if ($('.hero-section').length) {
            $(window).scroll(function() {
                var scrolled = $(window).scrollTop();
                var rate = scrolled * -0.5;
                $('.hero-slide').css('transform', 'translateY(' + rate + 'px)');
            });
        }

        // Enhanced dropdown behavior
        $('.navbar-nav .dropdown').hover(
            function() {
                $(this).find('.dropdown-menu').addClass('show');
                $(this).find('.dropdown-toggle').attr('aria-expanded', 'true');
            },
            function() {
                $(this).find('.dropdown-menu').removeClass('show');
                $(this).find('.dropdown-toggle').attr('aria-expanded', 'false');
            }
        );
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
        // Custom validation for all forms
        $('form').each(function() {
            setupCustomValidation($(this));
        });

        // Password strength indicator
        $('input[type="password"]').on('input', function() {
            validatePasswordStrength($(this));
        });
    }

    // Custom Form Validation Setup
    function setupCustomValidation(form) {
        form.on('submit', function(e) {
            var isValid = true;
            
            // Clear previous validation messages
            form.find('.is-invalid').removeClass('is-invalid');
            form.find('.invalid-feedback').remove();
            
            // Required field validation
            form.find('[required]').each(function() {
                var field = $(this);
                var value = field.val().trim();
                
                if (!value) {
                    field.addClass('is-invalid');
                    showValidationMessage(field, 'This field is required.');
                    isValid = false;
                }
            });
            
            // Email validation
            form.find('input[type="email"]').each(function() {
                var field = $(this);
                var email = field.val().trim();
                var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                
                if (email && !emailRegex.test(email)) {
                    field.addClass('is-invalid');
                    showValidationMessage(field, 'Please enter a valid email address.');
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                form.find('.is-invalid').first().focus();
            } else {
                showLoadingState(form);
            }
        });
        
        return isValid;
    }

    // Password Strength Validation
    function validatePasswordStrength(input) {
        var password = input.val();
        var strengthMeter = input.siblings('.password-strength');
        
        if (!strengthMeter.length) {
            strengthMeter = $('<div class="password-strength mt-2"></div>');
            input.after(strengthMeter);
        }
        
        var strength = 0;
        var feedback = [];
        
        if (password.length >= 8) strength++;
        else feedback.push('At least 8 characters');
        
        if (/[a-z]/.test(password)) strength++;
        else feedback.push('Lowercase letter');
        
        if (/[A-Z]/.test(password)) strength++;
        else feedback.push('Uppercase letter');
        
        if (/[0-9]/.test(password)) strength++;
        else feedback.push('Number');
        
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        else feedback.push('Special character');
        
        var strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        var strengthColor = ['danger', 'warning', 'info', 'success', 'success'];
        
        if (password.length > 0) {
            strengthMeter.html(`
                <div class="progress" style="height: 5px;">
                    <div class="progress-bar bg-${strengthColor[strength]}" style="width: ${(strength + 1) * 20}%"></div>
                </div>
                <small class="text-${strengthColor[strength]}">${strengthText[strength] || 'Very Weak'}</small>
                ${feedback.length ? `<small class="text-muted d-block">Missing: ${feedback.join(', ')}</small>` : ''}
            `);
        } else {
            strengthMeter.empty();
        }
    }

    // Search Handlers
    function setupSearchHandlers() {
        // Quick search functionality
        $('.quick-search-form').on('submit', function(e) {
            e.preventDefault();
            
            var checkIn = $(this).find('input[name="check_in"]').val();
            var checkOut = $(this).find('input[name="check_out"]').val();
            
            if (!checkIn || !checkOut) {
                showNotification('warning', 'Please select both check-in and check-out dates.');
                return;
            }
            
            var formData = $(this).serialize();
            window.location.href = '/rooms?' + formData;
        });
    }

    // Booking Handlers
    function setupBookingHandlers() {
        // Room selection
        $('.room-card .btn-primary').on('click', function(e) {
            e.preventDefault();
            
            var roomId = $(this).data('room-id');
            var checkIn = $('input[name="check_in"]').val();
            var checkOut = $('input[name="check_out"]').val();
            
            if (!checkIn || !checkOut) {
                showNotification('warning', 'Please select your dates first.');
                return;
            }
            
            window.location.href = `/booking/${roomId}?check_in=${checkIn}&check_out=${checkOut}`;
        });

        // Price calculation setup
        setupPriceCalculation();
    }

    // Price Calculation Setup
    function setupPriceCalculation() {
        $('input[name="check_in_date"], input[name="check_out_date"]').on('change', calculateBookingPrice);
    }

    // Calculate Booking Price
    function calculateBookingPrice() {
        var checkInDate = new Date($('input[name="check_in_date"]').val());
        var checkOutDate = new Date($('input[name="check_out_date"]').val());
        var pricePerNight = parseFloat($('#price-per-night').data('price') || 0);
        
        if (checkInDate && checkOutDate && checkOutDate > checkInDate) {
            var timeDiff = checkOutDate.getTime() - checkInDate.getTime();
            var nights = Math.ceil(timeDiff / (1000 * 3600 * 24));
            
            var subtotal = nights * pricePerNight;
            var taxes = subtotal * 0.12; // 12% tax
            var total = subtotal + taxes;
            
            updatePriceDisplay(nights, subtotal, taxes, total);
        }
    }

    // Update Price Display
    function updatePriceDisplay(nights, subtotal, taxes, total) {
        $('#nights-count').text(nights);
        $('#subtotal-amount').text(formatCurrency(subtotal));
        $('#taxes-amount').text(formatCurrency(taxes));
        $('#total-amount').text(formatCurrency(total));
        $('.price-breakdown').show();
    }

    // Contact Form Handlers
    function setupContactFormHandlers() {
        $('.contact-form').on('submit', function(e) {
            e.preventDefault();
            
            if (validateContactForm($(this))) {
                // Submit form via AJAX or normal submission
                $(this)[0].submit();
            }
        });
    }

    // Contact Form Validation
    function validateContactForm(form) {
        var isValid = true;
        
        form.find('input, textarea').each(function() {
            var field = $(this);
            var value = field.val().trim();
            
            hideValidationMessage(field);
            
            if (field.prop('required') && !value) {
                showValidationMessage(field, 'This field is required.');
                isValid = false;
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
        var feedback = $('<div class="invalid-feedback">' + message + '</div>');
        element.addClass('is-invalid');
        element.after(feedback);
    }

    function hideValidationMessage(element) {
        element.removeClass('is-invalid');
        element.siblings('.invalid-feedback').remove();
    }

    function formatCurrency(amount) {
        return '$' + amount.toFixed(2);
    }

    // ADMIN SPECIFIC FUNCTIONS
    
    // Switch View Function for Bookings Page
    window.switchView = function(viewType) {
        var tableView = document.getElementById('tableView');
        var calendarView = document.getElementById('calendarView');
        var tableBtn = document.getElementById('tableViewBtn');
        var calendarBtn = document.getElementById('calendarViewBtn');

        if (viewType === 'table') {
            // Show table view
            tableView.style.display = 'block';
            calendarView.style.display = 'none';
            
            // Update button states
            tableBtn.classList.add('active');
            calendarBtn.classList.remove('active');
        } else if (viewType === 'calendar') {
            // Show calendar view
            tableView.style.display = 'none';
            calendarView.style.display = 'block';
            
            // Update button states
            calendarBtn.classList.add('active');
            tableBtn.classList.remove('active');
            
            // Initialize calendar if not already done
            if (!window.adminCalendarInitialized) {
                initializeAdminCalendar();
                window.adminCalendarInitialized = true;
            }
        }
    };

    // Initialize Admin Calendar
    function initializeAdminCalendar() {
        // Check if FullCalendar is available
        if (typeof FullCalendar !== 'undefined') {
            var calendarEl = document.getElementById('adminCalendar');
            if (calendarEl) {
                var calendar = new FullCalendar.Calendar(calendarEl, {
                    initialView: 'dayGridMonth',
                    height: 'auto',
                    headerToolbar: {
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay'
                    },
                    events: '/admin/bookings/calendar-data', // This should be implemented in your backend
                    eventClick: function(info) {
                        // Handle booking click
                        showBookingDetails(info.event);
                    }
                });
                calendar.render();
                window.adminCalendar = calendar;
            }
        } else {
            console.warn('FullCalendar not loaded. Calendar view may not work properly.');
        }
    }

    // Export Bookings Function
    window.exportBookings = function() {
        // Get all checked bookings or all bookings if none checked
        var selectedBookings = [];
        $('table tbody input[type="checkbox"]:checked').each(function() {
            var row = $(this).closest('tr');
            var bookingData = {
                id: $(this).val(),
                guest: row.find('td:nth-child(3)').text().trim(),
                room: row.find('td:nth-child(4)').text().trim(),
                dates: row.find('td:nth-child(5)').text().trim(),
                status: row.find('td:nth-child(6)').text().trim(),
                payment: row.find('td:nth-child(7)').text().trim(),
                total: row.find('td:nth-child(8)').text().trim()
            };
            selectedBookings.push(bookingData);
        });

        if (selectedBookings.length === 0) {
            showNotification('info', 'No bookings selected. Exporting all visible bookings.');
            // Export all visible bookings
            $('table tbody tr:visible').each(function() {
                var row = $(this);
                var bookingData = {
                    id: row.find('input[type="checkbox"]').val(),
                    guest: row.find('td:nth-child(3)').text().trim(),
                    room: row.find('td:nth-child(4)').text().trim(),
                    dates: row.find('td:nth-child(5)').text().trim(),
                    status: row.find('td:nth-child(6)').text().trim(),
                    payment: row.find('td:nth-child(7)').text().trim(),
                    total: row.find('td:nth-child(8)').text().trim()
                };
                selectedBookings.push(bookingData);
            });
        }

        // Convert to CSV and download
        exportData(selectedBookings, 'bookings_export.csv', 'csv');
    };

    // Refresh Bookings Function
    window.refreshBookings = function() {
        showNotification('info', 'Refreshing bookings...');
        setTimeout(function() {
            window.location.reload();
        }, 500);
    };

    // Refresh Calendar Function
    window.refreshCalendar = function() {
        if (window.adminCalendar) {
            window.adminCalendar.refetchEvents();
            showNotification('success', 'Calendar refreshed!');
        } else {
            showNotification('warning', 'Calendar not initialized.');
        }
    };

    // Confirm Delete Function
    window.confirmDelete = function(type, id) {
        var itemName = type === 'room_type' ? 'room type' : 'room';
        if (confirm('Are you sure you want to delete this ' + itemName + '? This action cannot be undone.')) {
            // Create a form and submit it
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin/' + type.replace('_', '-') + 's/delete/' + id;
            
            // Add CSRF token
            var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            var csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            document.body.appendChild(form);
            form.submit();
        }
    };

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

// Global Date Selection Manager
window.DateSelectionManager = {
    // Keys for sessionStorage
    CHECK_IN_KEY: 'booking_check_in_date',
    CHECK_OUT_KEY: 'booking_check_out_date',
    ROOM_TYPE_KEY: 'booking_room_type_id',
    
    // Get stored dates
    getCheckInDate: function() {
        const dateStr = sessionStorage.getItem(this.CHECK_IN_KEY);
        return dateStr ? new Date(dateStr) : null;
    },
    
    getCheckOutDate: function() {
        const dateStr = sessionStorage.getItem(this.CHECK_OUT_KEY);
        return dateStr ? new Date(dateStr) : null;
    },
    
    getRoomTypeId: function() {
        return sessionStorage.getItem(this.ROOM_TYPE_KEY);
    },
    
    // Store dates
    setCheckInDate: function(date) {
        if (date) {
            sessionStorage.setItem(this.CHECK_IN_KEY, date.toISOString().split('T')[0]);
        } else {
            sessionStorage.removeItem(this.CHECK_IN_KEY);
        }
        this.notifyDateChange();
    },
    
    setCheckOutDate: function(date) {
        if (date) {
            sessionStorage.setItem(this.CHECK_OUT_KEY, date.toISOString().split('T')[0]);
        } else {
            sessionStorage.removeItem(this.CHECK_OUT_KEY);
        }
        this.notifyDateChange();
    },
    
    setRoomTypeId: function(roomTypeId) {
        if (roomTypeId) {
            sessionStorage.setItem(this.ROOM_TYPE_KEY, roomTypeId);
        } else {
            sessionStorage.removeItem(this.ROOM_TYPE_KEY);
        }
    },
    
    // Set both dates at once
    setDates: function(checkIn, checkOut, roomTypeId) {
        this.setCheckInDate(checkIn);
        this.setCheckOutDate(checkOut);
        if (roomTypeId) {
            this.setRoomTypeId(roomTypeId);
        }
    },
    
    // Clear all dates
    clearDates: function() {
        sessionStorage.removeItem(this.CHECK_IN_KEY);
        sessionStorage.removeItem(this.CHECK_OUT_KEY);
        sessionStorage.removeItem(this.ROOM_TYPE_KEY);
        this.notifyDateChange();
    },
    
    // Check if dates are set
    hasDates: function() {
        return this.getCheckInDate() && this.getCheckOutDate();
    },
    
    // Get formatted date strings
    getFormattedCheckIn: function() {
        const date = this.getCheckInDate();
        return date ? date.toISOString().split('T')[0] : '';
    },
    
    getFormattedCheckOut: function() {
        const date = this.getCheckOutDate();
        return date ? date.toISOString().split('T')[0] : '';
    },
    
    // Calculate nights
    getNights: function() {
        const checkIn = this.getCheckInDate();
        const checkOut = this.getCheckOutDate();
        if (checkIn && checkOut) {
            return Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
        }
        return 0;
    },
    
    // Event listeners for date changes
    listeners: [],
    
    // Add listener for date changes
    onDateChange: function(callback) {
        this.listeners.push(callback);
    },
    
    // Notify all listeners of date changes
    notifyDateChange: function() {
        this.listeners.forEach(callback => {
            try {
                callback();
            } catch (error) {
                console.error('Error in date change listener:', error);
            }
        });
    },
    
    // Initialize date inputs on page
    initializeDateInputs: function() {
        // Find check-in and check-out inputs
        const checkInInput = document.querySelector('input[name="check_in_date"], input[id*="check_in"], input[id*="checkin"]');
        const checkOutInput = document.querySelector('input[name="check_out_date"], input[id*="check_out"], input[id*="checkout"]');
        
        // Set stored values
        if (checkInInput && this.getFormattedCheckIn()) {
            checkInInput.value = this.getFormattedCheckIn();
        }
        
        if (checkOutInput && this.getFormattedCheckOut()) {
            checkOutInput.value = this.getFormattedCheckOut();
        }
        
        // Add event listeners to update storage when inputs change
        if (checkInInput) {
            checkInInput.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.setCheckInDate(new Date(e.target.value));
                } else {
                    this.setCheckInDate(null);
                }
            });
        }
        
        if (checkOutInput) {
            checkOutInput.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.setCheckOutDate(new Date(e.target.value));
                } else {
                    this.setCheckOutDate(null);
                }
            });
        }
        
        // Update booking summary if present
        this.updateBookingSummary();
    },
    
    // Update booking summary display
    updateBookingSummary: function() {
        const summaryCheckIn = document.getElementById('summaryCheckIn');
        const summaryCheckOut = document.getElementById('summaryCheckOut');
        const summaryNights = document.getElementById('summaryNights');
        const bookingSummary = document.getElementById('bookingSummary');
        
        if (this.hasDates()) {
            const checkInDate = this.getCheckInDate();
            const checkOutDate = this.getCheckOutDate();
            const nights = this.getNights();
            
            if (summaryCheckIn) {
                summaryCheckIn.textContent = checkInDate.toLocaleDateString();
            }
            
            if (summaryCheckOut) {
                summaryCheckOut.textContent = checkOutDate.toLocaleDateString();
            }
            
            if (summaryNights) {
                summaryNights.textContent = nights + (nights === 1 ? ' night' : ' nights');
            }
            
            if (bookingSummary) {
                bookingSummary.style.display = 'block';
            }
        } else {
            if (bookingSummary) {
                bookingSummary.style.display = 'none';
            }
        }
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date inputs with stored values
    DateSelectionManager.initializeDateInputs();
    
    // Listen for date changes to update displays
    DateSelectionManager.onDateChange(function() {
        DateSelectionManager.updateBookingSummary();
    });
});

// Clear dates on page refresh
window.addEventListener('beforeunload', function() {
    // Mark that we're about to unload
    sessionStorage.setItem('page_unloading', 'true');
});

// Check if page was refreshed and clear dates
window.addEventListener('load', function() {
    if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
        // This is a refresh, clear the dates
        DateSelectionManager.clearDates();
    } else {
        // This is navigation, remove the unloading flag
        sessionStorage.removeItem('page_unloading');
    }
});
