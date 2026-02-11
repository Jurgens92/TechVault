# TechVault Code Review: Workflow, UX/UI & Bugs

**Reviewer:** Code review focused on workflow, UX/UI, and bugs
**Date:** 2026-02-11
**Scope:** Full-stack review (Django REST backend + React/TypeScript frontend)
**Context:** Reviewing as an IT documentation platform comparable to ITGlue/Hudu

---

## Project Summary

TechVault is an enterprise-grade IT documentation platform with multi-tenant organization management, contacts, password vault, configurations, network devices, servers, endpoints, software/license tracking, VoIP, backups, infrastructure diagrams, reporting, and system backup/restore. Built with Django 5 + DRF backend, React 18 + TypeScript frontend, PostgreSQL database. Features 2FA, soft delete, version history, and role-based access control.

---

## CRITICAL FINDINGS

### 1. Multi-Tenant Isolation Is Not Enforced

**Category:** Security / Workflow
**Location:** `backend/core/permissions.py:8-37`, `backend/core/views.py:25-39`

All three permission classes (`IsOrganizationMember`, `IsOrganizationAdmin`, `IsOrganizationOwner`) are identical and only check `is_authenticated`. The `OrganizationMember` model with roles (owner/admin/member/viewer) exists but is never checked. Any authenticated user can see and modify all organizations' data.

```python
# permissions.py - All three classes do this:
def has_object_permission(self, request, view, obj):
    """All authenticated users have access to all objects."""
    return request.user and request.user.is_authenticated
```

```python
# views.py - No filtering by membership:
def get_user_organizations(self):
    return Organization.objects.all()

def filter_by_organization_access(self, queryset):
    return queryset
```

**Impact:** For an MSP-oriented system, this means Client A's data is visible to Client B. The data model supports proper isolation -- it just isn't wired up.

**Recommendation:** Implement actual membership checks:
```python
def filter_by_organization_access(self, queryset):
    user_orgs = OrganizationMember.objects.filter(
        user=self.request.user
    ).values_list('organization_id', flat=True)
    if hasattr(queryset.model, 'organization'):
        return queryset.filter(organization__in=user_orgs)
    return queryset
```

---

### 2. 2FA Setup Flow Has State Inconsistency

**Category:** Security / Workflow
**Location:** `backend/users/twofa_views.py:36-73`, `frontend/src/pages/TwoFactorSetup.tsx`

The 2FA secret is saved to the database before the user verifies it. If a user starts setup but doesn't finish, their account has a secret stored but 2FA not enabled. The frontend navigates to `/dashboard` after setup without ensuring an organization is selected.

**Recommendation:** Store the secret in a temporary session/cache until verification succeeds, then persist it.

---

### 3. Internet Connections Deleted on Network Device Update

**Category:** Data Integrity / Bug
**Location:** `backend/core/serializers.py:191-203`

When updating a NetworkDevice, all existing InternetConnection records are deleted and recreated:

```python
instance.internet_connections.all().delete()
for conn_data in connections_data:
    InternetConnection.objects.create(...)
```

**Impact:** External references to connection IDs break, audit trails are lost, and version history snapshots become stale.

**Recommendation:** Use update-or-create logic instead of delete-all-recreate.

---

### 4. Account Lockout May Not Be Enforced

**Category:** Security
**Location:** `backend/users/auth_views.py:71-101`, `backend/users/tests/test_login_security.py:187`

Tests explicitly note: "TODO: Should implement rate limiting and account lockout" and flag this as a security vulnerability. 10 failed login attempts succeed without throttling despite the code appearing to implement protections.

**Recommendation:** Verify that the `LoginRateThrottle` is actually applied to the login endpoint and test it end-to-end.

---

## HIGH-SEVERITY FINDINGS

### 5. Login Page Has No Registration Link

**Category:** Workflow / UX
**Location:** `frontend/src/pages/Login.tsx`

The Login page has no "Sign up" link. New users cannot discover registration from the login screen. The Register page links back to Login, but the inverse is missing.

**Recommendation:** Add "Don't have an account? Sign up" link below the login form.

---

### 6. Organization Context Race Condition

