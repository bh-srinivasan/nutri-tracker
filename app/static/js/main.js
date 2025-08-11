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
                const quantity = JSON.parse(preselectedQuantity.textContent);
                const qtyInput = document.getElementById('quantity') || document.getElementById('quantityInput');
                if (qtyInput && quantity) {
                    qtyInput.value = quantity;
                    this.updateNutritionPreview();
                    this.updateSubmitButton();
                }
            } catch (e) {
                console.error('Error parsing preselected quantity:', e);
            }
        }

        // Set up event listeners
        this.setupEventListeners();
    },

    /**
     * Set up event listeners for meal logging
     */
    setupEventListeners: function() {
        // Quantity input changes - resilient selector
        const quantityInput = document.getElementById('quantity') || document.getElementById('quantityInput');
        if (quantityInput) {
            quantityInput.addEventListener('input', () => {
                this.updateNutritionPreview();
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
        
        // Update selected food display
        this.updateSelectedFoodDisplay(name, brand, description, calories, protein, carbs, fat, imageUrl);
        
        // Clear search results
        const resultsDiv = document.getElementById('foodSearchResults');
        if (resultsDiv) resultsDiv.innerHTML = '';
        
        const searchInput = document.getElementById('foodSearch');
        if (searchInput) searchInput.value = '';
        
        // Calculate nutrition preview if quantity is set
        this.updateNutritionPreview();
        
        // Enable submit button when food is selected
        this.updateSubmitButton();
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
        
        const quantityInput = document.getElementById('quantity') || document.getElementById('quantityInput');
        const quantity = quantityInput ? parseFloat(quantityInput.value) || 0 : 0;
        
        const previewDiv = document.getElementById('nutritionPreview');
        if (!previewDiv) return;

        if (quantity <= 0) {
            previewDiv.style.display = 'none';
            return;
        }
        
        const multiplier = quantity / 100;
        
        const previewElements = {
            previewCalories: Math.round(this.selectedFood.calories * multiplier),
            previewProtein: (this.selectedFood.protein * multiplier).toFixed(1) + 'g',
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
     * Update submit button state based on form validity
     */
    updateSubmitButton: function() {
        const submitBtn = document.getElementById('submitBtn');
        if (!submitBtn) return;
        
        // Check if food is selected
        const hasFoodSelected = this.selectedFood && this.selectedFood.id;
        
        // Check if quantity is valid
        const quantityInput = document.getElementById('quantity') || document.getElementById('quantityInput');
        const quantity = quantityInput ? parseFloat(quantityInput.value) || 0 : 0;
        const hasValidQuantity = quantity > 0;
        
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
            submitBtn.textContent = 'Enter Quantity';
        } else if (!hasMealType) {
            submitBtn.textContent = 'Select Meal Type';
        } else {
            submitBtn.textContent = 'Log Meal';
        }
    }
};
