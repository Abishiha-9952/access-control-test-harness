# Target 3 Security Fixes

## Horizontal authorization

Normal users can access only their own `/api/users/<user_id>` resource.

Administrators can access user resources as required for administration.

## Verification

The authorization regression suite verifies:

- anonymous access is rejected;
- ordinary users cannot access the admin dashboard;
- User A cannot read User B's resource;
- User A cannot modify User B's resource;
- forbidden modifications do not change persisted state;
- administrators retain administrative access.
