"""
Donor Routes
Handles Donor dashboard, hair profile view, photo upload, and profile editing.
"""

import os
import time
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import role_required
from models.user import User
from models.donor import Donor
from config import Config

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@donor_bp.route('/dashboard')
@role_required('donor')
def dashboard():
    """Donor dashboard overview with profile completion summary."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    profile = Donor.get_by_user_id(user_id)

    # Calculate profile completion percentage
    fields = [
        profile.get('phone') if profile else None,
        profile.get('address') if profile else None,
        profile.get('district') if profile else None,
        profile.get('hair_length') if profile else None,
        profile.get('hair_type') if profile else None,
        profile.get('hair_condition') if profile else None,
        profile.get('photo') if profile else None
    ]
    completed_fields = sum(1 for f in fields if f)
    completion_percentage = int((completed_fields / len(fields)) * 100)

    return render_template(
        'donor/dashboard.html',
        user=user,
        profile=profile,
        completion_percentage=completion_percentage
    )


@donor_bp.route('/profile', methods=['GET', 'POST'])
@role_required('donor')
def profile():
    """View and update donor profile information including hair specs and photo."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    profile_data = Donor.get_by_user_id(user_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        district = request.form.get('district', '').strip()
        hair_length = request.form.get('hair_length', '').strip()
        hair_type = request.form.get('hair_type', '').strip()
        hair_condition = request.form.get('hair_condition', '').strip()

        # Validation
        if not name or not phone or not address or not district:
            flash('Name, phone, address, and district are mandatory fields.', 'danger')
            return render_template('donor/profile.html', user=user, profile=profile_data)

        # Handle file upload
        photo_filename = profile_data.get('photo') if profile_data else None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    safe_name = f"donor_{user_id}_{int(time.time())}.{ext}"
                    filepath = os.path.join(Config.UPLOAD_FOLDER, safe_name)
                    file.save(filepath)
                    photo_filename = safe_name
                else:
                    flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP.', 'danger')
                    return render_template('donor/profile.html', user=user, profile=profile_data)

        # Update User name if changed
        if name != user['name']:
            User.update_name_email(user_id, name, user['email'])
            session['user_name'] = name

        # Update or create donor profile
        Donor.create_or_update(
            user_id=user_id,
            phone=phone,
            address=address,
            district=district,
            hair_length=hair_length if hair_length else None,
            hair_type=hair_type if hair_type else None,
            hair_condition=hair_condition if hair_condition else None,
            photo=photo_filename
        )

        flash('Your donor profile has been updated successfully!', 'success')
        return redirect(url_for('donor.dashboard'))

    return render_template('donor/profile.html', user=user, profile=profile_data)
