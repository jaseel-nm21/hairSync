"""
NGO Routes (Module 1 & Module 2)
Handles NGO dashboard with pending verification alerts, organization profile management,
and physical hair donation center management (CRUD, ownership validation, status checks).
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import role_required
from models.user import User
from models.ngo import NGO
from models.donation_center import DonationCenter

ngo_bp = Blueprint('ngo', __name__, url_prefix='/ngo')


def ngo_approved_required(f):
    """Ensure NGO is logged in and officially approved before managing donation centers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        if session.get('role') != 'ngo':
            flash('Access denied. NGO credentials required.', 'danger')
            return redirect(url_for('index'))

        user_id = session.get('user_id')
        profile = NGO.get_by_user_id(user_id)
        if not profile or profile.get('approval_status') != 'approved':
            flash('Access restricted: Your organization account is pending administrative approval. You cannot manage donation centers until verified.', 'warning')
            return redirect(url_for('ngo.dashboard'))

        return f(*args, **kwargs)
    return decorated_function


def _validate_center_payload(form_data):
    """Validates form input for donation center creation and editing."""
    errors = []
    center_name = form_data.get('center_name', '').strip()
    address = form_data.get('address', '').strip()
    district = form_data.get('district', '').strip()
    city = form_data.get('city', '').strip()
    state = form_data.get('state', 'Kerala').strip()
    pincode = form_data.get('pincode', '').strip()
    phone = form_data.get('phone', '').strip()
    email = form_data.get('email', '').strip()
    opening_time = form_data.get('opening_time', '').strip()
    closing_time = form_data.get('closing_time', '').strip()
    working_days = form_data.get('working_days', '').strip()
    description = form_data.get('description', '').strip()
    lat_str = form_data.get('latitude', '').strip()
    lng_str = form_data.get('longitude', '').strip()
    status = form_data.get('status', 'Active').strip()

    if not center_name:
        errors.append("Center Name is required.")
    if not address:
        errors.append("Address is required.")
    if not district:
        errors.append("District is required.")
    if not city:
        errors.append("City is required.")
    if not pincode:
        errors.append("Pincode is required.")
    elif not pincode.isdigit() or len(pincode) != 6:
        errors.append("Pincode must be a 6-digit numeric code.")
    if not phone:
        errors.append("Phone number is required.")
    if not opening_time:
        errors.append("Opening Time is required.")
    if not closing_time:
        errors.append("Closing Time is required.")
    if not working_days:
        errors.append("Working Days is required.")

    lat_val = None
    if lat_str:
        try:
            lat_val = float(lat_str)
            if not (-90.0 <= lat_val <= 90.0):
                errors.append("Latitude must be between -90.0 and 90.0 degrees.")
        except ValueError:
            errors.append("Latitude must be a valid numeric decimal.")

    lng_val = None
    if lng_str:
        try:
            lng_val = float(lng_str)
            if not (-180.0 <= lng_val <= 180.0):
                errors.append("Longitude must be between -180.0 and 180.0 degrees.")
        except ValueError:
            errors.append("Longitude must be a valid numeric decimal.")

    if status not in ['Active', 'Inactive', 'Pending', 'Approved', 'Rejected']:
        status = 'Active'

    cleaned = {
        'center_name': center_name,
        'address': address,
        'district': district,
        'city': city,
        'state': state or 'Kerala',
        'pincode': pincode,
        'phone': phone,
        'email': email,
        'opening_time': opening_time,
        'closing_time': closing_time,
        'working_days': working_days,
        'description': description,
        'latitude': lat_val,
        'longitude': lng_val,
        'status': status
    }
    return errors, cleaned


@ngo_bp.route('/dashboard')
@role_required('ngo')
def dashboard():
    """NGO dashboard displaying verification status, center statistics, and quick action links."""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    profile = NGO.get_by_user_id(user_id)

    # Sync session approval status
    if profile:
        session['approval_status'] = profile['approval_status']

    is_approved = profile and profile.get('approval_status') == 'approved'

    # Get donation center statistics for this NGO
    center_counts = DonationCenter.get_counts(profile['id']) if profile else {
        'total': 0, 'active': 0, 'inactive': 0, 'pending': 0, 'rejected': 0, 'approved': 0
    }
    recent_centers = DonationCenter.get_by_ngo_id(profile['id'])[:4] if (profile and is_approved) else []

    return render_template(
        'ngo/dashboard.html',
        user=user,
        profile=profile,
        is_approved=is_approved,
        center_counts=center_counts,
        recent_centers=recent_centers
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


@ngo_bp.route('/donation-centers')
@role_required('ngo')
@ngo_approved_required
def donation_centers():
    """List and manage donation centers owned by the logged-in NGO."""
    user_id = session.get('user_id')
    profile_data = NGO.get_by_user_id(user_id)
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'all').strip()

    centers = DonationCenter.get_by_ngo_id(
        ngo_id=profile_data['id'],
        search=search_query if search_query else None,
        status=status_filter if status_filter != 'all' else None
    )
    counts = DonationCenter.get_counts(profile_data['id'])

    return render_template(
        'ngo/donation_centers/index.html',
        centers=centers,
        counts=counts,
        search_query=search_query,
        status_filter=status_filter,
        profile=profile_data
    )


