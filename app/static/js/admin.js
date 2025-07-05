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
        try {
            const response = await fetch('/api/admin/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            if (response.ok) {
                NutriTracker.utils.showToast('User added successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
                location.reload();
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to add user');
            }
        } catch (error) {
            console.error('Error adding user:', error);
            NutriTracker.utils.showToast(error.message || 'Error adding user', 'danger');
        }
    },

    /**
     * Submit edit user form
     */
    submitEditForm: async function(formData) {
        const userId = formData.get('user_id');
        
        // Basic validation
        const username = formData.get('username');
        const email = formData.get('email');
        const firstName = formData.get('first_name');
        const lastName = formData.get('last_name');
        
        if (!username || username.trim().length < 3) {
            NutriTracker.utils.showToast('Username must be at least 3 characters', 'danger');
            return;
        }
        
        if (!email || !email.includes('@')) {
            NutriTracker.utils.showToast('Please enter a valid email address', 'danger');
            return;
        }
        
        if (!firstName || !firstName.trim()) {
            NutriTracker.utils.showToast('First name is required', 'danger');
            return;
        }
        
        if (!lastName || !lastName.trim()) {
            NutriTracker.utils.showToast('Last name is required', 'danger');
            return;
        }
        
        try {
            // Convert checkbox value properly
            const requestData = {
                username: username.trim(),
                email: email.trim(),
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
     * Submit password reset form
     */
    submitPasswordReset: async function(event) {
        event.preventDefault();
        
        const form = document.getElementById('resetPasswordForm');
        const formData = new FormData(form);
        const userId = formData.get('user_id');
        const newPassword = formData.get('new_password');
        
        // Admin simplified flow - no confirm password validation needed
        
        // Validate password strength
        const isValidPassword = newPassword.length >= 8 && 
                              /[A-Z]/.test(newPassword) && 
                              /[a-z]/.test(newPassword) && 
                              /\d/.test(newPassword) && 
                              /[!@#$%^&*(),.?":{}|<>]/.test(newPassword);
        
        if (!isValidPassword) {
            NutriTracker.utils.showToast('Password does not meet security requirements', 'danger');
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
     * Handle successful password reset with clean toast-only flow
     */
    handlePasswordResetSuccess: function(userId, username, newPassword) {
        // Close the reset modal immediately
        const resetModalElement = document.getElementById('resetPasswordModal');
        if (resetModalElement) {
            bootstrap.Modal.getInstance(resetModalElement).hide();
        }
        
        // Log the action for audit purposes
        console.log(`Admin password reset completed for user: ${username} (ID: ${userId}) at ${new Date().toISOString()}`);
        
        // Show clean success toast with password and auto-dismiss
        Admin.users.showCleanSuccessToast(userId, username, newPassword);
    },

    /**
     * Show clean success toast with auto-dismiss and smooth redirect
     */
    showCleanSuccessToast: function(userId, username, newPassword) {
        // Create secure toast message without exposing password
        const toastMessage = `
            <div class="d-flex align-items-center">
                <i class="fas fa-check-circle text-success me-2"></i>
                <div>
                    <strong>Password reset successfully</strong><br>
                    <small>Password for ${username} has been updated</small>
                </div>
            </div>
        `;
        
        // Show toast with 2.5 second auto-dismiss
        NutriTracker.utils.showToast(toastMessage, 'success', 2500);
        
        // Add subtle visual feedback to the user row
        Admin.users.highlightUserRow(userId);
        
        // Smooth redirect after toast auto-dismiss
        setTimeout(() => {
            Admin.users.navigateBackToManageUsers();
        }, 2800);
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
            
            // Remove highlight after banner is dismissed
            setTimeout(() => {
                userRow.style.cssText = 'transition: all 0.5s ease;';
                setTimeout(() => {
                    userRow.style.cssText = '';
                }, 500);
            }, 3500);
        }
    },

    /**
     * Navigate back to Manage Users page with enhanced context preservation
     */
    navigateBackToManageUsers: function() {
        // Get current URL to preserve all parameters
        const currentUrl = new URL(window.location);
        
        // If we're already on the manage users page, just reload to refresh data
        if (currentUrl.pathname.includes('/admin/users') || currentUrl.pathname === '/admin/users') {
            // Preserve all query parameters (filters, search, pagination)
            window.location.reload();
        } else {
            // Navigate to manage users page, preserving any applicable filters
            const managersUsersUrl = new URL('/admin/users', window.location.origin);
            
            // Copy over relevant query parameters if they exist
            const relevantParams = ['search', 'status', 'role', 'show_details', 'page'];
            relevantParams.forEach(param => {
                if (currentUrl.searchParams.has(param)) {
                    managersUsersUrl.searchParams.set(param, currentUrl.searchParams.get(param));
                }
            });
            
            window.location.href = managersUsersUrl.toString();
        }
    },

    /**
     * Enhanced immediate navigation with smooth transition
     */
    immediateNavigateToManageUsers: function() {
        // Add a smooth fade effect before navigation
        const body = document.body;
        body.style.transition = 'opacity 0.2s ease-out';
        body.style.opacity = '0.9';
        
        setTimeout(() => {
            Admin.users.navigateBackToManageUsers();
        }, 150);
    },

    /**
     * Schedule auto-redirect to Manage Users after password reset success
     */
    scheduleRedirectToManageUsers: function(modalElement, userId, username) {
        // Add auto-redirect countdown to the modal
        const modalFooter = modalElement.querySelector('.modal-footer');
        if (modalFooter) {
            // Create countdown element
            const countdownElement = document.createElement('div');
            countdownElement.className = 'countdown-redirect me-auto';
            countdownElement.innerHTML = `
                <small class="text-muted">
                    <i class="fas fa-clock"></i> 
                    Returning to Manage Users in <span id="redirectCountdown">3</span> seconds...
                </small>
            `;
            
            // Insert before the Close button
            const closeButton = modalFooter.querySelector('button');
            modalFooter.insertBefore(countdownElement, closeButton);
            
            // Start countdown
            let countdown = 3;
            const countdownSpan = document.getElementById('redirectCountdown');
            
            const countdownInterval = setInterval(() => {
                countdown--;
                if (countdownSpan) {
                    countdownSpan.textContent = countdown;
                }
                
                if (countdown <= 0) {
                    clearInterval(countdownInterval);
                    
                    // Hide the modal
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Smooth redirect back to manage users
                    Admin.users.redirectToManageUsers(userId, username);
                }
            }, 1000);
            
            // Allow users to cancel auto-redirect by clicking the close button
            const closeBtn = modalFooter.querySelector('button[data-bs-dismiss="modal"]');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    clearInterval(countdownInterval);
                    // Remove the countdown element
                    if (countdownElement && countdownElement.parentNode) {
                        countdownElement.parentNode.removeChild(countdownElement);
                    }
                }, { once: true });
            }
        }
    },

    /**
     * Redirect to Manage Users view with success feedback
     */
    redirectToManageUsers: function(userId, username) {
        // Log the redirect action
        console.log(`Redirecting to Manage Users after password reset for user: ${username}`);
        
        // Smooth page transition
        document.body.style.opacity = '0.8';
        document.body.style.transition = 'opacity 0.3s ease-in-out';
        
        // Show a brief loading toast
        NutriTracker.utils.showToast(`Password reset completed for ${username}. Returning to user list...`, 'info');
        
        // Perform the redirect
        setTimeout(() => {
            // Use the current page URL to maintain context
            window.location.href = window.location.pathname + window.location.search;
        }, 300);
    },

};

// Food Management Functions
Admin.foods = {
    /**
     * Edit food
     */
    edit: async function(foodId) {
        try {
            const response = await fetch(`/api/foods/${foodId}`);
            const food = await response.json();
            
            // Populate edit form (similar to add form)
            // Implementation depends on having an edit food modal
            console.log('Edit food:', food);
            NutriTracker.utils.showToast('Edit food functionality to be implemented', 'info');
        } catch (error) {
            console.error('Error fetching food:', error);
            NutriTracker.utils.showToast('Error loading food data', 'danger');
        }
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
    }
};

// Export for global access
window.Admin = Admin;

// Initialize admin functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add User Form
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            Admin.users.submitAddForm(formData);
        });
    }

    // Edit User Form
    const editUserForm = document.getElementById('editUserForm');
    if (editUserForm) {
        editUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            Admin.users.submitEditForm(formData);
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
});

// Export for global access
window.Admin = Admin;
