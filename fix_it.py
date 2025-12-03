with open("web_dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add pagination code before "# Display each complaint"
if "items_per_page = 50" not in content:
    old_text = """    # Display each complaint
    for idx, row in page_df.iterrows():"""
    
    new_text = """    # Pagination: Show 50 per page
    items_per_page = 50
    total_items = len(display_df)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
        with col_p2:
            page = st.number_input(
                f" Page (1-{total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key="complaint_page"
            )
    else:
        page = 1
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_df = display_df.iloc[start_idx:end_idx]
    
    if total_pages > 1:
        st.markdown(f"** Showing complaints {start_idx + 1} to {end_idx} of {total_items} (Page {page} of {total_pages})**")
    
    # Display each complaint
    for idx, row in page_df.iterrows():"""
    
    content = content.replace(old_text, new_text)
    print("Added pagination")

# Fix text_area
content = content.replace(
    '''st.text_area(
                    "",
                    value=str(narrative_value),
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )''',
    '''st.text_area(
                    "Complaint Narrative",
                    value=str(narrative_value),
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"narrative_{page}_{row.get(complaint_id_col, '')}_{idx}"
                )'''
)
print("Fixed text_area key")

with open("web_dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")
