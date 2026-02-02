# Palette's Journal

## 2024-05-22 - Icon-Only Buttons and Accessibility
**Learning:** This application heavily relies on icon-only buttons for primary actions (View, Edit, PDF) in list views. These buttons completely lack accessible labels (`aria-label`) and tooltips (`title`), making them invisible to screen readers and ambiguous for some users.
**Action:** Systematically audit all icon-only buttons in list views and add descriptive `aria-label` and `title` attributes. Future components should enforce a `label` prop even for icon-only variants.
