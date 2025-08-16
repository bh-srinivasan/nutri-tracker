# Upload History Tab - User Experience Flow

## Overview
This document details exactly what happens when a user clicks on the "Upload History" tab in the Food Servings Upload interface, including all technical processes, UI updates, and data flows.

## User Journey: Clicking Upload History Tab

### 1. Initial Page Load
**URL**: `/admin/food-servings/uploads`
**Route**: `food_servings_uploads()` in [`app/admin/routes.py`](./app/admin/routes.py)

When the user first visits the page:
```python
# Get query parameters for tab selection
active_tab = request.args.get('tab', 'upload')  # Defaults to 'upload' tab
page = request.args.get('page', 1, type=int)
per_page = current_app.config.get('UPLOAD_JOBS_PER_PAGE', 10)
```

### 2. JavaScript Tab Click Event
**File**: [`app/templates/admin/food_servings_uploads.html`](./app/templates/admin/food_servings_uploads.html)

When user clicks the "History" tab:
```html
<ul class="nav nav-tabs" id="uploadTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="upload-tab" data-bs-toggle="tab" data-bs-target="#upload" type="button">
            <i class="fas fa-upload me-2"></i>Upload
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="history-tab" data-bs-toggle="tab" data-bs-target="#history" type="button">
            <i class="fas fa-history me-2"></i>History
        </button>
    </li>
</ul>
```

**JavaScript Execution**:
1. Bootstrap's tab component activates
2. Hide upload tab content (`#upload`)
3. Show history tab content (`#history`)
4. Update browser URL with `?tab=history` parameter (if configured)

### 3. Server-Side Data Processing

#### Backend Query Execution
**Location**: `food_servings_uploads()` function in [`app/admin/routes.py`](./app/admin/routes.py)

```python
# If history tab is requested, fetch job data
if active_tab == 'history':
    # Get jobs for current user with pagination
    jobs_query = ServingUploadJob.query.filter_by(created_by=current_user.id).order_by(desc(ServingUploadJob.created_at))
    jobs = jobs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Count pending jobs for badge display
    pending_jobs_count = ServingUploadJob.query.filter_by(
        created_by=current_user.id, 
        status='pending'
    ).count()
```

#### Database Queries Executed:
1. **Main Query**: Fetch paginated upload jobs for current user
   ```sql
   SELECT * FROM serving_upload_job 
   WHERE created_by = ? 
   ORDER BY created_at DESC 
   LIMIT ? OFFSET ?
   ```

2. **Count Query**: Get total jobs for pagination
   ```sql
   SELECT COUNT(*) FROM serving_upload_job 
   WHERE created_by = ?
   ```

3. **Pending Count**: Count jobs still processing
   ```sql
   SELECT COUNT(*) FROM serving_upload_job 
   WHERE created_by = ? AND status = 'pending'
   ```

### 4. Template Rendering

#### History Tab Content Structure
**File**: [`app/templates/admin/food_servings_uploads.html`](./app/templates/admin/food_servings_uploads.html)

```html
<div class="tab-pane fade" id="history" role="tabpanel">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0">
            <i class="fas fa-history me-2"></i>Upload History
            {% if pending_jobs_count > 0 %}
                <span class="badge bg-warning ms-2">{{ pending_jobs_count }} pending</span>
            {% endif %}
        </h5>
    </div>
    
    <!-- Job Statistics -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-primary">{{ jobs.total if jobs else 0 }}</h5>
                    <p class="card-text">Total Jobs</p>
                </div>
            </div>
        </div>
        <!-- More statistics cards... -->
    </div>
    
    <!-- Jobs Table -->
    <div class="card">
        <div class="card-body">
            {% if jobs and jobs.items %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <!-- Table content -->
                    </table>
                </div>
            {% else %}
                <div class="text-center py-4">
                    <i class="fas fa-history fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No upload jobs found</h5>
                </div>
            {% endif %}
        </div>
    </div>
</div>
```

### 5. Job Table Population

#### Table Headers and Data
Each job row displays:
```html
<tr>
    <td>
        <strong>{{ job.filename }}</strong><br>
        <small class="text-muted">{{ job.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</small>
    </td>
    <td>
        {% if job.status == 'completed' %}
            <span class="badge bg-success">Completed</span>
        {% elif job.status == 'failed' %}
            <span class="badge bg-danger">Failed</span>
        {% elif job.status == 'processing' %}
            <span class="badge bg-info">Processing</span>
        {% else %}
            <span class="badge bg-warning">Pending</span>
        {% endif %}
    </td>
    <td>
        <div class="progress" style="height: 20px;">
            <div class="progress-bar" style="width: {{ job.progress_percentage }}%">
                {{ job.progress_percentage }}%
            </div>
        </div>
    </td>
    <td>{{ job.total_rows or 0 }}</td>
    <td class="text-success">{{ job.successful_rows or 0 }}</td>
    <td class="text-danger">{{ job.failed_rows or 0 }}</td>
    <td>
        <button class="btn btn-sm btn-outline-primary" onclick="showJobDetails('{{ job.job_id }}')">
            <i class="fas fa-eye"></i> Details
        </button>
    </td>
</tr>
```

