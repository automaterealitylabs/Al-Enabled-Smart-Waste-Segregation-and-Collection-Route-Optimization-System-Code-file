"""
Waste Classification API Routes
"""
import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app
from database.models import WasteDetection
from ml_model.predict import WasteClassifier

from backend.utils import allowed_file, upload_image

classification_bp = Blueprint('classification', __name__, url_prefix='/api')

classifier = WasteClassifier()

@classification_bp.route('/classify', methods=['POST'])
def classify_waste():
    """Accepts uploaded waste image, runs AI classification, saves record to DB, returns results."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided in request.'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected image file.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP.'}), 400

    try:
        cloudinary_url = upload_image(file, prefix="waste")
        
        # We need the local path for ML Classification before it gets deleted, 
        # but upload_image deletes it on successful cloudinary upload.
        # Wait, the ML classification needs a local file. We should save it temporarily here 
        # or have the util not delete it until we say so.
        # Actually, let's fix the ML classification step.
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"waste_temp_{uuid.uuid4().hex[:10]}.{ext}"
        saved_path = os.path.join(upload_dir, unique_filename)
        file.seek(0)
        file.save(saved_path)
        
        # Run AI Classification Pipeline
        result = classifier.classify_image(saved_path)
        
        # Now we upload the file and get Cloudinary URL.
        # file.seek(0) to reset the pointer for upload_image
        file.seek(0)
        cloudinary_url = upload_image(file, prefix="waste")
        
        if os.path.exists(saved_path):
            os.remove(saved_path)


        # Store Detection Record in Database
        user_id = session.get('user_id')
        
        db_record = WasteDetection.create(
            category_name=result['category_name'],
            waste_type=result['waste_type'],
            bin_color=result['recommended_bin_color'],
            confidence_score=result['confidence_score'],
            image_path=cloudinary_url,
            disposal_suggestion=result['disposal_suggestion'],
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'detection_id': db_record.id if db_record else None,
            'user_id': user_id,
            'category_name': result['category_name'],
            'waste_type': result['waste_type'],
            'recommended_bin_color': result['recommended_bin_color'],
            'disposal_suggestion': result['disposal_suggestion'],
            'confidence_score': result['confidence_score'],
            'confidence_percent': result['confidence_percent'],
            'image_url': cloudinary_url,
            'detected_at': str(db_record.detected_at) if (db_record and db_record.detected_at) else None,
            'stored_in_db': True
        }), 200

    except Exception as e:
        if 'saved_path' in locals() and os.path.exists(saved_path):
            try:
                os.remove(saved_path)
            except Exception:
                pass
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }), 500



@classification_bp.route('/detections', methods=['GET'])
def get_detections():
    """Fetches recent waste classification records from the database."""
    recent_records = WasteDetection.get_recent(limit=15)
    return jsonify({
        'success': True,
        'count': len(recent_records),
        'detections': [r.to_dict() for r in recent_records]
    }), 200
