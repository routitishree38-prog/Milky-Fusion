// static/app/js/myscript.js

// ===== DEPENDENCY CHECK =====
if (typeof jQuery === 'undefined') {
    console.error('ERROR: jQuery is not loaded!');
    alert('jQuery is not loaded! Please check your base.html');
} else {
    console.log('jQuery version:', jQuery.fn.jquery);
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'info') {
    if (!$('#notification-container').length) {
        $('body').append('<div id="notification-container" style="position: fixed; top: 20px; right: 20px; z-index: 9999;"></div>');
    }

    const alertClass = type === 'success' ? 'alert-success' : (type === 'error' ? 'alert-danger' : (type === 'warning' ? 'alert-warning' : 'alert-info'));
    const icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-circle' : (type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'));

    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="min-width: 300px; margin-bottom: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
            <i class="fas ${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);

    $('#notification-container').append(notification);

    setTimeout(() => {
        notification.fadeOut(300, function () { $(this).remove(); });
    }, 3000);
}

// ===== LOADING SPINNER =====
function showLoading() {
    if (!$('#loading-spinner').length) {
        $('body').append(`
            <div id="loading-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 99999;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `);
    }
}

function hideLoading() {
    $('#loading-spinner').remove();
}


// Initialize AOS only when the library is available.
if (typeof AOS !== 'undefined') {
    AOS.init({
        duration: 1000,
        once: true
    });
} else {
    console.warn('AOS is not loaded; continuing without scroll animations.');
}

// Navbar active link
$(document).ready(function () {
    var currentUrl = window.location.pathname;
    $('.navbar-nav .nav-link').each(function () {
        if ($(this).attr('href') === currentUrl) {
            $(this).addClass('active');
        }
    });
});

// ===== CART UPDATE HELPER =====
function updateCartTotals(data, cartItem = null, price = null) {
    if (data.amount !== undefined) {
        $('#subtotal').text('₹'+parseFloat(data.amount).toFixed(2));
        $('#total').text('₹' + parseFloat(data.totalamount).toFixed(2));

        if ($('#gst').length) {
            const gst = (parseFloat(data.amount) * 0.05).toFixed(2);
            $('#gst').text('₹' + gst);
        }
    }

    if (cartItem && price && data.quantity) {
        const itemTotal = price * data.quantity;
        cartItem.find('.item-total-amount').text(itemTotal.toFixed(2));
    }

    if (data.totalitem !== undefined) {
        $('#mycart').text(data.totalitem || '');
    }
}

