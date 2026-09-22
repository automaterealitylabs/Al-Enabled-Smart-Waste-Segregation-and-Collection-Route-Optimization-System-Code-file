import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(file, prefix="img"):
    """
    Saves a file temporarily, uploads to Cloudinary if configured, 
    cleans up the temporary file, and returns the URL.
    """
    is_prod = os.getenv('RENDER') == 'true' or os.getenv('FLASK_ENV') == 'production'

    # Ensure upload directory exists
    upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{prefix}_{uuid.uuid4().hex[:10]}.{ext}"
    saved_path = os.path.join(upload_dir, unique_filename)
    
    # Save file temporarily
    file.save(saved_path)

    cloudinary_url = None
    try:
        # Cloudinary Persistent Storage Configuration
        cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME')
        api_key = current_app.config.get('CLOUDINARY_API_KEY')
        api_secret = current_app.config.get('CLOUDINARY_API_SECRET')

        missing_cloudinary = [k for k, v in [
            ('CLOUDINARY_CLOUD_NAME', cloud_name),
            ('CLOUDINARY_API_KEY', api_key),
            ('CLOUDINARY_API_SECRET', api_secret)
        ] if not v]

        if missing_cloudinary:
            if is_prod:
                raise ValueError(
                    f"Cloudinary persistent storage configuration is incomplete in production. "
                    f"Missing environment variables: {', '.join(missing_cloudinary)}. "
                    f"Render's local filesystem cannot be used for permanent image storage. "
                    f"Please configure Cloudinary credentials in your Render dashboard."
                )
            else:
                # Temporary development fallback only
                cloudinary_url = f"/static/uploads/{unique_filename}"
                current_app.logger.warning(
                    f"Development mode fallback: Cloudinary variables ({', '.join(missing_cloudinary)}) not set. "
                    f"Serving image locally from {cloudinary_url}."
                )
        else:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
            try:
                upload_result = cloudinary.uploader.upload(saved_path, public_id=unique_filename.split('.')[0])
                cloudinary_url = upload_result.get("secure_url")
            except Exception as upload_err:
                if is_prod:
                    raise RuntimeError(f"Cloudinary upload failed in production: {str(upload_err)}")
                else:
                    cloudinary_url = f"/static/uploads/{unique_filename}"

            # Always clean up temporary local file after successful Cloudinary upload
            if os.path.exists(saved_path):
                os.remove(saved_path)
                
    except Exception as e:
        # In production, ensure no temporary files linger on error
        if is_prod and os.path.exists(saved_path):
            try:
                os.remove(saved_path)
            except Exception:
                pass
        raise e

    return cloudinary_url