### 6. Interactive Features

#### Job Details Modal
When user clicks "Details" button:

**JavaScript Function**:
```javascript
function showJobDetails(jobId) {
    // Show loading state
    $('#jobDetailsModal').modal('show');
    $('#jobDetailsContent').html('<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading...</div>');
    
    // Fetch job details via AJAX
    fetch(`/admin/food-servings/uploads?action=job_details&job_id=${jobId}`)
        .then(response => response.json())
        .then(data => {
            // Populate modal with job details
            displayJobDetails(data);
        })
        .catch(error => {
            $('#jobDetailsContent').html('<div class="alert alert-danger">Error loading job details</div>');
        });
}
```

**Server Response** (from `food_servings_uploads()` route):
```python
if action == 'job_details':
    job_id = request.args.get('job_id')
    job = ServingUploadJob.query.filter_by(job_id=job_id, created_by=current_user.id).first()
    if job:
        return jsonify({
            'job_id': job.job_id,
            'filename': job.filename,
            'status': job.status,
            'total_rows': job.total_rows,
            'processed_rows': job.processed_rows,
            'successful_rows': job.successful_rows,
            'failed_rows': job.failed_rows,
            'created_at': job.created_at.isoformat(),
            'error_message': job.error_message
        })
```

#### Modal Content Display:
```html
<div class="modal fade" id="jobDetailsModal">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Job Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="jobDetailsContent">
                <!-- Dynamic content populated by JavaScript -->
            </div>
        </div>
    </div>
</div>
```

### 7. Pagination System

#### Pagination Controls
```html
{% if jobs.pages > 1 %}
<nav aria-label="Upload jobs pagination">
    <ul class="pagination justify-content-center">
        {% if jobs.has_prev %}
            <li class="page-item">
                <a class="page-link" href="{{ url_for('admin.food_servings_uploads', tab='history', page=jobs.prev_num) }}">Previous</a>
            </li>
        {% endif %}
        
        {% for page_num in jobs.iter_pages() %}
            {% if page_num %}
                {% if page_num != jobs.page %}
                    <li class="page-item">
                        <a class="page-link" href="{{ url_for('admin.food_servings_uploads', tab='history', page=page_num) }}">{{ page_num }}</a>
                    </li>
                {% else %}
                    <li class="page-item active">
                        <span class="page-link">{{ page_num }}</span>
                    </li>
                {% endif %}
            {% endif %}
        {% endfor %}
        
        {% if jobs.has_next %}
            <li class="page-item">
                <a class="page-link" href="{{ url_for('admin.food_servings_uploads', tab='history', page=jobs.next_num) }}">Next</a>
            </li>
        {% endif %}
    </ul>
</nav>
{% endif %}
```

### 8. Real-Time Updates

#### Progress Polling (for active jobs)
```javascript
// Check for jobs with 'processing' status
if (document.querySelectorAll('.badge.bg-info').length > 0) {
    // Poll for updates every 3 seconds
    setInterval(function() {
        // Refresh job status without full page reload
        fetch('/admin/food-servings/uploads?action=status_check')
            .then(response => response.json())
            .then(data => {
                updateJobStatuses(data);
            });
    }, 3000);
}
```

### 9. Error Handling

#### No Jobs State
When no upload jobs exist:
```html
<div class="text-center py-5">
    <i class="fas fa-history fa-4x text-muted mb-3"></i>
    <h5 class="text-muted">No upload jobs found</h5>
    <p class="text-muted">Upload some serving data to see the history here.</p>
    <a href="#" class="btn btn-primary" onclick="switchToUploadTab()">
        <i class="fas fa-upload me-2"></i>Upload Now
    </a>
</div>
```

#### Error States
- **Job Load Errors**: Graceful error messages in job details modal
- **Network Errors**: Retry mechanisms for AJAX requests
- **Authentication Errors**: Redirect to login if session expires

### 10. Mobile Responsiveness

#### Responsive Table
```html
<div class="table-responsive">
    <table class="table table-hover">
        <!-- On mobile, some columns may be hidden -->
        <thead>
            <tr>
                <th>File & Date</th>
                <th>Status</th>
                <th class="d-none d-md-table-cell">Progress</th>
                <th class="d-none d-lg-table-cell">Total Rows</th>
                <th class="d-none d-lg-table-cell">Success</th>
                <th class="d-none d-lg-table-cell">Failed</th>
                <th>Actions</th>
            </tr>
        </thead>
    </table>
</div>
```

## Summary

When a user clicks the Upload History tab, the system:

1. **Activates Bootstrap tab** - Switches UI to history view
2. **Executes database queries** - Fetches paginated job data for current user
3. **Renders job table** - Displays jobs with status, progress, and statistics
4. **Enables interactions** - Provides job details, pagination, and real-time updates
5. **Handles edge cases** - Shows appropriate messages for empty states and errors

The entire process is seamless, responsive, and provides comprehensive visibility into all bulk upload operations performed by the current admin user.
