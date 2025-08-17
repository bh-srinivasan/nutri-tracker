/**
 * Nutri Tracker - Main JavaScript File
 * Common functionality across the application
 */

// Global variables and configuration
const NutriTracker = {
    config: {
        apiBaseUrl: '/api',
        debounceDelay: 300,
        animationDuration: 300
    },
    utils: {},
    api: {},
    ui: {}
};

// Utility Functions
NutriTracker.utils = {
    /**
     * Debounce function to limit function calls
     */
    debounce: function(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },

    /**
     * Format number with specified decimal places
     */
    formatNumber: function(number, decimals = 1) {
        return parseFloat(number).toFixed(decimals);
    },

    /**
     * Format date to locale string
     */
    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    },

    /**
     * Show loading spinner
     */
    showLoading: function() {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        spinner.id = 'loading-spinner';
        document.body.appendChild(spinner);
    },

    /**
     * Hide loading spinner
     */
    hideLoading: function() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    /**
     * Show toast notification with enhanced options
     */
    showToast: function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '1055';
        toast.setAttribute('role', 'alert');
        
        // Support HTML content in messages
        const isHtml = message.includes('<');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Create toast with custom delay
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });
        bsToast.show();
        
        // Auto-remove after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
        
        return bsToast;
    },

    /**
     * Validate form data
     */
    validateForm: function(formData, rules) {
        const errors = {};
        
        for (const field in rules) {
            const value = formData.get(field);
            const rule = rules[field];
            
            if (rule.required && (!value || value.trim() === '')) {
                errors[field] = `${rule.label} is required`;
                continue;
            }
            
            if (value && rule.type === 'email') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    errors[field] = 'Please enter a valid email address';
                }
            }
            
            if (value && rule.type === 'number') {
                const num = parseFloat(value);
                if (isNaN(num)) {
                    errors[field] = `${rule.label} must be a number`;
                } else if (rule.min !== undefined && num < rule.min) {
                    errors[field] = `${rule.label} must be at least ${rule.min}`;
                } else if (rule.max !== undefined && num > rule.max) {
                    errors[field] = `${rule.label} must be no more than ${rule.max}`;
                }
            }
        }
        
        return errors;
    },

    /**
     * Display form errors
     */
    displayFormErrors: function(errors) {
        // Clear previous errors
        document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        
        // Display new errors
        for (const field in errors) {
            const input = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = errors[field];
                
                input.parentNode.appendChild(errorDiv);
            }
        }
    }
};

// API Functions
NutriTracker.api = {
    /**
     * Make API request with error handling
     */
    request: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            NutriTracker.utils.showLoading();
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            NutriTracker.utils.showToast('An error occurred. Please try again.', 'danger');
            throw error;
        } finally {
            NutriTracker.utils.hideLoading();
        }
    },

    /**
     * Search foods
     */
    searchFoods: async function(query) {
        const url = `${NutriTracker.config.apiBaseUrl}/foods/search-verified?q=${encodeURIComponent(query)}`;
        return await this.request(url);
    },

    /**
     * Get food by ID
     */
    getFood: async function(foodId) {
        const url = `${NutriTracker.config.apiBaseUrl}/foods/${foodId}`;
        return await this.request(url);
    },

    /**
     * Log meal
     */
    logMeal: async function(mealData) {
        const url = `${NutriTracker.config.apiBaseUrl}/meals/log`;
        return await this.request(url, {
            method: 'POST',
            body: JSON.stringify(mealData)
        });
    },

    /**
     * Update meal
     */
    updateMeal: async function(mealId, mealData) {
        const url = `${NutriTracker.config.apiBaseUrl}/meals/${mealId}`;
        return await this.request(url, {
            method: 'PUT',
            body: JSON.stringify(mealData)
        });
    },

    /**
     * Delete meal
     */
    deleteMeal: async function(mealId) {
        const url = `${NutriTracker.config.apiBaseUrl}/meals/${mealId}`;
        return await this.request(url, {
            method: 'DELETE'
        });
    }
};

// UI Functions
NutriTracker.ui = {
    /**
     * Initialize common UI components
     */
    init: function() {
        this.initTooltips();
        this.initDatePickers();
        this.initFormValidation();
        this.initAnimations();
    },

    /**
     * Initialize Bootstrap tooltips
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Initialize date pickers
     */
    initDatePickers: function() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            if (!input.value) {
                input.value = new Date().toISOString().split('T')[0];
            }
        });
    },

    /**
     * Initialize form validation
     */
    initFormValidation: function() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    /**
     * Initialize animations
     */
    initAnimations: function() {
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
    },

    /**
     * Update progress bar
     */
    updateProgressBar: function(selector, percentage, animated = true) {
        const progressBar = document.querySelector(selector);
        if (progressBar) {
            if (animated) {
                progressBar.style.transition = 'width 0.6s ease';
            }
            progressBar.style.width = `${Math.min(percentage, 100)}%`;
            
            // Update aria-valuenow
            progressBar.setAttribute('aria-valuenow', percentage);
        }
    },

    /**
     * Create confirmation modal
     */
    confirmAction: function(message, onConfirm, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Action</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirm-action">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        
        modal.querySelector('#confirm-action').addEventListener('click', () => {
            bsModal.hide();
            if (onConfirm) onConfirm();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (onCancel) onCancel();
        });
        
        bsModal.show();
    }
};