@ngo_bp.route('/donation-centers/add', methods=['GET', 'POST'])
@role_required('ngo')
@ngo_approved_required
def add_center():
    """Create a new donation center for the approved NGO."""
    user_id = session.get('user_id')
    profile_data = NGO.get_by_user_id(user_id)

    if request.method == 'POST':
        errors, cleaned = _validate_center_payload(request.form)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'ngo/donation_centers/form.html',
                action='add',
                center=request.form,
                profile=profile_data
            )

        new_id = DonationCenter.create(
            ngo_id=profile_data['id'],
            center_name=cleaned['center_name'],
            address=cleaned['address'],
            district=cleaned['district'],
            city=cleaned['city'],
            state=cleaned['state'],
            pincode=cleaned['pincode'],
            phone=cleaned['phone'],
            email=cleaned['email'],
            opening_time=cleaned['opening_time'],
            closing_time=cleaned['closing_time'],
            working_days=cleaned['working_days'],
            description=cleaned['description'],
            latitude=cleaned['latitude'],
            longitude=cleaned['longitude'],
            status=cleaned['status']
        )
        flash(f"Donation Center '{cleaned['center_name']}' created successfully!", 'success')
        return redirect(url_for('ngo.donation_centers'))

    # Default preset from NGO profile
    preset = {
        'state': 'Kerala',
        'district': profile_data['district'] if profile_data else '',
        'phone': profile_data['phone'] if profile_data else '',
        'email': profile_data['email'] if profile_data else '',
        'opening_time': '09:00',
        'closing_time': '17:00',
        'working_days': 'Monday - Saturday',
        'status': 'Active'
    }
    return render_template(
        'ngo/donation_centers/form.html',
        action='add',
        center=preset,
        profile=profile_data
    )


@ngo_bp.route('/donation-centers/<int:center_id>')
@role_required('ngo')
def view_center(center_id):
    """View details of a specific donation center owned by this NGO."""
    user_id = session.get('user_id')
    profile_data = NGO.get_by_user_id(user_id)
    center = DonationCenter.get_by_id(center_id)

    if not center or center['ngo_id'] != profile_data['id']:
        flash('Access denied: You can only view your own donation centers.', 'danger')
        return render_template('errors/403.html', message="ACCESS DENIED: You cannot view another NGO's donation center."), 403

    return render_template(
        'ngo/donation_centers/view.html',
        center=center,
        profile=profile_data
    )


@ngo_bp.route('/donation-centers/<int:center_id>/edit', methods=['GET', 'POST'])
@role_required('ngo')
@ngo_approved_required
def edit_center(center_id):
    """Edit donation center details with strict NGO ownership verification."""
    user_id = session.get('user_id')
    profile_data = NGO.get_by_user_id(user_id)
    center = DonationCenter.get_by_id(center_id)

    if not center:
        flash('Donation center not found.', 'danger')
        return redirect(url_for('ngo.donation_centers'))

    # Strict security check: MUST belong to this NGO
    if center['ngo_id'] != profile_data['id']:
        flash("ACCESS DENIED: You do not have permission to modify another NGO's donation center.", 'danger')
        return render_template('errors/403.html', message="ACCESS DENIED: You cannot modify another NGO's donation center."), 403

    if request.method == 'POST':
        errors, cleaned = _validate_center_payload(request.form)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'ngo/donation_centers/form.html',
                action='edit',
                center=request.form,
                center_id=center_id,
                profile=profile_data
            )

        success = DonationCenter.update(
            center_id=center_id,
            center_name=cleaned['center_name'],
            address=cleaned['address'],
            district=cleaned['district'],
            city=cleaned['city'],
            state=cleaned['state'],
            pincode=cleaned['pincode'],
            phone=cleaned['phone'],
            email=cleaned['email'],
            opening_time=cleaned['opening_time'],
            closing_time=cleaned['closing_time'],
            working_days=cleaned['working_days'],
            description=cleaned['description'],
            latitude=cleaned['latitude'],
            longitude=cleaned['longitude'],
            status=cleaned['status'],
            ngo_id=profile_data['id']
        )

        if not success:
            flash("ACCESS DENIED: Ownership validation failed.", 'danger')
            return render_template('errors/403.html', message="ACCESS DENIED: Ownership validation failed."), 403

        flash(f"Donation Center '{cleaned['center_name']}' updated successfully!", 'success')
        return redirect(url_for('ngo.donation_centers'))

    return render_template(
        'ngo/donation_centers/form.html',
        action='edit',
        center=center,
        center_id=center_id,
        profile=profile_data
    )


@ngo_bp.route('/donation-centers/<int:center_id>/delete', methods=['POST'])
@role_required('ngo')
@ngo_approved_required
def delete_center(center_id):
    """Delete a donation center with strict NGO ownership verification."""
    user_id = session.get('user_id')
    profile_data = NGO.get_by_user_id(user_id)
    center = DonationCenter.get_by_id(center_id)

    if not center:
        flash('Donation center not found.', 'danger')
        return redirect(url_for('ngo.donation_centers'))

    # Strict security check: MUST belong to this NGO
    if center['ngo_id'] != profile_data['id']:
        flash("ACCESS DENIED: You cannot delete another NGO's donation center.", 'danger')
        return render_template('errors/403.html', message="ACCESS DENIED: You cannot delete another NGO's donation center."), 403

    success = DonationCenter.delete(center_id, ngo_id=profile_data['id'])
    if not success:
        flash("ACCESS DENIED: Deletion unauthorized.", 'danger')
        return render_template('errors/403.html', message="ACCESS DENIED: Deletion unauthorized."), 403

    flash(f"Donation center '{center['center_name']}' has been deleted successfully.", 'info')
    return redirect(url_for('ngo.donation_centers'))

