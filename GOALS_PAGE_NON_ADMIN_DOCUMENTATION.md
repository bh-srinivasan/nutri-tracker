# Nutri Tracker - Goals Page Documentation for Non-Admin Users

## Overview

The Goals Page (`/nutrition-goals`) is a comprehensive interface for non-admin users to set, update, and track their nutrition goals. It provides personal nutrition target setting based on user's physical attributes and fitness objectives.

## Page Sections

### 1. Current Goals Display Section

#### Purpose
Displays the user's currently active nutrition goals if they exist.

#### Fields Displayed
- **Current Goals Card**: Shows active nutrition targets
  - **Target Calories**: `Float` - Daily calorie target (e.g., "2000 Calories/day")
  - **Target Protein**: `Float` - Daily protein target in grams (e.g., "150g Protein/day")
  - **Target Carbs**: `Float` - Daily carbohydrate target in grams (e.g., "250g Carbs/day")
  - **Target Fat**: `Float` - Daily fat target in grams (e.g., "67g Fat/day")
  - **Target Fiber**: `Float` - Daily fiber target in grams (optional, e.g., "25g Fiber/day")
  - **Target Weight**: `Float` - Weight goal in kg (optional, e.g., "70kg Target Weight")

#### Goal Timing Information
- **Goal Last Updated**: `DateTime` - When the goal was last set/updated
- **Target Completion Date**: `Date` - When user aims to achieve the goal
  - Shows status indicators:
    - "Past due" with warning icon if date has passed
    - "Today!" with star icon if target date is today
    - "X days to go" for future dates

### 2. Goal Timeline Section (Optional)

#### Fields
- **Target Duration**: `SelectField` - Dropdown with predefined timeframes
  - Data Type: `String`
  - Options:
    - `''` - "Not sure yet"
    - `'2_weeks'` - "2 weeks"
    - `'1_month'` - "1 month"
    - `'2_months'` - "2 months"
    - `'3_months'` - "3 months"
    - `'6_months'` - "6 months"
    - `'1_year'` - "1 year"
    - `'custom'` - "Custom timeframe"

- **Target Completion Date**: `DateField` - Manual date selection
  - Data Type: `Date`
  - Validation: Cannot be in the past
  - Auto-populated based on duration selection
  - User can override manually
  - Clear button available

#### Interactive Features
- **Dynamic Date Calculation**: Automatically calculates target date when duration is selected
- **Manual Override**: Users can set custom dates, which switches duration to "Custom timeframe"
- **Smart Sync**: If manual date matches a standard duration (±3 days), duration dropdown updates accordingly
- **Reset Option**: Button appears to reset to duration-based date when manually overridden
- **Validation Messages**: Real-time feedback for date selection

### 3. Personal Information Section

#### Fields for Goal Calculation
- **Current Weight**: `FloatField`
  - Data Type: `Float`
  - Unit: kg
  - Validation: 20-300 kg range
  - Required: Yes

- **Target Weight**: `FloatField`
  - Data Type: `Float`
  - Unit: kg
  - Validation: 20-300 kg range
  - Required: No (Optional)

- **Height**: `FloatField`
  - Data Type: `Float`
  - Unit: cm
  - Validation: 100-250 cm range
  - Required: Yes

- **Age**: `FloatField`
  - Data Type: `Float`
  - Unit: years
  - Validation: 10-120 years range
  - Required: Yes

- **Gender**: `SelectField`
  - Data Type: `String`
  - Options: 'male', 'female'
  - Required: Yes

- **Activity Level**: `SelectField`
  - Data Type: `String`
  - Options:
    - `'sedentary'` - "Sedentary (little/no exercise)"
    - `'light'` - "Light activity (light exercise 1-3 days/week)"
    - `'moderate'` - "Moderate activity (moderate exercise 3-5 days/week)"
    - `'high'` - "High activity (hard exercise 6-7 days/week)"
    - `'very_high'` - "Very high activity (very hard exercise, physical job)"
  - Required: Yes

