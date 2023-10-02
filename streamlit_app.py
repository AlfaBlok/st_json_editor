import streamlit as st
import json
import copy

FILENAME = "pages.json"
API_CONFIG_FILENAME = "api_configuration.json"
TOPICS = "topics.json"
CATEGORIES = "categories.json"


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
                if key == "config_name":
                    # st.write(st.session_state.selected_api_config)
                    config = st.session_state.api_config[st.session_state.selected_api_config]
                    with col2.expander("API Config"):
                        display_json(config, "API Config > ", unique_key)

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


def clear_values(data):
    if isinstance(data, dict):
        for key in data:
            if isinstance(data[key], (dict, list)):
                clear_values(data[key])
            else:
                data[key] = ""
    elif isinstance(data, list):
        for item in data:
            clear_values(item)

def initialize():

    if "data" not in st.session_state:
        st.session_state.data = load_json(FILENAME)

    if "api_config" not in st.session_state:
        st.session_state.api_config = load_json(API_CONFIG_FILENAME)

    if "selected_value" not in st.session_state:
        st.session_state.selected_value = ""

    if "selected_api_config" not in st.session_state:
        st.session_state.selected_api_config = 0


def handle_data():
    if isinstance(st.session_state.data, dict):
        # For dictionaries, we can select a key from the top-level items
        selected_key = st.sidebar.selectbox("Select a top level item:", list(st.session_state.data.keys()))
        # for the selected key, we check if 'config_name' is present. If so, we retrieve it.
        if 'config_name' in st.session_state.data[selected_key]:
            # we get the index of the config name in the api_config list, by matching config_name to name
            config_index = next((index for (index, d) in enumerate(st.session_state.api_config) if d["name"] == st.session_state.data[selected_key]['config_name']), None)
            st.session_state.selected_api_config = config_index
        page_data = st.session_state.data[selected_key]
        # config_data = st.session_state.api_config[config_index] if 'config_name' in st.session_state.data[selected_key] else None
        display_json(page_data, prefix=selected_key + " > ", hierarchy_path=selected_key)

    # Check if the loaded data is a list
    elif isinstance(st.session_state.data, list):
        selected_key = st.sidebar.selectbox("Browse by:", list(st.session_state.data[0].keys()))
        values = [item[selected_key] for item in st.session_state.data]
        selected_value = st.sidebar.selectbox("Select a value:", values, index = values.index(st.session_state.selected_value) if st.session_state.selected_value in values else 0)
        selected_index = values.index(selected_value)
        st.title(selected_value)
        # we get the index of the config name in the api_config list, by matching config_name to name
        config_index = next((index for (index, d) in enumerate(st.session_state.api_config) if d["name"] == st.session_state.data[selected_index]["sections"][0]["config_name"]), None)
        st.session_state.selected_api_config = config_index
        display_json(st.session_state.data[selected_index], prefix="", hierarchy_path=selected_value)


def add_page():
    new_page = copy.deepcopy(st.session_state.data[-1])
    clear_values(new_page)
    new_page['title'] = f"New Page {len(st.session_state.data) + 1}"  # Use the length to generate a new name
    st.session_state.data.append(new_page)
    # Update the selected_value to the title of the new page
    st.session_state.selected_value = new_page['title']




# Streamlit app
def main():
    new_pages = 0
    
    initialize()
    # Check if the loaded data is a dictionary

    handle_data()

    # Add a page button
    st.sidebar.markdown("---")
    if st.sidebar.button("Add a Page"):
        add_page()
        st.rerun()


    # Save changes back to the JSON file
    st.sidebar.markdown("---")
    if st.sidebar.button("Save Changes"):
        save_json(st.session_state.data, FILENAME)
        save_json(st.session_state.api_config, API_CONFIG_FILENAME)  # Save changes to the API config
        st.success("Saved!")

if __name__ == "__main__":
    main()