**Category:** Bug
**Location:** `frontend/src/contexts/OrganizationContext.tsx:67-70`

`loadOrganizations()` triggers on `isAuthenticated` change but doesn't guard against auth not being fully initialized. Dashboard pages may render with "no organization selected" even when organizations exist.

**Recommendation:** Add a guard that waits for auth initialization to complete before loading organizations.

---

### 7. Empty Organization State Is a Dead End

**Category:** UX
**Location:** Multiple list pages (Passwords, Documentations, Locations, Endpoints, etc.)

The `EmptyOrgState` component shows "No Organization Selected" with no call-to-action. Users are stuck with no button to navigate to organization selection or creation.

**Recommendation:** Add a CTA button that links to the Organizations page or opens the org selector in the sidebar.

---

### 8. Form Validation Errors Not Displayed

**Category:** UX / Bug
**Location:** All form pages (PasswordForm, OrganizationForm, ContactForm, etc.)

Forms only handle `err.response?.data?.detail` from the API. Field-specific validation errors like `{name: ['This field is required']}` are silently discarded. Users have to guess which field is wrong.

**Recommendation:** Implement a shared error parsing utility that maps API field errors to form fields.

---

### 9. Soft Delete + Unique Constraints Conflict

**Category:** Data Integrity
**Location:** Location, SoftwareAssignment, VoIPAssignment models

`unique_together` constraints include soft-deleted records. If you delete a Location named "HQ" and try to create a new one with the same name, you get a constraint violation. The deleted record is invisible to users but still blocks creation.

**Recommendation:** Use partial unique indexes that exclude soft-deleted records:
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['organization', 'name'],
            condition=models.Q(is_deleted=False),
            name='unique_active_location_name'
        )
    ]
