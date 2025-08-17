# Refactored NutriTracker.logMeal Module

## Key Changes Made:

### 1. **Removed Duplicate Functions**
- **loadServingData**: Removed the second implementation (lines 1279-1309)
- **populateServingDropdown**: Removed the second implementation (lines 1313-1340) 
- **getSelectedServing**: Removed the first implementation using `#servingSelect`

### 2. **Fixed API Integration**
- Added `credentials: 'same-origin'` to fetch call for authentication
- Proper error logging without browser alerts
- Correct field mapping from API response

### 3. **Normalized DOM Element IDs**
- All references now use `#serving-id` (not `#servingSelect`)
- Updated event handlers to use correct IDs
- Fixed dropdown population to match template structure

### 4. **Enhanced User Experience**
- Disabled placeholder option as required
- Better error handling and console logging
- Default serving selection with proper updates

---

## Complete Refactored Code:

```javascript
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
                const quantity = JSON.parse(preselectedQuantity.textContent);
                if (quantity) {
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
        this.updateSubmitButton();
    },

    /**
     * Set quantity value based on current mode
     */
    setQuantityValue: function(value) {
        if (this.currentMode === 'serving') {
            const servingQuantity = document.getElementById('serving-quantity');
            if (servingQuantity) servingQuantity.value = value;
        } else {
            const gramsQuantity = document.getElementById('grams-quantity');
            if (gramsQuantity) gramsQuantity.value = value;
        }
        this.updateEquivalentDisplays();
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
     * Set up event listeners for meal logging
     */
    setupEventListeners: function() {
        // Serving quantity input changes
        const servingQuantityInput = document.getElementById('serving-quantity');
        if (servingQuantityInput) {
            servingQuantityInput.addEventListener('input', () => {
                this.updateEquivalentDisplays();
                this.updateNutritionPreview();
                this.updateSubmitButton();
            });
        }

        // Grams quantity input changes
        const gramsQuantityInput = document.getElementById('grams-quantity');
        if (gramsQuantityInput) {
            gramsQuantityInput.addEventListener('input', () => {
                this.updateEquivalentDisplays();
                this.updateNutritionPreview();
                this.updateSubmitButton();
            });
        }

        // Serving selection changes - UNIFIED to use #serving-id
        const servingSelect = document.getElementById('serving-id');
        if (servingSelect) {
            servingSelect.addEventListener('change', () => {
                const selectedServing = this.getSelectedServing();
                if (selectedServing) {
                    // Update hidden serving ID field
                    const servingIdField = document.getElementById('serving_id');
                    if (servingIdField) servingIdField.value = selectedServing.id;
                    
                    // Update serving unit display
                    const servingUnit = document.getElementById('serving-unit');
                    if (servingUnit) servingUnit.textContent = selectedServing.unit + 's';
                }
                
                this.updateEquivalentDisplays();
                this.updateNutritionPreview();
                this.updateSubmitButton();
            });
        }

        // Food search input with debounced live search
        const foodSearchInput = document.getElementById('foodSearch');
        if (foodSearchInput) {
            const debouncedSearch = NutriTracker.utils.debounce(() => {
                this.searchFoods();
            }, NutriTracker.config.debounceDelay);
            
            foodSearchInput.addEventListener('input', () => {
                const query = foodSearchInput.value.trim();
                if (query.length >= 2) {
                    debouncedSearch();
                } else if (query.length === 0) {
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
            searchButton.onclick = null;
            searchButton.addEventListener('click', () => this.searchFoods());
        }

        // Meal type dropdown
        const mealTypeSelect = document.getElementById('meal_type');
        if (mealTypeSelect) {
            mealTypeSelect.addEventListener('change', () => this.updateSubmitButton());
        }

        // Form submission handler
        const mealLogForm = document.getElementById('mealLogForm');
        if (mealLogForm) {
            mealLogForm.addEventListener('submit', (event) => this.handleFormSubmit(event));
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
    loadServingData: function(foodId) {
        console.log(`Loading serving data for food ID: ${foodId}`);
        
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
                console.log(`API response status: ${response.status}`);
                if (!response.ok) {
                    console.error(`HTTP error! status: ${response.status}`);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API response data:', data);
                
                if (data.servings && data.servings.length > 0) {
                    // Map API response to expected format
                    const servings = data.servings.map(s => ({
                        id: s.id,
                        serving_name: s.description,
                        unit: s.unit_type,
                        grams_per_unit: s.size_in_grams
                    }));
                    
                    console.log(`Mapped ${servings.length} servings:`, servings);
                    
                    // Store servings in selected food
                    if (this.selectedFood) {
                        this.selectedFood.servings = servings;
                    }
                    
                    // Populate serving dropdown
                    this.populateServingDropdown(servings);
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
        console.log('Creating fallback servings due to API failure');
        
        const fallbackServings = [
            { id: 1, serving_name: '100g', unit: 'g', grams_per_unit: 100 },
            { id: 2, serving_name: '1 cup', unit: 'cup', grams_per_unit: 240 },
            { id: 3, serving_name: '1 piece', unit: 'piece', grams_per_unit: 100 }
        ];
        
        if (this.selectedFood) {
            this.selectedFood.servings = fallbackServings;
        }
        
        this.populateServingDropdown(fallbackServings);
        
        // Show warning to user
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
    populateServingDropdown: function(servings) {
        const servingSelect = document.getElementById('serving-id');
        if (!servingSelect) {
            console.error('Serving dropdown not found with ID: serving-id');
            return;
        }
        
        console.log(`Populating dropdown with ${servings.length} servings`);
        
        // Clear and add disabled placeholder option
        servingSelect.innerHTML = '<option value="" disabled selected>Choose serving size...</option>';
        
        // Add serving options
        servings.forEach((serving, index) => {
            console.log(`Adding serving ${index + 1}:`, serving);
            const option = document.createElement('option');
            option.value = serving.id;
            option.textContent = `${serving.serving_name} (${serving.grams_per_unit}g)`;
            option.dataset.gramsPerUnit = serving.grams_per_unit;
            option.dataset.unit = serving.unit;
            option.dataset.servingName = serving.serving_name;
            servingSelect.appendChild(option);
        });
        
        console.log(`Dropdown now has ${servingSelect.options.length} options`);
        
        // Select the first serving by default if available
        if (servings.length > 0) {
            servingSelect.value = servings[0].id;
            console.log(`Selected default serving: ${servings[0].serving_name}`);
            
            // Update displays after selecting default
            this.updateEquivalentDisplays();
            this.updateNutritionPreview();
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
                const quantity = parseFloat(servingQuantityInput.value) || 0;
                totalGrams = quantity * selectedServing.grams_per_unit;
            }
        } else {
            const gramsQuantityInput = document.getElementById('grams-quantity');
            if (gramsQuantityInput) {
                totalGrams = parseFloat(gramsQuantityInput.value) || 0;
            }
        }

        if (totalGrams <= 0) {
            previewDiv.style.display = 'none';
            return;
        }
        
        // Calculate nutrition based on per-100g values
        const multiplier = totalGrams / 100;
        
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
        if (!this.selectedFood || !this.selectedFood.id) {
            event.preventDefault();
            alert('Please select a food item first.');
            return;
        }
        
        // Get form data based on current mode
        let quantityGrams;
        let servingId = null;
        let unitType = this.currentMode;
        
        if (this.currentMode === 'serving') {
            const servingQuantity = document.getElementById('serving-quantity');
            const selectedServing = this.getSelectedServing();
            
            if (!selectedServing || !servingQuantity || parseFloat(servingQuantity.value) <= 0) {
                event.preventDefault();
                alert('Please select a serving size and enter a valid quantity.');
                return;
            }
            
            const quantity = parseFloat(servingQuantity.value);
            quantityGrams = quantity * selectedServing.grams_per_unit;
            servingId = selectedServing.id;
        } else {
            const gramsQuantity = document.getElementById('grams-quantity');
            
            if (!gramsQuantity || parseFloat(gramsQuantity.value) <= 0) {
                event.preventDefault();
                alert('Please enter a valid weight in grams.');
                return;
            }
            
            quantityGrams = parseFloat(gramsQuantity.value);
        }
        
        const mealTypeSelect = document.getElementById('meal_type');
        if (!mealTypeSelect || !mealTypeSelect.value) {
            event.preventDefault();
            alert('Please select a meal type.');
            return;
        }
        
        // Update hidden form fields before submission
        const foodIdInput = document.getElementById('food_id');
        const quantityInput = document.getElementById('quantity');
        const unitTypeInput = document.getElementById('unit_type');
        const servingIdInput = document.getElementById('serving_id');
        
        if (foodIdInput) foodIdInput.value = this.selectedFood.id;
        if (quantityInput) quantityInput.value = quantityGrams;
        if (unitTypeInput) unitTypeInput.value = unitType;
        if (servingIdInput && servingId) servingIdInput.value = servingId;
        
        // Let the form submit normally
    }
};
```

## Summary of Key Fixes:

1. **✅ Removed Duplicates**: Single `loadServingData`, `populateServingDropdown`, `getSelectedServing`
2. **✅ Fixed Authentication**: Added `credentials: 'same-origin'` to API fetch
3. **✅ Normalized IDs**: All references use `#serving-id` (not `#servingSelect`)
4. **✅ Proper API Mapping**: Correctly maps `{id, unit_type, size_in_grams, description}` to expected format
5. **✅ Disabled Placeholder**: Uses `<option value="" disabled selected>` as required
6. **✅ Enhanced Logging**: Console debugging without browser alerts
7. **✅ Default Selection**: Automatically selects first serving and triggers updates
8. **✅ Unified Data Flow**: Single source of truth for serving data in `this.selectedFood.servings`

This refactored version should resolve the empty dropdown issue while maintaining all existing functionality.
