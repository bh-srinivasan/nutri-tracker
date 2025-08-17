/**
 * Admin Panel JavaScript
 * Handles admin-specific functionality
 */

// Admin namespace
const Admin = {
    users: {},
    foods: {},
    challenges: {}
};

// User Management Functions
Admin.users = {
    // Navigation state to prevent duplicate navigation calls
    isNavigating: false,

    /**
     * Edit user
     */
    edit: async function(userId) {
        try {
            const response = await fetch(`/api/admin/users/${userId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const user = await response.json();
            
            // Populate edit form
            document.getElementById('editUserId').value = user.id;
            document.getElementById('editUserIdDisplay').value = user.user_id || ''; // Show user_id as read-only
            document.getElementById('editUsername').value = user.username || '';
            document.getElementById('editFirstName').value = user.first_name || '';
            document.getElementById('editLastName').value = user.last_name || '';
            document.getElementById('editEmail').value = user.email || '';
            document.getElementById('editIsAdmin').checked = user.is_admin || false;
            document.getElementById('editIsActive').checked = user.is_active !== false; // Default to true if undefined
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
            modal.show();
        } catch (error) {
            console.error('Error fetching user:', error);
            NutriTracker.utils.showToast('Error loading user data: ' + error.message, 'danger');
        }
    },

    /**
     * Toggle user status
     */
    toggleStatus: async function(userId) {
        NutriTracker.ui.confirmAction(
            'Are you sure you want to change this user\'s status?',
            async () => {
                try {
                    const response = await fetch(`/api/admin/users/${userId}/toggle-status`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        NutriTracker.utils.showToast('User status updated successfully', 'success');
                        location.reload(); // Refresh to show updated status
                    } else {
                        throw new Error('Failed to update user status');
                    }
                } catch (error) {
                    console.error('Error toggling user status:', error);
                    NutriTracker.utils.showToast('Error updating user status', 'danger');
                }
            }
        );
    },

    /**
     * Submit add user form
     */
    submitAddForm: async function(formData) {
        // Enhanced validation for Add User form
        const validationErrors = Admin.users.validateAddUserForm(formData);
        if (validationErrors.length > 0) {
            NutriTracker.utils.showToast(validationErrors[0], 'danger');
            return;
        }
        
        // Get and sanitize form values
        const userId = Admin.users.sanitizeInput(formData.get('user_id'));
        const email = Admin.users.sanitizeInput(formData.get('email'));
        const firstName = Admin.users.sanitizeInput(formData.get('first_name'));
        const lastName = Admin.users.sanitizeInput(formData.get('last_name'));
        const password = formData.get('password'); // Don't sanitize password
        
        try {
            // Prepare sanitized data
            const requestData = {
                user_id: userId.trim(),
                email: email && email.trim() ? email.trim() : null, // Handle optional email - send null instead of empty string
                first_name: firstName.trim(),
                last_name: lastName.trim(),
                password: password,
                is_admin: formData.get('is_admin') === 'on'
            };
            
            const response = await fetch('/api/admin/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            });
            
            if (response.ok) {
                NutriTracker.utils.showToast('User added successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
                location.reload();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to add user');
            }
        } catch (error) {
            console.error('Error adding user:', error);
            NutriTracker.utils.showToast(error.message || 'Error adding user', 'danger');
        }
    },

    /**
     * Enhanced form validation for Add User form
     */
    validateAddUserForm: function(formData) {
        const errors = [];
        
        // Get form values
        const userId = formData.get('user_id');
        const email = formData.get('email');
        const firstName = formData.get('first_name');
        const lastName = formData.get('last_name');
        const password = formData.get('password');
        
        // Validate user ID (REQUIRED)
        if (!userId || userId.trim().length < 1) {
            errors.push('User ID is required');
        } else if (userId.trim().length > 36) {
            errors.push('User ID must be 36 characters or less');
        } else if (!/^[a-zA-Z0-9\-_]+$/.test(userId.trim())) {
            errors.push('User ID can only contain letters, numbers, hyphens, and underscores');
        }
        
        // Validate email (OPTIONAL - only validate if provided)
        if (email && email.trim()) {
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(email.trim())) {
                errors.push('Please enter a valid email address');
            } else if (email.trim().length > 254) {
                errors.push('Email address is too long');
            }
        }
        
        // Validate first name (REQUIRED)
        if (!firstName || firstName.trim().length < 1) {
            errors.push('First name is required');
        } else if (firstName.trim().length > 50) {
            errors.push('First name must be less than 50 characters');
        } else if (!/^[a-zA-Z\s\-']+$/.test(firstName.trim())) {
            errors.push('First name can only contain letters, spaces, hyphens, and apostrophes');
        }
        
        // Validate last name (REQUIRED)
        if (!lastName || lastName.trim().length < 1) {
            errors.push('Last name is required');
        } else if (lastName.trim().length > 50) {
            errors.push('Last name must be less than 50 characters');
        } else if (!/^[a-zA-Z\s\-']+$/.test(lastName.trim())) {
            errors.push('Last name can only contain letters, spaces, hyphens, and apostrophes');
        }
        
        // Validate password (REQUIRED)
        const passwordErrors = Admin.users.validatePassword(password);
        errors.push(...passwordErrors);
        
        return errors;
    },

    /**
     * Enhanced form validation with comprehensive checks and UX indicators
     */
    validateEditUserForm: function(formData) {
        const errors = [];
        
        // Get form values
        const username = formData.get('username');
        const email = formData.get('email');
        const firstName = formData.get('first_name');
        const lastName = formData.get('last_name');
        
        // Clear previous validation indicators
        Admin.users.clearValidationIndicators();
        
        // Validate username (REQUIRED)
        if (!username || username.trim().length < 3) {
            errors.push('Username must be at least 3 characters');
            Admin.users.showFieldError('editUsername', 'Username is required (minimum 3 characters)');
        } else if (username.trim().length > 50) {
            errors.push('Username must be less than 50 characters');
            Admin.users.showFieldError('editUsername', 'Username must be less than 50 characters');
        } else if (!/^[a-zA-Z0-9_-]+$/.test(username.trim())) {
            errors.push('Username can only contain letters, numbers, underscores, and hyphens');
            Admin.users.showFieldError('editUsername', 'Username can only contain letters, numbers, underscores, and hyphens');
        } else {
            Admin.users.showFieldSuccess('editUsername');
        }
        
        // Validate email (OPTIONAL - only validate if provided)
        if (email && email.trim()) {
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(email.trim())) {
                errors.push('Please enter a valid email address');
                Admin.users.showFieldError('editEmail', 'Please enter a valid email address');
            } else if (email.trim().length > 254) {
                errors.push('Email address is too long');
                Admin.users.showFieldError('editEmail', 'Email address is too long');
            } else {
                Admin.users.showFieldSuccess('editEmail');
            }
        } else {
            // Email is optional - show neutral state
            Admin.users.showFieldNeutral('editEmail');
        }
        
        // Validate first name (REQUIRED)
        if (!firstName || firstName.trim().length < 1) {
            errors.push('First name is required');
            Admin.users.showFieldError('editFirstName', 'First name is required');
        } else if (firstName.trim().length > 50) {
            errors.push('First name must be less than 50 characters');
            Admin.users.showFieldError('editFirstName', 'First name must be less than 50 characters');
        } else if (!/^[a-zA-Z\s\-']+$/.test(firstName.trim())) {
            errors.push('First name can only contain letters, spaces, hyphens, and apostrophes');
            Admin.users.showFieldError('editFirstName', 'First name can only contain letters, spaces, hyphens, and apostrophes');
        } else {
            Admin.users.showFieldSuccess('editFirstName');
        }
        
        // Validate last name (REQUIRED)
        if (!lastName || lastName.trim().length < 1) {
            errors.push('Last name is required');
            Admin.users.showFieldError('editLastName', 'Last name is required');
        } else if (lastName.trim().length > 50) {
            errors.push('Last name must be less than 50 characters');
            Admin.users.showFieldError('editLastName', 'Last name must be less than 50 characters');
        } else if (!/^[a-zA-Z\s\-']+$/.test(lastName.trim())) {
            errors.push('Last name can only contain letters, spaces, hyphens, and apostrophes');
            Admin.users.showFieldError('editLastName', 'Last name can only contain letters, spaces, hyphens, and apostrophes');
        } else {
            Admin.users.showFieldSuccess('editLastName');
        }
        
        return errors;
    },

    /**
     * UI Validation Indicator Functions
     */
    clearValidationIndicators: function() {
        const fields = ['editUsername', 'editEmail', 'editFirstName', 'editLastName'];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.classList.remove('is-valid', 'is-invalid');
                // Remove any existing feedback elements
                const feedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
                if (feedback) {
                    feedback.remove();
                }
            }
        });
    },
    
    showFieldError: function(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            
            // Remove existing feedback
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            // Add error feedback
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            field.parentNode.appendChild(feedback);
        }
    },
    
    showFieldSuccess: function(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            
            // Remove existing feedback
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            // Add success feedback
            const feedback = document.createElement('div');
            feedback.className = 'valid-feedback';
            feedback.textContent = '✓ Valid';
            field.parentNode.appendChild(feedback);
        }
    },
    
    showFieldNeutral: function(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.remove('is-valid', 'is-invalid');
            
            // Remove existing feedback
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
        }
    },

    /**
     * Add visual indicators to form fields (required/optional)
     */
    initializeFormFieldIndicators: function() {
        // Add required indicators for Edit User form
        const editRequiredFields = [
            { id: 'editUsername', label: 'Username' },
            { id: 'editFirstName', label: 'First Name' },
            { id: 'editLastName', label: 'Last Name' }
        ];
        
        const editOptionalFields = [
            { id: 'editEmail', label: 'Email' }
        ];
        
        editRequiredFields.forEach(field => {
            Admin.users.addRequiredIndicator(field.id, field.label);
        });
        
        editOptionalFields.forEach(field => {
            Admin.users.addOptionalIndicator(field.id, field.label);
        });
        
        // Add required indicators for Add User form
        const addRequiredFields = [
            { id: 'firstName', label: 'First Name' },
            { id: 'lastName', label: 'Last Name' },
            { id: 'password', label: 'Password' }
        ];
        
        const addOptionalFields = [
            { id: 'email', label: 'Email' }
        ];
        
        addRequiredFields.forEach(field => {
            Admin.users.addRequiredIndicator(field.id, field.label);
        });
        
        addOptionalFields.forEach(field => {
            Admin.users.addOptionalIndicator(field.id, field.label);
        });
    },
    
    addRequiredIndicator: function(fieldId, labelText) {
        const field = document.getElementById(fieldId);
        if (field) {
            const label = document.querySelector(`label[for="${fieldId}"]`);
            if (label) {
                // Add asterisk if not already present
                if (!label.textContent.includes('*')) {
                    label.innerHTML = `${labelText} <span class="text-danger">*</span>`;
                }
                // Add title attribute for accessibility
                label.title = 'Required field';
            }
        }
    },
    
    addOptionalIndicator: function(fieldId, labelText) {
        const field = document.getElementById(fieldId);
        if (field) {
            const label = document.querySelector(`label[for="${fieldId}"]`);
            if (label) {
                // Add optional indicator
                label.innerHTML = `${labelText} <span class="text-muted small">(optional)</span>`;
                // Add title attribute for accessibility
                label.title = 'Optional field';
            }
        }
    },

    /**
     * Modal close and navigation handlers
     */
    handleModalClose: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            bootstrap.Modal.getInstance(modal)?.hide();
            
            // Navigate back to Manage Users page after modal closes
            setTimeout(() => {
                Admin.users.navigateBackToManageUsers();
            }, 300); // Small delay to allow modal close animation
        }
    },

    /**
     * Initialize modal event listeners for proper navigation
     */
    initializeModalEventListeners: function() {
        // Edit User Modal
        const editUserModal = document.getElementById('editUserModal');
        if (editUserModal) {
            // Handle close button clicks
            const closeButtons = editUserModal.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
            closeButtons.forEach(button => {
                button.addEventListener('click', () => {
                    Admin.users.handleModalClose('editUserModal');
                });
            });
            
            // Handle modal hide event (when closed by any means)
            editUserModal.addEventListener('hidden.bs.modal', () => {
                // Clear validation indicators when modal is closed
                Admin.users.clearValidationIndicators();
                
                // Navigate back if not already navigating
                if (!Admin.users.isNavigating) {
                    Admin.users.navigateBackToManageUsers();
                }
            });
        }
        
        // Password Reset Modal
        const resetPasswordModal = document.getElementById('resetPasswordModal');
        if (resetPasswordModal) {
            const closeButtons = resetPasswordModal.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
            closeButtons.forEach(button => {
                button.addEventListener('click', () => {
                    Admin.users.handleModalClose('resetPasswordModal');
                });
            });
            
            resetPasswordModal.addEventListener('hidden.bs.modal', () => {
                // Clear password form when modal is closed
                const resetForm = document.getElementById('resetPasswordForm');
                if (resetForm) {
                    resetForm.reset();
                }
                
                // Navigate back if not already navigating
                if (!Admin.users.isNavigating) {
                    Admin.users.navigateBackToManageUsers();
                }
            });
        }
    },

    /**
     * Enhanced password validation with better UX
     */
    validatePassword: function(password) {
        const errors = [];
        
        if (!password) {
            errors.push('Password is required');
            return errors;
        }
        
        if (password.length < 8) {
            errors.push('Password must be at least 8 characters long');
        }
        
        if (password.length > 128) {
            errors.push('Password is too long');
        }
        
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        const missing = [];
        if (!hasUpper) missing.push('uppercase letter');
        if (!hasLower) missing.push('lowercase letter');
        if (!hasDigit) missing.push('number');
        if (!hasSpecial) missing.push('special character');
        
        if (missing.length > 0) {
            errors.push(`Password must contain at least one: ${missing.join(', ')}`);
        }
        
        return errors;
    },

    /**
     * Validate password reset form (email is NOT required)
     */
    validatePasswordResetForm: function(formData) {
        const errors = [];
        const newPassword = formData.get('new_password');
        
        // Only validate password - email is not required for password reset
        const passwordErrors = Admin.users.validatePassword(newPassword);
        errors.push(...passwordErrors);
        
        return errors;
    },

    /**
     * Sanitize string input to prevent XSS
     */
    sanitizeInput: function(input) {
        if (!input) return '';
        
        // Create a temporary element to leverage browser's HTML escaping
        const temp = document.createElement('div');
        temp.textContent = input;
        return temp.innerHTML.trim();
    },

    /**
     * Submit edit user form with enhanced validation
     */
    submitEditForm: async function(formData) {
        const userId = formData.get('user_id');
        
        // Enhanced validation
        const validationErrors = Admin.users.validateEditUserForm(formData);
        if (validationErrors.length > 0) {
            NutriTracker.utils.showToast(validationErrors[0], 'danger');
            return;
        }
        
        // Get and sanitize form values
        const username = Admin.users.sanitizeInput(formData.get('username'));
        const email = Admin.users.sanitizeInput(formData.get('email'));
        const firstName = Admin.users.sanitizeInput(formData.get('first_name'));
        const lastName = Admin.users.sanitizeInput(formData.get('last_name'));
        
        try {
            // Prepare sanitized data
            const requestData = {
                username: username.trim(),
                email: email && email.trim() ? email.trim() : null, // Handle optional email - send null instead of empty string
                first_name: firstName.trim(),
                last_name: lastName.trim(),
                is_admin: formData.get('is_admin') === 'on',
                is_active: formData.get('is_active') !== null ? formData.get('is_active') === 'on' : true
            };
            
            const response = await fetch(`/api/admin/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Set navigation flag to prevent duplicate navigation
                Admin.users.isNavigating = true;
                
                NutriTracker.utils.showToast('User updated successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
                
                // Refresh the page to show updated data
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                throw new Error(result.error || 'Failed to update user');
            }
        } catch (error) {
            console.error('Error updating user:', error);
            NutriTracker.utils.showToast(error.message || 'Error updating user', 'danger');
        }
    },

    /**
     * Open password reset modal
     */
    openPasswordResetModal: function(userId, username) {
        console.log('Opening password reset modal for user:', userId, username);
        
        // Set the user ID and username in the modal with null checks
        const resetUserIdElement = document.getElementById('resetUserId');
        const resetUsernameElement = document.getElementById('resetUsername');
        
        if (resetUserIdElement) {
            resetUserIdElement.value = userId;
            console.log('Set resetUserId to:', userId);
        } else {
            console.error('Element with ID "resetUserId" not found');
        }
        
        if (resetUsernameElement) {
            resetUsernameElement.textContent = username;
            console.log('Set resetUsername to:', username);
        } else {
            console.error('Element with ID "resetUsername" not found');
        }
        
        // Clear the form
        const resetPasswordForm = document.getElementById('resetPasswordForm');
        if (resetPasswordForm) {
            resetPasswordForm.reset();
        }
        
        // Reset password strength meter
        const strengthBar = document.getElementById('passwordStrength');
        const strengthText = document.getElementById('passwordStrengthText');
        if (strengthBar) {
            strengthBar.style.width = '0%';
            strengthBar.className = 'progress-bar';
        }
        if (strengthText) {
            strengthText.textContent = 'Enter a password to see strength';
            strengthText.className = 'form-text text-muted';
        }
        
        // Reset requirements checklist
        const requirements = ['req-length', 'req-uppercase', 'req-lowercase', 'req-number', 'req-special'];
        requirements.forEach(reqId => {
            const element = document.getElementById(reqId);
            if (element) {
                const icon = element.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-times text-danger';
                }
                element.classList.remove('text-success');
                element.classList.add('text-danger');
            }
        });
        
        // Disable submit button
        const resetBtn = document.getElementById('resetPasswordBtn');
        if (resetBtn) {
            resetBtn.disabled = true;
        }
        
        // Show the modal
        const modalElement = document.getElementById('resetPasswordModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else {
            console.error('Reset password modal element not found');
            NutriTracker.utils.showToast('Error: Password reset modal not found', 'danger');
        }
    },

    /**
     * Submit password reset form with enhanced validation
     */
    submitPasswordReset: async function(event) {
        event.preventDefault();
        
        const form = document.getElementById('resetPasswordForm');
        const formData = new FormData(form);
        const userId = formData.get('user_id');
        const newPassword = formData.get('new_password');
        
        // Enhanced password validation (no email validation needed)
        const validationErrors = Admin.users.validatePasswordResetForm(formData);
        if (validationErrors.length > 0) {
            NutriTracker.utils.showToast(validationErrors[0], 'danger');
            return;
        }
        
        try {
            const response = await fetch(`/api/admin/users/${userId}/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    new_password: newPassword
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Set navigation flag to prevent duplicate navigation
                Admin.users.isNavigating = true;
                
                // Enhanced admin flow - immediate success feedback
                Admin.users.handlePasswordResetSuccess(userId, result.username, newPassword);
            } else {
                throw new Error(result.message || 'Failed to reset password');
            }
        } catch (error) {
            console.error('Error resetting password:', error);
            NutriTracker.utils.showToast(error.message || 'Error resetting password', 'danger');
        }
    },

    /**
     * Handle successful password reset with toast and auto-navigation
     */
    handlePasswordResetSuccess: function(userId, username, newPassword) {
        // Close the reset modal immediately
        const resetModalElement = document.getElementById('resetPasswordModal');
        if (resetModalElement) {
            bootstrap.Modal.getInstance(resetModalElement).hide();
        }
        
        // Log the action for audit purposes
        console.log(`Admin password reset completed for user: ${username} (ID: ${userId}) at ${new Date().toISOString()}`);
        
        // Show success toast and auto-navigate back to Manage Users
        Admin.users.showSuccessToastAndNavigate(userId, username);
    },

    /**
     * Show success toast and auto-navigate back to Manage Users
     */
    showSuccessToastAndNavigate: function(userId, username) {
        // Create success toast message
        const toastMessage = `
            <div class="d-flex align-items-center">
                <i class="fas fa-check-circle text-success me-2"></i>
                <div>
                    <strong>Password reset successfully</strong><br>
                    <small>Password for ${username} has been updated. Returning to user list...</small>
                </div>
            </div>
        `;
        
        // Show toast notification that will auto-dismiss
        NutriTracker.utils.showToast(toastMessage, 'success', 2000);
        
        // Add visual feedback to the user row if visible
        Admin.users.highlightUserRow(userId);
        
        // Auto-navigate back to Manage Users after 2 seconds
        setTimeout(() => {
            Admin.users.navigateBackToManageUsers();
        }, 2000);
    },

    /**
     * Highlight the user row that was just updated
     */
    highlightUserRow: function(userId) {
        const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
        if (userRow) {
            // Add gentle highlight animation
            userRow.style.cssText = `
                background: linear-gradient(90deg, rgba(40, 167, 69, 0.1), transparent);
                transition: all 0.3s ease;
                border-left: 4px solid #28a745;
            `;
            
            // Scroll the row into view if needed
            userRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Remove highlight after 2.5 seconds
            setTimeout(() => {
                userRow.style.cssText = 'transition: all 0.5s ease;';
                setTimeout(() => {
                    userRow.style.cssText = '';
                }, 500);
            }, 2500);
        }
    },

    /**
     * Navigate back to Manage Users page with navigation lock
     */
    navigateBackToManageUsers: function() {
        // Prevent multiple simultaneous navigation calls
        if (Admin.users.isNavigating) {
            return;
        }
        
        Admin.users.isNavigating = true;
        
        // Get current URL to preserve parameters
        const currentUrl = new URL(window.location);
        
        // If we're already on the manage users page, just reload to refresh
        if (currentUrl.pathname.includes('/admin/users') || currentUrl.pathname === '/admin/users') {
            // Preserve query parameters (filters, search, pagination) and refresh
            window.location.reload();
        } else {
            // Navigate to manage users page
            const manageUsersUrl = new URL('/admin/users', window.location.origin);
            
            // Copy over relevant query parameters if they exist
            const relevantParams = ['search', 'status', 'role', 'show_details', 'page'];
            relevantParams.forEach(param => {
                if (currentUrl.searchParams.has(param)) {
                    manageUsersUrl.searchParams.set(param, currentUrl.searchParams.get(param));
                }
            });
            
            window.location.href = manageUsersUrl.toString();
        }
    },

    /**
     * Generate a new UUID for user ID
     */
    generateUserId: function() {
        // Generate UUID v4
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    /**
     * Check if user ID is available (real-time validation)
     */
    checkUserIdAvailable: async function(userId) {
        if (!userId || userId.trim().length === 0) {
            return { available: false, error: 'User ID is required' };
        }

        try {
            const response = await fetch(`/api/admin/users/check-user-id?user_id=${encodeURIComponent(userId.trim())}`);
            const result = await response.json();
            
            if (response.ok) {
                return result;
            } else {
                return { available: false, error: result.error || 'Error checking User ID' };
            }
        } catch (error) {
            console.error('Error checking user ID:', error);
            return { available: false, error: 'Network error checking User ID' };
        }
    },

    /**
     * Validate user ID field and show feedback
     */
    validateUserIdField: async function(userIdElement) {
        const userId = userIdElement.value.trim();
        const feedbackElement = document.getElementById('userIdFeedback');
        
        // Clear previous validation state
        userIdElement.classList.remove('is-valid', 'is-invalid');
        feedbackElement.textContent = '';
        
        if (!userId) {
            userIdElement.classList.add('is-invalid');
            feedbackElement.textContent = 'User ID is required';
            return false;
        }

        // Check format
        if (userId.length > 36) {
            userIdElement.classList.add('is-invalid');
            feedbackElement.textContent = 'User ID must be 36 characters or less';
            return false;
        }

        if (!/^[a-zA-Z0-9\-_]+$/.test(userId)) {
            userIdElement.classList.add('is-invalid');
            feedbackElement.textContent = 'User ID can only contain letters, numbers, hyphens, and underscores';
            return false;
        }

        // Check availability
        const result = await Admin.users.checkUserIdAvailable(userId);
        
        if (!result.available) {
            userIdElement.classList.add('is-invalid');
            feedbackElement.textContent = result.error || 'User ID is not available';
            return false;
        }

        userIdElement.classList.add('is-valid');
        feedbackElement.textContent = '';
        return true;
    },

};

// Food Management Functions
Admin.foods = {
    /**
     * Edit food
     */
    edit: function(foodId) {
        // Redirect to existing edit food page
        window.location.href = `/admin/foods/${foodId}/edit`;
    },

    /**
     * Toggle food verification status
     */
    toggleStatus: async function(foodId) {
        NutriTracker.ui.confirmAction(
            'Are you sure you want to change this food\'s verification status?',
            async () => {
                try {
                    const response = await fetch(`/api/admin/foods/${foodId}/toggle-status`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        NutriTracker.utils.showToast('Food status updated successfully', 'success');
                        location.reload();
                    } else {
                        throw new Error('Failed to update food status');
                    }
                } catch (error) {
                    console.error('Error toggling food status:', error);
                    NutriTracker.utils.showToast('Error updating food status', 'danger');
                }
            }
        );
    },

    /**
     * Delete food
     */
    delete: async function(foodId) {
        NutriTracker.ui.confirmAction(
            'Are you sure you want to delete this food? This action cannot be undone.',
            async () => {
                try {
                    const response = await fetch(`/api/admin/foods/${foodId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        NutriTracker.utils.showToast('Food deleted successfully', 'success');
                        location.reload();
                    } else {
                        throw new Error('Failed to delete food');
                    }
                } catch (error) {
                    console.error('Error deleting food:', error);
                    NutriTracker.utils.showToast('Error deleting food', 'danger');
                }
            }
        );
    },

    /**
     * Submit add food form
     */
    submitAddForm: async function(formData) {
        try {
            const response = await fetch('/api/admin/foods', {
                method: 'POST',
                body: formData // FormData object for file upload
            });
            
            if (response.ok) {
                NutriTracker.utils.showToast('Food added successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('addFoodModal')).hide();
                location.reload();
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to add food');
            }
        } catch (error) {
            console.error('Error adding food:', error);
            NutriTracker.utils.showToast(error.message || 'Error adding food', 'danger');
        }
    },

    /**
     * Submit bulk upload form
     */
    submitBulkUpload: async function(formData) {
        try {
            const response = await fetch('/api/admin/foods/bulk-upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                NutriTracker.utils.showToast(
                    `Bulk upload completed. ${result.success_count} foods added, ${result.error_count} errors.`,
                    result.error_count > 0 ? 'warning' : 'success'
                );
                bootstrap.Modal.getInstance(document.getElementById('bulkUploadModal')).hide();
                location.reload();
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Bulk upload failed');
            }
        } catch (error) {
            console.error('Error with bulk upload:', error);
            NutriTracker.utils.showToast(error.message || 'Bulk upload failed', 'danger');
        }
    },

    /**
     * Food Servings Management Module
     */
    servings: {
        // Validation constants
        validationRules: {
            servingName: { min: 2, max: 50 },
            unit: { min: 1, max: 20 },
            gramsPerUnit: { min: 0.1, max: 2000 }
        },

        /**
         * Bind events for serving management
         */
        bindEvents: function() {
            // Guard to prevent double binding
            if (Admin.foods.servings._bound) return;
            Admin.foods.servings._bound = true;

            // Bind add serving form submit
            const addServingForm = document.getElementById('add-serving-form');
            if (addServingForm) {
                addServingForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    const foodId = this.querySelector('[data-food-id]').getAttribute('data-food-id');
                    Admin.foods.servings.add(foodId, this);
                });

                // Add real-time validation for add form
                const addNameField = addServingForm.querySelector('input[name="serving_name"]');
                const addUnitField = addServingForm.querySelector('input[name="unit"]');
                const addGramsField = addServingForm.querySelector('input[name="grams_per_unit"]');

                if (addNameField) {
                    addNameField.addEventListener('input', () => Admin.foods.servings.validateField(addNameField, 'name'));
                    addNameField.addEventListener('blur', () => Admin.foods.servings.validateField(addNameField, 'name'));
                }
                if (addUnitField) {
                    addUnitField.addEventListener('input', () => Admin.foods.servings.validateField(addUnitField, 'unit'));
                    addUnitField.addEventListener('blur', () => Admin.foods.servings.validateField(addUnitField, 'unit'));
                }
                if (addGramsField) {
                    addGramsField.addEventListener('input', () => Admin.foods.servings.validateField(addGramsField, 'grams'));
                    addGramsField.addEventListener('blur', () => Admin.foods.servings.validateField(addGramsField, 'grams'));
                }
            }

            // Single document-level click listener using .closest() and button classes
            document.addEventListener('click', function(e) {
                // Delete button
                const delBtn = e.target.closest('.delete-serving-btn');
                if (delBtn) {
                    e.preventDefault();
                    const servingId = delBtn.dataset.servingId || delBtn.getAttribute('data-serving-id');
                    const foodId = document.querySelector('[data-food-id]')?.getAttribute('data-food-id');
                    if (servingId && foodId) {
                        Admin.foods.servings.remove(foodId, servingId);
                    }
                    return;
                }

                // Edit button
                const editBtn = e.target.closest('.edit-serving-btn');
                if (editBtn) {
                    e.preventDefault();
                    const servingId = editBtn.dataset.servingId || editBtn.getAttribute('data-serving-id');
                    const foodId = document.querySelector('[data-food-id]')?.getAttribute('data-food-id');
                    if (servingId && foodId) {
                        Admin.foods.servings.edit(foodId, servingId);
                    }
                    return;
                }

                // Set Default button
                const setBtn = e.target.closest('.set-default-serving-btn');
                if (setBtn) {
                    e.preventDefault();
                    const servingId = setBtn.dataset.servingId || setBtn.getAttribute('data-serving-id');
                    const foodId = document.querySelector('[data-food-id]')?.getAttribute('data-food-id');
                    if (servingId && foodId) {
                        Admin.foods.servings.setDefault(foodId, servingId);
                    }
                    return;
                }

                // Unset Default button
                const unsetBtn = e.target.closest('.unset-default-serving-btn');
                if (unsetBtn) {
                    e.preventDefault();
                    const servingId = unsetBtn.dataset.servingId || unsetBtn.getAttribute('data-serving-id');
                    const foodId = document.querySelector('[data-food-id]')?.getAttribute('data-food-id');
                    if (servingId && foodId) {
                        Admin.foods.servings.unsetDefault(foodId, servingId);
                    }
                    return;
                }
            });
        },

        /**
         * Validate form field
         */
        validateField: function(field, type) {
            const value = field.value.trim();
            let error = null;

            switch(type) {
                case 'name':
                    error = this.validateServingName(value);
                    if (!error && value) {
                        // Check for duplicates if unit field also has value
                        const form = field.closest('form');
                        const unitField = form.querySelector('input[name="unit"]');
                        if (unitField && unitField.value.trim()) {
                            if (this.checkDuplicateServing(value, unitField.value.trim())) {
                                error = 'This serving name and unit combination already exists';
                            }
                        }
                    }
                    break;
                case 'unit':
                    error = this.validateUnit(value);
                    if (!error && value) {
                        // Check for duplicates if name field also has value
                        const form = field.closest('form');
                        const nameField = form.querySelector('input[name="serving_name"]');
                        if (nameField && nameField.value.trim()) {
                            if (this.checkDuplicateServing(nameField.value.trim(), value)) {
                                error = 'This serving name and unit combination already exists';
                            }
                        }
                    }
                    break;
                case 'grams':
                    error = this.validateGramsPerUnit(value);
                    break;
            }

            if (error) {
                this.showFieldError(field, error);
            } else if (value) {
                this.clearFieldError(field);
            }

            return !error;
        },

        /**
         * Validate serving name
         */
        validateServingName: function(name) {
            if (!name || name.length < this.validationRules.servingName.min) {
                return `Serving name must be at least ${this.validationRules.servingName.min} characters`;
            }
            if (name.length > this.validationRules.servingName.max) {
                return `Serving name must be no more than ${this.validationRules.servingName.max} characters`;
            }
            return null;
        },

        /**
         * Validate unit
         */
        validateUnit: function(unit) {
            if (!unit || unit.length < this.validationRules.unit.min) {
                return `Unit must be at least ${this.validationRules.unit.min} character`;
            }
            if (unit.length > this.validationRules.unit.max) {
                return `Unit must be no more than ${this.validationRules.unit.max} characters`;
            }
            return null;
        },

        /**
         * Validate grams per unit
         */
        validateGramsPerUnit: function(grams) {
            const num = parseFloat(grams);
            if (isNaN(num) || num < this.validationRules.gramsPerUnit.min) {
                return `Grams per unit must be at least ${this.validationRules.gramsPerUnit.min}`;
            }
            if (num > this.validationRules.gramsPerUnit.max) {
                return `Grams per unit must be no more than ${this.validationRules.gramsPerUnit.max}`;
            }
            return null;
        },

        /**
         * Check for duplicate serving
         */
        checkDuplicateServing: function(name, unit, currentId = null) {
            const tbody = document.getElementById('servings-body');
            if (!tbody) return false;

            const rows = tbody.querySelectorAll('tr[data-serving-id]');
            for (const row of rows) {
                const rowId = row.getAttribute('data-serving-id');
                if (currentId && rowId === currentId) continue; // Skip current row when editing
                
                const rowName = row.querySelector('.serving-name').textContent.replace('Default', '').trim();
                const rowUnit = row.querySelector('.serving-unit').textContent.trim();
                
                if (rowName.toLowerCase() === name.toLowerCase() && 
                    rowUnit.toLowerCase() === unit.toLowerCase()) {
                    return true;
                }
            }
            return false;
        },

        /**
         * Show field error
         */
        showFieldError: function(field, message) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            
            let feedback = field.parentElement.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentElement.appendChild(feedback);
            }
            feedback.textContent = message;
        },

        /**
         * Clear field error
         */
        clearFieldError: function(field) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            
            const feedback = field.parentElement.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = '';
            }
        },

        /**
         * Add new serving
         */
        add: async function(foodId, formEl) {
            try {
                // Validate all fields first
                const nameField = formEl.querySelector('input[name="serving_name"]');
                const unitField = formEl.querySelector('input[name="unit"]');
                const gramsField = formEl.querySelector('input[name="grams_per_unit"]');

                let hasErrors = false;
                
                if (!this.validateField(nameField, 'name')) hasErrors = true;
                if (!this.validateField(unitField, 'unit')) hasErrors = true;
                if (!this.validateField(gramsField, 'grams')) hasErrors = true;

                // Check for duplicates
                const name = nameField.value.trim();
                const unit = unitField.value.trim();
                if (!hasErrors && this.checkDuplicateServing(name, unit)) {
                    NutriTracker.utils.showToast('This serving name and unit combination already exists', 'danger');
                    return;
                }

                if (hasErrors) {
                    NutriTracker.utils.showToast('Please fix the validation errors above', 'danger');
                    return;
                }

                const formData = new FormData(formEl);
                // Add CSRF token
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                formData.append('csrf_token', csrfToken);

                const response = await fetch(`/admin/add_food_serving`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Success - reload page to show updated servings
                    window.location.reload();
                } else if (response.status === 400) {
                    // Show validation error
                    NutriTracker.utils.showToast(data.message || 'Invalid serving data', 'danger');
                } else {
                    throw new Error(data.message || 'Failed to add serving');
                }
            } catch (error) {
                console.error('Error adding serving:', error);
                NutriTracker.utils.showToast('Failed to add serving', 'danger');
            }
        },

        /**
         * Set serving as default
         */
        setDefault: async function(foodId, servingId) {
            try {
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                
                const response = await fetch(`/admin/foods/${foodId}/servings/${servingId}/set-default`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    this.updateDefaultBadges(servingId);
                    NutriTracker.utils.showToast('Default serving updated!', 'success');
                } else {
                    throw new Error(data.error || 'Failed to set default serving');
                }
            } catch (error) {
                console.error('Error setting default serving:', error);
                NutriTracker.utils.showToast('Failed to set default serving', 'danger');
            }
        },

        /**
         * Unset serving as default
         */
        unsetDefault: async function(foodId, servingId) {
            try {
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                
                const response = await fetch(`/admin/foods/${foodId}/servings/${servingId}/unset-default`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    this.updateDefaultBadges(null); // No serving is default
                    NutriTracker.utils.showToast('Default serving removed. System default (100 g) is now active.', 'success');
                } else {
                    throw new Error(data.error || 'Failed to unset default serving');
                }
            } catch (error) {
                console.error('Error unsetting default serving:', error);
                NutriTracker.utils.showToast('Failed to unset default serving', 'danger');
            }
        },

        /**
         * Edit serving inline
         */
        edit: function(foodId, servingId) {
            const row = document.querySelector(`tr[data-serving-id="${servingId}"]`);
            if (!row) return;

            const nameCell = row.querySelector('.serving-name');
            const unitCell = row.querySelector('.serving-unit');
            const gramsCell = row.querySelector('.serving-grams');

            // Get current values (remove any badges)
            const currentName = nameCell.textContent.replace('Default', '').trim();
            const currentUnit = unitCell.textContent.trim();
            const currentGrams = gramsCell.textContent.trim();

            // Create inline edit form with validation
            nameCell.innerHTML = `
                <input type="text" class="form-control form-control-sm" value="${currentName}" 
                       maxlength="50" data-original="${currentName}">
                <div class="invalid-feedback"></div>
            `;
            unitCell.innerHTML = `
                <input type="text" class="form-control form-control-sm" value="${currentUnit}" 
                       maxlength="20" data-original="${currentUnit}">
                <div class="invalid-feedback"></div>
            `;
            gramsCell.innerHTML = `
                <input type="number" class="form-control form-control-sm" value="${currentGrams}" 
                       step="0.1" min="0.1" max="2000" data-original="${currentGrams}">
                <div class="invalid-feedback"></div>
            `;

            // Add real-time validation to edit fields
            const nameInput = nameCell.querySelector('input');
            const unitInput = unitCell.querySelector('input');
            const gramsInput = gramsCell.querySelector('input');

            nameInput.addEventListener('input', () => this.validateEditField(nameInput, 'name', servingId));
            nameInput.addEventListener('blur', () => this.validateEditField(nameInput, 'name', servingId));
            unitInput.addEventListener('input', () => this.validateEditField(unitInput, 'unit', servingId));
            unitInput.addEventListener('blur', () => this.validateEditField(unitInput, 'unit', servingId));
            gramsInput.addEventListener('input', () => this.validateEditField(gramsInput, 'grams', servingId));
            gramsInput.addEventListener('blur', () => this.validateEditField(gramsInput, 'grams', servingId));

            // Update action buttons
            const actionsCell = row.querySelector('td:last-child .btn-group');
            actionsCell.innerHTML = `
                <button class="btn btn-sm btn-success" onclick="Admin.foods.servings.saveEdit(${foodId}, ${servingId})">
                    <i class="fas fa-save me-1"></i>Save
                </button>
                <button class="btn btn-sm btn-secondary" onclick="Admin.foods.servings.cancelEdit(${servingId}, '${currentName}', '${currentUnit}', '${currentGrams}')">
                    <i class="fas fa-times me-1"></i>Cancel
                </button>
            `;
        },

        /**
         * Validate edit field
         */
        validateEditField: function(field, type, currentId) {
            const value = field.value.trim();
            let error = null;

            switch(type) {
                case 'name':
                    error = this.validateServingName(value);
                    if (!error && value) {
                        // Check for duplicates
                        const row = field.closest('tr');
                        const unitInput = row.querySelector('.serving-unit input');
                        if (unitInput && unitInput.value.trim()) {
                            if (this.checkDuplicateServing(value, unitInput.value.trim(), currentId)) {
                                error = 'This serving name and unit combination already exists';
                            }
                        }
                    }
                    break;
                case 'unit':
                    error = this.validateUnit(value);
                    if (!error && value) {
                        // Check for duplicates
                        const row = field.closest('tr');
                        const nameInput = row.querySelector('.serving-name input');
                        if (nameInput && nameInput.value.trim()) {
                            if (this.checkDuplicateServing(nameInput.value.trim(), value, currentId)) {
                                error = 'This serving name and unit combination already exists';
                            }
                        }
                    }
                    break;
                case 'grams':
                    error = this.validateGramsPerUnit(value);
                    break;
            }

            if (error) {
                this.showFieldError(field, error);
            } else if (value) {
                this.clearFieldError(field);
            }

            return !error;
        },

        /**
         * Save inline edit
         */
        saveEdit: async function(foodId, servingId) {
            const row = document.querySelector(`tr[data-serving-id="${servingId}"]`);
            if (!row) return;

            const nameInput = row.querySelector('.serving-name input');
            const unitInput = row.querySelector('.serving-unit input');
            const gramsInput = row.querySelector('.serving-grams input');

            const servingName = nameInput.value.trim();
            const unit = unitInput.value.trim();
            const gramsPerUnit = gramsInput.value.trim();

            // Validate all fields
            let hasErrors = false;
            
            if (!this.validateEditField(nameInput, 'name', servingId)) hasErrors = true;
            if (!this.validateEditField(unitInput, 'unit', servingId)) hasErrors = true;
            if (!this.validateEditField(gramsInput, 'grams', servingId)) hasErrors = true;

            if (hasErrors) {
                NutriTracker.utils.showToast('Please fix the validation errors', 'danger');
                return;
            }

            try {
                const formData = new FormData();
                formData.append('serving_id', servingId);
                formData.append('serving_name', servingName);
                formData.append('unit', unit);
                formData.append('grams_per_unit', gramsPerUnit);
                formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);

                const response = await fetch('/admin/edit_food_serving', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Update cells with new values
                    row.querySelector('.serving-name').textContent = servingName;
                    row.querySelector('.serving-unit').textContent = unit;
                    row.querySelector('.serving-grams').textContent = gramsPerUnit;

                    // Restore action buttons
                    this.restoreActionButtons(row, servingId);
                    
                    NutriTracker.utils.showToast('Serving updated successfully!', 'success');
                } else {
                    throw new Error(data.message || 'Failed to update serving');
                }
            } catch (error) {
                console.error('Error updating serving:', error);
                NutriTracker.utils.showToast('Failed to update serving', 'danger');
            }
        },

        /**
         * Cancel inline edit
         */
        cancelEdit: function(servingId, originalName, originalUnit, originalGrams) {
            const row = document.querySelector(`tr[data-serving-id="${servingId}"]`);
            if (!row) return;

            // Restore original values
            row.querySelector('.serving-name').textContent = originalName;
            row.querySelector('.serving-unit').textContent = originalUnit;
            row.querySelector('.serving-grams').textContent = originalGrams;

            // Restore action buttons
            this.restoreActionButtons(row, servingId);
        },

        /**
         * Remove serving
         */
        remove: async function(foodId, servingId) {
            console.debug('servings.remove() → foodId=%s, servingId=%s', foodId, servingId);
            
            const row = document.querySelector(`tr[data-serving-id="${servingId}"]`);
            if (!row) return;
            
            // In-flight guard to prevent double execution
            if (row.dataset.deleting === '1') return;
            row.dataset.deleting = '1';

            const servingName = row.querySelector('.serving-name').textContent.replace('Default', '').trim();
            
            if (!confirm(`Are you sure you want to delete the serving "${servingName}"?`)) {
                delete row.dataset.deleting;
                return;
            }

            try {
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                
                const response = await fetch(`/admin/foods/${foodId}/servings/${servingId}/delete`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Remove row from table
                    row.remove();
                    NutriTracker.utils.showToast('Serving deleted successfully!', 'success');
                } else if (response.status === 409) {
                    // Handle conflict - serving is referenced
                    console.debug('delete response: status=%s, data=%o', response.status, data);
                    NutriTracker.utils.showToast(data.error || 'Cannot delete serving as it is used in meal logs', 'warning');
                } else {
                    console.debug('delete response: status=%s, data=%o', response.status, data);
                    throw new Error(data.error || 'Failed to delete serving');
                }
            } catch (error) {
                console.error('Error deleting serving:', error);
                NutriTracker.utils.showToast('Failed to delete serving', 'danger');
            } finally {
                // Clear the guard if the row still exists
                if (row && document.body.contains(row)) {
                    delete row.dataset.deleting;
                }
            }
        },

        /**
         * Save inline edit
         */
        saveEdit: async function(foodId, servingId) {
            const row = document.querySelector(`tr[data-serving-id="${servingId}"]`);
            if (!row) return;

            const nameInput = row.querySelector('.serving-name input');
            const unitInput = row.querySelector('.serving-unit input');
            const gramsInput = row.querySelector('.serving-grams input');

            const servingName = nameInput.value.trim();
            const unit = unitInput.value.trim();
            const gramsPerUnit = gramsInput.value.trim();

            // Validation
            if (!servingName || !unit || !gramsPerUnit) {
                NutriTracker.utils.showToast('All fields are required', 'danger');
                return;
            }

            try {
                const formData = new FormData();
                formData.append('serving_name', servingName);
                formData.append('unit', unit);
                formData.append('grams_per_unit', gramsPerUnit);
                formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);

                const response = await fetch(`/admin/foods/${foodId}/servings/${servingId}/edit`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Update cells with new values
                    row.querySelector('.serving-name').textContent = servingName;
                    row.querySelector('.serving-unit').textContent = unit;
                    row.querySelector('.serving-grams').textContent = gramsPerUnit;

                    // Restore action buttons
                    Admin.foods.servings.restoreActionButtons(row, servingId);
                    
                    NutriTracker.utils.showToast('Serving updated successfully!', 'success');
                } else {
                    throw new Error(data.error || 'Failed to update serving');
                }
            } catch (error) {
                console.error('Error updating serving:', error);
                NutriTracker.utils.showToast('Failed to update serving', 'danger');
            }
        },

        /**
         * Cancel inline edit
         */
        cancelEdit: function(servingId, originalName, originalUnit, originalGrams) {
            const row = document.querySelector(`tr[data-serving-id="${servingId}"]`);
            if (!row) return;

            // Restore original values
            row.querySelector('.serving-name').textContent = originalName;
            row.querySelector('.serving-unit').textContent = originalUnit;
            row.querySelector('.serving-grams').textContent = originalGrams;

            // Restore action buttons
            this.restoreActionButtons(row, servingId);
        },

        /**
         * Helper: Prepend new serving row to table
         */
        prependServingRow: function(serving) {
            const tbody = document.getElementById('servings-body');
            if (!tbody) return;

            // Remove "no servings" row if it exists
            const noServingsRow = document.getElementById('noServingsRow');
            if (noServingsRow) {
                noServingsRow.remove();
            }

            const row = document.createElement('tr');
            row.setAttribute('data-serving-id', serving.id);
            row.innerHTML = `
                <td class="serving-name">${serving.serving_name}</td>
                <td class="serving-unit">${serving.unit}</td>
                <td class="serving-grams">${serving.grams_per_unit}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" 
                            data-serving-id="${serving.id}" title="Set as default">
                        <i class="fas fa-check me-1"></i>Set Default
                    </button>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-secondary edit-serving-btn" 
                                data-serving-id="${serving.id}" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger delete-serving-btn" 
                                data-serving-id="${serving.id}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;

            // Insert after the system default row
            const systemDefaultRow = tbody.querySelector('.table-secondary');
            if (systemDefaultRow) {
                systemDefaultRow.insertAdjacentElement('afterend', row);
            } else {
                tbody.appendChild(row);
            }
        },

        /**
         * Helper: Update default badges and buttons
         */
        updateDefaultBadges: function(defaultServingId) {
            const tbody = document.getElementById('servings-body');
            if (!tbody) return;

            // Update system default (100g row)
            const systemDefaultCell = tbody.querySelector('.table-secondary td:nth-child(4)');
            if (systemDefaultCell) {
                if (defaultServingId === null) {
                    systemDefaultCell.innerHTML = `
                        <span class="badge bg-primary">Default</span>
                        <small class="text-muted d-block">System default</small>
                    `;
                } else {
                    systemDefaultCell.innerHTML = '<span class="text-muted">-</span>';
                }
            }

            // Update all custom servings
            tbody.querySelectorAll('tr[data-serving-id]').forEach(row => {
                const servingId = row.getAttribute('data-serving-id');
                const nameCell = row.querySelector('.serving-name');
                const defaultCell = row.querySelector('td:nth-child(4)');
                
                if (servingId === defaultServingId) {
                    // This serving is now default - add badge to name and update buttons
                    const servingName = nameCell.textContent.trim();
                    nameCell.innerHTML = `
                        ${servingName}
                        <span class="badge bg-primary ms-2">Default</span>
                    `;
                    defaultCell.innerHTML = `
                        <button class="btn btn-sm btn-outline-secondary" 
                                data-serving-id="${servingId}" title="Unset default">
                            <i class="fas fa-times me-1"></i>Unset Default
                        </button>
                    `;
                } else {
                    // This serving is not default - remove badge and update buttons
                    const servingName = nameCell.textContent.replace('Default', '').trim();
                    nameCell.innerHTML = servingName;
                    defaultCell.innerHTML = `
                        <button class="btn btn-sm btn-outline-primary" 
                                data-serving-id="${servingId}" title="Set as default">
                            <i class="fas fa-check me-1"></i>Set Default
                        </button>
                    `;
                }
            });
        },

        /**
         * Helper: Restore action buttons for a row
         */
        restoreActionButtons: function(row, servingId) {
            const actionsCell = row.querySelector('td:last-child .btn-group');
            actionsCell.innerHTML = `
                <button class="btn btn-outline-secondary edit-serving-btn" 
                        data-serving-id="${servingId}" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-danger delete-serving-btn" 
                        data-serving-id="${servingId}" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }
    }
};