- **Goal Type**: `SelectField`
  - Data Type: `String`
  - Options:
    - `'lose'` - "Lose Weight"
    - `'maintain'` - "Maintain Weight"
    - `'gain'` - "Gain Weight"
  - Required: Yes

### 4. Daily Nutrition Targets Section

#### Manual Goal Setting Fields
- **Target Calories**: `FloatField`
  - Data Type: `Float`
  - Unit: calories
  - Validation: 800-5000 calories range
  - Required: Yes

- **Target Protein**: `FloatField`
  - Data Type: `Float`
  - Unit: grams
  - Validation: 10-300g range
  - Required: Yes

- **Target Carbs**: `FloatField`
  - Data Type: `Float`
  - Unit: grams
  - Validation: 0-500g range
  - Required: No (Optional)

- **Target Fat**: `FloatField`
  - Data Type: `Float`
  - Unit: grams
  - Validation: 0-200g range
  - Required: No (Optional)

- **Target Fiber**: `FloatField`
  - Data Type: `Float`
  - Unit: grams
  - Validation: 0-100g range
  - Required: No (Optional)

### 5. Goal History Section

#### Displays
- **Historical Goals Table**: Shows previous nutrition goals
  - **Created Date**: When the goal was set
  - **Calories**: Historical calorie target
  - **Protein**: Historical protein target
  - **Carbs**: Historical carbohydrate target
  - **Fat**: Historical fat target
  - **Status**: "Active" or "Completed" badge

## Buttons and Interactive Elements

### 1. "Calculate Recommended Goals" Button

#### Location
Right side of the form, next to goal type selection

#### Functionality
- **Purpose**: Auto-calculates nutrition targets based on user's personal information
- **JavaScript Function**: `calculateGoals()`
- **Requirements**: All personal information fields must be filled
- **Calculation Method**:
  - Uses Mifflin-St Jeor Equation for BMR calculation
  - Applies activity level multipliers
  - Adjusts for goal type (±500 calories for weight loss/gain)
  - Calculates macros: 1g protein per lb body weight, 25% calories from fat, remaining from carbs
  - Fiber: 14g per 1000 calories

#### Calculation Logic
```javascript
// BMR Calculation (Mifflin-St Jeor)
Male: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
Female: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

// TDEE = BMR × Activity Multiplier
Activity Multipliers:
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extremely Active: 1.9

// Goal Adjustment
- Weight Loss: TDEE - 500 calories
- Weight Gain: TDEE + 500 calories
- Maintain: TDEE (no change)

// Macro Distribution
- Protein: 2.2g per kg body weight
- Fat: 25% of total calories
- Carbs: Remaining calories after protein and fat
- Fiber: 14g per 1000 calories
```

#### Error Handling
- Shows toast notification if required fields are missing
- Fallback to alert() if toast system unavailable

### 2. "Back to Dashboard" Button

#### Location
Top-right corner of the page

#### Functionality
- **Purpose**: Navigate back to main dashboard
- **Route**: `{{ url_for('dashboard.index') }}`
- **Style**: Outline secondary button with back arrow icon

### 3. "Set Goals" / "Update Goals" Submit Button

#### Location
Bottom of the form

#### Functionality
- **Purpose**: Submit the nutrition goals form
- **Dynamic Text**: Shows "Update" if current goal exists, "Set" if new
- **Validation**: Triggers form validation before submission
- **POST Route**: `/nutrition-goals`

### 4. Target Date Management Buttons

#### Clear Date Button (×)
- **Location**: Next to target date input field
- **Purpose**: Clear the target completion date
- **JavaScript Function**: `clearTargetDate()`

#### Reset to Duration Date Button
- **Location**: Appears when user manually overrides auto-calculated date
- **Purpose**: Reset date back to duration-based calculation
- **JavaScript Function**: `resetToDurationDate()`

## Form Processing and Data Flow

### GET Request (Page Load)
1. **User Data Pre-population**: Form fields populated with existing user profile data
2. **Current Goal Loading**: If active goal exists, form populated with current targets
3. **Goal History Retrieval**: Previous goals loaded for history section