// Food Search Component
class FoodSearch {
    constructor(inputSelector, resultsSelector, onSelect) {
        this.input = document.querySelector(inputSelector);
        this.resultsContainer = document.querySelector(resultsSelector);
        this.onSelect = onSelect;
        this.searchCache = new Map();
        
        this.init();
    }
    
    init() {
        if (!this.input || !this.resultsContainer) return;
        
        this.input.addEventListener('input', 
            NutriTracker.utils.debounce(this.search.bind(this), NutriTracker.config.debounceDelay)
        );
        
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.search();
            }
        });
    }
    
    async search() {
        const query = this.input.value.trim();
        
        if (query.length < 2) {
            this.clearResults();
            return;
        }
        
        try {
            // Check cache first
            if (this.searchCache.has(query)) {
                this.displayResults(this.searchCache.get(query));
                return;
            }
            
            const data = await NutriTracker.api.searchFoods(query);
            
            // Cache results - API returns array directly
            this.searchCache.set(query, data);
            
            this.displayResults(data);
        } catch (error) {
            console.error('Search failed:', error);
            this.displayError('Search failed. Please try again.');
        }
    }
    
    displayResults(foods) {
        if (!foods || foods.length === 0) {
            this.resultsContainer.innerHTML = '<p class="text-muted">No foods found. Try a different search term.</p>';
            return;
        }
        
        const html = foods.map(food => `
            <button type="button" class="list-group-item list-group-item-action" 
                    data-food-id="${food.id}">
                <div class="d-flex align-items-center">
                    ${food.image_url ? `<img src="${food.image_url}" alt="${food.name}" class="rounded me-3" style="width: 40px; height: 40px; object-fit: cover;">` : ''}
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${food.name}</h6>
                        ${food.brand ? `<span class="badge bg-secondary me-2">${food.brand}</span>` : ''}
                        <small class="text-muted">${food.calories_per_100g} cal, ${food.protein_per_100g}g protein per 100g</small>
                    </div>
                </div>
            </button>
        `).join('');
        
        this.resultsContainer.innerHTML = `<div class="list-group">${html}</div>`;
        
        // Add click handlers
        this.resultsContainer.querySelectorAll('[data-food-id]').forEach(button => {
            button.addEventListener('click', () => {
                const foodId = button.getAttribute('data-food-id');
                const food = foods.find(f => f.id == foodId);
                if (this.onSelect) {
                    this.onSelect(food);
                }
                this.clearResults();
            });
        });
    }
    
    displayError(message) {
        this.resultsContainer.innerHTML = `<p class="text-danger">${message}</p>`;
    }
    
    clearResults() {
        this.resultsContainer.innerHTML = '';
    }
}

// Nutrition Calculator
class NutritionCalculator {
    static calculate(food, quantity) {
        const multiplier = quantity / 100;
        
        return {
            calories: Math.round((food.calories_per_100g || 0) * multiplier),
            protein: parseFloat(((food.protein_per_100g || 0) * multiplier).toFixed(1)),
            carbs: parseFloat(((food.carbs_per_100g || 0) * multiplier).toFixed(1)),
            fat: parseFloat(((food.fat_per_100g || 0) * multiplier).toFixed(1)),
            fiber: parseFloat(((food.fiber_per_100g || 0) * multiplier).toFixed(1))
        };
    }
    
    static formatNutrition(nutrition) {
        return {
            calories: `${nutrition.calories} cal`,
            protein: `${nutrition.protein}g`,
            carbs: `${nutrition.carbs}g`,
            fat: `${nutrition.fat}g`,
            fiber: `${nutrition.fiber}g`
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    NutriTracker.ui.init();
    
    // Initialize meal logging if on log meal page
    if (document.getElementById('mealLogForm') || document.getElementById('foodSearch')) {
        NutriTracker.logMeal.init();
    }
    
    // Dashboard event delegation
    document.addEventListener('click', function(e) {
        // Handle edit meal buttons
        if (e.target.closest('.edit-meal-btn')) {
            const mealId = e.target.closest('.edit-meal-btn').dataset.mealId;
            NutriTracker.dashboard.editMeal(mealId);
        }
        
        // Handle delete meal buttons
        if (e.target.closest('.delete-meal-btn')) {
            const mealId = e.target.closest('.delete-meal-btn').dataset.mealId;
            NutriTracker.dashboard.deleteMeal(mealId);
        }
        
        // Handle join challenge buttons
        if (e.target.closest('.join-challenge-btn')) {
            const challengeId = e.target.closest('.join-challenge-btn').dataset.challengeId;
            NutriTracker.dashboard.joinChallenge(challengeId);
        }

        // Handle show food details buttons
        if (e.target.closest('.show-food-details-btn')) {
            const foodId = e.target.closest('.show-food-details-btn').dataset.foodId;
            NutriTracker.dashboard.showFoodDetails(foodId);
        }

        // Handle quick select food buttons
        if (e.target.closest('.quick-select-food-btn')) {
            const foodId = e.target.closest('.quick-select-food-btn').dataset.foodId;
            NutriTracker.dashboard.quickSelectFood(foodId);
        }
    });
    
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        NutriTracker.utils.showToast('An unexpected error occurred.', 'danger');
    });
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        NutriTracker.utils.showToast('An error occurred processing your request.', 'danger');
    });
});

// Export for use in other modules
window.NutriTracker = NutriTracker;
window.FoodSearch = FoodSearch;
window.NutritionCalculator = NutritionCalculator;

