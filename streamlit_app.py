import streamlit as st
import json
import copy

FILENAME = "pages.json"
API_CONFIG_FILENAME = "api_configuration.json"
TOPICS = "topics.json"
CATEGORIES = "categories.json"
CHART_TYPES = "chart_types.json"

def initialize():
    if "data" not in st.session_state:
        st.session_state.data = load_json(FILENAME)
    if "api_config" not in st.session_state:
        st.session_state.api_config = load_json(API_CONFIG_FILENAME)
    if "topics" not in st.session_state:
        st.session_state.topics = load_json(TOPICS)
    if "categories" not in st.session_state:
        st.session_state.categories = load_json(CATEGORIES)
    if "chart_types" not in st.session_state:
        st.session_state.chart_types = load_json(CHART_TYPES)
    if "selected_value" not in st.session_state:
        st.session_state.selected_value = ""
    if "selected_api_config" not in st.session_state:
        st.session_state.selected_api_config = 0
    if "topic_selections" not in st.session_state:
        st.session_state.topic_selections = {}
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)
def save_json(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
def handle_topic(value="", unique_key=""):
    col1, col2 = st.columns([1,5])
    col2.write("Select topics for this page:")
    # Extract the topics dictionary from the list
    topics_dict = st.session_state.topics[0]

    # Get the current selected topics from the value of the key 'topic' in your data
    selected_topics_from_file = value.split(',')

    # we want to display the checkboxes in 6 columns. We always leave column 1 empty, so we have 5 columns left. If ther are more than 5 topics, we need to add a new row
    columns = st.columns(5)
    num_topics = len(topics_dict)
    topic_idx = 0

    for topic_key, topic_name in topics_dict.items():
        default_checked = topic_name in selected_topics_from_file
        # Check if a stored state exists for this checkbox
        checkbox_key = str(unique_key) + "-" + topic_key
        if checkbox_key not in st.session_state.topic_selections:
            st.session_state.topic_selections[checkbox_key] = default_checked
        col_index = int(topic_idx) % 4 + 1
        st.session_state.topic_selections[checkbox_key] = columns[col_index].checkbox(topic_name, st.session_state.topic_selections[checkbox_key], key=checkbox_key)
        topic_idx += 1
    # Extract selected topics from session state
    selected_topics = [topic_name for topic_key, topic_name in topics_dict.items() if st.session_state.topic_selections.get(str(unique_key) + "-" + topic_key, False)]

    # Update the value based on the selected checkboxes
    new_value = ", ".join(selected_topics)
    return new_value
def handle_category(value="", unique_key=""):
    col1, col2 = st.columns([1,5])
    col2.write("Select a category for this page:")
    categories_dict = st.session_state.categories[0]
    categories_list = list(categories_dict.values())
    selected_category_from_file = value
    # If the value from the file is not in the category list, notify the user and use the default value
    if selected_category_from_file not in categories_list:
        col2.warning(f"The category '{selected_category_from_file}' from the file is not available. Please choose from the available options.")
        selected_category_from_file = categories_list[0]  # default to the first category
    # Check if a stored state exists for this radio button
    radio_key = str(unique_key) + "-category"
    if radio_key not in st.session_state.topic_selections:
        st.session_state.topic_selections[radio_key] = selected_category_from_file
    # Extract selected category from session state
    selected_category = st.session_state.topic_selections.get(radio_key, "")
    # Update the value based on the selected radio button
    new_value = col2.radio("Categories", categories_list, index=categories_list.index(selected_category) if selected_category in categories_list else 0, key=radio_key)
    st.session_state.topic_selections[radio_key] = new_value
    return new_value
def display_api_configuration(value="", unique_key=""):
        # st.write(st.session_state.selected_api_config)
    col1, col2 = st.columns([1,5])
     
    config = st.session_state.api_config[st.session_state.selected_api_config]
    with col2.expander("Chart API config details"):
        render_json(config, "API Config > ", unique_key)
def handle_chartType(value="", unique_key=""):
    col1, col2 = st.columns([1,5])
    options = [item["chart_type"] for item in st.session_state.chart_types]
    current_chart = next((index for (index, d) in enumerate(st.session_state.chart_types) if d["chart_type"] == value), None)
    col2.code("CHART TYPE: " + options[current_chart])

    new_value = col2.selectbox("Chart Type", options, current_chart, key=unique_key + "-chartType")
    col2.warning("Changing the chart type will erase current chart configuration.")
    if col2.button("Change chart type", key=unique_key):
        # Delete the current chart configuration
        del st.session_state.api_config[st.session_state.selected_api_config]

        # Retrieve a copy of the default chart configuration for the new chart type
        default_config = next((item for item in st.session_state.chart_types if item["chart_type"] == new_value), None)
        # we navigate to the key "default_settings" in the default config
        default_config = default_config["default_settings"]
        # Add a new chart configuration 
        st.session_state.api_config.append(copy.deepcopy(default_config))
        st.session_state.api_config[-1]["name"] = st.session_state.data[st.session_state.selected_article]["title"] + " // " + new_value + " chart settings"
        st.session_state.selected_api_config = len(st.session_state.api_config) - 1

        # we update page data to point to the new config
        st.write(st.session_state.selected_article)
        # st.session_state.data[st.session_state.selected_article]["config_name"] = unique_key
        # st.session_state.data[st.session_state.selected_article]["chartType"] = new_value
        st.session_state.data[st.session_state.selected_article]["sections"][0]["config_name"] = unique_key
        st.session_state.data[st.session_state.selected_article]["sections"][0]["content"]["chartType"] = new_value

        col2.success("Chart type changed to " + new_value)
        
        # we wait 1 sec
        import time
        time.sleep(1)

        st.rerun()
    else:
        new_value = value

    return new_value



def handle_selectConfig(value="", unique_key=""):
    col1, col2 = st.columns([1,5])
        
    # we find config_name possibilities
    options = [item["name"] for item in st.session_state.api_config]

    # we find the index of the option that matches config_name for current page, we default to last index if not found
    # current_config = len(st.session_state.api_config) - 1


    current_config = next((index for (index, d) in enumerate(st.session_state.api_config) if d["name"] == value), len(st.session_state.api_config) - 1)
    st.session_state.selected_api_config = current_config

    # new_value = col2.selectbox("Configuration name", options, current_config, key=unique_key)

    col2.code("CONFIG NAME: " + options[current_config])
    new_value = value   

    return new_value
def handle_text_chart_selection(value="", unique_key=""):
    col1, col2 = st.columns([1,5])
    # col1.write("Value: " + value)
    # get names from chart_types.json
    options = ['chart','text']
    # # we find which of the options is the current value, and use that index as the default index
    # current_chart = next((index for (index, d) in enumerate(options) if d == value), None)
    # col2.write("value:" + value)
    if value:
        col2.code("SECTION TYPE: " + value)
        new_value = value
        return new_value
    else:
        return None

def render_data_ux():
    selected_key = "title" #st.sidebar.selectbox("Browse by:", list(st.session_state.data[0].keys()))
    values = [item[selected_key] for item in st.session_state.data]
    selected_value = st.sidebar.selectbox("Select an article:", values, index = values.index(st.session_state.selected_value) if st.session_state.selected_value in values else 0)
    selected_index = values.index(selected_value)
    st.title(selected_value)
    # we get the index of the config name in the api_config list, by matching config_name to name
    config_index = next((index for (index, d) in enumerate(st.session_state.api_config) if d["name"] == st.session_state.data[selected_index]["sections"][0]["config_name"]), None)
    st.session_state.selected_api_config = config_index
    st.session_state.selected_article = selected_index
    render_json(st.session_state.data[selected_index], prefix="", hierarchy_path=selected_value)
def render_json(data, prefix="", hierarchy_path=""):
    if isinstance(data, dict):
        for key, value in data.items():
            col1, col2 = st.columns([1,5])
            # if value != "": col1.write(key)
            unique_key = hierarchy_path + "-" + key
            
            if isinstance(value, (dict, list)):
                st.subheader(prefix + key)
                render_json(value, prefix + key + " > ", unique_key)
            else:
                if key == "topic":
                    new_value = handle_topic(value, unique_key=unique_key)
                elif key == "category":
                    new_value = handle_category(value, unique_key=unique_key)    
                elif key == "chartType":
                    new_value = handle_chartType(value, unique_key=unique_key)
                elif key == "config_name":
                    new_value = handle_selectConfig(value, unique_key=unique_key)
                elif key == "type":
                    new_value = handle_text_chart_selection(value, unique_key=unique_key)
                else:
                    new_value = col2.text_input(prefix + key + " Value", value, key=unique_key)
                
                data[key] = new_value   

                if key == "chartType":
                    display_api_configuration(new_value, unique_key=unique_key)
               

    elif isinstance(data, list):
        for i, item in enumerate(data):
            unique_key = hierarchy_path + f"-Item-{i}"
            is_paragraphs = all(isinstance(item, dict) and 'title' in item and 'content' in item for item in data)
            st.subheader(prefix + str(i+1))
            if isinstance(item, (dict, list)):
                render_json(item, prefix + f"{i+1} > ", unique_key)
            else:
                new_value = st.text_input(prefix + f"Item {i+1}", item, key=unique_key)
                data[i] = new_value
        
        # Add Paragraph button for "paragraphs" type lists
        if is_paragraphs and st.button("Add Paragraph", key=hierarchy_path + "-AddParagraph"):
            data.append({"title": "", "content": ""})


def add_page():
    new_page = copy.deepcopy(st.session_state.data[-1])
    clear_values(new_page)
    new_page['title'] = f"New Page {len(st.session_state.data) + 1}"  # Use the length to generate a new name
    st.session_state.data.append(new_page)
    # Update the selected_value to the title of the new page
    st.session_state.selected_value = new_page['title']
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
def clone_page():
    # selected index is simply the last item in the list
    selected_index = len(st.session_state.data) - 1
    # selected_index = [item['title'] for item in st.session_state.data].index(st.session_state.selected_value)
    cloned_page = copy.deepcopy(st.session_state.data[selected_index])
    cloned_page['title'] = f"{cloned_page['title']} (Clone)"
    st.session_state.data.append(cloned_page)
    st.session_state.selected_value = cloned_page['title']


# Streamlit app
def main():
    new_pages = 0
    
    initialize()
    # Check if the loaded data is a dictionary

    render_data_ux()

    # Add a page button
    st.sidebar.markdown("---")

    if st.sidebar.button("Clone current Page"):
        clone_page()
        st.rerun()


    if st.sidebar.button("Add a blank Page"):
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