// Initialize admin functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form field indicators for better UX
    setTimeout(() => {
        Admin.users.initializeFormFieldIndicators();
        Admin.users.initializeModalEventListeners();
    }, 500); // Delay to ensure DOM is fully loaded
    
    // Add User Form
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            Admin.users.submitAddForm(formData);
        });
        
        // User ID field functionality
        const userIdField = document.getElementById('userIdField');
        const generateUserIdBtn = document.getElementById('generateUserIdBtn');
        
        if (userIdField && generateUserIdBtn) {
            // Generate initial User ID when modal opens
            const addUserModal = document.getElementById('addUserModal');
            if (addUserModal) {
                addUserModal.addEventListener('show.bs.modal', function() {
                    if (!userIdField.value.trim()) {
                        userIdField.value = Admin.users.generateUserId();
                    }
                });
                
                // Clear form when modal is hidden
                addUserModal.addEventListener('hidden.bs.modal', function() {
                    addUserForm.reset();
                    userIdField.classList.remove('is-valid', 'is-invalid');
                    document.getElementById('userIdFeedback').textContent = '';
                });
            }
            
            // Generate new User ID button
            generateUserIdBtn.addEventListener('click', function() {
                userIdField.value = Admin.users.generateUserId();
                Admin.users.validateUserIdField(userIdField);
            });
            
            // Real-time validation for User ID
            let validationTimeout;
            userIdField.addEventListener('input', function() {
                clearTimeout(validationTimeout);
                validationTimeout = setTimeout(() => {
                    Admin.users.validateUserIdField(userIdField);
                }, 500); // Debounce validation
            });
            
            userIdField.addEventListener('blur', function() {
                Admin.users.validateUserIdField(userIdField);
            });
        }
    }

    // Edit User Form with enhanced validation
    const editUserForm = document.getElementById('editUserForm');
    if (editUserForm) {
        editUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            Admin.users.submitEditForm(formData);
        });
        
        // Add real-time validation for better UX
        const formFields = editUserForm.querySelectorAll('input[type="text"], input[type="email"]');
        formFields.forEach(field => {
            field.addEventListener('blur', function() {
                // Create temporary FormData for validation
                const tempFormData = new FormData(editUserForm);
                Admin.users.validateEditUserForm(tempFormData);
            });
        });
    }

    // Add Food Form
    const addFoodForm = document.getElementById('addFoodForm');
    if (addFoodForm) {
        addFoodForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            Admin.foods.submitAddForm(formData);
        });
    }

    // Bulk Upload Form
    const bulkUploadForm = document.getElementById('bulkUploadForm');
    if (bulkUploadForm) {
        bulkUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            Admin.foods.submitBulkUpload(formData);
        });
    }

    // Event delegation for user management buttons
    document.addEventListener('click', function(e) {
        // Edit User buttons
        if (e.target.closest('.edit-user-btn')) {
            const userId = e.target.closest('.edit-user-btn').dataset.userId;
            Admin.users.edit(userId);
        }
        
        // Reset Password buttons
        if (e.target.closest('.reset-password-btn')) {
            const btn = e.target.closest('.reset-password-btn');
            const userId = btn.dataset.userId;
            const username = btn.dataset.username;
            if (userId && username) {
                Admin.users.openPasswordResetModal(userId, username);
            } else {
                console.error('Missing user data for password reset:', {userId, username});
                NutriTracker.utils.showToast('Error: Missing user information', 'danger');
            }
        }
        
        // Toggle User Status buttons
        if (e.target.closest('.toggle-user-status-btn')) {
            const userId = e.target.closest('.toggle-user-status-btn').dataset.userId;
            Admin.users.toggleStatus(userId);
        }
        
        // Edit Food buttons
        if (e.target.closest('.edit-food-btn')) {
            const foodId = e.target.closest('.edit-food-btn').dataset.foodId;
            Admin.foods.edit(foodId);
        }
        
        // Toggle Food Status buttons
        if (e.target.closest('.toggle-food-status-btn')) {
            const foodId = e.target.closest('.toggle-food-status-btn').dataset.foodId;
            Admin.foods.toggleStatus(foodId);
        }
        
        // Delete Food buttons
        if (e.target.closest('.delete-food-btn')) {
            const foodId = e.target.closest('.delete-food-btn').dataset.foodId;
            Admin.foods.delete(foodId);
        }
        
        // Reset Password buttons
        if (e.target.closest('.reset-password-btn')) {
            const btn = e.target.closest('.reset-password-btn');
            const userId = btn.dataset.userId;
            const username = btn.dataset.username;
            Admin.users.openPasswordResetModal(userId, username);
        }
    });

    // Password reset form submission
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', Admin.users.submitPasswordReset);
    }

    // Real-time search for user and food tables
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', NutriTracker.utils.debounce(function() {
            // Trigger form submission for real-time search
            this.closest('form').submit();
        }, 500));
    });
    
    // Initialize serving management for food edit pages
    try {
        Admin.foods.servings.bindEvents();
    } catch (e) {
        console.warn('servings.bindEvents failed:', e);
    }
});

// Export for global access
window.Admin = Admin;
