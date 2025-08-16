#!/usr/bin/env python3
"""
Simple verification script to test the target duration fix.
This creates a minimal HTML file to test the JavaScript functionality.
"""

def create_test_file():
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Target Duration Fix Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select, input { padding: 8px; font-size: 14px; width: 200px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 4px; }
        .alert-info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .test-controls { background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .result { background-color: #e9ecef; padding: 10px; border-radius: 4px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Target Duration Fix Test</h1>
    
    <div class="test-controls">
        <h3>Test Instructions:</h3>
        <p>1. Set a custom target date (like 45 days from today)</p>
        <p>2. Check that the duration dropdown changes to "Custom timeframe"</p>
        <p>3. The result should show "custom" not empty string</p>
    </div>
    
    <form>
        <div class="form-group">
            <label for="target_duration">How long do you plan to work on this goal?</label>
            <select id="target_duration">
                <option value="">Not sure yet</option>
                <option value="2_weeks">2 weeks</option>
                <option value="1_month">1 month</option>
                <option value="2_months">2 months</option>
                <option value="3_months">3 months</option>
                <option value="6_months">6 months</option>
                <option value="1_year">1 year</option>
                <option value="custom">Custom timeframe</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="target_date">Target Completion Date</label>
            <input type="date" id="target_date" onchange="handleManualDateChange()">
        </div>
        
        <div id="dateCustomMessage" class="message alert-success" style="display: none;">
            <span id="customText">Custom date set. We won't change this unless you update the duration again.</span>
        </div>
    </form>
    
    <div class="result">
        <h4>Test Result:</h4>
        <p><strong>Current Duration Value:</strong> <span id="currentValue">""</span></p>
        <p><strong>Expected for Custom Date:</strong> "custom"</p>
        <p><strong>Status:</strong> <span id="testStatus">Not tested yet</span></p>
    </div>
    
    <script>
        // Duration to days mapping (from original code)
        const durationToDays = {
            '2_weeks': 14,
            '1_month': 30,
            '2_months': 60,
            '3_months': 90,
            '6_months': 180,
            '1_year': 365
        };

        // Days to duration mapping (reverse lookup)
        const daysToDuration = {
            '14': '2_weeks',
            '30': '1_month',
            '60': '2_months',
            '90': '3_months',
            '180': '6_months',
            '365': '1_year'
        };
        
        let userEditedDate = false;
        let lastDurationBasedDate = null;
        let programmaticChange = false;

        function handleManualDateChange() {
            // Skip processing if this is a programmatic change
            if (programmaticChange) {
                console.log('Skipping handleManualDateChange - programmatic change');
                return;
            }
            
            const dateInput = document.getElementById('target_date');
            const durationSelect = document.getElementById('target_duration');
            const selectedDate = dateInput.value;
            
            console.log('handleManualDateChange called - user manual change');
            
            hideAllMessages();
            
            if (!selectedDate) {
                updateTestResult('', 'Date cleared');
                return;
            }
            
            // Check if date is in the past
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const targetDate = new Date(selectedDate);
            
            if (targetDate < today) {
                updateTestResult('', 'Past date - no change');
                return;
            }
            
            // Calculate days difference
            const timeDiff = targetDate.getTime() - today.getTime();
            const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
            
            // Check if it matches a predefined duration (with 2-day tolerance)
            let matchingDuration = null;
            for (const [days, duration] of Object.entries(daysToDuration)) {
                if (Math.abs(daysDiff - parseInt(days)) <= 2) {
                    matchingDuration = duration;
                    break;
                }
            }
            
            if (matchingDuration) {
                // Update duration dropdown to match
                durationSelect.value = matchingDuration;
                userEditedDate = false; // This is now synced
                
                showCustomMessage("We've updated the duration to match your new target date.");
                updateTestResult(matchingDuration, 'Matched predefined duration');
            } else {
                // Set to custom timeframe
                durationSelect.value = 'custom';
                userEditedDate = true;
                
                showCustomMessage("Custom date set. We won't change this unless you update the duration again.");
                updateTestResult('custom', 'Custom date - should be "custom"');
            }
        }
        
        function hideAllMessages() {
            const dateCustomMessage = document.getElementById('dateCustomMessage');
            if (dateCustomMessage) dateCustomMessage.style.display = 'none';
        }

        function showCustomMessage(message) {
            hideAllMessages();
            const customMessageDiv = document.getElementById('dateCustomMessage');
            if (customMessageDiv) {
                customMessageDiv.style.display = 'block';
                if (message) {
                    const customText = document.getElementById('customText');
                    if (customText) customText.textContent = message;
                }
            }
        }
        
        function updateTestResult(value, status) {
            const currentValueSpan = document.getElementById('currentValue');
            const testStatusSpan = document.getElementById('testStatus');
            
            currentValueSpan.textContent = `"${value}"`;
            testStatusSpan.textContent = status;
            
            // Auto-check if this is the expected fix
            if (status.includes('Custom date') && value === 'custom') {
                testStatusSpan.style.color = 'green';
                testStatusSpan.textContent += ' ✅ CORRECT - Fix is working!';
            } else if (status.includes('Custom date') && value === '') {
                testStatusSpan.style.color = 'red';  
                testStatusSpan.textContent += ' ❌ WRONG - Still setting empty string';
            }
        }
        
        // Initialize with today's date + 45 days for testing
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date();
            const futureDate = new Date(today);
            futureDate.setDate(today.getDate() + 45); // 45 days should not match any preset
            
            const dateInput = document.getElementById('target_date');
            dateInput.value = futureDate.toISOString().split('T')[0];
            
            console.log('Test page loaded with date:', dateInput.value);
        });
    </script>
</body>
</html>'''
    
    with open('test_duration_fix.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Test file created: test_duration_fix.html")
    print("📖 Open this file in a browser to test the fix")
    print("🎯 The target date should automatically trigger the change event")
    print("📝 Expected result: Duration should be set to 'custom' (not empty string)")

if __name__ == "__main__":
    create_test_file()