// Dashboard functions
NutriTracker.dashboard = {
    /**
     * Edit a meal entry
     */
    editMeal: function(mealId) {
        // Redirect to log meal page with meal ID for editing
        window.location.href = `/dashboard/log-meal?edit=${mealId}`;
    },

    /**
     * Delete a meal entry
     */
    deleteMeal: function(mealId) {
        if (confirm('Are you sure you want to delete this meal entry?')) {
            fetch(`/api/meals/${mealId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (response.ok) {
                    NutriTracker.utils.showToast('Meal deleted successfully', 'success');
                    location.reload();
                } else {
                    throw new Error('Failed to delete meal');
                }
            })
            .catch(error => {
                console.error('Error deleting meal:', error);
                NutriTracker.utils.showToast('Error deleting meal', 'danger');
            });
        }
    },

    /**
     * Join a challenge
     */
    joinChallenge: function(challengeId) {
        if (confirm('Are you sure you want to start this challenge?')) {
            fetch('/api/challenges/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ challenge_id: challengeId })
            })
            .then(response => {
                if (response.ok) {
                    NutriTracker.utils.showToast('Challenge started successfully!', 'success');
                    location.reload();
                } else {
                    throw new Error('Failed to join challenge');
                }
            })
            .catch(error => {
                console.error('Error joining challenge:', error);
                NutriTracker.utils.showToast('Error starting challenge', 'danger');
            });
        }
    },

    /**
     * Show food details modal
     */
    showFoodDetails: function(foodId) {
        fetch(`/api/foods/${foodId}`)
            .then(response => response.json())
            .then(food => {
                // Update modal content
                document.getElementById('modalFoodName').textContent = food.name;
                document.getElementById('modalFoodBrand').textContent = food.brand || '';
                document.getElementById('modalFoodDescription').textContent = food.description || '';
                document.getElementById('modalFoodCalories').textContent = food.calories_per_100g;
                document.getElementById('modalFoodProtein').textContent = food.protein_per_100g + 'g';
                document.getElementById('modalFoodCarbs').textContent = (food.carbs_per_100g || 0) + 'g';
                document.getElementById('modalFoodFat').textContent = (food.fat_per_100g || 0) + 'g';
                
                if (food.image_url) {
                    document.getElementById('modalFoodImage').src = food.image_url;
                    document.getElementById('modalFoodImage').style.display = 'block';
                } else {
                    document.getElementById('modalFoodImage').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error fetching food details:', error);
                NutriTracker.utils.showToast('Error loading food details', 'danger');
            });
    },

    /**
     * Quick select food for meal logging
     */
    quickSelectFood: function(foodId) {
        fetch(`/api/foods/${foodId}`)
            .then(response => response.json())
            .then(food => {
                if (typeof NutriTracker.logMeal !== 'undefined' && NutriTracker.logMeal.selectFood) {
                    NutriTracker.logMeal.selectFood(food.id, food.name, food.brand || '', food.description || '', 
                                                   food.calories_per_100g, food.protein_per_100g, 
                                                   food.carbs_per_100g || 0, food.fat_per_100g || 0, 
                                                   food.image_url || '');
                }
            })
            .catch(error => {
                console.error('Error selecting food:', error);
                NutriTracker.utils.showToast('Error selecting food', 'danger');
            });
    }
};

// Meal Logging Module
NutriTracker.logMeal = {
    selectedFood: null,
    currentMode: 'serving', // 'serving' or 'grams'

    /**
     * Initialize meal logging page
     */
    init: function() {
        // Handle pre-selected food data
        const preselectedFoodData = document.getElementById('preselected-food-data');
        if (preselectedFoodData) {
            try {
                const foodData = JSON.parse(preselectedFoodData.textContent);
                this.selectFood(foodData.id, foodData.name, foodData.brand ?? '', 
                              foodData.description ?? '', foodData.calories_per_100g, 
                              foodData.protein_per_100g, foodData.carbs_per_100g ?? 0, 
                              foodData.fat_per_100g ?? 0, foodData.image_url ?? '');
            } catch (e) {
                console.error('Error parsing preselected food data:', e);
            }
        }

        // Handle pre-selected meal type
        const preselectedMealType = document.getElementById('preselected-meal-type');
        if (preselectedMealType) {
            try {
                const mealType = JSON.parse(preselectedMealType.textContent);
                const mealTypeSelect = document.getElementById('meal_type');
                if (mealTypeSelect) {
                    mealTypeSelect.value = mealType;
                    this.updateSubmitButton();
                }
            } catch (e) {
                console.error('Error parsing preselected meal type:', e);
            }
        }

        // Handle pre-selected quantity
        const preselectedQuantity = document.getElementById('preselected-quantity');
        if (preselectedQuantity) {
            try {
                console.log(`Debug: Found preselected-quantity element with content: "${preselectedQuantity.textContent}"`);
                const quantity = JSON.parse(preselectedQuantity.textContent);
                console.log(`Debug: Parsed preselected quantity as: ${quantity}`);
                if (quantity) {
                    // Set the appropriate input based on current mode
                    this.setQuantityValue(quantity);
                    this.updateNutritionPreview();
                    this.updateSubmitButton();
                }
            } catch (e) {
                console.error('Error parsing preselected quantity:', e);
            }
        }

        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize toggle state
        this.initializeToggle();
        
        // Ensure submit button state is correct on load
        this.updateSubmitButton();
    },

    /**
     * Initialize the serving/grams toggle
     */
    initializeToggle: function() {
        const servingsToggle = document.getElementById('servings-toggle');
        const gramsToggle = document.getElementById('grams-toggle');
        
        if (servingsToggle && gramsToggle) {
            servingsToggle.addEventListener('change', () => {
                if (servingsToggle.checked) {
                    this.switchToServingMode();
                }
            });
            
            gramsToggle.addEventListener('change', () => {
                if (gramsToggle.checked) {
                    this.switchToGramsMode();
                }
            });
        }
        
        // Start in serving mode by default
        this.switchToServingMode();
    },

    /**
     * Switch to serving mode
     */
    switchToServingMode: function() {
        this.currentMode = 'serving';
        
        const servingsMode = document.getElementById('servings-mode');
        const gramsMode = document.getElementById('grams-mode');
        const unitTypeField = document.getElementById('unit_type');
        
        if (servingsMode) servingsMode.style.display = 'block';
        if (gramsMode) gramsMode.style.display = 'none';
        if (unitTypeField) unitTypeField.value = 'serving';
        
        this.updateEquivalentDisplays();
        this.updateNutritionPreview();
        this.updateHiddenQuantityField(); // Update hidden field
        this.updateSubmitButton();
    },

    /**
     * Switch to grams mode  
     */
    switchToGramsMode: function() {
        this.currentMode = 'grams';
        
        const servingsMode = document.getElementById('servings-mode');
        const gramsMode = document.getElementById('grams-mode');
        const unitTypeField = document.getElementById('unit_type');
        
        if (servingsMode) servingsMode.style.display = 'none';
        if (gramsMode) gramsMode.style.display = 'block';
        if (unitTypeField) unitTypeField.value = 'grams';
        
        this.updateEquivalentDisplays();
        this.updateNutritionPreview();
        this.updateHiddenQuantityField(); // Update hidden field
        this.updateSubmitButton();
    },

    /**
     * Set quantity value based on current mode
     */
    setQuantityValue: function(value) {
        console.log(`Debug: setQuantityValue called with value = ${value}`);
        if (this.currentMode === 'serving') {
            const servingQuantity = document.getElementById('serving-quantity');
            if (servingQuantity) {
                console.log(`Debug: Setting serving-quantity from ${servingQuantity.value} to ${value}`);
                servingQuantity.value = value;
            }
        } else {
            const gramsQuantity = document.getElementById('grams-quantity');
            if (gramsQuantity) gramsQuantity.value = value;
        }
        this.updateEquivalentDisplays();
    },

    /**
     * Set up event listeners for meal logging
     */
    setupEventListeners: function() {
        // Serving quantity input changes
        const servingQuantityInput = document.getElementById('serving-quantity');
        if (servingQuantityInput) {
            servingQuantityInput.addEventListener('input', () => {
                this.updateEquivalentDisplays();
                this.updateNutritionPreview();
                this.updateHiddenQuantityField(); // Update hidden field
                this.updateSubmitButton();
            });
        }

        // Grams quantity input changes
        const gramsQuantityInput = document.getElementById('grams-quantity');
        if (gramsQuantityInput) {
            gramsQuantityInput.addEventListener('input', () => {
                this.updateEquivalentDisplays();
                this.updateNutritionPreview();
                this.updateHiddenQuantityField(); // Update hidden field
                this.updateSubmitButton();
            });
        }

        // Serving selection changes - UNIFIED to use #serving-id
        const servingSelect = document.getElementById('serving-id');
        if (servingSelect) {
            servingSelect.addEventListener('change', () => {
                console.log('Serving dropdown changed, value:', servingSelect.value);
                const selectedServing = this.getSelectedServing();
                console.log('Selected serving object:', selectedServing);
                
                if (selectedServing) {
                    // Update hidden serving ID field
                    const servingIdField = document.getElementById('serving_id');
                    if (servingIdField) {
                        servingIdField.value = selectedServing.id;
                        console.log('Updated hidden serving_id field to:', selectedServing.id);
                    }
                    
                    // Update serving unit display
                    const servingUnit = document.getElementById('serving-unit');
                    if (servingUnit) {
                        servingUnit.textContent = selectedServing.unit + 's';
                        console.log('Updated serving unit display to:', selectedServing.unit + 's');
                    }
                }
                
                this.updateEquivalentDisplays();
                this.updateNutritionPreview();
                this.updateHiddenQuantityField(); // Update hidden field
                this.updateSubmitButton();
            });
        }

        // Food search input with debounced live search
        const foodSearchInput = document.getElementById('foodSearch');
        if (foodSearchInput) {
            // Setup debounced search function
            const debouncedSearch = NutriTracker.utils.debounce(() => {
                this.searchFoods();
            }, NutriTracker.config.debounceDelay);
            
            foodSearchInput.addEventListener('input', () => {
                const query = foodSearchInput.value.trim();
                if (query.length >= 2) {
                    debouncedSearch();
                } else if (query.length === 0) {
                    // Clear results when search is empty
                    const resultsDiv = document.getElementById('foodSearchResults');
                    if (resultsDiv) resultsDiv.innerHTML = '';
                }
            });
            
            foodSearchInput.addEventListener('keyup', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    this.searchFoods();
                }
            });
        }

        // Search button
        const searchButton = document.querySelector('button[onclick="searchFoods()"]');
        if (searchButton) {
            searchButton.onclick = null; // Remove inline handler
            searchButton.addEventListener('click', () => this.searchFoods());
        }

        // Meal type dropdown
        const mealTypeSelect = document.getElementById('meal_type');
        if (mealTypeSelect) {
            mealTypeSelect.addEventListener('change', () => this.updateSubmitButton());
        }

        // Initialize submit button state
        this.updateSubmitButton();

        // Form submission handler
        const mealLogForm = document.getElementById('mealLogForm');
        if (mealLogForm) {
            mealLogForm.addEventListener('submit', (event) => this.handleFormSubmit(event));
        }
    },

    /**
     * Search for foods
     */
    searchFoods: function() {
        const query = document.getElementById('foodSearch').value;
        if (query.length < 2) return;

        NutriTracker.utils.showLoading();
        
        fetch(`/api/foods/search-verified?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                this.displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
                NutriTracker.utils.showToast('Error searching foods', 'danger');
            })
            .finally(() => {
                NutriTracker.utils.hideLoading();
            });
    },

    /**
     * Display search results
     */
    displaySearchResults: function(foods) {
        const resultsDiv = document.getElementById('foodSearchResults');
        if (!resultsDiv) return;

        if (foods.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No foods found. Try a different search term.</p>';
            return;
        }

        let html = '<div class="list-group">';
        foods.forEach(food => {
            html += `
                <button type="button" class="list-group-item list-group-item-action" 
                        data-food-id="${food.id}" data-food-name="${food.name}" 
                        data-food-brand="${food.brand || ''}" data-food-description="${food.description || ''}"
                        data-food-calories="${food.calories_per_100g}" data-food-protein="${food.protein_per_100g}"
                        data-food-carbs="${food.carbs_per_100g || 0}" data-food-fat="${food.fat_per_100g || 0}"
                        data-food-image="${food.image_url || ''}" onclick="NutriTracker.logMeal.selectFoodFromSearch(this)">
                    <div class="d-flex align-items-center">
                        ${food.image_url ? `<img src="${food.image_url}" alt="${food.name}" class="rounded me-3" style="width: 40px; height: 40px; object-fit: cover;">` : ''}
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${food.name}</h6>
                            ${food.brand ? `<span class="badge bg-secondary me-2">${food.brand}</span>` : ''}
                            <small class="text-muted">${food.calories_per_100g} cal, ${food.protein_per_100g}g protein per 100g</small>
                        </div>
                    </div>
                </button>
            `;
        });
        html += '</div>';
        resultsDiv.innerHTML = html;
    },

    /**
     * Select food from search results
     */
    selectFoodFromSearch: function(element) {
        const id = element.dataset.foodId;
        const name = element.dataset.foodName;
        const brand = element.dataset.foodBrand;
        const description = element.dataset.foodDescription;
        const calories = parseFloat(element.dataset.foodCalories);
        const protein = parseFloat(element.dataset.foodProtein);
        const carbs = parseFloat(element.dataset.foodCarbs);
        const fat = parseFloat(element.dataset.foodFat);
        const imageUrl = element.dataset.foodImage;

        this.selectFood(id, name, brand, description, calories, protein, carbs, fat, imageUrl);
    },

    /**
     * Select a food item
     */
    selectFood: function(id, name, brand, description, calories, protein, carbs, fat, imageUrl) {
        this.selectedFood = { id, name, brand, description, calories, protein, carbs, fat, imageUrl };
        
        // Update form
        const foodIdInput = document.getElementById('food_id');
        if (foodIdInput) foodIdInput.value = id;
        
        // Set a default quantity value to prevent HTML5 validation error
        const quantityInput = document.getElementById('quantity');
        if (quantityInput) quantityInput.value = '100'; // Default 100g
        
        // Update selected food display
        this.updateSelectedFoodDisplay(name, brand, description, calories, protein, carbs, fat, imageUrl);
        
        // Clear search results
        const resultsDiv = document.getElementById('foodSearchResults');
        if (resultsDiv) resultsDiv.innerHTML = '';
        
        const searchInput = document.getElementById('foodSearch');
        if (searchInput) searchInput.value = '';
        
        // Load serving data for this food
        this.loadServingData(id);
        
        // Show serving size section
        const servingSizeSection = document.getElementById('servingSizeSection');
        if (servingSizeSection) servingSizeSection.style.display = 'block';
        
        // Calculate nutrition preview if quantity is set
        this.updateNutritionPreview();
        
        // Enable submit button when food is selected
        this.updateSubmitButton();
    },

    /**
     * Load serving data for a food - UNIFIED IMPLEMENTATION
     */
    /**
     * Load serving data for a food - UNIFIED IMPLEMENTATION
     */
    loadServingData: function(foodId) {
        console.debug(`Loading serving data for food ID: ${foodId}`);
        
        // Show loading state
        const servingSelect = document.getElementById('serving-id');
        if (servingSelect) {
            servingSelect.innerHTML = '<option value="">Loading servings...</option>';
        }
        
        // Fetch real serving data from API with authentication
        fetch(`/api/foods/${foodId}/servings`, { 
            credentials: 'same-origin' 
        })
            .then(response => {
                console.debug(`API response status: ${response.status}`);
                if (!response.ok) {
                    console.error(`HTTP error! status: ${response.status}`);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.debug('API response data:', data);
                
                if (data.servings && data.servings.length > 0) {
                    // Map API response to internal format
                    const servings = data.servings.map(s => ({
                        id: s.id,
                        serving_name: s.description,
                        unit: s.unit_type,
                        grams_per_unit: s.size_in_grams,
                        is_default: !!s.is_default
                    }));
                    
                    console.debug(`Mapped ${servings.length} servings`);
                    
                    // Store servings and API data in selected food
                    if (this.selectedFood) {
                        this.selectedFood.servings = servings;
                        this.selectedFood.default_serving_id = data.default_serving_id;
                    }
                    
                    // Populate serving dropdown with default selection
                    this.populateServingDropdown(servings, data.default_serving_id);
                } else {
                    console.warn('No servings data received from API');
                    this.createFallbackServings();
                }
            })
            .catch(error => {
                console.error('Error loading serving data:', error);
                this.createFallbackServings();
            });
    },

    /**
     * Create fallback servings when API fails
     */
    createFallbackServings: function() {
        console.debug('Creating fallback servings due to API failure');
        
        const fallbackServings = [
            { id: 1, serving_name: '100g', unit: 'g', grams_per_unit: 100, is_default: false },
            { id: 2, serving_name: '1 cup', unit: 'cup', grams_per_unit: 240, is_default: false },
            { id: 3, serving_name: '1 piece', unit: 'piece', grams_per_unit: 100, is_default: false }
        ];
        
        if (this.selectedFood) {
            this.selectedFood.servings = fallbackServings;
        }
        
        this.populateServingDropdown(fallbackServings, null);
        
        // Show a warning to user
        const servingSelect = document.getElementById('serving-id');
        if (servingSelect && servingSelect.parentNode) {
            const warning = document.createElement('div');
            warning.className = 'text-warning small mt-1';
            warning.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Using default servings - some serving sizes may not be available';
            warning.id = 'serving-warning';
            
            // Remove any existing warning
            const existingWarning = document.getElementById('serving-warning');
            if (existingWarning) {
                existingWarning.remove();
            }
            
            servingSelect.parentNode.appendChild(warning);
        }
    },

    /**
     * Populate serving dropdown with options - UNIFIED IMPLEMENTATION
     */
    /**
     * Populate serving dropdown with proper default selection - UNIFIED IMPLEMENTATION
     */
    populateServingDropdown: function(servings, defaultServingId) {
        const servingSelect = document.getElementById('serving-id');
        if (!servingSelect) {
            console.error('Serving dropdown not found with ID: serving-id');
            return;
        }
        
        console.debug(`Populating dropdown with ${servings.length} servings`);
        
        // Clear and add placeholder option
        servingSelect.innerHTML = '<option value="" disabled selected>Choose serving size...</option>';
        
        // Add serving options
        servings.forEach((serving, index) => {
            const option = document.createElement('option');
            option.value = serving.id;
            option.textContent = `${serving.serving_name} (${serving.grams_per_unit}g)`;
            option.dataset.gramsPerUnit = serving.grams_per_unit;
            option.dataset.unit = serving.unit;
            option.dataset.servingName = serving.serving_name;
            servingSelect.appendChild(option);
        });
        
        // Auto-select default serving with priority logic
        let selectedServing = null;
        
        // Priority 1: Look for serving marked as is_default
        selectedServing = servings.find(s => s.is_default === true);
        
        // Priority 2: Use default_serving_id from API response
        if (!selectedServing && defaultServingId) {
            selectedServing = servings.find(s => s.id === defaultServingId);
        }
        
        // Priority 3: Fall back to first serving
        if (!selectedServing && servings.length > 0) {
            selectedServing = servings[0];
        }
        
        if (selectedServing) {
            servingSelect.value = selectedServing.id;
            console.debug(`Default selection made: ${selectedServing.serving_name}`);
            
            // Update hidden serving ID field
            const servingIdField = document.getElementById('serving_id');
            if (servingIdField) servingIdField.value = selectedServing.id;
            
            // Update serving unit display  
            const servingUnit = document.getElementById('serving-unit');
            if (servingUnit) servingUnit.textContent = selectedServing.unit + 's';
            
            // Trigger updates
            this.updateEquivalentDisplays();
            this.updateNutritionPreview();
            this.updateHiddenQuantityField();
            this.updateSubmitButton();
        }
    },

    /**
     * Update equivalent displays for both modes - UNIFIED IMPLEMENTATION
     */
    updateEquivalentDisplays: function() {
        if (this.currentMode === 'serving') {
            this.updateGramsEquivalent();
        } else {
            this.updateServingEquivalent();
        }
    },

    /**
     * Update grams equivalent display - UNIFIED IMPLEMENTATION
     */
    updateGramsEquivalent: function() {
        const servingQuantity = document.getElementById('serving-quantity');
        const gramsEquivalent = document.getElementById('grams-equivalent');
        const selectedServing = this.getSelectedServing();
        
        if (!servingQuantity || !gramsEquivalent || !selectedServing) return;
        
        const quantity = parseFloat(servingQuantity.value) || 0;
        const totalGrams = quantity * selectedServing.grams_per_unit;
        
        gramsEquivalent.textContent = `≈ ${totalGrams.toFixed(1)}g`;
    },

    /**
     * Update serving equivalent display - UNIFIED IMPLEMENTATION
     */
    updateServingEquivalent: function() {
        const gramsQuantity = document.getElementById('grams-quantity');
        const servingEquivalent = document.getElementById('serving-equivalent');
        
        if (!gramsQuantity || !servingEquivalent || !this.selectedFood || !this.selectedFood.servings) return;
        
        const grams = parseFloat(gramsQuantity.value) || 0;
        
        // Use the first serving as reference for conversion
        const referenceServing = this.selectedFood.servings[0];
        if (referenceServing) {
            const servingQuantity = grams / referenceServing.grams_per_unit;
            servingEquivalent.textContent = `≈ ${servingQuantity.toFixed(2)} ${referenceServing.serving_name}`;
        }
    },

    /**
     * Update selected food display
     */
    updateSelectedFoodDisplay: function(name, brand, description, calories, protein, carbs, fat, imageUrl) {
        const elements = {
            selectedFoodName: name,
            selectedFoodBrand: brand,
            selectedFoodDescription: description,
            selectedFoodCalories: calories,
            selectedFoodProtein: protein + 'g',
            selectedFoodCarbs: carbs + 'g',
            selectedFoodFat: fat + 'g'
        };

        for (const [elementId, value] of Object.entries(elements)) {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = value;
                if (elementId === 'selectedFoodBrand') {
                    element.style.display = brand ? 'inline' : 'none';
                }
            }
        }

        // Handle image
        const imageElement = document.getElementById('selectedFoodImage');
        if (imageElement) {
            if (imageUrl) {
                imageElement.src = imageUrl;
                imageElement.style.display = 'block';
            } else {
                imageElement.style.display = 'none';
            }
        }

        // Show selected food section
        const selectedSection = document.getElementById('selectedFoodSection');
        if (selectedSection) {
            selectedSection.style.display = 'block';
        }
    },

    /**
     * Update nutrition preview
     */
    updateNutritionPreview: function() {
        if (!this.selectedFood) return;
        
        const previewDiv = document.getElementById('nutritionPreview');
        if (!previewDiv) return;

        let totalGrams = 0;

        if (this.currentMode === 'serving') {
            const servingQuantityInput = document.getElementById('serving-quantity');
            const selectedServing = this.getSelectedServing();
            
            if (servingQuantityInput && selectedServing) {
                const servingQuantity = parseFloat(servingQuantityInput.value) || 0;
                console.log(`Debug: Serving quantity input value = "${servingQuantityInput.value}" -> parsed as ${servingQuantity}`);
                console.log(`Debug: Selected serving grams per unit = ${selectedServing.grams_per_unit}`);
                totalGrams = servingQuantity * selectedServing.grams_per_unit;
                console.log(`Serving calculation: ${servingQuantity} × ${selectedServing.grams_per_unit}g = ${totalGrams}g`);
            }
        } else {
            const gramsQuantityInput = document.getElementById('grams-quantity');
            if (gramsQuantityInput) {
                totalGrams = parseFloat(gramsQuantityInput.value) || 0;
                console.log(`Grams calculation: ${totalGrams}g`);
            }
        }

        if (totalGrams <= 0) {
            previewDiv.style.display = 'none';
            return;
        }
        
        // Calculate nutrition based on per-100g values
        const multiplier = totalGrams / 100;
        console.log(`Nutrition calculation: ${totalGrams}g ÷ 100 = ${multiplier} multiplier`);
        console.log(`Food nutrition per 100g: ${this.selectedFood.calories} cal, ${this.selectedFood.protein}g protein`);
        
        const calculatedCalories = this.selectedFood.calories * multiplier;
        const calculatedProtein = this.selectedFood.protein * multiplier;
        
        console.log(`Final calculation: ${this.selectedFood.calories} × ${multiplier} = ${calculatedCalories} calories`);
        console.log(`Final calculation: ${this.selectedFood.protein} × ${multiplier} = ${calculatedProtein} protein`);
        
        const previewElements = {
            previewCalories: Math.round(calculatedCalories),
            previewProtein: calculatedProtein.toFixed(1) + 'g',
            previewCarbs: (this.selectedFood.carbs * multiplier).toFixed(1) + 'g',
            previewFat: (this.selectedFood.fat * multiplier).toFixed(1) + 'g'
        };

        for (const [elementId, value] of Object.entries(previewElements)) {
            const element = document.getElementById(elementId);
            if (element) element.textContent = value;
        }
        
        previewDiv.style.display = 'block';
    },

    
    /**
     * Get the currently selected serving
     */
    getSelectedServing: function() {
        const servingSelect = document.getElementById('serving-id');
        if (!servingSelect || !servingSelect.value) return null;
        
        const servingId = parseInt(servingSelect.value);
        return this.selectedFood && this.selectedFood.servings ? 
               this.selectedFood.servings.find(s => s.id === servingId) : null;
    },

    /**
     * Update the hidden quantity field with the calculated grams value
     */
    updateHiddenQuantityField: function() {
        const quantityInput = document.getElementById('quantity');
        if (!quantityInput) return;
        
        let totalGrams = 0;
        
        if (this.currentMode === 'serving') {
            const servingQuantityInput = document.getElementById('serving-quantity');
            const selectedServing = this.getSelectedServing();
            
            if (servingQuantityInput && selectedServing) {
                const servingQuantity = parseFloat(servingQuantityInput.value) || 0;
                totalGrams = servingQuantity * selectedServing.grams_per_unit;
            }
        } else {
            const gramsQuantityInput = document.getElementById('grams-quantity');
            if (gramsQuantityInput) {
                totalGrams = parseFloat(gramsQuantityInput.value) || 0;
            }
        }
        
        // Always update the hidden field, even if 0
        quantityInput.value = totalGrams;
        console.log('Updated hidden quantity field to:', totalGrams, 'grams');
    },

    /**
     * Update submit button state based on form validity
     */
    updateSubmitButton: function() {
        const submitBtn = document.getElementById('submitBtn');
        if (!submitBtn) return;
        
        // Check if food is selected
        const hasFoodSelected = this.selectedFood && this.selectedFood.id;
        
        // Check if quantity is valid based on current mode
        let hasValidQuantity = false;
        
        if (this.currentMode === 'serving') {
            const servingQuantity = document.getElementById('serving-quantity');
            const selectedServing = this.getSelectedServing();
            const quantity = servingQuantity ? parseFloat(servingQuantity.value) || 0 : 0;
            hasValidQuantity = quantity > 0 && selectedServing;
        } else {
            const gramsQuantity = document.getElementById('grams-quantity');
            const quantity = gramsQuantity ? parseFloat(gramsQuantity.value) || 0 : 0;
            hasValidQuantity = quantity > 0;
        }
        
        // Check if meal type is selected
        const mealTypeSelect = document.getElementById('meal_type');
        const hasMealType = mealTypeSelect ? mealTypeSelect.value : false;
        
        // Enable button only if all required fields are filled
        const isFormValid = hasFoodSelected && hasValidQuantity && hasMealType;
        
        submitBtn.disabled = !isFormValid;
        
        // Update button text to provide feedback
        if (!hasFoodSelected) {
            submitBtn.textContent = 'Select a Food First';
        } else if (!hasValidQuantity) {
            if (this.currentMode === 'serving') {
                if (!this.getSelectedServing()) {
                    submitBtn.textContent = 'Select Serving Size';
                } else {
                    submitBtn.textContent = 'Enter Serving Quantity';
                }
            } else {
                submitBtn.textContent = 'Enter Weight in Grams';
            }
        } else if (!hasMealType) {
            submitBtn.textContent = 'Select Meal Type';
        } else {
            submitBtn.textContent = 'Log Meal';
        }
    },

    /**
     * Handle form submission
     */
    handleFormSubmit: function(event) {
        console.log('Form submit event triggered');
        
        // Don't prevent default - let Flask handle the form submission
        // But update the hidden form fields first
        
        if (!this.selectedFood || !this.selectedFood.id) {
            event.preventDefault();
            console.log('No food selected - preventing submission');
            alert('Please select a food item first.');
            return;
        }
        
        console.log('Selected food:', this.selectedFood);
        
        // Get form data based on current mode
        let quantityGrams;
        let servingId = null;
        let unitType = this.currentMode;
        
        console.log('Current mode:', unitType);
        
        if (this.currentMode === 'serving') {
            const servingQuantity = document.getElementById('serving-quantity');
            const selectedServing = this.getSelectedServing();
            
            console.log('Serving quantity element:', servingQuantity);
            console.log('Selected serving:', selectedServing);
            
            if (!selectedServing || !servingQuantity || parseFloat(servingQuantity.value) <= 0) {
                event.preventDefault();
                console.log('Invalid serving data - preventing submission');
                alert('Please select a serving size and enter a valid quantity.');
                return;
            }
            
            const quantity = parseFloat(servingQuantity.value);
            quantityGrams = quantity * selectedServing.grams_per_unit;
            servingId = selectedServing.id;
            
            console.log('Calculated grams from serving:', quantityGrams);
        } else {
            const gramsQuantity = document.getElementById('grams-quantity');
            
            if (!gramsQuantity || parseFloat(gramsQuantity.value) <= 0) {
                event.preventDefault();
                console.log('Invalid grams quantity - preventing submission');
                alert('Please enter a valid weight in grams.');
                return;
            }
            
            quantityGrams = parseFloat(gramsQuantity.value);
            console.log('Grams quantity:', quantityGrams);
        }
        
        const mealTypeSelect = document.getElementById('meal_type');
        if (!mealTypeSelect || !mealTypeSelect.value) {
            event.preventDefault();
            console.log('No meal type selected - preventing submission');
            alert('Please select a meal type.');
            return;
        }
        
        console.log('Meal type:', mealTypeSelect.value);
        
        // Update hidden form fields before submission
        const foodIdInput = document.getElementById('food_id');
        const quantityInput = document.getElementById('quantity');
        const unitTypeInput = document.getElementById('unit_type');
        const servingIdInput = document.getElementById('serving_id');
        
        console.log('Updating hidden fields...');
        if (foodIdInput) {
            foodIdInput.value = this.selectedFood.id;
            console.log('Set food_id to:', this.selectedFood.id);
        }
        if (quantityInput) {
            quantityInput.value = quantityGrams;
            console.log('Set quantity to:', quantityGrams);
        }
        if (unitTypeInput) {
            unitTypeInput.value = unitType;
            console.log('Set unit_type to:', unitType);
        }
        if (servingIdInput && servingId) {
            servingIdInput.value = servingId;
            console.log('Set serving_id to:', servingId);
        }
        
        console.log('Form validation passed - allowing submission');
        // Let the form submit normally
    }
};
