import streamlit as st
import json
import copy

FILENAME = "pages.json"

# Load JSON data from a file
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)

# Save JSON data to a file
def save_json(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# Recursive function to display and edit nested JSON
def display_json(data, prefix="", hierarchy_path=""):
    if isinstance(data, dict):
        for key, value in data.items():
            col1, col2 = st.columns([1,5])
            # if value != "": col1.write(key)
            unique_key = hierarchy_path + "-" + key
            if isinstance(value, (dict, list)):
                st.subheader(prefix + key)
                display_json(value, prefix + key + " > ", unique_key)
            else:
                new_value = col2.text_input(prefix + key + " Value", value, key=unique_key)
                data[key] = new_value
    elif isinstance(data, list):
        for i, item in enumerate(data):
            unique_key = hierarchy_path + f"-Item-{i}"
            is_paragraphs = all(isinstance(item, dict) and 'title' in item and 'content' in item for item in data)
            st.subheader(prefix + str(i+1))
            if isinstance(item, (dict, list)):
                display_json(item, prefix + f"{i+1} > ", unique_key)
            else:
                new_value = st.text_input(prefix + f"Item {i+1}", item, key=unique_key)
                data[i] = new_value
        
        # Add Paragraph button for "paragraphs" type lists
        if is_paragraphs and st.button("Add Paragraph", key=hierarchy_path + "-AddParagraph"):
            data.append({"title": "", "content": ""})

# Streamlit app
def main():
    # Load data into session state if it's not already loaded
    if "data" not in st.session_state:
        st.session_state.data = load_json(FILENAME)

    # Check if the loaded data is a dictionary
    if isinstance(st.session_state.data, dict):
        # For dictionaries, we can select a key from the top-level items
        selected_key = st.sidebar.selectbox("Select a top level item:", list(st.session_state.data.keys()))
        display_json(st.session_state.data[selected_key], prefix=selected_key + " > ", hierarchy_path=selected_key)

    # Check if the loaded data is a list
    elif isinstance(st.session_state.data, list):
        selected_key = st.sidebar.selectbox("Browse by:", list(st.session_state.data[0].keys()))
        values = [item[selected_key] for item in st.session_state.data]
        selected_value = st.sidebar.selectbox("Select a value:", values)
        selected_index = values.index(selected_value)
        st.title(selected_value)
        display_json(st.session_state.data[selected_index], prefix="", hierarchy_path=selected_value)

    # Save changes back to the JSON file
    st.sidebar.markdown("---")
    if st.sidebar.button("Save Changes"):
        save_json(st.session_state.data, FILENAME)
        st.success("Saved!")

if __name__ == "__main__":
    main()