```

---

### 10. Missing CRUD Endpoints for Assignments

**Category:** Workflow
**Location:** `backend/api/urls.py`

`SoftwareAssignment` and `VoIPAssignment` have models and serializers but no registered API endpoints. Users cannot directly manage individual assignments -- only through parent entity updates.

**Recommendation:** Register ViewSets for both assignment models in the router.

---

### 11. No Pagination in Frontend Lists

**Category:** UX / Performance
**Location:** All frontend list pages

The API returns paginated responses, but the frontend ignores pagination and loads all records at once. For an MSP with hundreds of clients and thousands of assets, this will degrade quickly.

**Recommendation:** Implement pagination controls in list pages, or at minimum use infinite scroll.

---

## MEDIUM-SEVERITY FINDINGS

### 12. Inconsistent Delete Confirmation UI

**Category:** UX
**Location:** Organizations.tsx, Passwords.tsx (use `window.confirm()`), Endpoints.tsx (uses styled `DeleteConfirmationModal`)

Some pages use native browser confirm dialogs while others use the custom modal component. This creates an inconsistent user experience.

**Recommendation:** Use `DeleteConfirmationModal` everywhere.

---

### 13. No Success Notifications

**Category:** UX
**Location:** Entire frontend

No toast/notification system exists. After saving, deleting, or updating, the action completes silently. Users don't know if their action succeeded.

**Recommendation:** Add a toast notification system (e.g., react-hot-toast or shadcn/ui toast) for all mutation operations.

---

### 14. No IP/MAC Address Validation

**Category:** Data Integrity
**Location:** Network device, server, endpoint models

`ip_address` and `mac_address` fields are plain `CharField` with no validators. Users can enter invalid values like `999.999.999.999`.

**Recommendation:** Add Django validators for IP and MAC address formats.

---

### 15. CSV Import Fails on Duplicates Without Row-Level Feedback

**Category:** Workflow
**Location:** `backend/core/views.py:523-644`

If a CSV row violates a unique constraint (e.g., duplicate email), the entire import fails with a generic error. No indication of which row caused the problem.

**Recommendation:** Wrap each row in a try/except, collect per-row errors, and return a detailed report.

---

### 16. Password Encryption Uses Static Salt

**Category:** Security
**Location:** `backend/core/encryption.py:27-48`

The encryption key is derived from `SECRET_KEY` with a hardcoded salt: `b'TechVault_Password_Encryption_Salt_v1'`.

**Recommendation:** Use a per-installation random salt stored separately from the codebase.

---

### 17. Version Restore Silently Skips Missing Fields

**Category:** Bug
**Location:** `backend/core/views.py:221-260`

When restoring a version, if the model has changed since the snapshot, missing fields are silently ignored via `except: pass`. No warning to the user.

**Recommendation:** Collect skipped fields and return them in the response so users know what wasn't restored.

---

### 18. Soft Delete Restore Doesn't Validate Parent Records

**Category:** Data Integrity
**Location:** `backend/core/views.py:291-321`

Restoring a soft-deleted Contact whose Organization was also deleted creates an orphan record pointing to a deleted parent.

**Recommendation:** Check parent record status before allowing restore and warn the user if parent is also deleted.

---

### 19. HttpOnly Cookies + localStorage Token Double Auth

**Category:** Bug
**Location:** `frontend/src/services/api.ts`

The API client sends both `withCredentials: true` (cookies) AND a `Bearer` token from localStorage. This dual approach creates ambiguity about which auth mechanism is authoritative.

**Recommendation:** Pick one auth mechanism and use it consistently.

---

### 20. Endpoints Tab Race Condition

**Category:** Bug
**Location:** `frontend/src/pages/Endpoints.tsx:155-165`

If a user switches organizations while tab counts are loading, stale data from the previous org could briefly display.

**Recommendation:** Use an AbortController to cancel in-flight requests when the organization changes.

---

## LOW-SEVERITY FINDINGS

| # | Issue | Category | Location |
|---|-------|----------|----------|
| 21 | No password show/hide toggle on login/register forms | UX | Login.tsx, Register.tsx |
| 22 | No keyboard trap or Escape handling in modals | Accessibility | Settings.tsx |
| 23 | Color-only status indicators (inaccessible for colorblind) | Accessibility | Endpoints.tsx:856-866 |
| 24 | No React error boundary -- one crash takes down the app | Bug | App.tsx |
| 25 | Settings security section shows "coming soon" placeholder | UX | Settings.tsx:199 |
| 26 | Disabled delete button on current user has no tooltip | UX | Settings.tsx:312 |
| 27 | 2FA verify input accepts 50 chars with confusing placeholder | UX | TwoFactorAuth.tsx:284 |
| 28 | No change password endpoint in the API | Workflow | Missing endpoint |
| 29 | Audit logging covers only password retrieval and login | Workflow | Partial implementation |
| 30 | No bulk delete operations for large inventories | Workflow | Missing endpoint |

---

## SUMMARY

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Security | 2 | 0 | 2 | 0 |
| Workflow | 0 | 3 | 1 | 3 |
| UX/UI | 0 | 3 | 2 | 4 |
| Bugs | 1 | 2 | 3 | 1 |
| Data Integrity | 1 | 1 | 1 | 0 |
| **Total** | **4** | **9** | **9** | **8** |

---

## TOP RECOMMENDATIONS

1. **Fix multi-tenant isolation** -- Wire up the `OrganizationMember` permission checks. This is a dealbreaker for MSP use cases where client data must be isolated.
2. **Implement form validation error display** -- A single shared pattern fix that improves every form in the app.
3. **Add toast notification system** -- Silent operation completion makes the app feel unresponsive and untrustworthy.
4. **Fix the 2FA setup state management** -- Don't persist secrets until verification succeeds.
5. **Add pagination to frontend lists** -- Required for any deployment beyond a handful of records.

---

## OVERALL ASSESSMENT

The architecture and data model are solid. The codebase is well-structured with proper separation of concerns, good use of Django REST Framework patterns, and a clean React component hierarchy. The soft delete system, version history, and audit trail show thoughtful design.

The critical findings are fixable without architectural changes. The multi-tenant permission gap is the most urgent item -- the data model already supports proper isolation, it just needs to be enforced. The UX issues (validation errors, notifications, empty states) are typical of active development moving toward production polish.

For an open-source ITGlue alternative, this project has a strong foundation. Addressing the critical and high-severity items would make it suitable for production use in MSP environments.
