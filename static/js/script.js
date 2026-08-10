/**
 * HairSync Frontend JavaScript
 * Handles dynamic role forms, client-side validation, image previews, and UI polish.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Password Visibility Toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);
            const icon = this.querySelector('i');

            if (targetInput) {
                if (targetInput.type === 'password') {
                    targetInput.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                } else {
                    targetInput.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                }
            }
        });
    });

    // 2. Dynamic Registration Form Role Switcher
    const roleSelector = document.getElementById('registerRoleSelect');
    if (roleSelector) {
        function updateRoleFields() {
            const selectedRole = roleSelector.value;
            const donorFields = document.getElementById('donorFields');
            const ngoFields = document.getElementById('ngoFields');
            const recipientFields = document.getElementById('recipientFields');
            const roleBadge = document.getElementById('selectedRoleBadge');

            // Hide all first
            if (donorFields) donorFields.style.display = 'none';
            if (ngoFields) ngoFields.style.display = 'none';
            if (recipientFields) recipientFields.style.display = 'none';

            // Reset required attributes where appropriate
            toggleRequired(donorFields, false);
            toggleRequired(ngoFields, false);
            toggleRequired(recipientFields, false);

            if (selectedRole === 'donor' && donorFields) {
                donorFields.style.display = 'block';
                toggleRequired(donorFields, true);
                if (roleBadge) {
                    roleBadge.textContent = 'Registering as Hair Donor';
                    roleBadge.className = 'badge badge-role-donor px-3 py-2';
                }
            } else if (selectedRole === 'ngo' && ngoFields) {
                ngoFields.style.display = 'block';
                toggleRequired(ngoFields, true);
                if (roleBadge) {
                    roleBadge.textContent = 'Registering as NGO / Donation Organization';
                    roleBadge.className = 'badge badge-role-ngo px-3 py-2';
                }
            } else if (selectedRole === 'recipient' && recipientFields) {
                recipientFields.style.display = 'block';
                toggleRequired(recipientFields, true);
                if (roleBadge) {
                    roleBadge.textContent = 'Registering as Wig Recipient';
                    roleBadge.className = 'badge badge-role-recipient px-3 py-2';
                }
            }
        }

        function toggleRequired(container, isRequired) {
            if (!container) return;
            const requiredInputs = container.querySelectorAll('[data-role-required="true"]');
            requiredInputs.forEach(input => {
                input.required = isRequired;
            });
        }

        roleSelector.addEventListener('change', updateRoleFields);
        updateRoleFields(); // Run on initial page load
    }

    // 3. Photo Upload Preview (Donor Profile)
    const photoInput = document.getElementById('photoInput');
    const photoPreview = document.getElementById('photoPreview');
    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size exceeds 5MB limit. Please choose a smaller image.');
                    this.value = '';
                    return;
                }
                const reader = new FileReader();
                reader.onload = function (e) {
                    photoPreview.src = e.target.result;
                    photoPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 4. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // 5. Confirmation for Admin Actions
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(element => {
        element.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
