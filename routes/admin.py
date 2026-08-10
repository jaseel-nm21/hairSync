"""
Admin Routes
Handles administrative dashboard, NGO approval/rejection workflows,
and system user management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import role_required
from models.user import User
from models.ngo import NGO
from models.donor import Donor
from models.recipient import Recipient

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    """Admin centralized metrics, pending NGO review queue, and recent users."""
    role_counts = User.get_role_counts()
    pending_ngo_count = NGO.get_pending_count()
    pending_ngos = NGO.get_all(approval_status='pending')
    recent_users = User.get_all()[:8]

    return render_template(
        'admin/dashboard.html',
        counts=role_counts,
        pending_ngo_count=pending_ngo_count,
        pending_ngos=pending_ngos,
        recent_users=recent_users
    )


@admin_bp.route('/ngos')
@role_required('admin')
def ngos():
    """Manage NGOs and filter by approval status."""
    status_filter = request.args.get('status', 'all').lower()
    if status_filter in ['pending', 'approved', 'rejected']:
        ngo_list = NGO.get_all(approval_status=status_filter)
    else:
        status_filter = 'all'
        ngo_list = NGO.get_all()

    return render_template(
        'admin/ngos.html',
        ngos=ngo_list,
        status_filter=status_filter,
        pending_count=NGO.get_pending_count()
    )


@admin_bp.route('/ngos/<int:ngo_id>/approve', methods=['POST'])
@role_required('admin')
def approve_ngo(ngo_id):
    """Approve a pending NGO registration."""
    ngo = NGO.get_by_id(ngo_id)
    if not ngo:
        flash('NGO record not found.', 'danger')
        return redirect(url_for('admin.ngos'))

    NGO.update_approval_status(ngo_id, 'approved')
    flash(f"NGO '{ngo['organization_name']}' has been officially approved! They now have full platform access.", 'success')
    return redirect(request.referrer or url_for('admin.ngos'))


@admin_bp.route('/ngos/<int:ngo_id>/reject', methods=['POST'])
@role_required('admin')
def reject_ngo(ngo_id):
    """Reject an NGO registration."""
    ngo = NGO.get_by_id(ngo_id)
    if not ngo:
        flash('NGO record not found.', 'danger')
        return redirect(url_for('admin.ngos'))

    NGO.update_approval_status(ngo_id, 'rejected')
    flash(f"NGO '{ngo['organization_name']}' registration has been rejected.", 'warning')
    return redirect(request.referrer or url_for('admin.ngos'))


@admin_bp.route('/users')
@role_required('admin')
def users():
    """View and manage system users."""
    role_filter = request.args.get('role', 'all').lower()
    if role_filter in ['donor', 'ngo', 'recipient', 'admin']:
        user_list = User.get_all(role=role_filter)
    else:
        role_filter = 'all'
        user_list = User.get_all()

    return render_template(
        'admin/users.html',
        users=user_list,
        role_filter=role_filter
    )


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_user_status(user_id):
    """Toggle user active / inactive status."""
    # Prevent admin from deactivating their own account
    if user_id == session.get('user_id'):
        flash('You cannot deactivate your own administrative account.', 'danger')
        return redirect(request.referrer or url_for('admin.users'))

    user = User.get_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))

    new_status = 'inactive' if user['status'] == 'active' else 'active'
    User.update_status(user_id, new_status)
    flash(f"Account for {user['name']} has been marked as {new_status}.", 'info')
    return redirect(request.referrer or url_for('admin.users'))


@admin_bp.route('/donors')
@role_required('admin')
def donors():
    """View all registered donors and their hair profiles."""
    all_donors = Donor.get_all()
    return render_template('admin/donors.html', donors=all_donors)


@admin_bp.route('/recipients')
@role_required('admin')
def recipients():
    """View all registered wig recipients."""
    all_recipients = Recipient.get_all()
    return render_template('admin/recipients.html', recipients=all_recipients)
