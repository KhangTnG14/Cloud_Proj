const STAFF_ROLES = ['admin', 'staff', 'provider', 'creator'];

export function getUserRole(user) {
  const storedRole = localStorage.getItem('role') || '';
  const apiRole = user?.role || '';
  return (storedRole || apiRole).toLowerCase();
}

export function isRegularCustomer(user) {
  if (user?.is_staff || user?.is_superuser) return false;

  const role = getUserRole(user);
  return !STAFF_ROLES.includes(role);
}
