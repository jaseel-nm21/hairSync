"""
NGO Routes
Handles NGO dashboard with pending verification alerts and organization profile management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import role_required
from models.user import User
from models.ngo import NGO

ngo_bp = Blueprint('ngo', __name__, url_prefix='/ngo')


@ngo_bp.route('/dashboard')
@role_required('ngo')
def dashboard():
    """NGO dashboard displaying verification status, organization preview, and future module hooks."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    profile = NGO.get_by_user_id(user_id)

    # Sync session approval status
    if profile:
        session['approval_status'] = profile['approval_status']

    is_approved = profile and profile.get('approval_status') == 'approved'

    return render_template(
        'ngo/dashboard.html',
        user=user,
        profile=profile,
        is_approved=is_approved
    )


@ngo_bp.route('/profile', methods=['GET', 'POST'])
@role_required('ngo')
def profile():
    """View and edit NGO organization details."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    profile_data = NGO.get_by_user_id(user_id)

    if request.method == 'POST':
        org_name = request.form.get('org_name', '').strip()
        reg_number = request.form.get('reg_number', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        district = request.form.get('district', '').strip()
        description = request.form.get('description', '').strip()

        # Validation
        if not org_name or not reg_number or not phone or not email or not address or not district:
            flash('Organization name, registration number, phone, email, address, and district are mandatory.', 'danger')
            return render_template('ngo/profile.html', user=user, profile=profile_data)

        # Check registration number uniqueness if changed
        if profile_data and profile_data['registration_number'] != reg_number:
            existing = NGO.get_by_reg_no(reg_number)
            if existing and existing['user_id'] != user_id:
                flash('Another organization is already registered with this official registration number.', 'danger')
                return render_template('ngo/profile.html', user=user, profile=profile_data)

        # Update User name if organization name changed
        if org_name != user['name']:
            User.update_name_email(user_id, org_name, user['email'])
            session['user_name'] = org_name

        # Update profile
        NGO.create_or_update(
            user_id=user_id,
            organization_name=org_name,
            registration_number=reg_number,
            phone=phone,
            email=email,
            address=address,
            district=district,
            description=description
        )

        flash('Organization profile updated successfully!', 'success')
        return redirect(url_for('ngo.dashboard'))

    return render_template('ngo/profile.html', user=user, profile=profile_data)
