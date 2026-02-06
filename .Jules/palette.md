# Palette's Journal

## 2024-05-22 - Icon-Only Buttons and Accessibility
**Learning:** This application heavily relies on icon-only buttons for primary actions (View, Edit, PDF) in list views. These buttons completely lack accessible labels (`aria-label`) and tooltips (`title`), making them invisible to screen readers and ambiguous for some users.
**Action:** Systematically audit all icon-only buttons in list views and add descriptive `aria-label` and `title` attributes. Future components should enforce a `label` prop even for icon-only variants.

## 2024-05-23 - Broken FontAwesome Icons
**Learning:** The application was using `fas fa-*` (FontAwesome) classes in `projects` and `products` templates, but FontAwesome CSS was not loaded, rendering these icons invisible. The base template loads Lucide icons.
**Action:** Replaced all legacy FontAwesome icons with Lucide icons (`data-lucide`) to ensure visibility and consistency with the design system. Future audits should check for `fas` usage and migrate to Lucide.