### POST Request (Form Submission)
1. **Form Validation**: Server-side validation of all fields
2. **User Profile Update**: Personal information saved to user record
3. **Target Date Calculation**: If duration selected but no manual date, auto-calculate
4. **Goal Deactivation**: Current active goal marked as inactive
5. **New Goal Creation**: New NutritionGoal record created and marked active
6. **Database Commit**: All changes saved to database
7. **Success Redirect**: User redirected to dashboard with success message

## Validation Rules

### Field-Level Validation
- **Weight**: 20-300 kg
- **Height**: 100-250 cm  
- **Age**: 10-120 years
- **Target Calories**: 800-5000 calories
- **Target Protein**: 10-300g
- **Target Carbs**: 0-500g
- **Target Fat**: 0-200g
- **Target Fiber**: 0-100g
- **Target Date**: Cannot be in the past

### Business Logic Validation
- **Complete Profile Required**: Personal information needed for goal calculation
- **Date Consistency**: Target date must align with selected duration (with tolerance)
- **Active Goal Management**: Only one active goal per user at a time

## JavaScript Functionality

### Goal Timeline Features
- **Duration-Date Sync**: Automatic date calculation when duration changes
- **Manual Override Detection**: Tracks when user manually edits dates
- **Smart Duration Matching**: Auto-selects duration when manual date matches standard timeframe
- **Validation Messages**: Real-time feedback with styled alert boxes
- **Reset Capabilities**: Option to revert to auto-calculated dates

### Goal Calculation
- **BMR/TDEE Calculator**: Client-side nutrition calculation
- **Form Auto-fill**: Populates target fields with calculated values
- **Error Handling**: Graceful fallback for missing data or calculation errors

## File References

### Template Files
- **Main Template**: [`app/templates/dashboard/nutrition_goals.html`](app/templates/dashboard/nutrition_goals.html)
- **Base Template**: [`app/templates/base.html`](app/templates/base.html)

### Backend Files
- **Routes**: [`app/dashboard/routes.py`](app/dashboard/routes.py) (lines 332-420)
- **Forms**: [`app/dashboard/forms.py`](app/dashboard/forms.py) (lines 37-85)
- **Models**: [`app/models.py`](app/models.py) (lines 311-336)

### Utility Functions
- **Target Date Calculation**: [`app/dashboard/routes.py`](app/dashboard/routes.py) (lines 27-44)
- **Recommended Nutrition**: [`app/dashboard/routes.py`](app/dashboard/routes.py) (lines 675-716)

### Database Schema
- **NutritionGoal Model**: [`app/models.py`](app/models.py) (lines 311-336)
- **User Model**: [`app/models.py`](app/models.py) (includes personal information fields)

### Form Validation
- **Custom Validators**: [`app/dashboard/forms.py`](app/dashboard/forms.py) (validate_target_date function)

## User Experience Flow

1. **Page Access**: User navigates to Goals page from dashboard
2. **Current Goals Review**: If goals exist, user sees current targets and progress
3. **Information Input**: User fills/updates personal information
4. **Goal Calculation**: User can auto-calculate or manually set targets
5. **Timeline Setting**: Optional goal duration and target date selection
6. **Form Submission**: Goals saved and user redirected with confirmation
7. **History Tracking**: Previous goals stored for user reference

## Security and Access Control

- **Login Required**: `@login_required` decorator ensures authenticated access
- **User Isolation**: All goals tied to `current_user.id`
- **Form CSRF Protection**: `{{ form.hidden_tag() }}` includes CSRF tokens
- **Input Validation**: Both client-side and server-side validation implemented

## Error Handling

- **Field Validation Errors**: Individual field error messages displayed
- **Form-Level Errors**: General form validation errors shown
- **JavaScript Errors**: Graceful fallbacks for calculation and date functions
- **Database Errors**: Transaction rollback and error logging

This comprehensive documentation covers all aspects of the Goals Page functionality for non-admin users, including field specifications, button behaviors, validation rules, and file references.