// ===== HELPER: ESCAPE HTML =====
function escapeHtml(str) {
    if (str === null || str === undefined) {
        return '';
    }
    var stringValue = String(str);
    return stringValue
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ===== ADDRESS MANAGEMENT FUNCTIONS =====

/**
 * LOAD ADDRESSES FROM SERVER
 */
function loadAddressList() {
    console.log('Loading address list...');
    showLoading();

    $.ajax({
        type: "GET",
        url: "/get-addresses/",
        dataType: "json",
        success: function (response) {
            console.log('Addresses received:', response);

            if (response.success) {
                if (response.addresses && response.addresses.length > 0) {
                    renderAddressList(response.addresses);
                    updateAddressCount(response.count);
                } else {
                    showEmptyAddressMessage();
                }
            } else {
                showNotification('Failed to load addresses: ' + (response.error || 'Unknown error'), 'error');
            }
        },
        error: function (xhr, status, error) {
            console.error('Error loading addresses:', xhr, status, error);
            showNotification('Could not load addresses. Please refresh the page.', 'error');
        },
        complete: function () {
            hideLoading();
        }
    });
}

/**
 * RENDER ADDRESS CARDS DYNAMICALLY
 */
function renderAddressList(addresses) {
    console.log('Rendering addresses:', addresses);
    var container = $('#addressContainer');

    // Clear existing content
    container.empty();

    // Create row container
    var rowDiv = $('<div class="row g-4"></div>');

    // Loop through each address and create card
    addresses.forEach(function (address, index) {
        var addressCard = createAddressCard(address, index + 1);
        rowDiv.append(addressCard);
    });

    container.append(rowDiv);

    // Re-bind event handlers for dynamically created elements
    bindAddressEvents();

    console.log('Rendered ' + addresses.length + ' addresses');
}

/**
 * CREATE HTML FOR SINGLE ADDRESS CARD
 */
function createAddressCard(address, counter) {
    var addressId = address.id || 'unknown';
    var addressName = address.name || 'No Name';
    var addressLocality = address.locality || '';
    var addressCity = address.city || '';
    var addressState = address.state || '';
    var addressMobile = address.mobile || '';
    var addressEmail = address.email || '';
    var isDefault = address.is_default === true;

    var defaultBadge = isDefault ?
        '<span class="badge bg-success default-badge ms-2">Default</span>' : '';

    var defaultChecked = isDefault ? 'checked' : '';

    // Escape all user-provided content
    var escapedName = escapeHtml(addressName);
    var escapedLocality = escapeHtml(addressLocality);
    var escapedCity = escapeHtml(addressCity);
    var escapedState = escapeHtml(addressState);
    var escapedMobile = escapeHtml(addressMobile);
    var escapedEmail = escapeHtml(addressEmail);

    var card = $(`
        <div class="col-md-6">
            <div class="address-card card border-0 shadow-sm h-100" id="address-${addressId}" data-address-id="${addressId}">
                <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-primary me-2">Address ${counter}</span>
                        ${defaultBadge}
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-link text-dark p-0" type="button" data-bs-toggle="dropdown">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li>
                                <a class="dropdown-item" href="/updateaddress/${addressId}">
                                    <i class="fas fa-edit me-2 text-primary"></i>Edit
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item text-danger delete-address" href="#" data-address-id="${addressId}" data-address-name="${escapedName}">
                                    <i class="fas fa-trash-alt me-2"></i>Delete
                                </a>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <a class="dropdown-item set-default-address" href="#" data-address-id="${addressId}">
                                    <i class="fas fa-check-circle me-2 text-success"></i>Set as Default
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
                <div class="card-body">
                    <div class="address-details">
                        <h6 class="fw-bold mb-3 text-black">${escapedName}</h6>
                        <div class="detail-item mb-2">
                            <i class="fas fa-map-pin text-muted me-2" style="width: 20px"></i>
                            <span>${escapedLocality}${escapedLocality && escapedCity ? ', ' : ''}${escapedCity}</span>
                        </div>
                        <div class="detail-item mb-2">
                            <i class="fas fa-globe text-muted me-2" style="width: 20px"></i>
                            <span>${escapedState}</span>
                        </div>
                        <div class="detail-item mb-2">
                            <i class="fas fa-phone-alt text-muted me-2" style="width: 20px"></i>
                            <span>${escapedMobile}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-envelope text-muted me-2" style="width: 20px"></i>
                            <span>${escapedEmail}</span>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-white py-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="form-check">
                            <input class="form-check-input default-address-radio" type="radio" name="defaultAddress" id="default${addressId}" ${defaultChecked} data-address-id="${addressId}">
                            <label class="form-check-label small" for="default${addressId}">Default Address</label>
                        </div>
                        <div class="action-buttons">
                            <a href="/updateaddress/${addressId}" class="btn btn-sm btn-outline-primary me-1">
                                <i class="fas fa-edit"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger delete-address" data-address-id="${addressId}" data-address-name="${escapedName}">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);

    return card;
}

/**
 * SHOW EMPTY ADDRESS MESSAGE
 */
function showEmptyAddressMessage() {
    $('#addressContainer').html(`
        <div class="empty-state text-center py-5" id="emptyAddressState">
            <div class="empty-state-icon mb-4">
                <i class="fas fa-map-marked-alt fa-5x text-muted"></i>
            </div>
            <h5 class="fw-bold mb-3">No Addresses Found</h5>
            <p class="text-muted mb-4">You haven't added any delivery addresses yet.</p>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addAddressModal">
                <i class="fas fa-plus me-2"></i>Add Your First Address
            </button>
        </div>
    `);
}

/**
 * UPDATE ADDRESS COUNT BADGE
 */
function updateAddressCount(count) {
    $('.address-count').text(count);
    $('.badge.bg-primary.rounded-pill.ms-auto').text(count);
}

/**
 * BIND EVENT HANDLERS FOR ADDRESS ACTIONS
 */
function bindAddressEvents() {
    // Delete address handler
    $('.delete-address').off('click').on('click', function (e) {
        e.preventDefault();
        var addressId = $(this).data('address-id');
        var addressName = $(this).data('address-name');

        $('#deleteAddressName').text('Address for: ' + addressName);
        $('#confirmDeleteBtn').data('address-id', addressId);

        var deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        deleteModal.show();
    });

    // Set default address from dropdown
    $('.set-default-address').off('click').on('click', function (e) {
        e.preventDefault();
        var addressId = $(this).data('address-id');
        setDefaultAddress(addressId);
    });

    // Set default address from radio button
    $('.default-address-radio').off('change').on('change', function () {
        var addressId = $(this).data('address-id');
        setDefaultAddress(addressId);
    });
}

/**
 * SAVE NEW ADDRESS
 */
function saveNewAddress() {
    var formData = {
        'name': $('#addressName').val(),
        'mobile': $('#addressMobile').val(),
        'email': $('#addressEmail').val(),
        'locality': $('#addressLocality').val(),
        'city': $('#addressCity').val(),
        'state': $('#addressState').val(),
        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
    };

    // Validate mobile number
    if (!/^\d{10}$/.test(formData.mobile)) {
        showNotification('Please enter a valid 10-digit mobile number', 'error');
        return false;
    }

    // Validate email
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        showNotification('Please enter a valid email address', 'error');
        return false;
    }

    // Check all required fields
    var requiredFields = ['name', 'mobile', 'email', 'locality', 'city', 'state'];
    for (var i = 0; i < requiredFields.length; i++) {
        var field = requiredFields[i];
        if (!formData[field] || formData[field].trim() === '') {
            showNotification('Please fill all fields', 'error');
            return false;
        }
    }

    // Show loading state
    var saveBtn = $('#saveAddressBtn');
    var originalText = saveBtn.html();
    saveBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...').prop('disabled', true);

    console.log('Saving address:', formData);

    $.ajax({
        type: "POST",
        url: "/profile/",
        data: formData,
        success: function (response) {
            console.log('Save success:', response);
            showNotification('Address added successfully!', 'success');

            // Close modal
            var modal = bootstrap.Modal.getInstance(document.getElementById('addAddressModal'));
            if (modal) modal.hide();

            // Clear form
            $('#addAddressForm')[0].reset();

            // Reload address list to show new address
            setTimeout(function () {
                loadAddressList();
            }, 500);
        },
        error: function (xhr) {
            console.error('Save error:', xhr);
            var errorMsg = 'Error saving address. Please try again.';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            showNotification(errorMsg, 'error');
            saveBtn.html(originalText).prop('disabled', false);
        }
    });
    return false;
}

/**
 * SET DEFAULT ADDRESS
 */
function setDefaultAddress(addressId) {
    showLoading();

    $.ajax({
        type: "POST",
        url: "/set-default-address/",
        data: {
            'address_id': addressId,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').first().val()
        },
        success: function (response) {
            if (response.success) {
                // Update UI - remove default badge from all, add to selected
                $('.address-card').each(function () {
                    var card = $(this);
                    var defaultBadge = card.find('.default-badge');
                    var radio = card.find('.default-address-radio');

                    if (card.attr('id') === 'address-' + addressId) {
                        if (defaultBadge.length === 0) {
                            card.find('.card-header div').append('<span class="badge bg-success default-badge ms-2">Default</span>');
                        }
                        radio.prop('checked', true);
                    } else {
                        defaultBadge.remove();
                        radio.prop('checked', false);
                    }
                });
                showNotification('Default address updated', 'success');
            } else {
                showNotification('Error setting default address', 'error');
            }
        },
        error: function () {
            showNotification('Error setting default address', 'error');
        },
        complete: function () {
            hideLoading();
        }
    });
}

/**
 * DELETE ADDRESS
 */
function deleteAddressById(addressId) {
    var addressCard = $('#address-' + addressId);
    addressCard.addClass('deleting');

    $.ajax({
        type: "POST",
        url: "/delete-address/",
        data: {
            'address_id': addressId,
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').first().val()
        },
        success: function (response) {
            if (response.success) {
                setTimeout(function () {
                    addressCard.remove();
                    var remainingAddresses = $('.address-card').length;
                    updateAddressCount(remainingAddresses);
                    showNotification('Address deleted successfully', 'success');

                    if (remainingAddresses === 0) {
                        showEmptyAddressMessage();
                    }
                }, 300);

                var deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal'));
                if (deleteModal) deleteModal.hide();
            } else {
                showNotification('Error deleting address', 'error');
                addressCard.removeClass('deleting');
            }
        },
        error: function () {
            showNotification('Error deleting address. Please try again.', 'error');
            addressCard.removeClass('deleting');
        }
    });
}

// ===== DOCUMENT READY INITIALIZATION =====
$(document).ready(function () {
    console.log('Document ready - initializing...');

    // Initialize carousels
    if ($('#slider1, #slider2, #slider3, .product-carousel').length) {
        $('#slider1, #slider2, #slider3, .product-carousel').owlCarousel({
            loop: true,
            margin: 20,
            responsiveClass: true,
            nav: true,
            dots: false,
            autoplay: true,
            autoplayTimeout: 5000,
            autoplayHoverPause: true,
            responsive: {
                0: { items: 1, nav: false },
                576: { items: 2, nav: false },
                768: { items: 3, nav: true },
                992: { items: 4, nav: true },
                1200: { items: 5, nav: true }
            }
        });
    }

    // Initialize tooltips
    if ($('[data-bs-toggle="tooltip"]').length) {
        $('[data-bs-toggle="tooltip"]').tooltip();
    }

    // Profile completion calculation
    if ($('#completionPercentage').length) {
        calculateProfileCompletion();
    }

    // Back to top button
    if (!$('#back-to-top').length) {
        $('body').append(`
            <button id="back-to-top" title="Back to Top" style="display: none; position: fixed; bottom: 20px; right: 20px; z-index: 99; width: 40px; height: 40px; border-radius: 50%; background: #2b5a3a; color: white; border: none; cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <i class="fas fa-arrow-up"></i>
            </button>
        `);
    }

    // Image error handling
    $('img').on('error', function () {
        if (!$(this).hasClass('error-handled')) {
            $(this).addClass('error-handled').attr('src', '/static/app/images/placeholder.jpg');
        }
    });

    // ===== LOAD ADDRESSES ON ADDRESS PAGE =====
    if ($('#addressContainer').length) {
        console.log('Address page detected - loading addresses...');
        loadAddressList();
    }

    // Save address button handler
    $('#saveAddressBtn').off('click').on('click', function (e) {
        e.preventDefault();
        saveNewAddress();
    });

    // Confirm delete button handler
    $('#confirmDeleteBtn').off('click').on('click', function (e) {
        e.preventDefault();
        var addressId = $(this).data('address-id');
        if (addressId) {
            deleteAddressById(addressId);
        }
    });

    // Back to top scroll handler
    $(window).scroll(function () {
        $('#back-to-top').toggle($(this).scrollTop() > 300);
    });

    $(document).on('click', '#back-to-top', function () {
        $('html, body').animate({ scrollTop: 0 }, 300);
    });
});

// ===== CART FUNCTIONALITY =====
$(document).on('click', '.add-to-cart', function (e) {
    e.preventDefault();
    const id = $(this).attr("data-pid");
    const button = $(this);

    $.ajax({
        type: "GET",
        url: "/add-to-cart",
        data: { prod_id: id },
        success: function (data) {
            showNotification('Product added to cart successfully!', 'success');
            updateCartTotals(data);

            button.html('<i class="fas fa-check"></i> Added');
            setTimeout(() => button.html('<i class="fas fa-shopping-cart"></i> Add to Cart'), 2000);
        },
        error: () => showNotification('Error adding product to cart. Please try again.', 'error')
    });
});

$(document).on('click', '.plus-cart', function () {
    const id = $(this).attr("pid");
    const button = $(this);
    const quantitySpan = $(this).siblings('.quantity-value');
    const cartItem = $(this).closest('.cart-item');
    const price = parseFloat(cartItem.data('price'));

    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: { prod_id: id },
        success: function (data) {
            if (data.status === 'success' || data.quantity) {
                quantitySpan.text(data.quantity);
                updateCartTotals(data, cartItem, price);

                button.addClass('btn-success');
                setTimeout(() => button.removeClass('btn-success'), 200);
            } else {
                showNotification('Error: ' + (data.message || 'Unknown error'), 'error');
            }
        },
        error: () => showNotification('Error updating cart. Please try again.', 'error')
    });
});

$(document).on('click', '.minus-cart', function () {
    const id = $(this).attr("pid");
    const quantitySpan = $(this).siblings('.quantity-value');
    const currentQty = parseInt(quantitySpan.text());
    const cartItem = $(this).closest('.cart-item');
    const price = parseFloat(cartItem.data('price'));

    if (currentQty <= 1) {
        showNotification('Minimum quantity is 1', 'warning');
        return;
    }

    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: { prod_id: id },
        success: function (data) {
            if (data.status === 'success' || data.quantity) {
                quantitySpan.text(data.quantity);
                updateCartTotals(data, cartItem, price);
            } else {
                showNotification('Error: ' + (data.message || 'Unknown error'), 'error');
            }
        },
        error: () => showNotification('Error updating cart. Please try again.', 'error')
    });
});

$(document).on('click', '.remove-cart', function () {
    const id = $(this).attr("pid");
    const cartItem = $(this).closest('.cart-item');

    if (confirm('Are you sure you want to remove this item from your cart?')) {
        $.ajax({
            type: "GET",
            url: "/removecart",
            data: { prod_id: id },
            success: function (data) {
                if (data.status === 'success' || data.pcount !== undefined) {
                    cartItem.slideUp(300, function () {
                        $(this).remove();
                        updateCartTotals(data);

                        if (data.pcount === 0) location.reload();
                    });
                    showNotification('Item removed from cart', 'info');
                } else {
                    showNotification('Error: ' + (data.message || 'Unknown error'), 'error');
                }
            },
            error: () => showNotification('Error removing item. Please try again.', 'error')
        });
    }
});

// ===== WISHLIST FUNCTIONALITY =====
$(document).on('click', '.plus-wishlist', function () {
    const id = $(this).attr("pid");
    const button = $(this);

    $.ajax({
        type: "GET",
        url: "/pluswishlist",
        data: { prod_id: id },
        success: function (data) {
            const currentCount = parseInt($('.wishlist-count').text() || 0);
            $('.wishlist-count').text(currentCount + 1);

            button.removeClass('plus-wishlist btn-outline-primary').addClass('minus-wishlist btn-danger')
                .html('<i class="fas fa-heart"></i> Remove from Wishlist');
            showNotification('Added to wishlist!', 'success');
        },
        error: () => showNotification('Error adding to wishlist. Please try again.', 'error')
    });
});

$(document).on('click', '.minus-wishlist', function () {
    const id = $(this).attr("pid");
    const button = $(this);

    $.ajax({
        type: "GET",
        url: "/minuswishlist",
        data: { prod_id: id },
        success: function (data) {
            const currentCount = parseInt($('.wishlist-count').text() || 0);
            $('.wishlist-count').text(Math.max(0, currentCount - 1));

            button.removeClass('minus-wishlist btn-danger').addClass('plus-wishlist btn-outline-primary')
                .html('<i class="far fa-heart"></i> Add to Wishlist');
            showNotification('Removed from wishlist', 'info');
        },
        error: () => showNotification('Error removing from wishlist. Please try again.', 'error')
    });
});

// ===== SEARCH FUNCTIONALITY =====
let searchTimeout;
$(document).on('input', '#search-input', function () {
    clearTimeout(searchTimeout);
    const query = $(this).val();

    if (query.length < 3) {
        $('#search-results').hide();
        return;
    }

    searchTimeout = setTimeout(() => {
        $.ajax({
            type: "GET",
            url: "/search-suggestions/",
            data: { q: query },
            success: function (data) {
                if (data.results && data.results.length > 0) {
                    displaySearchResults(data.results);
                } else {
                    $('#search-results').hide();
                }
            },
            error: () => $('#search-results').hide()
        });
    }, 300);
});

function displaySearchResults(results) {
    console.log('Search results:', results);
}

// ===== QUANTITY INPUT HANDLING =====
$(document).on('change', '.quantity-input', function () {
    let newQty = parseInt($(this).val());
    const maxQty = parseInt($(this).attr('max') || 10);
    const minQty = parseInt($(this).attr('min') || 1);

    if (isNaN(newQty) || newQty < minQty) {
        $(this).val(minQty);
    } else if (newQty > maxQty) {
        $(this).val(maxQty);
        showNotification(`Maximum quantity is ${maxQty}`, 'warning');
    }
});

// ===== PRICE FILTER =====
$(document).on('input', '#priceRange', function () {
    const value = $(this).val();
    $('#priceValue').text('₹' + value);
    filterProductsByPrice(value);
});

function filterProductsByPrice(maxPrice) {
    $('.product-card').each(function () {
        $(this).toggle(parseFloat($(this).data('price')) <= maxPrice);
    });
}

// ===== SORT FUNCTIONALITY =====
$(document).on('change', '#sortBy', function () {
    const sortBy = $(this).val();
    const products = $('.product-card').get();

    products.sort((a, b) => {
        if (sortBy === 'price-low') return $(a).data('price') - $(b).data('price');
        if (sortBy === 'price-high') return $(b).data('price') - $(a).data('price');
        if (sortBy === 'name') return $(a).data('name').localeCompare($(b).data('name'));
        return 0;
    });

    $.each(products, (index, product) => $('#productsGridView').append(product));
});

// ===== FORM VALIDATION =====
$(document).on('submit', 'form', function (e) {
    let isValid = true;
    const form = $(this);

    form.find('[required]').each(function () {
        if (!$(this).val()) {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });

    if (!isValid) {
        e.preventDefault();
        showNotification('Please fill in all required fields', 'warning');
    }
});

// ===== EMAIL VALIDATION =====
$(document).on('blur', 'input[type="email"]', function () {
    const email = $(this).val();
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (email && !regex.test(email)) {
        $(this).addClass('is-invalid').after('<div class="invalid-feedback">Please enter a valid email address</div>');
    } else {
        $(this).removeClass('is-invalid').next('.invalid-feedback').remove();
    }
});

// ===== PHONE NUMBER VALIDATION =====
$(document).on('blur', 'input[type="tel"], input[name="mobile"]', function () {
    const phone = $(this).val();
    const regex = /^[0-9]{10}$/;

    if (phone && !regex.test(phone)) {
        $(this).addClass('is-invalid').after('<div class="invalid-feedback">Please enter a valid 10-digit phone number</div>');
    } else {
        $(this).removeClass('is-invalid').next('.invalid-feedback').remove();
    }
});

// ===== PROFILE IMAGE UPLOAD =====
$(document).on('change', '#profileImageInput', function (e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            $('.avatar-placeholder').html(`<img src="${e.target.result}" class="rounded-circle" width="100" height="100" style="object-fit: cover;">`);
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append('profile_image', file);
        formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').first().val());

        $.ajax({
            type: "POST",
            url: "/upload-profile-image/",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                showNotification('Profile image updated', 'success');
                setTimeout(() => location.reload(), 1000);
            },
            error: function (xhr) {
                showNotification('Error uploading image: ' + (xhr.responseJSON?.error || 'Unknown error'), 'error');
            }
        });
    }
});

// ===== PROFILE COMPLETION CALCULATION =====
function calculateProfileCompletion() {
    const fields = ['#id_name', '#id_mobile', '#id_locality', '#id_city', '#id_state'];
    const completedFields = fields.filter(field => $(field).val() && $(field).val().trim() !== '').length;
    const percentage = Math.round((completedFields / fields.length) * 100);

    $('#completionPercentage').text(percentage + '%');
    $('#completionBar').css('width', percentage + '%');
}
