"""
Citizen Waste Reporting API Route
"""
from flask import Blueprint, request, jsonify, session
from database.models import WasteReport, Dumpyard
from backend.utils import allowed_file, upload_image
from route_optimization.optimizer import RouteOptimizer

report_bp = Blueprint('report', __name__, url_prefix='/api/reports')

@report_bp.route('/submit', methods=['POST'])
def submit_report():
    """Submit a new garbage report from an authenticated citizen."""
    # 1. Require authenticated user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Authentication required to submit a report.'}), 401

    # 2. Validate image
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided in request.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected image file.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP.'}), 400

    # 3. Read form fields
    description = request.form.get('description', '').strip()
    address = request.form.get('address', '').strip()
    waste_type = request.form.get('waste_type', '').strip()
    
    try:
        latitude = float(request.form.get('latitude', 0.0))
        longitude = float(request.form.get('longitude', 0.0))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid latitude or longitude.'}), 400

    # 4. Upload the image using shared helper
    try:
        image_url = upload_image(file, prefix="report")
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to upload image: {str(e)}'}), 500

    # 5. Calculate nearest active dumpyard
    all_dumpyards = Dumpyard.get_all()
    active_dumpyards = [d for d in all_dumpyards if d.status == 'ACTIVE']
    
    nearest_dumpyard_id = None
    if active_dumpyards:
        min_dist = float('inf')
        for d in active_dumpyards:
            dist = RouteOptimizer.haversine_distance(latitude, longitude, d.latitude, d.longitude)
            if dist < min_dist:
                min_dist = dist
                nearest_dumpyard_id = d.id

    # 6. Create WasteReport
    report = WasteReport.create(
        citizen_id=user_id,
        image_url=image_url,
        description=description,
        waste_type=waste_type,
        latitude=latitude,
        longitude=longitude,
        address=address,
        assigned_dumpyard_id=nearest_dumpyard_id
    )

    if not report:
        return jsonify({'success': False, 'message': 'Database error while creating report.'}), 500

    return jsonify({
        'success': True,
        'message': 'Waste report submitted successfully.',
        'report_id': report.id,
        'status': report.status,
        'assigned_dumpyard_id': report.assigned_dumpyard_id
    }), 201
